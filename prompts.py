from typing import Optional

from constants import INTEGRATE_TEXT_IN_IMAGE

STORY_GENERATOR_PROMPT_SP = """
You are a story generation assistant. Given a structured input describing a protagonist, story premise, visual style, and target page length, you will generate a children's story accordingly. Follow these rules carefully:
1. Begin with a captivating opening that introduces the protagonist and the setting.
2. Develop the story through a series of pages, each with a specific illustration prompt.
3. Ensure the story is age-appropriate, engaging, and imaginative.
4. Incorporate the specified visual style into the illustration prompts.
5. Adhere to the target page length, ensuring each page contributes to the overall narrative.
6. Conclude with a satisfying ending that wraps up the story. Ensure the story is complete and coherent and has a clear moral or lesson.
7. Ensure the protagonist resembles (in terms of features) the attached reference image.
8. Ensure there are at least 2 characters in the story including the protagonist.

Ensure the output is in valid JSON format as per the following schema:
{story_schema}

Do not include any explanations or additional text outside the JSON structure. DO NOT OMIT ANY FIELDS. DO NOT include $defs or $schema in the output. Ensure the JSON is properly formatted and can be parsed without errors.
"""

STORY_GENERATOR_PROMPT_UP = """
You are a story generation assistant. Given the below details about the story to be generated, you will generate a children's story accordingly.

Here are some of the protagonist details: {protagonist_details}
The story should be {page_count} pages long. Every page has a maximum of 3 sentences.
The art style for the illustrations should be {style}.
The story premise is as follows: {premise}
The target audience for the story is: {audience}. Adjust your language, vocabulary, and themes to be suitable for this age group.
"""


CHARACTERSHEET_IMAGE_GENERATION_PROMPT = """
Given a detailed character sheet prompt, you will generate a character sheet image for a children's story. The character sheet should include a full-body view of the protagonist and other key characters in the story. Ensure the characters are depicted in a way that reflects their personalities and roles within the story. Each of the characters is bordered with an outline. The background is white. The characters should be clearly visible and easily distinguishable from one another. All the charaters should be in a single image and should be in a collage format. The charaters should be portryed in {style} style and should be full bodied. {protagonist_image_prompt}. All the characters should have a border around their image and a name under their corresponding image within the border. These are the character details:
{character_sheet_prompt}
"""

COVER_IMAGE_GENERATION_PROMPT = """
Given a detailed cover image prompt, you will generate a cover image for a children's story. The cover image should feature all the main characters in the story in a collage format. The title of the story should be prominently displayed on the cover. The characters should be depicted in a way that reflects their personalities and roles within the story. The cover should be visually appealing and engaging, capturing the essence of the story. The characters should be clearly visible and easily distinguishable from one another. The background should be vibrant and colorful, drawing attention to the cover. The characters should be portryed in {style} style. Used the attached character sheet as a reference for the characters' appearances. The only text on the cover should be the title of the story. No other text should be present on the cover e.g Autor's name, illustrator's name, tagline, etc.
The title of the story is: {story_title}
"""

ILLUSTRATION_IMAGE_GENERATION_PROMPT = """
{image_prompt}
The text corresponding to the image is {image_text}.
Integrate the text seamlessly into the image composition. The text should be clearly legible, placed to avoid covering key visual elements or focal points. Use a bold, energetic comic book font in superhero style typography. The text should appear naturally as part of the scene, with appropriate lighting, perspective, and color contrast to maintain readability without disrupting the image's visual flow.”
"""


def get_illustration_image_generation_prompt(image_prompt: str, image_text: str) -> str:
    return (
        ILLUSTRATION_IMAGE_GENERATION_PROMPT.format(
            image_prompt=image_prompt, image_text=image_text
        )
        if INTEGRATE_TEXT_IN_IMAGE
        else image_prompt
    )


def get_story_generation_system_prompt(story_schema: str) -> str:
    return STORY_GENERATOR_PROMPT_SP.format(story_schema=story_schema)


def get_story_generation_user_prompt(
    protagonist_details: str, page_count: str, style: str, premise: str, audience: str
) -> str:
    return STORY_GENERATOR_PROMPT_UP.format(
        protagonist_details=protagonist_details,
        page_count=page_count,
        style=style,
        premise=premise,
        audience=audience,
    )


def get_charactersheet_image_generation_prompt(
    character_sheet_prompt: str, style: str, protagonist_image: Optional[str] = None
) -> str:
    protagonist_image_prompt = ""
    if protagonist_image:
        protagonist_image_prompt = (
            f" The protagonist should resemble the attached reference image"
        )
    print(protagonist_image_prompt)
    return CHARACTERSHEET_IMAGE_GENERATION_PROMPT.format(
        character_sheet_prompt=character_sheet_prompt,
        style=style,
        protagonist_image_prompt=protagonist_image_prompt,
    )


def get_cover_image_generation_prompt(style: str, story_title: str) -> str:
    return COVER_IMAGE_GENERATION_PROMPT.format(style=style, story_title=story_title)
