import base64
import io
import mimetypes
import re
from io import BytesIO
from pathlib import Path
from typing import Any, Dict

import streamlit as st
from PIL import Image


def classify_image_aspect(image: Image.Image, threshold: float = 0.2) -> str:
    width, height = image.size
    aspect_ratio = width / height

    if abs(aspect_ratio - 1.0) < threshold:  # Within threshold of square
        return "square"
    elif aspect_ratio > 1.0:
        return "landscape"
    else:
        return "portrait"


def get_b64_for_image_path(image_path):

    path = Path(image_path)
    if not path.exists():
        raise FileNotFoundError(f"Image file not found: {image_path}")

    mime_type, _ = mimetypes.guess_type(path)
    if not mime_type or not mime_type.startswith("image/"):
        raise ValueError(f"Unsupported or unrecognized image type: {mime_type}")

    with open(path, "rb") as img_file:
        encoded = base64.b64encode(img_file.read()).decode("utf-8")

    return f"data:{mime_type};base64,{encoded}"


def set_state(key: str, value: Any):
    st.session_state[key] = value


def set_states(states: Dict[str, Any]):
    st.session_state.update(states)


def get_state(key: str, default: Any = None) -> Any:
    return st.session_state.get(key, default)


def get_image_as_bytesIO(image_path: str) -> BytesIO:
    with Image.open(image_path) as img:
        img_bytes = io.BytesIO()
        img.save(img_bytes, format=img.format)  # Preserve original format
        img_bytes.seek(0)
        return img_bytes


def to_kebab_case(input_string: str, limit=50) -> str:
    input_string = str(input_string)
    cleaned_string = re.sub(r"[^a-zA-Z0-9\s_]", "", input_string)
    kebab_string = re.sub(r"[_\s]+", "-", cleaned_string)
    return kebab_string.lower()[:limit]
