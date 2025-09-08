import random
import threading
from typing import List, Optional

import streamlit as st
from PIL import Image

from constants import Audience, Key, PageCount, Session, Style
from models import Story
from pages.story import make_story_app
from utils import get_image_as_bytesIO, get_state, set_state, set_states, to_kebab_case


def auto_fill_example():
    set_state(
        Key.PROTAGONIST_DETAILS,
        "Luna is a curious, adventurous girl who loves exploring the outdoors and has a magical locket.",
    )
    set_state(
        Key.PREMISE,
        "Luna discovers a magical locket that transports her to a whimsical world where she learns valuable life lesson about friendship and bravery.",
    )
    set_state(Key.AUDIENCE, random.choice(list(Audience)).value)
    set_state(Key.ART_STYLE, Style.CARTOON.value)
    set_state(Key.PAGE_COUNT, PageCount.TENish.value)
    set_state(
        Key.PROTAGONIST_IMAGE_DISPLAY,
        get_image_as_bytesIO("static/images/luna.jpeg"),
    )


def generate_story(
    protagonist_details,
    premise,
    audience,
    style,
    page_count,
    protagonist_image,
    user_id,
) -> Optional[Story]:
    print("(Thread) Starting story generation...")
    audience = Audience(audience)
    style = Style(style)
    page_count = PageCount(page_count)
    story: Story = Story.generate_story(
        protagonist_details=protagonist_details,
        premise=premise,
        audience=audience,
        style=style,
        page_count=page_count,
        protagonist_image=(
            Image.open(protagonist_image) if protagonist_image else None
        ),
        user_id=user_id,
    )
    return story


def switch_to_story_page(story: Story):
    set_state(Session.CREATE_STORY_STATE, None)
    st.switch_page(
        st.Page(
            make_story_app(story.title),
            title=story.title,
            url_path=to_kebab_case(story.title),
        )
    )


def render_create():

    st.header("Create Your Story")
    create_story_state = get_state(Session.CREATE_STORY_STATE)
    user_id = str(get_state(Session.ID))
    print(
        f"(render_create) Current create_story_state for {user_id}: {create_story_state}"
    )
    if create_story_state == "generating":
        with st.container(horizontal=True, horizontal_alignment="center"):
            print(f"(render_create) Rendering your({user_id}) generating story...")
            st.write("Generating your story, please wait...")
            story: Story = generate_story(
                protagonist_details=get_state(Key.PROTAGONIST_DETAILS),
                premise=get_state(Key.PREMISE),
                audience=get_state(Key.AUDIENCE),
                style=get_state(Key.ART_STYLE),
                page_count=get_state(Key.PAGE_COUNT),
                protagonist_image=get_state(Key.PROTAGONIST_IMAGE_DISPLAY),
                user_id=user_id,
            )
            if story is None:
                st.toast(
                    "An error occurred while generating the story. Please try again."
                )
                return
            stories: List[Story] = get_state(Session.ALL_STORIES) or []
            stories.append(story)
            set_states(
                {
                    Session.CREATE_STORY_STATE: "generated",
                    Session.ALL_STORIES: stories,
                }
            )
            st.rerun()
    elif create_story_state == "generated":
        st.toast("Story generated successfully!")
        switch_to_story_page(story=get_state(Session.ALL_STORIES)[-1])
        return

    st.info(
        "Fill in the details below to create a new story. Or, alternatively, use the **`Auto-Fill Example`** button to fill in and/or modify some example details and then click **`Generate Story`** at the bottom of the form."
    )
    st.info(
        "A default story 'Luna and the Whispering Locket' is fully generated and available for viewing in the under 'View Your Stories'(in the sidebar)."
    )
    with st.container(horizontal=True, horizontal_alignment="right"):
        st.button("Auto-Fill Example", on_click=auto_fill_example)

    with st.container(horizontal=True, border=True):
        with st.container(
            horizontal=False, vertical_alignment="distribute", border=True
        ):
            st.file_uploader(
                "Upload a reference image for the protagonist",
                type=["png", "jpg", "jpeg"],
                key="key_protagonist_image",
            )
            with st.container(
                horizontal=True,
                horizontal_alignment="center",
                vertical_alignment="center",
            ):
                image_file = get_state("key_protagonist_image") or get_state(
                    "key_protagonist_image_display"
                )
                if image_file is not None:
                    st.image(image_file, caption="Protagonist Reference Image")

        with st.container(horizontal=False, border=True):
            st.text_area(
                "Enter details about the protagonist",
                height=200,
                key="key_protagonist_details",
            )
            st.text_area("Enter the story premise", height=200, key="key_premise")
            st.selectbox(
                "Select the target audience",
                options=[member.value for member in Audience],
                key="key_audience",
            )
            st.selectbox(
                "Select the art style",
                options=[member.value for member in Style],
                key="key_art_style",
            )
            st.selectbox(
                "Select the approximate page count",
                options=[member.value for member in PageCount],
                key="key_page_count",
            )

    with st.container(horizontal=True, horizontal_alignment="right"):
        if st.button("Generate Story", type="primary"):
            print("Starting story generation...")
            set_state(Session.CREATE_STORY_STATE, "generating")
            st.rerun()


render_create()
