from collections import namedtuple
from enum import Enum

STORIES_BASE_DIR = ".data/stories"
GEMINI_IMAGE_GENERATION_MODEL = "models/gemini-2.5-flash-image-preview"
GEMINI_TEXT_GENERATION_MODEL_FAST = "models/gemini-2.5-flash"
GEMINI_TEXT_GENERATION_MODEL_ACCURATE = "models/gemini-2.5-pro"
INTEGRATE_TEXT_IN_IMAGE = True  # Whether to integrate text in image generation (for better text rendering in images)


class PageCount(str, Enum):
    TENish = "8-10 pages"
    TWENTYish = "15-20 pages"
    THIRTYish = "25-30 pages"


class Style(str, Enum):
    CARTOON = "Cartoon: Bold outlines, simplified shapes, and vibrant flat colors that create a playful, high-energy feel."
    REALISTIC = "Realistic: Detailed proportions, nuanced lighting, and textured rendering that aim for a lifelike, authentic depiction."
    WATERCOLOUR = "Watercolour: Soft translucent washes, organic bleeds, and gentle gradients that evoke a dreamy, storybook atmosphere."
    PENCIL_SKETCH = "Pencil Sketch: Visible graphite strokes, shading, and cross-hatching that give an intimate, hand-drawn, organic feel."
    DIGITAL_ART = "Digital Art: Clean, polished forms with smooth gradients and controlled lighting, providing a modern, versatile aesthetic."
    PIXAR_STYLE = "Pixar Style: 3D-inspired expressive characters with cinematic lighting and warm stylization balancing realism and charm."


class Audience(str, Enum):
    TODDLERS = "Toddlers (Ages 1-4)"
    PRESCHOOLERS = "Preschoolers (Ages 5-7)"
    KIDS = "Kids (Ages 7-12)"
    TEENS = "Teens (Ages 12-18)"


class Key:
    PROTAGONIST_DETAILS = "key_protagonist_details"
    PREMISE = "key_premise"
    AUDIENCE = "key_audience"
    ART_STYLE = "key_art_style"
    PAGE_COUNT = "key_page_count"
    PROTAGONIST_IMAGE = "key_protagonist_image"
    PROTAGONIST_IMAGE_DISPLAY = "key_protagonist_image_display"
    GENERATE_ASSETS_SELECTED_ASSET = "key_generate_assets_selected_asset"


class Session:
    ALL_STORIES = "session_all_stories"
    CREATE_STORY_STATE = "session_create_story_state"
    ID = "session_id"
    CHARACTER_SHEET_ASSET_VALUE = "session_character_sheet_asset_value"
    COVER_IMAGE_ASSET_VALUE = "session_cover_image_asset_value"
    PAGE_ILLUSTRATION_ASSET_VALUES = "session_page_illustration_asset_values"


class Orientation(str, Enum):
    PORTRAIT = "portrait"
    LANDSCAPE = "landscape"
    SQUARE = "square"
    UNKNOWN = "unknown"


OrientationDetails = namedtuple("OrientationDetails", ["width", "height"])
ORIENTATION_DETAILS_LOOKUP = {
    Orientation.PORTRAIT: OrientationDetails(width=1080, height=1920),
    Orientation.LANDSCAPE: OrientationDetails(width=1920, height=1080),
    Orientation.SQUARE: OrientationDetails(width=1080, height=1080),
}


HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: Arial, sans-serif;
            background: #f5f5f5;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            padding: 20px;
        }

        .flipbook-container {
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 20px;
            width: 100%;
            max-width: {{WIDTH}}px;
        }

        .flip-book {
            box-shadow: 0 0 20px rgba(0, 0, 0, 0.3);
            margin: 0 auto;
            background: #fff;
        }

        .page {
            background: #fdfaf7;
            color: #785e3a;
            border: 1px solid #c2b5a3;
            padding: 20px;
            display: flex;
            flex-direction: column;
            height: 100%;
            padding: 0;
        }

        .page-content {
            display: flex;
            flex-direction: column;
            height: 100%;
        }

        .page-header {
            font-size: 1.2em;
            text-align: center;
            margin-bottom: 15px;
            color: #785e3a;
        }

        .page-image {
            flex: 1;
            background-size: contain;
            background-position: center;
            background-repeat: no-repeat;
            margin-top: 5px;
            margin-bottom: 5px;
            min-height: 200px;
        }

        .page-text {
            font-size: 0.9em;
            text-align: justify;
            padding: 10px;
            border-top: 1px solid #f4e8d7;
            max-height: 150px;
            overflow-y: auto;
        }

        .page-footer {
            text-align: center;
            padding-top: 10px;
            font-size: 0.8em;
            color: #998466;
            border-top: 1px solid #f4e8d7;
            margin-top: auto;
        }

        .controls {
            display: flex;
            gap: 20px;
            align-items: center;
        }

        .btn {
            padding: 8px 16px;
            background: #17a2b8;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 14px;
            transition: background 0.3s;
        }

        .btn:hover {
            background: #138496;
        }

        .btn:disabled {
            background: #ccc;
            cursor: not-allowed;
        }

        .page-info {
            font-size: 14px;
            color: #666;
        }
    </style>

    <script src="https://cdn.jsdelivr.net/npm/page-flip@2.0.7/dist/js/page-flip.browser.js"></script>
</head>
<body>
    <div class="flipbook-container">
        <div class="controls">
            <button class="btn" id="prev-btn">Previous</button>
            <span class="page-info">
                Page <span id="current-page">1</span> of <span id="total-pages">1</span>
            </span>
            <button class="btn" id="next-btn">Next</button>
        </div>

        <div id="flipbook" class="flip-book">
            <!-- Pages will be inserted here -->
        </div>

    </div>

    <script>
        const CONFIG = {
            width: {{WIDTH}},
            height: {{HEIGHT}},
            pages: {{PAGES_DATA}}
        };

        document.addEventListener('DOMContentLoaded', function() {
            const flipbookElement = document.getElementById('flipbook');

            CONFIG.pages.forEach((pageData, index) => {
                const pageDiv = document.createElement('div');
                pageDiv.className = 'page';

                const content = `
                    <div class="page-content">
                        ${pageData.image ? `<div class="page-image" style="background-image: url('${pageData.image}')"></div>` : ''}
                        ${pageData.text ? `<div class="page-text">${pageData.text}</div>` : ''}
                        <div class="page-footer">${index + 1}</div>
                    </div>
                `;

                pageDiv.innerHTML = content;
                flipbookElement.appendChild(pageDiv);
            });

            const pageFlip = new St.PageFlip(flipbookElement, {
                width: CONFIG.width,
                height: CONFIG.height,
                size: 'fixed',
                maxShadowOpacity: 0.5,
                showCover: false,
                mobileScrollSupport: false,
                drawShadow: true,
                flippingTime: 1000
            });

            pageFlip.loadFromHTML(document.querySelectorAll('.page'));

            const updatePageInfo = () => {
                const currentPageNum = pageFlip.getCurrentPageIndex() + 1;
                document.getElementById('current-page').textContent = currentPageNum;
                document.getElementById('total-pages').textContent = CONFIG.pages.length;

                document.getElementById('prev-btn').disabled = currentPageNum === 1;
                document.getElementById('next-btn').disabled = currentPageNum === CONFIG.pages.length;
            };

            document.getElementById('prev-btn').addEventListener('click', () => {
                pageFlip.flipPrev();
            });

            document.getElementById('next-btn').addEventListener('click', () => {
                pageFlip.flipNext();
            });

            pageFlip.on('flip', () => {
                updatePageInfo();
            });

            updatePageInfo();
        });
    </script>
</body>
</html>
"""
