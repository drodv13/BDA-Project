import os
from dotenv import load_dotenv
from google import genai

def connect_genai():
    print("Connecting to the Gemini API...")
    load_dotenv()

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key: raise RuntimeError("The Gemini API Key was not found.")

    client = genai.Client(api_key=api_key)

    if not client: raise RuntimeError("Client is None.")

    print("Connected to the Gemini API")
    return client