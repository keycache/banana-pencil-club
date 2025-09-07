import uuid

import streamlit as st

from constants import Session
from models import Story, get_stories
from pages.story import make_story_app
from utils import get_state, set_state, to_kebab_case


def generate_session_id():
    return "16620a51-e0a2-4ab4-8416-6765b1a40011"
    return str(uuid.uuid4())


st.set_page_config(
    layout="wide",
    page_title="Banana Pencil Club",
    page_icon="static/images/banana-pencil-club-1.jpeg",
)

if get_state(Session.ID) is None:
    set_state(Session.ID, generate_session_id())

# st.write("Session ID:", get_state(Session.ID))

target_page = st.query_params.get("page", None)
print(f"Target Page: {target_page}")
stories: list[Story] = get_state(Session.ALL_STORIES)
if stories is None:
    stories = get_stories(str(get_state(Session.ID)))
    set_state(Session.ALL_STORIES, stories)
print(f"Loaded {len(stories)} stories from disk.")
pages = {
    "Overview": [
        st.Page("pages/about.py", title="About"),
    ],
    "Generate Story": [
        st.Page("pages/create.py", title="Create new story"),
    ],
    "View Your Stories": [
        st.Page(
            make_story_app(story.title),
            title=story.title,
            url_path=to_kebab_case(story.title),
        )
        for story in stories
    ],
}

pg = st.navigation(pages)
pg.run()
