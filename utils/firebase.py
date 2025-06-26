import firebase_admin
from firebase_admin import credentials, firestore
import os

# Always use environment variables for Firebase configuration
firebase_config = {
    "type": "service_account",
    "project_id": os.getenv("FIREBASE_PROJECT_ID"),
    "private_key_id": os.getenv("FIREBASE_PRIVATE_KEY_ID"),
    "private_key": os.getenv("FIREBASE_PRIVATE_KEY", "").replace("\\n", "\n") if os.getenv("FIREBASE_PRIVATE_KEY") else None,
    "client_email": os.getenv("FIREBASE_CLIENT_EMAIL"),
    "client_id": os.getenv("FIREBASE_CLIENT_ID"),
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": os.getenv("FIREBASE_CLIENT_X509_CERT_URL"),
    "universe_domain": "googleapis.com"
}

# Debug: Check if all required environment variables are set
required_vars = ["FIREBASE_PROJECT_ID", "FIREBASE_PRIVATE_KEY", "FIREBASE_CLIENT_EMAIL"]
missing_vars = [var for var in required_vars if not os.getenv(var)]

if missing_vars:
    print(f"Missing Firebase environment variables: {missing_vars}")
    print(f"Available environment variables: {[k for k in os.environ.keys() if 'FIREBASE' in k]}")

cred = credentials.Certificate(firebase_config)
firebase_admin.initialize_app(cred)
db = firestore.client()