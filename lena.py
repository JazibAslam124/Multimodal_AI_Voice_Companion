# # lena.py - Main loop for Lena, German learning AI companion
# # Controls: Hold ALT_GR to speak, release to send. Press ESC to quit.
#
# import asyncio
# import os
# import re
# import numpy as np
# import pyaudio
# import keyboard
# import torch
# from dotenv import load_dotenv
# from faster_whisper import WhisperModel
#
# from brain import LenaBrain
# from tts import LenaTTS
#
# load_dotenv(override=True)
#
# # ── Config ────────────────────────────────────────────────────────────────────
# PTT_KEY      = "alt_gr"
# WHISPER_SIZE = "medium"
# WHISPER_CACHE = "models/whisper"
# SAMPLE_RATE  = 16000
# CHUNK        = int(SAMPLE_RATE * 30 / 1000)  # 30ms frames
#
# # ── STT ───────────────────────────────────────────────────────────────────────
# def load_whisper():
#     device  = "cuda" if torch.cuda.is_available() else "cpu"
#     compute = "float16" if device == "cuda" else "int8"
#     os.makedirs(WHISPER_CACHE, exist_ok=True)
#     print(f"   [STT] Loading Whisper {WHISPER_SIZE} on {device}...")
#     model = WhisperModel(WHISPER_SIZE, device=device, compute_type=compute, download_root=WHISPER_CACHE)
#     print("   [STT] Whisper ready.")
#     return model
#
# def transcribe(whisper: WhisperModel, audio_bytes: bytes) -> str:
#     arr = np.frombuffer(audio_bytes, dtype=np.int16).astype(np.float32) / 32768.0
#     segments, _ = whisper.transcribe(
#         arr,
#         beam_size=5,
#         language="en",        # English input — change to "de" when ready to speak German
#         vad_filter=True,
#         vad_parameters=dict(
#             threshold=0.80,
#             min_speech_duration_ms=300,
#             min_silence_duration_ms=500,
#         ),
#     )
#     return "".join(s.text for s in segments).strip()
#
# # ── Main ──────────────────────────────────────────────────────────────────────
# async def main():
#     print("\n╔══════════════════════════════════╗")
#     print("║        Lena — Dein Deutsch-KI    ║")
#     print("╠══════════════════════════════════╣")
#     print(f"║  Hold [{PTT_KEY.upper()}] to speak          ║")
#     print("║  Press [ESC] to quit             ║")
#     print("╚══════════════════════════════════╝\n")
#
#     whisper = await asyncio.to_thread(load_whisper)
#     brain   = LenaBrain()
#     tts     = LenaTTS()
#
#     pa     = pyaudio.PyAudio()
#     stream = pa.open(
#         format=pyaudio.paInt16,
#         channels=1,
#         rate=SAMPLE_RATE,
#         input=True,
#         frames_per_buffer=CHUNK,
#     )
#
#     recording  = False
#     frames     = []
#     processing = False   # guard — don't accept new input while Gemini is thinking
#
#     print("✅ Lena ist bereit! Los geht's.\n")
#
#     try:
#         while True:
#             # ESC to quit
#             if keyboard.is_pressed("esc"):
#                 print("\nTschüss! 👋")
#                 break
#
#             ptt_held = keyboard.is_pressed(PTT_KEY)
#
#             if ptt_held:
#                 # Interrupt Lena if she's speaking
#                 if tts.is_speaking:
#                     tts.stop()
#
#                 # Don't record while still processing last input
#                 if processing:
#                     await asyncio.sleep(0.02)
#                     continue
#
#                 if not recording:
#                     recording = True
#                     frames    = []
#                     print("🎤 Aufnahme...")
#
#                 try:
#                     data = stream.read(CHUNK, exception_on_overflow=False)
#                     frames.append(data)
#                 except OSError:
#                     pass
#
#             else:
#                 # PTT released — process whatever was recorded
#                 if recording and frames:
#                     recording  = False
#                     processing = True
#                     print("🎤 Verarbeite...")
#
#                     audio = b"".join(frames)
#                     frames = []
#
#                     # Transcribe
#                     user_text = await asyncio.to_thread(transcribe, whisper, audio)
#
#                     if not user_text or len(user_text) < 2:
#                         print("   (Nichts erkannt)\n")
#                         processing = False
#                         continue
#
#                     print(f"Du:   {user_text}")
#
#                     # Get Lena's response — only fires HERE, on PTT release
#                     response = await brain.chat(user_text)
#                     print(f"Lena: {response}\n")
#
#                     # Speak only the German part (strip [English translation])
#                     spoken = re.sub(r'\[.*?\]', '', response).strip()
#                     await tts.speak(spoken)
#
#                     processing = False
#
#             await asyncio.sleep(0.02)
#
#     finally:
#         stream.stop_stream()
#         stream.close()
#         pa.terminate()
#         print("Auf Wiedersehen!")
#
#
# if __name__ == "__main__":
#     asyncio.run(main())



































# # lena.py - Main loop for Lena AI companion
# # Controls: Hold ALT_GR to speak, release to send. Press ESC to quit.
#
# import asyncio
# import os
# import re
# import numpy as np
# import pyaudio
# import keyboard
# import torch
# from dotenv import load_dotenv
# from faster_whisper import WhisperModel
#
# from brain import LenaBrain
# from tts import LenaTTS
# from vision import LenaVision
#
# load_dotenv(override=True)
#
# # ── Config ────────────────────────────────────────────────────────────────────
# PTT_KEY       = "alt_gr"
# WHISPER_SIZE  = "medium"
# WHISPER_CACHE = "models/whisper"
# SAMPLE_RATE   = 16000
# CHUNK         = int(SAMPLE_RATE * 30 / 1000)
#
# # Vision trigger words — if user says any of these, grab a fresh screenshot
# VISION_TRIGGERS = [
#     "see", "look", "screen", "what's on", "what is on",
#     "watch", "show", "read", "describe", "what do you see",
# ]
#
# # ── STT ───────────────────────────────────────────────────────────────────────
# def load_whisper():
#     device  = "cuda" if torch.cuda.is_available() else "cpu"
#     compute = "float16" if device == "cuda" else "int8"
#     os.makedirs(WHISPER_CACHE, exist_ok=True)
#     print(f"   [STT] Loading Whisper {WHISPER_SIZE} on {device}...")
#     model = WhisperModel(WHISPER_SIZE, device=device, compute_type=compute, download_root=WHISPER_CACHE)
#     print("   [STT] Whisper ready.")
#     return model
#
# def transcribe(whisper: WhisperModel, audio_bytes: bytes) -> str:
#     arr = np.frombuffer(audio_bytes, dtype=np.int16).astype(np.float32) / 32768.0
#     segments, _ = whisper.transcribe(
#         arr,
#         beam_size=5,
#         language="en",
#         vad_filter=True,
#         vad_parameters=dict(
#             threshold=0.80,
#             min_speech_duration_ms=300,
#             min_silence_duration_ms=500,
#         ),
#     )
#     return "".join(s.text for s in segments).strip()
#
# def wants_vision(text: str) -> bool:
#     lower = text.lower()
#     return any(trigger in lower for trigger in VISION_TRIGGERS)
#
# # ── Main ──────────────────────────────────────────────────────────────────────
# async def main():
#     print("\n╔══════════════════════════════════╗")
#     print("║           Lena — AI              ║")
#     print("╠══════════════════════════════════╣")
#     print(f"║  Hold [{PTT_KEY.upper()}] to speak          ║")
#     print("║  Hold [ALT] for vision           ║")
#     print("║  Press [ESC] to quit             ║")
#     print("╚══════════════════════════════════╝\n")
#
#     whisper = await asyncio.to_thread(load_whisper)
#     brain   = LenaBrain()
#     tts     = LenaTTS()
#     vision  = LenaVision()
#
#     pa     = pyaudio.PyAudio()
#     stream = pa.open(
#         format=pyaudio.paInt16,
#         channels=1,
#         rate=SAMPLE_RATE,
#         input=True,
#         frames_per_buffer=CHUNK,
#     )
#
#     recording  = False
#     frames     = []
#     processing = False
#
#     print("✅ Lena is ready!\n")
#
#     try:
#         while True:
#             if keyboard.is_pressed("esc"):
#                 print("\nGoodbye!")
#                 break
#
#             ptt_held = keyboard.is_pressed(PTT_KEY)
#
#             if ptt_held:
#                 if tts.is_speaking:
#                     tts.stop()
#
#                 if processing:
#                     await asyncio.sleep(0.02)
#                     continue
#
#                 if not recording:
#                     recording = True
#                     frames    = []
#                     print("🎤 Recording...")
#
#                 try:
#                     data = stream.read(CHUNK, exception_on_overflow=False)
#                     frames.append(data)
#                 except OSError:
#                     pass
#
#             else:
#                 if recording and frames:
#                     recording  = False
#                     processing = True
#                     print("🎤 Processing...")
#
#                     audio = b"".join(frames)
#                     frames = []
#
#                     # Transcribe
#                     user_text = await asyncio.to_thread(transcribe, whisper, audio)
#
#                     if not user_text or len(user_text) < 2:
#                         print("   (Nothing detected)\n")
#                         processing = False
#                         continue
#
#                     print(f"You:  {user_text}")
#
#                     # Vision — only capture if user is asking about the screen
#                     # Vision — capture if vision key was held during PTT or user asks
#                     vision_context = ""
#                     if vision.ready and (keyboard.is_pressed("ctrl") or wants_vision(user_text)):
#                         print("   [Vision] Capturing screen...")
#                         vision_context = await vision.describe_screen(force_fresh=True)
#
#                     # Get response
#                     response = await brain.chat(user_text, vision_context=vision_context)
#                     print(f"Lena: {response}\n")
#
#                     await tts.speak(response)
#                     processing = False
#
#             await asyncio.sleep(0.02)
#
#     finally:
#         stream.stop_stream()
#         stream.close()
#         pa.terminate()
#         print("Goodbye!")
#
#
# if __name__ == "__main__":
#     asyncio.run(main())




























# # Best so far
#
# # lena.py - Main loop for Lena AI companion
# # Controls: Hold ALT_GR to speak, release to send.
# #           Hold TAB + ALT_GR to speak WITH vision (Lena sees your screen)
# #           Press ESC to quit.
#
# import asyncio
# import os
# import re
# import numpy as np
# import pyaudio
# import keyboard
# import torch
# from dotenv import load_dotenv
# from faster_whisper import WhisperModel
#
# from brain import LenaBrain
# from tts import LenaTTS
# from vision import LenaVision
#
# load_dotenv(override=True)
#
# # ── Config ────────────────────────────────────────────────────────────────────
# PTT_KEY       = "alt_gr"
# VISION_KEY    = "tab"
# WHISPER_SIZE  = "medium"
# WHISPER_CACHE = "models/whisper"
# SAMPLE_RATE   = 16000
# CHUNK         = int(SAMPLE_RATE * 30 / 1000)
#
# # ── STT ───────────────────────────────────────────────────────────────────────
# def load_whisper():
#     device  = "cuda" if torch.cuda.is_available() else "cpu"
#     compute = "float16" if device == "cuda" else "int8"
#     os.makedirs(WHISPER_CACHE, exist_ok=True)
#     print(f"   [STT] Loading Whisper {WHISPER_SIZE} on {device}...")
#     model = WhisperModel(WHISPER_SIZE, device=device, compute_type=compute, download_root=WHISPER_CACHE)
#     print("   [STT] Whisper ready.")
#     return model
#
# def transcribe(whisper: WhisperModel, audio_bytes: bytes) -> str:
#     arr = np.frombuffer(audio_bytes, dtype=np.int16).astype(np.float32) / 32768.0
#     segments, _ = whisper.transcribe(
#         arr,
#         beam_size=5,
#         language="en",
#         vad_filter=True,
#         vad_parameters=dict(
#             threshold=0.80,
#             min_speech_duration_ms=300,
#             min_silence_duration_ms=500,
#         ),
#     )
#     return "".join(s.text for s in segments).strip()
#
# # ── Main ──────────────────────────────────────────────────────────────────────
# async def main():
#     print("\n╔══════════════════════════════════════╗")
#     print("║           Lena — AI                  ║")
#     print("╠══════════════════════════════════════╣")
#     print(f"║  Hold [{PTT_KEY.upper()}] to speak            ║")
#     print(f"║  Hold [TAB + {PTT_KEY.upper()}] for vision    ║")
#     print("║  Press [ESC] to quit                 ║")
#     print("╚══════════════════════════════════════╝\n")
#
#     whisper = await asyncio.to_thread(load_whisper)
#     brain   = LenaBrain()
#     tts     = LenaTTS()
#     vision  = LenaVision()
#
#     pa     = pyaudio.PyAudio()
#     stream = pa.open(
#         format=pyaudio.paInt16,
#         channels=1,
#         rate=SAMPLE_RATE,
#         input=True,
#         frames_per_buffer=CHUNK,
#     )
#
#     recording      = False
#     frames         = []
#     processing     = False
#     vision_flagged = False  # was TAB held at any point during this recording?
#
#     print("✅ Lena is ready!\n")
#
#     try:
#         while True:
#             if keyboard.is_pressed("esc"):
#                 print("\nGoodbye!")
#                 break
#
#             ptt_held = keyboard.is_pressed(PTT_KEY)
#
#             if ptt_held:
#                 # Interrupt Lena if she's speaking
#                 if tts.is_speaking:
#                     tts.stop()
#
#                 if processing:
#                     await asyncio.sleep(0.02)
#                     continue
#
#                 if not recording:
#                     recording      = True
#                     frames         = []
#                     vision_flagged = False
#                     print("🎤 Recording...")
#
#                 # Check if TAB is held during recording
#                 if keyboard.is_pressed(VISION_KEY):
#                     if not vision_flagged:
#                         vision_flagged = True
#                         print("   [Vision] Vision key detected — will capture screen on send.")
#
#                 try:
#                     data = stream.read(CHUNK, exception_on_overflow=False)
#                     frames.append(data)
#                 except OSError:
#                     pass
#
#             else:
#                 if recording and frames:
#                     recording  = False
#                     processing = True
#                     print("🎤 Processing...")
#
#                     audio = b"".join(frames)
#                     frames = []
#
#                     # Transcribe
#                     user_text = await asyncio.to_thread(transcribe, whisper, audio)
#
#                     if not user_text or len(user_text) < 2:
#                         print("   (Nothing detected)\n")
#                         processing     = False
#                         vision_flagged = False
#                         continue
#
#                     print(f"You:  {user_text}")
#
#                     # Vision — only if TAB was held during recording
#                     vision_context = ""
#                     if vision.ready and vision_flagged:
#                         print("   [Vision] Capturing screen...")
#                         vision_context = await vision.describe_screen(force_fresh=True)
#                         if vision_context:
#                             print(f"   [Vision] Got: {vision_context[:60]}...")
#                         else:
#                             print("   [Vision] No description returned.")
#
#                     # Get response
#                     response = await brain.chat(user_text, vision_context=vision_context)
#                     print(f"Lena: {response}\n")
#
#                     await tts.speak(response)
#
#                     processing     = False
#                     vision_flagged = False
#
#             await asyncio.sleep(0.02)
#
#     finally:
#         stream.stop_stream()
#         stream.close()
#         pa.terminate()
#         print("Goodbye!")
#
#
# if __name__ == "__main__":
#     asyncio.run(main())



# lena.py - Main loop for Lena AI companion
# Controls: Hold ALT_GR to speak, release to send.
#           Hold TAB + ALT_GR to speak WITH vision (Lena sees your screen)
#           Press ESC to quit.




















# import asyncio
# import os
# import io
# import numpy as np
# import pyaudio
# import keyboard
# from dotenv import load_dotenv
# from groq import AsyncGroq
#
# from brain import LenaBrain
# from tts import LenaTTS
# from vision import LenaVision
#
# load_dotenv(override=True)
#
# # ── Config ────────────────────────────────────────────────────────────────────
# PTT_KEY       = "alt_gr"
# VISION_KEY    = "tab"
# SAMPLE_RATE   = 16000
# CHUNK         = int(SAMPLE_RATE * 30 / 1000)
#
# GROQ_STT_KEY  = os.getenv("GROQ_STT_KEY", "")
#
# # ── STT via Groq Whisper ──────────────────────────────────────────────────────
# async def transcribe_groq(client: AsyncGroq, audio_bytes: bytes) -> str:
#     try:
#         # Groq expects a file-like object with a name
#         audio_file = io.BytesIO(audio_bytes)
#         audio_file.name = "audio.wav"
#
#         # Write proper WAV header
#         import wave
#         wav_buffer = io.BytesIO()
#         with wave.open(wav_buffer, 'wb') as wf:
#             wf.setnchannels(1)
#             wf.setsampwidth(2)  # 16-bit
#             wf.setframerate(SAMPLE_RATE)
#             wf.writeframes(audio_bytes)
#         wav_buffer.seek(0)
#         wav_buffer.name = "audio.wav"
#
#         result = await client.audio.transcriptions.create(
#             file=wav_buffer,
#             model="whisper-large-v3",
#             language="en",
#             response_format="text",
#         )
#         return result.strip() if result else ""
#     except Exception as e:
#         print(f"   [STT] Groq transcription error: {e}")
#         return ""
#
# # ── Main ──────────────────────────────────────────────────────────────────────
# async def main():
#     print("\n╔══════════════════════════════════════╗")
#     print("║           Lena — AI                  ║")
#     print("╠══════════════════════════════════════╣")
#     print(f"║  Hold [{PTT_KEY.upper()}] to speak            ║")
#     print(f"║  Hold [TAB + {PTT_KEY.upper()}] for vision    ║")
#     print("║  Press [ESC] to quit                 ║")
#     print("╚══════════════════════════════════════╝\n")
#
#     if not GROQ_STT_KEY:
#         print("   [STT] ERROR: GROQ_STT_KEY not set in .env")
#         return
#
#     stt_client = AsyncGroq(api_key=GROQ_STT_KEY)
#     print("   [STT] Groq Whisper ready (whisper-large-v3).")
#
#     brain  = LenaBrain()
#     tts    = LenaTTS()
#     vision = LenaVision()
#
#     pa     = pyaudio.PyAudio()
#     stream = pa.open(
#         format=pyaudio.paInt16,
#         channels=1,
#         rate=SAMPLE_RATE,
#         input=True,
#         frames_per_buffer=CHUNK,
#     )
#
#     recording      = False
#     frames         = []
#     processing     = False
#     vision_flagged = False
#
#     print("✅ Lena is ready!\n")
#
#     try:
#         while True:
#             if keyboard.is_pressed("esc"):
#                 print("\nGoodbye!")
#                 break
#
#             ptt_held = keyboard.is_pressed(PTT_KEY)
#
#             if ptt_held:
#                 if tts.is_speaking:
#                     tts.stop()
#
#                 if processing:
#                     await asyncio.sleep(0.02)
#                     continue
#
#                 if not recording:
#                     recording      = True
#                     frames         = []
#                     vision_flagged = False
#                     print("🎤 Recording...")
#
#                 if keyboard.is_pressed(VISION_KEY):
#                     if not vision_flagged:
#                         vision_flagged = True
#                         print("   [Vision] Vision key detected — will capture screen on send.")
#
#                 try:
#                     data = stream.read(CHUNK, exception_on_overflow=False)
#                     frames.append(data)
#                 except OSError:
#                     pass
#
#             else:
#                 if recording and frames:
#                     recording  = False
#                     processing = True
#                     print("🎤 Processing...")
#
#                     audio = b"".join(frames)
#                     frames = []
#
#                     # Transcribe via Groq
#                     user_text = await transcribe_groq(stt_client, audio)
#
#                     if not user_text or len(user_text) < 2:
#                         print("   (Nothing detected)\n")
#                         processing     = False
#                         vision_flagged = False
#                         continue
#
#                     print(f"You:  {user_text}")
#
#                     # Vision — only if TAB was held
#                     vision_context = ""
#                     if vision.ready and vision_flagged:
#                         print("   [Vision] Capturing screen...")
#                         vision_context = await vision.describe_screen(force_fresh=True)
#                         if vision_context:
#                             print(f"   [Vision] Got: {vision_context[:60]}...")
#                         else:
#                             print("   [Vision] No description returned.")
#
#                     # Get response
#                     response = await brain.chat(user_text, vision_context=vision_context)
#                     print(f"Lena: {response}\n")
#
#                     await tts.speak(response)
#
#                     processing     = False
#                     vision_flagged = False
#
#             await asyncio.sleep(0.02)
#
#     finally:
#         stream.stop_stream()
#         stream.close()
#         pa.terminate()
#         print("Goodbye!")
#
#
# if __name__ == "__main__":
#     asyncio.run(main())

























# latest best one
# # lena.py - Main loop for Lena AI companion with memory
# # Controls: Hold ALT_GR to speak, release to send.
# #           Hold TAB + ALT_GR for vision
# #           Press ESC to quit.
#
# import asyncio
# import os
# import io
# import wave
# import numpy as np
# import pyaudio
# import keyboard
# from dotenv import load_dotenv
# from groq import AsyncGroq
#
# from brain import LenaBrain
# from tts import LenaTTS
# from vision import LenaVision
# from memory import MemoryManager
# from memory_extractor import extract_memories
#
# load_dotenv(override=True)
#
# PTT_KEY       = "alt_gr"
# VISION_KEY    = "tab"
# SAMPLE_RATE   = 16000
# CHUNK         = int(SAMPLE_RATE * 30 / 1000)
# GROQ_STT_KEY  = os.getenv("GROQ_STT_KEY", "")
#
#
# async def transcribe_groq(client: AsyncGroq, audio_bytes: bytes) -> str:
#     try:
#         wav_buffer = io.BytesIO()
#         with wave.open(wav_buffer, 'wb') as wf:
#             wf.setnchannels(1)
#             wf.setsampwidth(2)
#             wf.setframerate(SAMPLE_RATE)
#             wf.writeframes(audio_bytes)
#         wav_buffer.seek(0)
#         wav_buffer.name = "audio.wav"
#
#         result = await client.audio.transcriptions.create(
#             file=wav_buffer,
#             model="whisper-large-v3",
#             language="en",
#             response_format="text",
#         )
#         return result.strip() if result else ""
#     except Exception as e:
#         print(f"   [STT] Error: {e}")
#         return ""
#
#
# async def main():
#     print("\n╔══════════════════════════════════════╗")
#     print("║           Lena — AI                  ║")
#     print("╠══════════════════════════════════════╣")
#     print(f"║  Hold [{PTT_KEY.upper()}] to speak            ║")
#     print(f"║  Hold [TAB + {PTT_KEY.upper()}] for vision    ║")
#     print("║  Press [ESC] to quit                 ║")
#     print("╚══════════════════════════════════════╝\n")
#
#     if not GROQ_STT_KEY:
#         print("   [STT] ERROR: GROQ_STT_KEY not set in .env")
#         return
#
#     stt_client = AsyncGroq(api_key=GROQ_STT_KEY)
#     print("   [STT] Groq Whisper ready.")
#
#     brain   = LenaBrain()
#     tts     = LenaTTS()
#     vision  = LenaVision()
#     memory  = MemoryManager()
#
#     pa     = pyaudio.PyAudio()
#     stream = pa.open(
#         format=pyaudio.paInt16,
#         channels=1,
#         rate=SAMPLE_RATE,
#         input=True,
#         frames_per_buffer=CHUNK,
#     )
#
#     recording      = False
#     frames         = []
#     processing     = False
#     vision_flagged = False
#
#     print("✅ Lena is ready!\n")
#
#     try:
#         while True:
#             if keyboard.is_pressed("esc"):
#                 print("\nGoodbye!")
#                 break
#
#             ptt_held = keyboard.is_pressed(PTT_KEY)
#
#             if ptt_held:
#                 if tts.is_speaking:
#                     tts.stop()
#
#                 if processing:
#                     await asyncio.sleep(0.02)
#                     continue
#
#                 if not recording:
#                     recording      = True
#                     frames         = []
#                     vision_flagged = False
#                     print("🎤 Recording...")
#
#                 if keyboard.is_pressed(VISION_KEY):
#                     if not vision_flagged:
#                         vision_flagged = True
#                         print("   [Vision] Vision key detected.")
#
#                 try:
#                     data = stream.read(CHUNK, exception_on_overflow=False)
#                     frames.append(data)
#                 except OSError:
#                     pass
#
#             else:
#                 if recording and frames:
#                     recording  = False
#                     processing = True
#                     print("🎤 Processing...")
#
#                     audio = b"".join(frames)
#                     frames = []
#
#                     user_text = await transcribe_groq(stt_client, audio)
#
#                     if not user_text or len(user_text) < 2:
#                         print("   (Nothing detected)\n")
#                         processing     = False
#                         vision_flagged = False
#                         continue
#
#                     print(f"You:  {user_text}")
#
#                     # Vision
#                     vision_context = ""
#                     if vision.ready and vision_flagged:
#                         print("   [Vision] Capturing screen...")
#                         vision_context = await vision.describe_screen(force_fresh=True)
#
#                     # Memory retrieval
#                     memory_context = memory.get_context(user_text)
#
#                     # Get response
#                     response = await brain.chat(
#                         user_text,
#                         vision_context=vision_context,
#                         memory_context=memory_context,
#                     )
#                     print(f"Lena: {response}\n")
#
#                     await tts.speak(response)
#
#                     # Save turn and extract facts in background
#                     memory.add_turn(user_text, response)
#                     asyncio.create_task(
#                         _extract_and_store(memory, user_text, brain.history)
#                     )
#
#                     processing     = False
#                     vision_flagged = False
#
#             await asyncio.sleep(0.02)
#
#     finally:
#         stream.stop_stream()
#         stream.close()
#         pa.terminate()
#         print("Goodbye!")
#
#
# async def _extract_and_store(memory: MemoryManager, user_text: str, history: list):
#     """Background task: extract facts and store them."""
#     try:
#         facts = await extract_memories(user_text, history)
#         if facts:
#             memory.store_facts(facts)
#     except Exception as e:
#         print(f"   [Memory] Background extraction failed: {e}")
#
#
# if __name__ == "__main__":
#     asyncio.run(main())























# # lena.py - English chill mode with session memory and lore system
# # Controls: Hold ALT_GR to speak, release to send.
# #           Hold TAB + ALT_GR for vision
# #           Press ESC to quit and save session log.
#
# import asyncio
# import os
# import io
# import re
# import wave
# import glob
# import pyaudio
# import keyboard
# from datetime import datetime
# from dotenv import load_dotenv
# from groq import AsyncGroq
#
# from brain import LenaBrain
# from tts import LenaTTS
# from vision import LenaVision
# from memory import MemoryManager
# from memory_extractor import extract_memories
#
# load_dotenv(override=True)
#
# PTT_KEY          = "alt_gr"
# VISION_KEY       = "tab"
# SAMPLE_RATE      = 16000
# CHUNK            = int(SAMPLE_RATE * 30 / 1000)
# GROQ_API_KEY     = os.getenv("GROQ_API_KEY", "")
# GROQ_STT_KEY     = os.getenv("GROQ_STT_KEY", "")
# PERSONALITY_FILE = "personality_english.txt"
#
#
# # ── Startup Brief ─────────────────────────────────────────────────────────────
#
# async def generate_startup_brief(groq_client: AsyncGroq) -> str:
#     """Reads the last lore file and generates a session opening brief."""
#     lore_files = sorted(glob.glob("lore/english*.md"), key=os.path.getmtime, reverse=True)
#     if not lore_files:
#         return ""
#
#     try:
#         with open(lore_files[0], "r", encoding="utf-8") as f:
#             lore = f.read()[-4000:]
#
#         response = await groq_client.chat.completions.create(
#             model="llama-3.3-70b-versatile",
#             messages=[
#                 {
#                     "role": "system",
#                     "content": (
#                         "You are Lena, a casual AI companion. "
#                         "Write a short 1-2 sentence opening for your next session with your friend. "
#                         "Reference what you talked about last time naturally and casually. "
#                         "Sound like a friend picking up a conversation, not reading a report. "
#                         "Write in first person as Lena. Keep it under 40 words. "
#                         "Be warm but not over the top."
#                     )
#                 },
#                 {
#                     "role": "user",
#                     "content": f"Last session notes:\n{lore}\n\nWrite your opening for this session."
#                 }
#             ],
#             max_tokens=80,
#             temperature=0.8,
#         )
#         brief = response.choices[0].message.content.strip()
#         print(f"   [Brief] Generated: {brief[:60]}...")
#         return brief
#     except Exception as e:
#         print(f"   [Brief] Failed: {e}")
#         return ""
#
#
# # ── End of Session Lore ───────────────────────────────────────────────────────
#
# async def write_session_lore(groq_client: AsyncGroq, session_log: list):
#     """At end of session, generates a lore entry and saves it."""
#     if not session_log:
#         return
#
#     os.makedirs("lore", exist_ok=True)
#     date_str = datetime.now().strftime("%Y-%m-%d")
#     conversation = "\n".join(session_log[:40])
#
#     try:
#         response = await groq_client.chat.completions.create(
#             model="llama-3.3-70b-versatile",
#             messages=[
#                 {
#                     "role": "system",
#                     "content": (
#                         "You are summarizing a casual conversation session for an AI companion named Lena. "
#                         "Write 3-4 bullet points covering: main topics discussed, "
#                         "anything personal the user shared, mood/vibe of the session, "
#                         "and anything worth remembering for next time. "
#                         "Be specific. This will be used to brief Lena at the start of next session. "
#                         "Output bullet points only, no headers."
#                     )
#                 },
#                 {
#                     "role": "user",
#                     "content": f"Session date: {date_str}\n\nConversation:\n{conversation}\n\nWrite the session summary."
#                 }
#             ],
#             max_tokens=200,
#             temperature=0.3,
#         )
#         summary = response.choices[0].message.content.strip()
#
#         lore_path = "lore/english.md"
#         with open(lore_path, "a", encoding="utf-8") as f:
#             f.write(f"\n\n## Session: {date_str}\n\n")
#             f.write(summary)
#             f.write("\n")
#
#         print(f"   [Lore] Session notes saved → {lore_path}")
#
#     except Exception as e:
#         print(f"   [Lore] Failed to write lore: {e}")
#
#
# # ── Session Log ───────────────────────────────────────────────────────────────
#
# def save_session_log(session_log: list):
#     """Saves a readable session log to sessions/ folder."""
#     os.makedirs("sessions", exist_ok=True)
#     date_str = datetime.now().strftime("%Y-%m-%d_%H-%M")
#     path = os.path.join("sessions", f"english_{date_str}.txt")
#
#     with open(path, "w", encoding="utf-8") as f:
#         f.write(f"English Session\n")
#         f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
#         f.write("=" * 50 + "\n\n")
#         for entry in session_log:
#             f.write(f"{entry}\n")
#
#     print(f"   [Session] Log saved → {path}")
#
#
# # ── STT ───────────────────────────────────────────────────────────────────────
#
# async def transcribe_groq(client: AsyncGroq, audio_bytes: bytes) -> str:
#     try:
#         wav_buffer = io.BytesIO()
#         with wave.open(wav_buffer, 'wb') as wf:
#             wf.setnchannels(1)
#             wf.setsampwidth(2)
#             wf.setframerate(SAMPLE_RATE)
#             wf.writeframes(audio_bytes)
#         wav_buffer.seek(0)
#         wav_buffer.name = "audio.wav"
#         result = await client.audio.transcriptions.create(
#             file=wav_buffer,
#             model="whisper-large-v3",
#             language="en",
#             response_format="text",
#         )
#         return result.strip() if result else ""
#     except Exception as e:
#         print(f"   [STT] Error: {e}")
#         return ""
#
#
# # ── Main ──────────────────────────────────────────────────────────────────────
#
# async def main():
#     print("\n╔══════════════════════════════════════╗")
#     print("║           Lena — AI                  ║")
#     print("╠══════════════════════════════════════╣")
#     print(f"║  Hold [{PTT_KEY.upper()}] to speak            ║")
#     print(f"║  Hold [TAB + {PTT_KEY.upper()}] for vision    ║")
#     print("║  Press [ESC] to quit + save log      ║")
#     print("╚══════════════════════════════════════╝\n")
#
#     if not GROQ_STT_KEY:
#         print("   [STT] ERROR: GROQ_STT_KEY not set in .env")
#         return
#
#     stt_client  = AsyncGroq(api_key=GROQ_STT_KEY)
#     groq_client = AsyncGroq(api_key=GROQ_API_KEY)
#     print("   [STT] Groq Whisper ready.")
#
#     brain  = LenaBrain(personality_file=PERSONALITY_FILE)
#     tts    = LenaTTS()
#     vision = LenaVision()
#     memory = MemoryManager()
#
#     # Generate startup brief from last session
#     print("   [Brief] Loading last session notes...")
#     startup_brief = await generate_startup_brief(groq_client)
#
#     pa     = pyaudio.PyAudio()
#     stream = pa.open(
#         format=pyaudio.paInt16,
#         channels=1,
#         rate=SAMPLE_RATE,
#         input=True,
#         frames_per_buffer=CHUNK,
#     )
#
#     recording      = False
#     frames         = []
#     processing     = False
#     vision_flagged = False
#     first_message  = True
#
#     session_log = []
#
#     print("✅ Lena is ready!\n")
#
#     # Speak opening if we have a brief
#     if startup_brief:
#         print(f"Lena: {startup_brief}\n")
#         await tts.speak(startup_brief)
#         session_log.append(f"Lena: {startup_brief}")
#         brain.history.append({"role": "assistant", "content": startup_brief})
#
#     try:
#         while True:
#             if keyboard.is_pressed("esc"):
#                 print("\nSession ended — saving...")
#                 break
#
#             ptt_held = keyboard.is_pressed(PTT_KEY)
#
#             if ptt_held:
#                 if tts.is_speaking:
#                     tts.stop()
#
#                 if processing:
#                     await asyncio.sleep(0.02)
#                     continue
#
#                 if not recording:
#                     recording      = True
#                     frames         = []
#                     vision_flagged = False
#                     print("🎤 Recording...")
#
#                 if keyboard.is_pressed(VISION_KEY):
#                     if not vision_flagged:
#                         vision_flagged = True
#                         print("   [Vision] Vision key detected.")
#
#                 try:
#                     data = stream.read(CHUNK, exception_on_overflow=False)
#                     frames.append(data)
#                 except OSError:
#                     pass
#
#             else:
#                 if recording and frames:
#                     recording  = False
#                     processing = True
#                     print("🎤 Processing...")
#
#                     audio = b"".join(frames)
#                     frames = []
#
#                     user_text = await transcribe_groq(stt_client, audio)
#
#                     if not user_text or len(user_text) < 2:
#                         print("   (Nothing detected)\n")
#                         processing     = False
#                         vision_flagged = False
#                         continue
#
#                     print(f"You:  {user_text}")
#                     session_log.append(f"You:  {user_text}")
#
#                     # Vision
#                     vision_context = ""
#                     if vision.ready and vision_flagged:
#                         print("   [Vision] Capturing screen...")
#                         vision_context = await vision.describe_screen(force_fresh=True)
#
#                     # Memory
#                     memory_context = memory.get_context(user_text)
#
#                     # Inject startup brief into first turn
#                     if first_message and startup_brief:
#                         memory_context = f"Session opening you already said: {startup_brief}\n\n" + memory_context
#                         first_message = False
#
#                     # Get response
#                     response = await brain.chat(
#                         user_text,
#                         vision_context=vision_context,
#                         memory_context=memory_context,
#                     )
#
#                     print(f"Lena: {response}\n")
#                     session_log.append(f"Lena: {response}")
#
#                     await tts.speak(response)
#
#                     memory.add_turn(user_text, response)
#                     asyncio.create_task(
#                         _extract_and_store(memory, user_text, brain.history)
#                     )
#
#                     processing     = False
#                     vision_flagged = False
#
#             await asyncio.sleep(0.02)
#
#     finally:
#         stream.stop_stream()
#         stream.close()
#         pa.terminate()
#
#         if session_log:
#             save_session_log(session_log)
#             await write_session_lore(groq_client, session_log)
#
#         print("Goodbye!")
#
#
# async def _extract_and_store(memory: MemoryManager, user_text: str, history: list):
#     try:
#         facts = await extract_memories(user_text, history)
#         if facts:
#             memory.store_facts(facts)
#     except Exception as e:
#         print(f"   [Memory] Background extraction failed: {e}")
#
#
# if __name__ == "__main__":
#     asyncio.run(main())

















# # lena.py - English mode
# # PTT: Hold ALT_GR to speak, release to send
# # Vision: automatic heartbeat every 60s
# # Close terminal to quit
#
# import asyncio
# import io
# import os
# import re
# import wave
# import glob
# import pyaudio
# import keyboard
# from datetime import datetime
# from dotenv import load_dotenv
# from groq import AsyncGroq
#
# from brain import LenaBrain
# from tts import LenaTTS
# from vision import LenaVision
# from memory import MemoryManager
# from memory_extractor import extract_memories
#
# load_dotenv(override=True)
#
# # ── Config ────────────────────────────────────────────────────────────────────
# PTT_KEY        = "alt_gr"
# SAMPLE_RATE    = 16000
# CHUNK          = int(SAMPLE_RATE * 30 / 1000)
# VISION_INTERVAL = 30
#
# GROQ_API_KEY     = os.getenv("GROQ_API_KEY", "")
# GROQ_STT_KEY     = os.getenv("GROQ_STT_KEY", "")
# PERSONALITY_FILE = "personality_english.txt"
#
#
# # ── Startup Brief ─────────────────────────────────────────────────────────────
#
# async def generate_startup_brief(groq_client: AsyncGroq) -> str:
#     lore_files = sorted(glob.glob("lore/english*.md"), key=os.path.getmtime, reverse=True)
#     if not lore_files:
#         return ""
#     try:
#         with open(lore_files[0], "r", encoding="utf-8") as f:
#             lore = f.read()[-4000:]
#         response = await groq_client.chat.completions.create(
#             model="llama-3.3-70b-versatile",
#             messages=[
#                 {
#                     "role": "system",
#                     "content": (
#                         "You are Lena, a casual AI companion. "
#                         "Write a short 1-2 sentence opening for your next session. "
#                         "Reference what you talked about last time naturally. "
#                         "Sound like a friend picking up a conversation. Under 40 words."
#                     )
#                 },
#                 {"role": "user", "content": f"Last session:\n{lore}\n\nWrite your opening."}
#             ],
#             max_tokens=80,
#             temperature=0.8,
#         )
#         return response.choices[0].message.content.strip()
#     except Exception as e:
#         print(f"   [Brief] Failed: {e}")
#         return ""
#
#
# # ── End of Session ────────────────────────────────────────────────────────────
#
# async def write_session_lore(groq_client: AsyncGroq, session_log: list):
#     if not session_log:
#         return
#     os.makedirs("lore", exist_ok=True)
#     date_str = datetime.now().strftime("%Y-%m-%d")
#     conversation = "\n".join(session_log[:40])
#     try:
#         response = await groq_client.chat.completions.create(
#             model="llama-3.3-70b-versatile",
#             messages=[
#                 {
#                     "role": "system",
#                     "content": (
#                         "Summarize this conversation for an AI companion named Lena. "
#                         "Write 3-4 bullet points: main topics, anything personal shared, "
#                         "mood/vibe, anything worth remembering next time. Bullet points only."
#                     )
#                 },
#                 {"role": "user", "content": f"Date: {date_str}\n\n{conversation}"}
#             ],
#             max_tokens=200,
#             temperature=0.3,
#         )
#         summary = response.choices[0].message.content.strip()
#         with open("lore/english.md", "a", encoding="utf-8") as f:
#             f.write(f"\n\n## Session: {date_str}\n\n{summary}\n")
#         print(f"   [Lore] Saved → lore/english.md")
#     except Exception as e:
#         print(f"   [Lore] Failed: {e}")
#
#
# def save_session_log(session_log: list):
#     os.makedirs("sessions", exist_ok=True)
#     date_str = datetime.now().strftime("%Y-%m-%d_%H-%M")
#     path = os.path.join("sessions", f"english_{date_str}.txt")
#     with open(path, "w", encoding="utf-8") as f:
#         f.write(f"English Session\nDate: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
#         f.write("=" * 50 + "\n\n")
#         for entry in session_log:
#             f.write(f"{entry}\n")
#     print(f"   [Session] Log saved → {path}")
#
#
# # ── STT ───────────────────────────────────────────────────────────────────────
#
# async def transcribe_groq(client: AsyncGroq, audio_bytes: bytes) -> str:
#     try:
#         wav_buffer = io.BytesIO()
#         with wave.open(wav_buffer, 'wb') as wf:
#             wf.setnchannels(1)
#             wf.setsampwidth(2)
#             wf.setframerate(SAMPLE_RATE)
#             wf.writeframes(audio_bytes)
#         wav_buffer.seek(0)
#         wav_buffer.name = "audio.wav"
#         result = await client.audio.transcriptions.create(
#             file=wav_buffer,
#             model="whisper-large-v3",
#             language="en",
#             response_format="text",
#         )
#         return result.strip() if result else ""
#     except Exception as e:
#         print(f"   [STT] Error: {e}")
#         return ""
#
#
# # ── Vision Heartbeat ──────────────────────────────────────────────────────────
#
# async def vision_heartbeat(vision: LenaVision, interval: int = 60):
#     print(f"   [Vision] Heartbeat active (every {interval}s).")
#     await asyncio.sleep(10)  # wait before first capture
#     while True:
#         if vision.ready:
#             desc = await vision.describe_screen(force_fresh=True)
#             if desc:
#                 print(f"   [Vision] Updated: {desc[:60]}...")
#         await asyncio.sleep(interval)
#
#
# # ── Main ──────────────────────────────────────────────────────────────────────
#
# async def main():
#     print("\n╔══════════════════════════════════════╗")
#     print("║           Lena — AI                  ║")
#     print("╠══════════════════════════════════════╣")
#     print(f"║  Hold [{PTT_KEY.upper()}] to speak            ║")
#     print("║  Vision auto-captures every 60s      ║")
#     print("║  Close terminal to quit              ║")
#     print("╚══════════════════════════════════════╝\n")
#
#     if not GROQ_STT_KEY:
#         print("   [STT] ERROR: GROQ_STT_KEY not set in .env")
#         return
#
#     stt_client  = AsyncGroq(api_key=GROQ_STT_KEY)
#     groq_client = AsyncGroq(api_key=GROQ_API_KEY)
#
#     brain  = LenaBrain(personality_file=PERSONALITY_FILE)
#     tts    = LenaTTS()
#     vision = LenaVision()
#     memory = MemoryManager()
#
#     print("   [STT] Groq Whisper ready.")
#
#     # Startup brief
#     print("   [Brief] Loading last session notes...")
#     startup_brief = await generate_startup_brief(groq_client)
#
#     pa     = pyaudio.PyAudio()
#     stream = pa.open(
#         format=pyaudio.paInt16,
#         channels=1,
#         rate=SAMPLE_RATE,
#         input=True,
#         frames_per_buffer=CHUNK,
#     )
#
#     recording      = False
#     frames         = []
#     processing     = False
#     first_message  = True
#     session_log    = []
#
#     print("✅ Lena is ready!\n")
#
#     # Speak startup brief
#     if startup_brief:
#         print(f"Lena: {startup_brief}\n")
#         await tts.speak(startup_brief)
#         session_log.append(f"Makise: {startup_brief}")
#         brain.history.append({"role": "assistant", "content": startup_brief})
#
#     # Start vision heartbeat in background
#     asyncio.create_task(vision_heartbeat(vision, VISION_INTERVAL))
#
#     try:
#         while True:
#             ptt_held = keyboard.is_pressed(PTT_KEY)
#
#             if ptt_held:
#                 # Interrupt if speaking
#                 if tts.is_speaking:
#                     tts.stop()
#
#                 if processing:
#                     await asyncio.sleep(0.02)
#                     continue
#
#                 if not recording:
#                     recording = True
#                     frames    = []
#                     print("🎤 Recording...")
#
#                 try:
#                     data = stream.read(CHUNK, exception_on_overflow=False)
#                     frames.append(data)
#                 except OSError:
#                     pass
#
#             else:
#                 if recording and frames:
#                     recording  = False
#                     processing = True
#                     print("🎤 Processing...")
#
#                     audio = b"".join(frames)
#                     frames = []
#
#                     user_text = await transcribe_groq(stt_client, audio)
#
#                     if not user_text or len(user_text) < 2:
#                         print("   (Nothing detected)\n")
#                         processing = False
#                         continue
#
#                     print(f"You:  {user_text}")
#                     session_log.append(f"You:  {user_text}")
#
#                     # Use latest cached vision — no extra API call on speak
#                     vision_context = vision.get_cached() if vision.ready else ""
#
#                     # Memory
#                     memory_context = memory.get_context(user_text)
#                     if first_message and startup_brief:
#                         memory_context = f"Session opening you already said: {startup_brief}\n\n" + memory_context
#                         first_message = False
#
#                     # Get response
#                     response = await brain.chat(
#                         user_text,
#                         vision_context=vision_context,
#                         memory_context=memory_context,
#                     )
#
#                     print(f"Lena: {response}\n")
#                     session_log.append(f"Makise: {response}")
#
#                     await tts.speak(response)
#
#                     memory.add_turn(user_text, response)
#                     asyncio.create_task(
#                         _extract_and_store(memory, user_text, brain.history)
#                     )
#
#                     processing = False
#
#             await asyncio.sleep(0.02)
#
#     except KeyboardInterrupt:
#         print("\nShutting down...")
#     finally:
#         stream.stop_stream()
#         stream.close()
#         pa.terminate()
#         if session_log:
#             save_session_log(session_log)
#             await write_session_lore(groq_client, session_log)
#         print("Goodbye!")
#
#
# async def _extract_and_store(memory: MemoryManager, user_text: str, history: list):
#     try:
#         facts = await extract_memories(user_text, history)
#         if facts:
#             memory.store_facts(facts)
#     except Exception as e:
#         print(f"   [Memory] Background extraction failed: {e}")
#
#
# if __name__ == "__main__":
#     asyncio.run(main())


#
# # lena.py - English mode
# # PTT: Hold ALT_GR to speak, release to send
# # Vision: automatic heartbeat every 60s
# # Close terminal to quit
#
# import asyncio
# import io
# import os
# import re
# import wave
# import glob
# import pyaudio
# import keyboard
# from datetime import datetime
# from dotenv import load_dotenv
# from groq import AsyncGroq
#
# from brain import LenaBrain
# from tts import LenaTTS
# from vision import LenaVision
# from memory import MemoryManager
# from memory_extractor import extract_memories
#
# try:
#     from avatar import avatar as kira_avatar
#     AVATAR_AVAILABLE = True
# except ImportError:
#     AVATAR_AVAILABLE = False
#
# load_dotenv(override=True)
#
# # ── Config ────────────────────────────────────────────────────────────────────
# PTT_KEY        = "alt_gr"
# SAMPLE_RATE    = 16000
# CHUNK          = int(SAMPLE_RATE * 30 / 1000)
# VISION_INTERVAL = 60
#
# GROQ_API_KEY     = os.getenv("GROQ_API_KEY", "")
# GROQ_STT_KEY     = os.getenv("GROQ_STT_KEY", "")
# PERSONALITY_FILE = "personality_english.txt"
#
#
# # ── Startup Brief ─────────────────────────────────────────────────────────────
#
# async def generate_startup_brief(groq_client: AsyncGroq) -> str:
#     lore_files = sorted(glob.glob("lore/english*.md"), key=os.path.getmtime, reverse=True)
#     if not lore_files:
#         return ""
#     try:
#         with open(lore_files[0], "r", encoding="utf-8") as f:
#             lore = f.read()[-4000:]
#         response = await groq_client.chat.completions.create(
#             model="llama-3.3-70b-versatile",
#             messages=[
#                 {
#                     "role": "system",
#                     "content": (
#                         "You are Lena, a casual AI companion. "
#                         "Write a short 1-2 sentence opening for your next session. "
#                         "Reference what you talked about last time naturally. "
#                         "Sound like a friend picking up a conversation. Under 40 words."
#                     )
#                 },
#                 {"role": "user", "content": f"Last session:\n{lore}\n\nWrite your opening."}
#             ],
#             max_tokens=80,
#             temperature=0.8,
#         )
#         return response.choices[0].message.content.strip()
#     except Exception as e:
#         print(f"   [Brief] Failed: {e}")
#         return ""
#
#
# # ── End of Session ────────────────────────────────────────────────────────────
#
# async def write_session_lore(groq_client: AsyncGroq, session_log: list):
#     if not session_log:
#         return
#     os.makedirs("lore", exist_ok=True)
#     date_str = datetime.now().strftime("%Y-%m-%d")
#     conversation = "\n".join(session_log[:40])
#     try:
#         response = await groq_client.chat.completions.create(
#             model="llama-3.3-70b-versatile",
#             messages=[
#                 {
#                     "role": "system",
#                     "content": (
#                         "Summarize this conversation for an AI companion named Lena. "
#                         "Write 3-4 bullet points: main topics, anything personal shared, "
#                         "mood/vibe, anything worth remembering next time. Bullet points only."
#                     )
#                 },
#                 {"role": "user", "content": f"Date: {date_str}\n\n{conversation}"}
#             ],
#             max_tokens=200,
#             temperature=0.3,
#         )
#         summary = response.choices[0].message.content.strip()
#         with open("lore/english.md", "a", encoding="utf-8") as f:
#             f.write(f"\n\n## Session: {date_str}\n\n{summary}\n")
#         print(f"   [Lore] Saved → lore/english.md")
#     except Exception as e:
#         print(f"   [Lore] Failed: {e}")
#
#
# def save_session_log(session_log: list):
#     os.makedirs("sessions", exist_ok=True)
#     date_str = datetime.now().strftime("%Y-%m-%d_%H-%M")
#     path = os.path.join("sessions", f"english_{date_str}.txt")
#     with open(path, "w", encoding="utf-8") as f:
#         f.write(f"English Session\nDate: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
#         f.write("=" * 50 + "\n\n")
#         for entry in session_log:
#             f.write(f"{entry}\n")
#     print(f"   [Session] Log saved → {path}")
#
#
# # ── STT ───────────────────────────────────────────────────────────────────────
#
# async def transcribe_groq(client: AsyncGroq, audio_bytes: bytes) -> str:
#     try:
#         wav_buffer = io.BytesIO()
#         with wave.open(wav_buffer, 'wb') as wf:
#             wf.setnchannels(1)
#             wf.setsampwidth(2)
#             wf.setframerate(SAMPLE_RATE)
#             wf.writeframes(audio_bytes)
#         wav_buffer.seek(0)
#         wav_buffer.name = "audio.wav"
#         result = await client.audio.transcriptions.create(
#             file=wav_buffer,
#             model="whisper-large-v3",
#             language="en",
#             response_format="text",
#         )
#         return result.strip() if result else ""
#     except Exception as e:
#         print(f"   [STT] Error: {e}")
#         return ""
#
#
# # ── Vision Heartbeat ──────────────────────────────────────────────────────────
#
# async def vision_heartbeat(vision: LenaVision, interval: int = 60):
#     print(f"   [Vision] Heartbeat active (every {interval}s).")
#     await asyncio.sleep(10)  # wait before first capture
#     while True:
#         if vision.ready:
#             desc = await vision.describe_screen(force_fresh=True)
#             if desc:
#                 print(f"   [Vision] Updated: {desc[:60]}...")
#         await asyncio.sleep(interval)
#
#
# # ── Main ──────────────────────────────────────────────────────────────────────
#
# async def main():
#     print("\n╔══════════════════════════════════════╗")
#     print("║           Lena — AI                  ║")
#     print("╠══════════════════════════════════════╣")
#     print(f"║  Hold [{PTT_KEY.upper()}] to speak            ║")
#     print("║  Vision auto-captures every 60s      ║")
#     print("║  Close terminal to quit              ║")
#     print("╚══════════════════════════════════════╝\n")
#
#     if not GROQ_STT_KEY:
#         print("   [STT] ERROR: GROQ_STT_KEY not set in .env")
#         return
#
#     stt_client  = AsyncGroq(api_key=GROQ_STT_KEY)
#     groq_client = AsyncGroq(api_key=GROQ_API_KEY)
#
#     brain  = LenaBrain(personality_file=PERSONALITY_FILE)
#     tts    = LenaTTS()
#     vision = LenaVision()
#     memory = MemoryManager()
#
#     print("   [STT] Groq Whisper ready.")
#
#     # Start avatar
#     if AVATAR_AVAILABLE:
#         kira_avatar.start()
#         print("   [Avatar] Kira avatar started.")
#
#     # Startup brief
#     print("   [Brief] Loading last session notes...")
#     startup_brief = await generate_startup_brief(groq_client)
#
#     pa     = pyaudio.PyAudio()
#     stream = pa.open(
#         format=pyaudio.paInt16,
#         channels=1,
#         rate=SAMPLE_RATE,
#         input=True,
#         frames_per_buffer=CHUNK,
#     )
#
#     recording      = False
#     frames         = []
#     processing     = False
#     first_message  = True
#     session_log    = []
#
#     print("✅ Lena is ready!\n")
#
#     # Speak startup brief
#     if startup_brief:
#         print(f"Lena: {startup_brief}\n")
#         await tts.speak(startup_brief)
#         session_log.append(f"Lena: {startup_brief}")
#         brain.history.append({"role": "assistant", "content": startup_brief})
#
#     # Start vision heartbeat in background
#     asyncio.create_task(vision_heartbeat(vision, VISION_INTERVAL))
#
#     try:
#         while True:
#             ptt_held = keyboard.is_pressed(PTT_KEY)
#
#             if ptt_held:
#                 # Interrupt if speaking
#                 if tts.is_speaking:
#                     tts.stop()
#
#                 if processing:
#                     await asyncio.sleep(0.02)
#                     continue
#
#                 if not recording:
#                     recording = True
#                     frames    = []
#                     print("🎤 Recording...")
#
#                 try:
#                     data = stream.read(CHUNK, exception_on_overflow=False)
#                     frames.append(data)
#                 except OSError:
#                     pass
#
#             else:
#                 if recording and frames:
#                     recording  = False
#                     processing = True
#                     print("🎤 Processing...")
#
#                     audio = b"".join(frames)
#                     frames = []
#
#                     user_text = await transcribe_groq(stt_client, audio)
#
#                     if not user_text or len(user_text) < 2:
#                         print("   (Nothing detected)\n")
#                         processing = False
#                         continue
#
#                     print(f"You:  {user_text}")
#                     session_log.append(f"You:  {user_text}")
#
#                     # Use latest cached vision — no extra API call on speak
#                     vision_context = vision.get_cached() if vision.ready else ""
#
#                     # Memory
#                     memory_context = memory.get_context(user_text)
#                     if first_message and startup_brief:
#                         memory_context = f"Session opening you already said: {startup_brief}\n\n" + memory_context
#                         first_message = False
#
#                     # Get response
#                     response = await brain.chat(
#                         user_text,
#                         vision_context=vision_context,
#                         memory_context=memory_context,
#                     )
#
#                     print(f"Lena: {response}\n")
#                     session_log.append(f"Lena: {response}")
#
#                     await tts.speak(response)
#
#                     memory.add_turn(user_text, response)
#                     asyncio.create_task(
#                         _extract_and_store(memory, user_text, brain.history)
#                     )
#
#                     processing = False
#
#             await asyncio.sleep(0.02)
#
#     except KeyboardInterrupt:
#         print("\nShutting down...")
#     finally:
#         stream.stop_stream()
#         stream.close()
#         pa.terminate()
#         if session_log:
#             save_session_log(session_log)
#             await write_session_lore(groq_client, session_log)
#         print("Goodbye!")
#
#
# async def _extract_and_store(memory: MemoryManager, user_text: str, history: list):
#     try:
#         facts = await extract_memories(user_text, history)
#         if facts:
#             memory.store_facts(facts)
#     except Exception as e:
#         print(f"   [Memory] Background extraction failed: {e}")
#
#
# if __name__ == "__main__":
#     asyncio.run(main())



















# lena.py - English mode
# PTT: Hold ALT_GR to speak, release to send
# Vision: automatic heartbeat every 60s
# Close terminal to quit

import asyncio
import io
import os
import re
import wave
import glob
import pyaudio
import keyboard
from datetime import datetime
from dotenv import load_dotenv
from groq import AsyncGroq

from brain import LenaBrain
from tts import LenaTTS
from vision import LenaVision
from memory import MemoryManager
from memory_extractor import extract_memories

try:
    from avatar import avatar as kira_avatar
    AVATAR_AVAILABLE = True
except ImportError:
    AVATAR_AVAILABLE = False

load_dotenv(override=True)

# ── Config ────────────────────────────────────────────────────────────────────
PTT_KEY        = "alt_gr"
SAMPLE_RATE    = 16000
CHUNK          = int(SAMPLE_RATE * 30 / 1000)
VISION_INTERVAL = 60

GROQ_API_KEY     = os.getenv("GROQ_API_KEY", "")
GROQ_STT_KEY     = os.getenv("GROQ_STT_KEY", "")
PERSONALITY_FILE = "personality_english.txt"


# ── Startup Brief ─────────────────────────────────────────────────────────────

async def generate_startup_brief(groq_client: AsyncGroq) -> str:
    lore_files = sorted(glob.glob("lore/english*.md"), key=os.path.getmtime, reverse=True)
    if not lore_files:
        return ""
    try:
        with open(lore_files[0], "r", encoding="utf-8") as f:
            lore = f.read()[-4000:]
        response = await groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are Lena, a casual AI companion. "
                        "Write a short 1-2 sentence opening for your next session. "
                        "Reference what you talked about last time naturally. "
                        "Sound like a friend picking up a conversation. Under 40 words."
                    )
                },
                {"role": "user", "content": f"Last session:\n{lore}\n\nWrite your opening."}
            ],
            max_tokens=80,
            temperature=0.8,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"   [Brief] Failed: {e}")
        return ""


# ── End of Session ────────────────────────────────────────────────────────────

async def write_session_lore(groq_client: AsyncGroq, session_log: list):
    if not session_log:
        return
    os.makedirs("lore", exist_ok=True)
    date_str = datetime.now().strftime("%Y-%m-%d")
    conversation = "\n".join(session_log[:40])
    try:
        response = await groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Summarize this conversation for an AI companion named Lena. "
                        "Write 3-4 bullet points: main topics, anything personal shared, "
                        "mood/vibe, anything worth remembering next time. Bullet points only."
                    )
                },
                {"role": "user", "content": f"Date: {date_str}\n\n{conversation}"}
            ],
            max_tokens=200,
            temperature=0.3,
        )
        summary = response.choices[0].message.content.strip()
        with open("lore/english.md", "a", encoding="utf-8") as f:
            f.write(f"\n\n## Session: {date_str}\n\n{summary}\n")
        print(f"   [Lore] Saved → lore/english.md")
    except Exception as e:
        print(f"   [Lore] Failed: {e}")


def save_session_log(session_log: list):
    os.makedirs("sessions", exist_ok=True)
    date_str = datetime.now().strftime("%Y-%m-%d_%H-%M")
    path = os.path.join("sessions", f"english_{date_str}.txt")
    with open(path, "w", encoding="utf-8") as f:
        f.write(f"English Session\nDate: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
        f.write("=" * 50 + "\n\n")
        for entry in session_log:
            f.write(f"{entry}\n")
    print(f"   [Session] Log saved → {path}")


# ── STT ───────────────────────────────────────────────────────────────────────

async def transcribe_groq(client: AsyncGroq, audio_bytes: bytes) -> str:
    try:
        wav_buffer = io.BytesIO()
        with wave.open(wav_buffer, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(SAMPLE_RATE)
            wf.writeframes(audio_bytes)
        wav_buffer.seek(0)
        wav_buffer.name = "audio.wav"
        result = await client.audio.transcriptions.create(
            file=wav_buffer,
            model="whisper-large-v3",
            language="en",
            response_format="text",
        )
        return result.strip() if result else ""
    except Exception as e:
        print(f"   [STT] Error: {e}")
        return ""


# ── Vision Heartbeat ──────────────────────────────────────────────────────────

async def vision_heartbeat(vision: LenaVision, interval: int = 60):
    print(f"   [Vision] Heartbeat active (every {interval}s).")
    await asyncio.sleep(10)  # wait before first capture
    while True:
        if vision.ready:
            desc = await vision.describe_screen(force_fresh=True)
            if desc:
                print(f"   [Vision] Updated: {desc[:60]}...")
        await asyncio.sleep(interval)


# ── Main ──────────────────────────────────────────────────────────────────────

async def main():
    print("\n╔══════════════════════════════════════╗")
    print("║           Lena — AI                  ║")
    print("╠══════════════════════════════════════╣")
    print(f"║  Hold [{PTT_KEY.upper()}] to speak            ║")
    print("║  Vision auto-captures every 60s      ║")
    print("║  Close terminal to quit              ║")
    print("╚══════════════════════════════════════╝\n")

    if not GROQ_STT_KEY:
        print("   [STT] ERROR: GROQ_STT_KEY not set in .env")
        return

    stt_client  = AsyncGroq(api_key=GROQ_STT_KEY)
    groq_client = AsyncGroq(api_key=GROQ_API_KEY)

    brain  = LenaBrain(personality_file=PERSONALITY_FILE)
    tts    = LenaTTS()
    vision = LenaVision()
    memory = MemoryManager()

    print("   [STT] Groq Whisper ready.")

    # Start avatar
    if AVATAR_AVAILABLE:
        kira_avatar.start()
        print("   [Avatar] Kira avatar started.")

    # Startup brief
    print("   [Brief] Loading last session notes...")
    startup_brief = await generate_startup_brief(groq_client)

    pa     = pyaudio.PyAudio()
    stream = pa.open(
        format=pyaudio.paInt16,
        channels=1,
        rate=SAMPLE_RATE,
        input=True,
        frames_per_buffer=CHUNK,
    )

    recording      = False
    frames         = []
    processing     = False
    first_message  = True
    session_log    = []
    turn_count     = 0

    print("✅ Lena is ready!\n")

    # Speak startup brief
    if startup_brief:
        print(f"Lena: {startup_brief}\n")
        await tts.speak(startup_brief)
        session_log.append(f"Lena: {startup_brief}")
        brain.history.append({"role": "assistant", "content": startup_brief})


    try:
        while True:
            ptt_held = keyboard.is_pressed(PTT_KEY)

            if ptt_held:
                # Interrupt if speaking
                if tts.is_speaking:
                    tts.stop()

                if processing:
                    await asyncio.sleep(0.02)
                    continue

                if not recording:
                    recording = True
                    frames    = []
                    print("🎤 Recording...")

                try:
                    data = stream.read(CHUNK, exception_on_overflow=False)
                    frames.append(data)
                except OSError:
                    pass

            else:
                if recording and frames:
                    recording  = False
                    processing = True
                    print("🎤 Processing...")

                    audio = b"".join(frames)
                    frames = []

                    user_text = await transcribe_groq(stt_client, audio)

                    if not user_text or len(user_text) < 2:
                        print("   (Nothing detected)\n")
                        processing = False
                        continue

                    print(f"You:  {user_text}")
                    session_log.append(f"You:  {user_text}")

                    # Capture fresh vision on every PTT press
                    vision_context = ""
                    if vision.ready:
                        vision_context = await vision.describe_screen(force_fresh=True)

                    # Memory
                    memory_context = memory.get_context(user_text)
                    if first_message and startup_brief:
                        memory_context = f"Session opening you already said: {startup_brief}\n\n" + memory_context
                        first_message = False

                    # Get response
                    response = await brain.chat(
                        user_text,
                        vision_context=vision_context,
                        memory_context=memory_context,
                    )

                    print(f"Lena: {response}\n")
                    session_log.append(f"Lena: {response}")

                    await tts.speak(response)

                    memory.add_turn(user_text, response)
                    turn_count += 1
                    if turn_count % 5 == 0 and len(user_text) > 40:
                        asyncio.create_task(
                            _extract_and_store(memory, user_text, brain.history)
                        )

                    processing = False

            await asyncio.sleep(0.02)

    except KeyboardInterrupt:
        print("\nShutting down...")
    finally:
        stream.stop_stream()
        stream.close()
        pa.terminate()
        if session_log:
            save_session_log(session_log)
            await write_session_lore(groq_client, session_log)
        print("Goodbye!")


async def _extract_and_store(memory: MemoryManager, user_text: str, history: list):
    try:
        facts = await extract_memories(user_text, history)
        if facts:
            memory.store_facts(facts)
    except Exception as e:
        print(f"   [Memory] Background extraction failed: {e}")


if __name__ == "__main__":
    asyncio.run(main())
