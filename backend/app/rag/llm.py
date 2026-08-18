import sys

from langchain_google_genai import ChatGoogleGenerativeAI
from app.config import GOOGLE_API_KEY, MODEL_NAME


print("=" * 60)
print("LLM DEBUG")
print("=" * 60)
print("Python Executable :", sys.executable)
print("Model Name        :", MODEL_NAME)
print("API Key Loaded    :", "YES" if GOOGLE_API_KEY else "NO")

if GOOGLE_API_KEY:
    print("API Key Prefix    :", GOOGLE_API_KEY[:10] + "...")
else:
    print("API Key Prefix    : None")

print("=" * 60)


def get_llm():
    return ChatGoogleGenerativeAI(
        model=MODEL_NAME,
        google_api_key=GOOGLE_API_KEY,
        temperature=0.3,
    )