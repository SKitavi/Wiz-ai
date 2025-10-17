
from dotenv import load_dotenv
import os
import google.generativeai as genai

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("Missing GEMINI_API_KEY in .env")

genai.configure(api_key=api_key)

try:
    # ✅ Supported model name in new SDK
    model = genai.GenerativeModel("gemini-1.5-flash-latest")
    response = model.generate_content("Hello Gemini, confirm you’re working.")
    print("✅ Gemini response:", response.text)
except Exception as e:
    print("❌ Error:", e)

