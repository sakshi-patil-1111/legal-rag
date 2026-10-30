import os
from pathlib import Path
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Database Configuration
    DATABASE_URL: str = "sqlite:///./nyaay.db"

    # Firebase Configuration
    FIREBASE_PROJECT_ID: str = "nyaay-ai"
    FIREBASE_SERVICE_ACCOUNT_PATH: str = "BACKEND/secrets/serviceAccountKey.json"

    # App Settings
    ENVIRONMENT: str = "development"
    GEMINI_API_KEY: str = ""
    GROQ_API_KEY: str = ""
    GEMINI_API_KEYS: str = ""
    CIVIC_MODEL: str = "gemini-flash-lite-latest"
    RERANK_CANDIDATE_POOL: int = 30
    # Cross-encoder rerank is ~0.1s/pair on CPU and dominates retrieval latency.
    # The multi-query path gathers cheap fused candidates from every sub-query
    # (+SC), dedupes, then reranks this many of the union ONCE — instead of
    # reranking each sub-query's pool separately. Bounds worst-case rerank cost.
    RERANK_MERGED_POOL: int = 32
    # The streaming provisional search runs concurrently with the analysis LLM
    # (~2.5s) purely to produce seed chunks. Reranking a full 30-candidate pool
    # there made it the long pole of that block; a smaller pool keeps its cost
    # fully hidden behind the analysis call.
    PROVISIONAL_CANDIDATE_POOL: int = 14
    PROVISIONAL_N_RESULTS: int = 12
    MAX_SUB_QUERIES: int = 3
    RERANK_BATCH_SIZE: int = 32
    TORCH_NUM_THREADS: int = 4
    # Gemini "thinking" is ON by default and was the single largest latency cost
    # (~7s on the analysis call) while also consuming max_output_tokens, which
    # truncated structured JSON. Only "minimal" and "low" are accepted by
    # gemini-3.6-flash / gemini-flash-lite-latest — thinking_budget=0 and
    # thinking_level="none" are rejected with HTTP 400.
    # Analysis is pure structured extraction, so it runs at "minimal". Generation
    # also runs at "minimal": measured against the answer model it was both
    # faster and far more consistent than "low" (which spiked to ~21s), and RAG
    # answer quality comes from the retrieved context rather than model thinking.
    ANALYSIS_THINKING_LEVEL: str = "minimal"
    GEN_THINKING_LEVEL: str = "minimal"
    # Firebase UIDs permitted to view operational metrics. Keep empty by
    # default so metrics are never exposed accidentally.
    ADMIN_UIDS: List[str] = []

    # CORS Allowed Origins
    # Comma-separated or list of origins. Development defaults provided.
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173"
    ]

    model_config = SettingsConfigDict(
        # Load from .env at the BACKEND root directory
        env_file=os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

    @property
    def firebase_service_account_absolute_path(self) -> str:
        path_str = self.FIREBASE_SERVICE_ACCOUNT_PATH.replace("\\", "/")
        path = Path(path_str)
        if path.is_absolute():
            return str(path)

        # Derive path based on backend directory
        backend_dir = Path(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))) # BACKEND/
        workspace_dir = backend_dir.parent # Root/

        if path_str.startswith("BACKEND/"):
            # If path includes BACKEND/ prefix, resolve from workspace root
            return str((workspace_dir / path_str).resolve())
        else:
            # Otherwise resolve directly from backend root
            return str((backend_dir / path_str).resolve())

    @property
    def is_development(self) -> bool:
        return self.ENVIRONMENT.lower() == "development"

settings = Settings()
