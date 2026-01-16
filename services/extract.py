import os
from pathlib import Path
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


async def extract_plot_data(file_path: Path) -> str:
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    # Read file as bytes
    file_bytes = file_path.read_bytes()

    file_part = types.Part.from_bytes(
        data=file_bytes,
        mime_type="image/png"
    )

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[
            file_part,
            """
            You are extracting plot plan data from a construction document.

            Fields:
            - lot_no
            - block
            - address
            - model_selected
            - elevation
            - garage_swing
            - external_structure
            - optional_notes

            Rules:
            - Return ONLY valid JSON
            - Include confidence (0–1) per field
            - If multiple candidates exist, choose the most semantically correct one
            - If uncertain, lower confidence
            """
        ],
    )

    return response.text
