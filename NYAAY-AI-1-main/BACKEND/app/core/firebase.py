import os
import json
import firebase_admin
from firebase_admin import credentials
from app.core.config import settings

def initialize_firebase():
    """
    Initializes the Firebase Admin SDK using env var or service account file path.
    """
    if not firebase_admin._apps:
        # 1. Try loading credentials from FIREBASE_SERVICE_ACCOUNT_JSON environment variable
        env_json = os.getenv("FIREBASE_SERVICE_ACCOUNT_JSON")
        if env_json:
            try:
                cred_dict = json.loads(env_json)
                cred = credentials.Certificate(cred_dict)
                firebase_admin.initialize_app(cred, {
                    'projectId': settings.FIREBASE_PROJECT_ID
                })
                print("Firebase Admin SDK initialized from FIREBASE_SERVICE_ACCOUNT_JSON environment variable.")
                return
            except Exception as e:
                print(f"Failed to parse FIREBASE_SERVICE_ACCOUNT_JSON environment variable: {e}")

        # 2. Try loading credentials from file path
        cred_path = settings.firebase_service_account_absolute_path
        if os.path.exists(cred_path):
            try:
                cred = credentials.Certificate(cred_path)
                firebase_admin.initialize_app(cred, {
                    'projectId': settings.FIREBASE_PROJECT_ID
                })
                print(f"Firebase Admin SDK initialized from file: {cred_path}")
                return
            except Exception as e:
                print(f"Failed to load Firebase service account key file: {e}")

        # 3. Fallback gracefully to prevent application crash on deployment
        print("WARNING: Firebase service account credentials file not found. Running with fallback auth mode.")

