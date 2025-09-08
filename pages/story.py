import json
from typing import Dict

import streamlit as st
import streamlit.components.v1 as components
from streamlit_javascript import st_javascript

from constants import HTML_TEMPLATE, Key, Session
from models import Story, get_stories
from prompts import (
    get_charactersheet_image_generation_prompt,
    get_cover_image_generation_prompt,
)
from utils import get_b64_for_image_path, get_state, set_state


def get_page_cover_image(story: Story) -> Dict[str, str]:
    return {
        "title": "",
        "image": (
            get_b64_for_image_path(story.cover_image.image_path)
            if story.cover_image.image_path
            else ""
        ),
        "text": "",
    }


def get_page_content(story: Story, page_index: int) -> Dict[str, str]:
    if page_index < 0 or page_index >= len(story.pages):
        return {"title": f"Page {page_index + 1}", "image": "", "text": "No content"}

    page = story.pages[page_index]
    return {
        "title": f"",
        "image": get_b64_for_image_path(page.image_path) if page.image_path else "",
        "text": page.text if page.text else "",
    }


def render_flipbook(story: Story):
    pages_data = [
        get_page_cover_image(story),
        *[get_page_content(story, i) for i in range(len(story.pages))],
    ]
    container_key: str = "flipbook"
    # Insert a probe element to measure container width
    components.html(
        f"""<div id="{container_key}-probe" style="width: 100%; height: 1px;"></div>""",
        height=5,
    )

    # Get the width using JavaScript
    detected_width = st_javascript(
        f"""
        const el = document.getElementById("{container_key}-probe");
        if (el) {{ return el.offsetWidth; }}
    """
    )

    # Use detected width or default
    width = (
        int(detected_width * 0.9) if detected_width else 600
    )  # 90% of container width

    # Calculate height if not provided (maintain aspect ratio)
    height = int(width * 1.4)  # Default aspect ratio

    # HTML template with replacements

    # Replace template variables
    html_content = HTML_TEMPLATE.replace("{{WIDTH}}", str(width))
    html_content = html_content.replace("{{HEIGHT}}", str(height))
    html_content = html_content.replace("{{PAGES_DATA}}", json.dumps(pages_data))

    # Render the flipbook
    components.html(html_content, height=height + 100)  # Extra height for controls


def handle_single_asset_generation(selected_asset: str, story: Story):
    if selected_asset == "Character Sheet":
        st.toast("Generating Character Sheet...")
        image_path = story.generate_character_sheet(force=True)
        set_state(Session.CHARACTER_SHEET_ASSET_VALUE, image_path)
    elif selected_asset == "Cover Image":
        st.toast("Generating Cover Image...")
        image_path = story.generate_cover_image(force=True)
        set_state(Session.COVER_IMAGE_ASSET_VALUE, image_path)
    elif selected_asset.startswith("Page"):
        page_number = int(selected_asset.split(" ")[1])
        page_index = page_number - 1
        if 0 <= page_index < len(story.pages):
            st.toast(f"Generating illustration for Page {page_number}.")
            image_path = story.generate_illustration(page_index, force=True)
            illustration_values = get_state(
                Session.PAGE_ILLUSTRATION_ASSET_VALUES, None
            )
            if illustration_values is None:
                illustration_values = [None] * len(story.pages)
            illustration_values[page_index] = image_path
            set_state(Session.PAGE_ILLUSTRATION_ASSET_VALUES, illustration_values)
        else:
            st.toast("Invalid page number selected.")
    else:
        st.toast("Unknown asset type selected.")


def handle_all_assets_generation(story: Story, force=False):
    st.toast(f"Generating all assets for story: {story.title}")

    st.toast("Generating Character Sheet...")
    character_sheet_path = story.generate_character_sheet(force=force)
    set_state(Session.CHARACTER_SHEET_ASSET_VALUE, character_sheet_path)
    st.toast("Character Sheet generated.")

    st.toast("Generating Cover Image...")
    cover_image_path = story.generate_cover_image(force=force)
    set_state(Session.COVER_IMAGE_ASSET_VALUE, cover_image_path)
    st.toast("Cover Image generated.")

    illustration_values = []
    for i in range(len(story.pages)):
        st.toast(f"Generating illustration for Page {i + 1}/{len(story.pages)}.")
        illustration_path = story.generate_illustration(i, force=force)
        illustration_values.append(illustration_path)
        st.toast(f"Illustration for Page {i + 1}/{len(story.pages)} generated.")
    set_state(Session.PAGE_ILLUSTRATION_ASSET_VALUES, illustration_values)


def get_story_by_name(story_name: str) -> Story:
    stories = get_stories(user_id=str(get_state(Session.ID)))
    for story in stories:
        if story.title == story_name:
            return story
    return None


def render_generate_assets(story_name: str):
    assets, assets_value = st.columns([3, 9])
    with assets:
        story: Story = get_story_by_name(story_name)
        story_assets = ["Character Sheet", "Cover Image"] + [
            f"Page {i + 1} Illustration" for i in range(len(story.pages))
        ]
        st.radio("Select Asset", story_assets, key=Key.GENERATE_ASSETS_SELECTED_ASSET)
    with assets_value:
        selected_asset = get_state(Key.GENERATE_ASSETS_SELECTED_ASSET)
        # st.write(f"Selected Asset: {selected_asset}")
        with st.container(horizontal=True, horizontal_alignment="right"):
            st.button(
                "Generate All Assets",
                type="secondary",
                on_click=handle_all_assets_generation,
                kwargs={"story": story},
                help="Generates all assets, irrespective of the selected asset",
            )
            st.button(
                f"Generate '{selected_asset}' Asset",
                type="primary",
                on_click=handle_single_asset_generation,
                kwargs={"selected_asset": selected_asset, "story": story},
            )
        selected_asset_path, selected_asset_prompt = None, ""

        if selected_asset == "Character Sheet":
            selected_asset_prompt = get_charactersheet_image_generation_prompt(
                character_sheet_prompt=story.character_sheet.prompt,
                style=story.style,
                protagonist_image=story.image_path,
            )
            selected_asset_path = story.character_sheet.image_path
        elif selected_asset == "Cover Image":
            selected_asset_prompt = get_cover_image_generation_prompt(
                style=story.style, story_title=story.title
            )
            selected_asset_path = story.cover_image.image_path
        elif selected_asset.startswith("Page"):
            page_number = int(selected_asset.split(" ")[1])
            page_index = page_number - 1
            illustration_values = get_state(
                Session.PAGE_ILLUSTRATION_ASSET_VALUES, None
            ) or [page.image_path for page in story.pages]
            if illustration_values is not None:
                selected_asset_prompt = story.pages[page_index].illustration_prompt
                selected_asset_path = story.pages[page_index].image_path
        # st.text_area("Asset Prompt", value=selected_asset_prompt, height=300)
        if selected_asset_path:
            st.markdown(
                "**If you do not like the below rendering, click the button again to re-generate.**"
            )
            st.image(selected_asset_path, caption=selected_asset)


def render_view_story(story_name: str):
    story = get_story_by_name(story_name)
    if not story:
        st.error("Story not found.")
        return

    missing_assets = story.get_missing_assets()
    if missing_assets:
        with st.container(horizontal=True, horizontal_alignment="right"):
            st.button(
                "Generate Missing Assets",
                type="primary",
                on_click=handle_all_assets_generation,
                kwargs={"story": story, "force": True},
            )
        st.markdown("### Missing Assets")
        st.markdown(
            "The following assets are missing. You can generate them by hitting the button above or individually from the 'Generate Assets' tab."
        )
        for asset in missing_assets:
            st.markdown(f"- {asset}")
    else:
        render_flipbook(story=story)
        # st.success("All assets have been generated for this story!")


def make_story_app(story_name: str):
    def story_app():
        st.title(f"Welcome to '{story_name}'!")
        st.info(
            "Select a tab to proceed. `Generate Assets` will provide you a list of assets to generate. Generate `Character Sheet` first (until the characters are to your liking), followed by the `Cover Image`, and then the page illustrations. The assets can be generated as many times as needed. Once all assets are generated, you can view the story in the `View Story` tab."
        )
        with st.container(horizontal=True, horizontal_alignment="center"):
            selection = st.pills(
                " ",
                ["Generate Assets", "View Story"],
                key="story_tab",
                default="Generate Assets",
            )
        with st.container():
            if selection == "Generate Assets":
                render_generate_assets(story_name=story_name)
            elif selection == "View Story":
                render_view_story(story_name=story_name)

    return story_app
