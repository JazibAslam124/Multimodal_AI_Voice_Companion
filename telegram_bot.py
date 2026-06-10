# # telegram_bot.py - Kira on Telegram (standalone)
# # Run: python telegram_bot.py
#
# import os
# import io
# import asyncio
# from dotenv import load_dotenv
# load_dotenv(override=True)
#
# from telegram import Update
# from telegram.ext import Application, MessageHandler, filters, ContextTypes
# from groq import AsyncGroq
#
# from brain import LenaBrain
# from memory import MemoryManager
# from memory_extractor import extract_memories
#
# TELEGRAM_TOKEN  = os.getenv("TELEGRAM_BOT_TOKEN", "")
# GROQ_STT_KEY    = os.getenv("GROQ_STT_KEY", "")
# ALLOWED_USER_ID = int(os.getenv("TELEGRAM_USER_ID", "0"))
#
#
# class KiraBot:
#     def __init__(self):
#         self.brain      = LenaBrain(personality_file="personality_english.txt")
#         self.memory     = MemoryManager()
#         self.stt        = AsyncGroq(api_key=GROQ_STT_KEY) if GROQ_STT_KEY else None
#         self.turn_count = 0
#         print("   [Telegram] Kira ready.")
#
#     def _allowed(self, update: Update) -> bool:
#         if ALLOWED_USER_ID and update.effective_user.id != ALLOWED_USER_ID:
#             return False
#         return True
#
#     async def on_text(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
#         if not self._allowed(update):
#             return
#         user_text = update.message.text.strip()
#         if not user_text:
#             return
#         print(f"You: {user_text}")
#         memory_context = self.memory.get_context(user_text)
#         response = await self.brain.chat(user_text, memory_context=memory_context)
#         print(f"Kira: {response}")
#         self.memory.add_turn(user_text, response)
#         self.turn_count += 1
#         if self.turn_count % 5 == 0 and len(user_text) > 40:
#             asyncio.create_task(self._extract(user_text))
#         await update.message.reply_text(response)
#
#     async def on_voice(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
#         if not self._allowed(update):
#             return
#         if not self.stt:
#             await update.message.reply_text("No STT key configured.")
#             return
#         voice_file  = await update.message.voice.get_file()
#         audio_bytes = bytes(await voice_file.download_as_bytearray())
#         try:
#             buf = io.BytesIO(audio_bytes)
#             buf.name = "voice.ogg"
#             result = await self.stt.audio.transcriptions.create(
#                 file=buf,
#                 model="whisper-large-v3",
#                 response_format="text",
#             )
#             user_text = result.strip() if result else ""
#         except Exception as e:
#             await update.message.reply_text(f"Transcription failed: {e}")
#             return
#         if not user_text or len(user_text) < 2:
#             await update.message.reply_text("Couldn't understand. Try again?")
#             return
#         print(f"You (voice): {user_text}")
#         memory_context = self.memory.get_context(user_text)
#         response = await self.brain.chat(user_text, memory_context=memory_context)
#         print(f"Kira: {response}")
#         self.memory.add_turn(user_text, response)
#         self.turn_count += 1
#         if self.turn_count % 5 == 0 and len(user_text) > 40:
#             asyncio.create_task(self._extract(user_text))
#         # Send voice reply
#         try:
#             import edge_tts
#             voice_name  = os.getenv("AZURE_SPEECH_VOICE", "en-US-AshleyNeural")
#             communicate = edge_tts.Communicate(response, voice_name)
#             audio_buf   = b""
#             async for chunk in communicate.stream():
#                 if chunk["type"] == "audio":
#                     audio_buf += chunk["data"]
#             if audio_buf:
#                 voice_io = io.BytesIO(audio_buf)
#                 voice_io.name = "voice.mp3"
#                 await update.message.reply_voice(voice=voice_io)
#                 await update.message.reply_text(response)
#                 return
#         except Exception as e:
#             print(f"   [TTS] Voice reply failed: {e}")
#         await update.message.reply_text(response)
#
#     async def _extract(self, user_text: str):
#         try:
#             facts = await extract_memories(user_text, self.brain.history)
#             if facts:
#                 self.memory.store_facts(facts)
#         except Exception as e:
#             print(f"   [Memory] {e}")
#
#
# def main():
#     if not TELEGRAM_TOKEN:
#         print("❌ TELEGRAM_BOT_TOKEN not set in .env")
#         return
#
#     print("\n=== Kira Telegram Bot ===")
#     print("Send a message to your bot on Telegram.\n")
#
#     kira = KiraBot()
#     app  = Application.builder().token(TELEGRAM_TOKEN).build()
#     app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, kira.on_text))
#     app.add_handler(MessageHandler(filters.VOICE, kira.on_voice))
#
#     print("✅ Kira is online!")
#     app.run_polling(drop_pending_updates=True)
#
#
# if __name__ == "__main__":
#     main()
















# telegram_bot.py - Kira on Telegram (standalone)
# Run: python telegram_bot.py

import os
import io
import asyncio
from dotenv import load_dotenv
load_dotenv(override=True)

from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
from groq import AsyncGroq

from brain import LenaBrain
from memory import MemoryManager
from memory_extractor import extract_memories

TELEGRAM_TOKEN  = os.getenv("TELEGRAM_BOT_TOKEN", "")
AZURE_KEY       = os.getenv("AZURE_SPEECH_KEY", "")
AZURE_REGION    = os.getenv("AZURE_SPEECH_REGION", "westeurope")
AZURE_VOICE     = os.getenv("AZURE_SPEECH_VOICE", "en-US-AshleyNeural")
AZURE_RATE      = os.getenv("AZURE_PROSODY_RATE", "25%")
AZURE_PITCH     = os.getenv("AZURE_PROSODY_PITCH", "+25%")


async def _azure_tts(text: str) -> bytes | None:
    """Generate speech using Azure Neural TTS."""
    if not AZURE_KEY:
        return None
    try:
        import azure.cognitiveservices.speech as speechsdk

        speech_config = speechsdk.SpeechConfig(
            subscription=AZURE_KEY.strip(),
            region=AZURE_REGION.strip()
        )

        class NullCallback(speechsdk.audio.PushAudioOutputStreamCallback):
            def write(self, data: memoryview) -> int: return data.nbytes
            def close(self) -> None: pass

        stream       = speechsdk.audio.PushAudioOutputStream(NullCallback())
        audio_config = speechsdk.audio.AudioConfig(stream=stream)
        synthesizer  = speechsdk.SpeechSynthesizer(
            speech_config=speech_config,
            audio_config=audio_config
        )
        ssml = (
            f'<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="en-US">'
            f'<voice name="{AZURE_VOICE}">'
            f'<prosody rate="{AZURE_RATE}" pitch="{AZURE_PITCH}">{text}</prosody>'
            f'</voice></speak>'
        )
        result = await asyncio.to_thread(synthesizer.speak_ssml, ssml)
        if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            return result.audio_data
        return None
    except Exception as e:
        print(f"   [TTS] Azure failed: {e}")
        return None
GROQ_STT_KEY    = os.getenv("GROQ_STT_KEY", "")
ALLOWED_USER_ID = int(os.getenv("TELEGRAM_USER_ID", "0"))


class KiraBot:
    def __init__(self):
        self.brain      = LenaBrain(personality_file="personality_english.txt")
        self.memory     = MemoryManager()
        self.stt        = AsyncGroq(api_key=GROQ_STT_KEY) if GROQ_STT_KEY else None
        self.turn_count = 0
        print("   [Telegram] Kira ready.")

    def _allowed(self, update: Update) -> bool:
        if ALLOWED_USER_ID and update.effective_user.id != ALLOWED_USER_ID:
            return False
        return True

    async def on_text(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not self._allowed(update):
            return
        user_text = update.message.text.strip()
        if not user_text:
            return
        print(f"You: {user_text}")
        memory_context = self.memory.get_context(user_text)
        response = await self.brain.chat(user_text, memory_context=memory_context)
        print(f"Kira: {response}")
        self.memory.add_turn(user_text, response)
        self.turn_count += 1
        if self.turn_count % 5 == 0 and len(user_text) > 40:
            asyncio.create_task(self._extract(user_text))
        await update.message.reply_text(response)

    async def on_voice(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not self._allowed(update):
            return
        if not self.stt:
            await update.message.reply_text("No STT key configured.")
            return
        voice_file  = await update.message.voice.get_file()
        audio_bytes = bytes(await voice_file.download_as_bytearray())
        try:
            buf = io.BytesIO(audio_bytes)
            buf.name = "voice.ogg"
            result = await self.stt.audio.transcriptions.create(
                file=buf,
                model="whisper-large-v3",
                response_format="text",
            )
            user_text = result.strip() if result else ""
        except Exception as e:
            await update.message.reply_text(f"Transcription failed: {e}")
            return
        if not user_text or len(user_text) < 2:
            await update.message.reply_text("Couldn't understand. Try again?")
            return
        print(f"You (voice): {user_text}")
        memory_context = self.memory.get_context(user_text)
        response = await self.brain.chat(user_text, memory_context=memory_context)
        print(f"Kira: {response}")
        self.memory.add_turn(user_text, response)
        self.turn_count += 1
        if self.turn_count % 5 == 0 and len(user_text) > 40:
            asyncio.create_task(self._extract(user_text))
        # Send voice reply via Azure TTS
        audio_buf = await _azure_tts(response)
        if audio_buf:
            voice_io      = io.BytesIO(audio_buf)
            voice_io.name = "voice.mp3"
            await update.message.reply_voice(voice=voice_io)
            await update.message.reply_text(response)
        else:
            await update.message.reply_text(response)

    async def _extract(self, user_text: str):
        try:
            facts = await extract_memories(user_text, self.brain.history)
            if facts:
                self.memory.store_facts(facts)
        except Exception as e:
            print(f"   [Memory] {e}")


def main():
    if not TELEGRAM_TOKEN:
        print("❌ TELEGRAM_BOT_TOKEN not set in .env")
        return

    print("\n=== Kira Telegram Bot ===")
    print("Send a message to your bot on Telegram.\n")

    kira = KiraBot()
    app  = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, kira.on_text))
    app.add_handler(MessageHandler(filters.VOICE, kira.on_voice))

    print("✅ Kira is online!")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()