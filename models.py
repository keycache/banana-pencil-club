import json
import os
from collections import Counter
from enum import Enum
from typing import List, Optional

from PIL import Image
from PIL.ImageFile import ImageFile
from pydantic import BaseModel, Field

from constants import (
    GEMINI_IMAGE_GENERATION_MODEL,
    GEMINI_TEXT_GENERATION_MODEL_ACCURATE,
    STORIES_BASE_DIR,
    Audience,
    Orientation,
    PageCount,
    Style,
)
from gemini import generate_image, generate_text
from prompts import (
    get_charactersheet_image_generation_prompt,
    get_cover_image_generation_prompt,
    get_illustration_image_generation_prompt,
    get_story_generation_system_prompt,
    get_story_generation_user_prompt,
)
from utils import classify_image_aspect, generate_narration, to_kebab_case


class Page(BaseModel):
    text: str = Field(
        ..., description="Text content for the page. Maximum of 2 to 3 sentences"
    )
    illustration_prompt: str = Field(
        ...,
        description="Prompt for generating the illustration for the page. This should be detailed. Include details of the scene, characters in the scene, background, mood, colors, lighting, and more. This includes the names of the characters in the scene.",
    )
    image_path: Optional[str] = (
        None  # Field(..., description="Path to the generated illustration image")
    )


class CharacterSheet(BaseModel):
    image_path: Optional[str] = (
        None  # Field(..., description="Path to the generated character sheet image")
    )
    prompt: str = Field(
        ...,
        description="Prompt for generating character sheet. This should be detailed. Include details of the protagonist interms of clothing, features, plus more. Include details of other characters in the story. This prompt will be used to generate a character sheet comprising of the full body view of the protagonist and other characters in the story.",
    )


class CoverImage(BaseModel):
    image_path: Optional[str] = (
        None  # Field(..., description="Path to the generated cover image")
    )
    prompt: str = Field(
        ...,
        description="Prompt for generating cover image. This should be detailed. Include all the characters in the story as a collage. Include the name of the story. This prompt will be used to generate the cover image for the story.",
    )


class Story(BaseModel):
    protagonist: str = Field(..., description="Name and details of the protagonist")
    image_path: Optional[str] = (
        None  # Field(..., description="Path to the protagonist's image")
    )
    user_id: Optional[str] = (
        None  # Field(None, description="ID of the user who created the story")
    )
    page_count: PageCount = Field(..., description="Desired length of the story")
    style: Style = Field(..., description="Art style for illustrations")
    premise: str = Field(..., description="Short summary of the story")
    audience: Audience = Field(..., description="Target age group for the story")
    title: str = Field(..., description="Title of the story")
    moral: str = Field(..., description="Moral or lesson of the story")
    character_sheet: CharacterSheet = Field(
        ..., description="Character sheet for the protagonist and other characters"
    )
    cover_image: CoverImage = Field(..., description="Cover image for the story")
    pages: List[Page] = Field(
        ...,
        description="The page text and illustration prompt. The number of Pages is based on the `page_count` field. This should be detailed. Include details of the scene, characters in the scene, background, mood, colors, lighting, and more. This prompt will be used to generate the illustrations for each page of the story.",
    )

    def get_base_dir(self) -> str:
        title = to_kebab_case(self.title)
        base_dir = os.path.join(STORIES_BASE_DIR, title)
        os.makedirs(base_dir, exist_ok=True)
        return base_dir

    def get_story_file_path(self) -> str:
        return os.path.join(self.get_base_dir(), f"{to_kebab_case(self.title)}.json")

    def get_character_sheet_image_path(self) -> str:
        return os.path.join(self.get_base_dir(), "character_sheet.jpeg")

    def get_cover_image_path(self) -> str:
        return os.path.join(self.get_base_dir(), "cover_image.jpeg")

    def get_illustration_image_path(self, page_index: int) -> str:
        return os.path.join(self.get_base_dir(), f"illustration_{page_index}.jpeg")

    def get_protagonist_image_path(self) -> str:
        return os.path.join(self.get_base_dir(), f"protagonist.jpeg")

    def save(self, file_path: Optional[str] = None) -> str:
        if not file_path:
            file_path = self.get_story_file_path()
        with open(file_path, "w") as f:
            json.dump(self.model_dump(), f, indent=2)
        print(f"Story saved to {file_path}")
        return file_path

    @staticmethod
    def load(file_path: str) -> "Story":
        with open(file_path, "r") as f:
            data = json.load(f)
        return Story.model_validate(data)

    @staticmethod
    def generate_story(
        protagonist_details: str,
        page_count: PageCount,
        style: Style,
        premise: str,
        audience: Audience,
        protagonist_image: Optional[ImageFile],
        user_id: Optional[str] = None,
    ) -> "Story":
        system_prompt = get_story_generation_system_prompt(
            story_schema=Story.model_json_schema()
        )

        user_prompt = get_story_generation_user_prompt(
            protagonist_details=protagonist_details,
            page_count=page_count,
            style=style,
            premise=premise,
            audience=audience,
        )
        story: Story = generate_text(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            model_name=GEMINI_TEXT_GENERATION_MODEL_ACCURATE,
            target_model=Story,
        )
        if protagonist_image:
            protagonist_image_path = story.get_protagonist_image_path()
            protagonist_image.save(protagonist_image_path)
            story.image_path = protagonist_image_path
        else:
            print("No protagonist image provided.")
        story.user_id = user_id
        story.save()
        return story

    def generate_illustrations(self, force: bool = False) -> List[Optional[str]]:
        illustration_paths = []
        for i in range(len(self.pages)):
            illustration_path = self.generate_illustration(page_index=i, force=force)
            illustration_paths.append(illustration_path)
        return illustration_paths

    def generate_illustration(
        self, page_index: int, force: bool = False
    ) -> Optional[str]:
        page = self.pages[page_index]
        if not force and page.image_path and os.path.exists(page.image_path):
            print(
                f"Illustration for page(index) {page_index} already exists. Skipping generation."
            )
            return page.image_path

        illustration_image = generate_image(
            prompt=get_illustration_image_generation_prompt(
                image_prompt=page.illustration_prompt, image_text=page.text
            ),
            model_name=GEMINI_IMAGE_GENERATION_MODEL,
            reference_image=(
                Image.open(self.character_sheet.image_path)
                if self.character_sheet.image_path
                else None
            ),
        )
        if illustration_image:
            illustration_image_path = self.get_illustration_image_path(page_index)
            illustration_image.save(illustration_image_path)
            page.image_path = illustration_image_path
            self.save()
        else:
            print(f"Failed to generate illustration for page {page_index+1}")
        return page.image_path

    def generate_cover_image(self, force: bool = False) -> Optional[str]:
        if (
            not force
            and self.cover_image.image_path
            and os.path.exists(self.cover_image.image_path)
        ):
            print("Cover image already exists. Skipping generation.")
            return self.cover_image.image_path

        cover_image_prompt = get_cover_image_generation_prompt(
            story_title=self.title, style=self.style
        )
        print(cover_image_prompt)

        cover_image = generate_image(
            prompt=cover_image_prompt,
            model_name=GEMINI_IMAGE_GENERATION_MODEL,
            reference_image=Image.open(self.character_sheet.image_path),
        )
        if cover_image:
            cover_image_path = self.get_cover_image_path()
            cover_image.save(cover_image_path)
            self.cover_image.image_path = cover_image_path
            self.save()
        else:
            print("Failed to generate cover image")
        return self.cover_image.image_path

    def generate_character_sheet(self, force: bool = False) -> Optional[str]:
        if (
            not force
            and self.character_sheet.image_path
            and os.path.exists(self.character_sheet.image_path)
        ):
            print("Character sheet image already exists. Skipping generation.")
            return self.character_sheet.image_path
        protagonist_image = None
        if self.image_path:
            protagonist_image = self.image_path

        character_sheet_prompt = get_charactersheet_image_generation_prompt(
            character_sheet_prompt=self.character_sheet.prompt,
            style=self.style,
            protagonist_image=protagonist_image,
        )

        character_sheet_image = generate_image(
            prompt=character_sheet_prompt,
            model_name=GEMINI_IMAGE_GENERATION_MODEL,
            reference_image=(
                Image.open(protagonist_image) if protagonist_image else None
            ),
        )
        if character_sheet_image:
            character_sheet_image_path = self.get_character_sheet_image_path()
            character_sheet_image.save(character_sheet_image_path)
            self.character_sheet.image_path = character_sheet_image_path
            self.save()
        else:
            print("Failed to generate character sheet image")
        return self.character_sheet.image_path

    def get_orientation(self) -> Orientation:
        most_common = Counter(
            [
                classify_image_aspect(Image.open(page.image_path))
                for page in story.pages
                if page.image_path and os.path.exists(page.image_path)
            ]
        ).most_common()
        return Orientation(most_common[0][0]) if most_common else Orientation.UNKNOWN

    def get_missing_assets(self) -> List[str]:
        missing_assets = []
        if not self.character_sheet.image_path or not os.path.exists(
            self.character_sheet.image_path
        ):
            missing_assets.append("Character Sheet")
        if not self.cover_image.image_path or not os.path.exists(
            self.cover_image.image_path
        ):
            missing_assets.append("Cover Image")
        for i, page in enumerate(self.pages):
            if not page.image_path or not os.path.exists(page.image_path):
                missing_assets.append(f"Page {i + 1}")
        return missing_assets


def get_stories(user_id: Optional[str] = None) -> List[Story]:
    stories = []
    if not os.path.exists(STORIES_BASE_DIR):
        return stories
    for story_dir in os.listdir(STORIES_BASE_DIR):
        story_path = os.path.join(STORIES_BASE_DIR, story_dir)
        if os.path.isdir(story_path):
            story_files = [
                f
                for f in os.listdir(story_path)
                if f.endswith(".json") and os.path.isfile(os.path.join(story_path, f))
            ]
            if story_files:
                try:
                    story = Story.load(os.path.join(story_path, story_files[0]))
                    if story.user_id == user_id or story.user_id is None:
                        stories.append(story)
                except Exception as e:
                    print(f"Error loading story from {story_files[0]}: {e}")
    return stories
