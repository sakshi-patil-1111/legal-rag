import os
import spaces
import gradio as gr
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# ── Stitch ChromaDB if needed ──────────────────────────────────────
try:
    base_dir = os.path.dirname(__file__)
    db_path = os.path.join(base_dir, "chroma_db_backup", "chroma.sqlite3")
    if not os.path.exists(db_path):
        from chroma_db_backup.stitch_db import stitch_file
        stitch_file(db_path)
except Exception as e:
    print(f"Chroma stitching note: {e}")

# ── ZeroGPU keep-alive ────────────────────────────────────────────
@spaces.GPU
def warmup_gpu():
    return "ZeroGPU Initialized & Online"

# ── Initialize backend services ────────────────────────────────────
from app.core.config import settings
from app.core.firebase import initialize_firebase
from app.database.database import Base, engine

# Ensure models are registered BEFORE create_all is called
from app.models import user, chat, document, reasoning

try:
    initialize_firebase()
    Base.metadata.create_all(bind=engine)
except Exception as e:
    print(f"Init note: {e}")

# ── Build standalone FastAPI backend ───────────────────────────────
from app.routes import auth, kanoon, upload_chat, chat as chat_routes, drafting, reasoning as reasoning_routes, admin, form_filler

backend = FastAPI(title="NYAAY AI Backend API")

backend.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

backend.include_router(auth.router,        prefix="/auth",        tags=["Authentication"])
backend.include_router(kanoon.router,      prefix="/kanoon",      tags=["Know Your Kanoon"])
backend.include_router(upload_chat.router, prefix="/upload-chat", tags=["Upload & Chat"])
backend.include_router(chat_routes.router, prefix="/chat",        tags=["Chat History"])
backend.include_router(drafting.router,    prefix="/drafting",    tags=["Drafting"])
backend.include_router(reasoning_routes.router, prefix="/reasoning",   tags=["Reasoning"])
backend.include_router(form_filler.router, prefix="/form-filler", tags=["Form Filler"])
backend.include_router(admin.router,       prefix="/admin",       tags=["Admin"])

@backend.get("/health")
async def health():
    return {"status": "ok", "environment": settings.ENVIRONMENT, "database": "configured"}

@backend.get("/ready")
async def ready():
    return {"status": "ready"}

# ── Gradio status UI ──────────────────────────────────────────────
with gr.Blocks(title="NYAAY AI — Civic Legal OS Backend", theme=gr.themes.Soft()) as demo:
    gr.Markdown("""
    # ⚖️ NYAAY AI Backend Service
    **Status: Online & Ready (NVIDIA ZeroGPU 16GB)**
    """)
    btn = gr.Button("GPU Heartbeat Check")
    out = gr.Textbox(label="Status", value="Ready")
    btn.click(warmup_gpu, outputs=out)
    demo.load(warmup_gpu, outputs=out)

# ── Monkey-patch uvicorn.Server.serve to wrap the ASGI app ─────────
import uvicorn

_original_serve = uvicorn.Server.serve

async def _patched_serve(self, *args, **kwargs):
    original_app = self.config.app

    class _Dispatcher:
        def __init__(self, gradio_app, api_app):
            self.gradio = gradio_app
            self.api = api_app

        async def __call__(self, scope, receive, send):
            if scope["type"] in ("http", "websocket"):
                path = scope.get("path", "")
                if path == "/v1" or path.startswith("/v1/"):
                    scope = dict(scope)
                    scope["path"] = path[3:] or "/"
                    scope["root_path"] = scope.get("root_path", "") + "/v1"
                    await self.api(scope, receive, send)
                    return
            await self.gradio(scope, receive, send)

    self.config.app = _Dispatcher(original_app, backend)
    return await _original_serve(self, *args, **kwargs)

uvicorn.Server.serve = _patched_serve

# ── Launch via Gradio (Preserves ZeroGPU lifecycle) ────────────────
demo.queue().launch(server_name="0.0.0.0", server_port=7860)
