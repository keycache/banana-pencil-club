import os
from io import BytesIO
from typing import Optional

from dotenv import load_dotenv
from google import genai
from google.genai import types
from PIL import Image
from PIL.ImageFile import ImageFile
from pydantic import BaseModel

from constants import GEMINI_IMAGE_GENERATION_MODEL, GEMINI_TEXT_GENERATION_MODEL_FAST

load_dotenv()
CLIENT = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


def generate_text(
    system_prompt: str,
    user_prompt: str,
    model_name: str = GEMINI_TEXT_GENERATION_MODEL_FAST,
    target_model: BaseModel = None,
) -> Optional[BaseModel]:
    config = {"response_mime_type": "application/json", "response_schema": target_model}

    contents = [
        types.Content(role="model", parts=[types.Part.from_text(text=system_prompt)]),
        types.Content(role="user", parts=[types.Part.from_text(text=user_prompt)]),
    ]
    print(f"(generate_text)Generating story with model: {model_name}")
    print(f"(generate_text)System Prompt: {system_prompt}")
    print(f"(generate_text)User Prompt: {user_prompt}")
    response = CLIENT.models.generate_content(
        model=model_name, contents=contents, config=config
    )
    print(f"(generate_text)Completed story generation.")
    return response.parsed


def generate_image(
    prompt: str,
    model_name: str = GEMINI_IMAGE_GENERATION_MODEL,
    reference_image: Optional[ImageFile] = None,
) -> Optional[ImageFile]:
    print(f"(generate_image)Generating image with model: {model_name}")
    print(f"(generate_image)Prompt: {prompt}")
    print(f"(generate_image)Reference Image: {bool(reference_image)}")

    response = CLIENT.models.generate_content(
        model=model_name,
        contents=[prompt, reference_image] if reference_image else [prompt],
    )

    for part in response.candidates[0].content.parts:
        if part.text is not None:
            print(part.text)
        elif part.inline_data is not None:
            return Image.open(BytesIO(part.inline_data.data))
