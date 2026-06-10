# # vision.py - Screen capture via Ollama moondream (local, no API needed)
#
# import asyncio
# import os
# import time
# import base64
# import json
# import urllib.request
# from io import BytesIO
# from dotenv import load_dotenv
# load_dotenv(override=True)
#
# from PIL import ImageGrab
#
# OLLAMA_URL   = "http://localhost:11434/api/generate"
# VISION_MODEL = "llava-phi3"
#
# # Moondream works best with direct questions, not description prompts
# DESCRIBE_PROMPT = "What is on this screen?"
#
#
# def _grab_screenshot() -> str:
#     img = ImageGrab.grab()
#     img.thumbnail((1920, 1080))
#     buffer = BytesIO()
#     img.save(buffer, format="JPEG", quality=85)
#     return base64.b64encode(buffer.getvalue()).decode("utf-8")
#
#
# class LenaVision:
#     def __init__(self):
#         self.ready = False
#         self.last_description = ""
#         self.last_capture_time = 0
#         self.cache_ttl = 8
#
#         try:
#             urllib.request.urlopen("http://localhost:11434", timeout=2)
#             self.ready = True
#             print(f"   [Vision] Ollama vision ready ({VISION_MODEL}).")
#         except Exception:
#             print("   [Vision] Ollama not running — start with: ollama serve")
#
#     async def describe_screen(self, force_fresh: bool = False) -> str:
#         if not self.ready:
#             return ""
#
#         if not force_fresh and self.last_description:
#             if time.time() - self.last_capture_time < self.cache_ttl:
#                 return self.last_description
#
#         def _run():
#             img_b64 = _grab_screenshot()
#             payload = json.dumps({
#                 "model": VISION_MODEL,
#                 "prompt": DESCRIBE_PROMPT,
#                 "images": [img_b64],
#                 "stream": False,
#                 "options": {"num_predict": 150, "temperature": 0.2},
#             }).encode("utf-8")
#
#             req = urllib.request.Request(
#                 OLLAMA_URL,
#                 data=payload,
#                 headers={"Content-Type": "application/json"},
#                 method="POST",
#             )
#             with urllib.request.urlopen(req, timeout=120) as resp:
#                 data = json.loads(resp.read().decode("utf-8"))
#                 return data.get("response", "").strip()
#
#         try:
#             result = await asyncio.to_thread(_run)
#             if result:
#                 self.last_description = result
#                 self.last_capture_time = time.time()
#                 print(f"   [Vision] {result[:80]}...")
#             else:
#                 print("   [Vision] Empty response from moondream.")
#             return result
#         except Exception as e:
#             print(f"   [Vision] Error: {e}")
#             return ""
#
#     def get_cached(self) -> str:
#         return self.last_description










# vision.py - Screen capture via Groq vision (llama-4-scout, free tier)

import asyncio
import os
import time
import base64
import json
import urllib.request
from io import BytesIO
from dotenv import load_dotenv
load_dotenv(override=True)

from PIL import ImageGrab
from groq import AsyncGroq

GROQ_VISION_KEY = os.getenv("GROQ_VISION_KEY", "")

VISION_MODEL = "meta-llama/llama-4-scout-17b-16e-instruct"

DESCRIBE_PROMPT = (
    "Describe what is on this screen in 2 short specific sentences. "
    "Mention what app, website, video, or content is visible. "
    "If you can see text, mention it. "
    "If the screen is blank or transitioning, say so."
)


def _grab_screenshot() -> str:
    """Captures screen and returns base64 JPEG string."""
    img = ImageGrab.grab()
    img.thumbnail((1920, 1080))
    buffer = BytesIO()
    img.save(buffer, format="JPEG", quality=85)
    return base64.b64encode(buffer.getvalue()).decode("utf-8")


class LenaVision:
    def __init__(self):
        self.ready = False
        self.last_description = ""
        self.last_capture_time = 0
        self.cache_ttl = 8

        if not GROQ_VISION_KEY:
            print("   [Vision] No GROQ_VISION_KEY in .env — vision disabled.")
            return

        self.client = AsyncGroq(api_key=GROQ_VISION_KEY)
        self.ready = True
        print("   [Vision] Groq vision ready (llama-4-scout).")

    async def describe_screen(self, force_fresh: bool = False) -> str:
        if not self.ready:
            return ""

        if not force_fresh and self.last_description:
            if time.time() - self.last_capture_time < self.cache_ttl:
                return self.last_description

        def _grab():
            return _grab_screenshot()

        try:
            img_b64 = await asyncio.to_thread(_grab)

            response = await self.client.chat.completions.create(
                model=VISION_MODEL,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{img_b64}"
                                }
                            },
                            {
                                "type": "text",
                                "text": DESCRIBE_PROMPT
                            }
                        ]
                    }
                ],
                max_tokens=150,
            )

            result = response.choices[0].message.content.strip()
            if result:
                self.last_description = result
                self.last_capture_time = time.time()
                print(f"   [Vision] {result[:80]}...")
            else:
                print("   [Vision] Empty response.")
            return result

        except Exception as e:
            err = str(e)
            if "429" in err:
                print(f"   [Vision] Rate limited — try again in a moment.")
            else:
                print(f"   [Vision] Error: {e}")
            return ""

    def get_cached(self) -> str:
        return self.last_description