import streamlit as st

st.markdown(
    """
# About "Banana Pencil Club"
This is a simple app for generating stories using AI for kids.
With a few quick entries about your protagonist and story premise, you can generate a complete story with images.
You can upload an image of yourself or your child to be the hero of the story or savior of the day!

This app is a hackathon project built in 48 hours.

It uses:
- [Nano Banana](https://blog.google/products/gemini/updated-image-editing-model/) for image generation
- [Gemini 2.5 Flash](https://blog.google/products/gemini/introducing-gemini-2-5-flash/) for text generation
- [Streamlit](https://streamlit.io/) for the web app
- [PIL](https://github.com/python-pillow/Pillow) for image processing
- [Pydantic](https://docs.pydantic.dev/latest/) for data validation
- [St Page Flip](https://nodlik.github.io/StPageFlip/) for the flipbook component


Built by [Akash Patki](https://keycache.github.io/)
"""
)
