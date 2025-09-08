Built a kids story generator using "Gemini 2.5 Pro": for structured story generation and "Nano Banana": for image generation.  Goal is to make multi-page illustrated stories from 1 uploaded photo and a short text premise

The core challenge was maintaining the visually consistency of the protagonist(and other secondary charaters) interms of face, hair, clothes, colors across pages, while letting the scenes vary (pose, lighting, background)

Pipeline looks like this:
* "Gemini 2.5 Pro" makes structured story json using `response_schema` — includes title, moral, pages, per-page prompts, character + cover prompts
* "Nano Banana" image model runs 3-step cascade:
  * photo → character sheet: Generates a full-body reference collage of the protagonist and other story characters to precise detail.
  * character sheet → cover image: Produces a consistent, vibrant cover illustration based on the canonical design.
  * character sheet + page prompt: Each page illustration aligns perfectly with the characters' established look.

Passing the character sheet inline seemed to stabilize identity via cross-attention — less hallucination
While it's not yet real-time, the loop is fast enough for quick kid-parent iterations, which makes the experience fun and interactive.