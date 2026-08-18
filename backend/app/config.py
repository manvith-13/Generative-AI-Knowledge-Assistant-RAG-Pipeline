from dotenv import load_dotenv
import os

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "gemini")

MODEL_NAME = os.getenv("MODEL_NAME", "gemini-3.6-flash")