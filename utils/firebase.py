import firebase_admin
from firebase_admin import credentials, firestore

cred = credentials.Certificate("mood-music-2eeeb-firebase-adminsdk-fbsvc-44f9be7f67.json")

firebase_admin.initialize_app(cred)
db = firestore.client()