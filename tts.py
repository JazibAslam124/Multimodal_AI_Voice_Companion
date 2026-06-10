# # tts.py - Lena's voice output via edge-tts + pygame
#
# import asyncio
# import io
# import pygame
# import edge_tts
#
# # German female voice — sounds natural for Lena
# VOICE = "en-US-AshleyNeural"
# RATE = "+20%"
# PITCH = "+20Hz"
#
# class LenaTTS:
#     def __init__(self):
#         self.is_speaking = False
#         self._stop = False
#
#         try:
#             pygame.mixer.pre_init(44100, -16, 2, 2048)
#             pygame.mixer.init()
#             print("   [TTS] Audio ready.")
#         except Exception as e:
#             print(f"   [TTS] Audio init failed: {e}")
#
#     async def speak(self, text: str):
#         if not text:
#             return
#
#         self._stop = False
#         self.is_speaking = True
#
#         try:
#             # Generate audio with edge-tts
#             communicate = edge_tts.Communicate(text, VOICE, rate=RATE, pitch=PITCH)
#             audio_buffer = b""
#             async for chunk in communicate.stream():
#                 if chunk["type"] == "audio":
#                     audio_buffer += chunk["data"]
#
#             if not audio_buffer:
#                 print("   [TTS] No audio generated.")
#                 return
#
#             # Play with pygame
#             sound = pygame.mixer.Sound(io.BytesIO(audio_buffer))
#             channel = sound.play()
#             while channel.get_busy():
#                 if self._stop:
#                     channel.stop()
#                     break
#                 await asyncio.sleep(0.05)
#
#         except Exception as e:
#             print(f"   [TTS] Error: {e}")
#         finally:
#             self.is_speaking = False
#
#     def stop(self):
#         self._stop = True
#         pygame.mixer.stop()










# #best version
# # tts.py - Lena's voice output via Azure Neural TTS + pygame
#
# import asyncio
# import io
# import os
# import pygame
# from dotenv import load_dotenv
# load_dotenv(override=True)
#
# AZURE_SPEECH_KEY    = os.getenv("AZURE_SPEECH_KEY", "")
# AZURE_SPEECH_REGION = os.getenv("AZURE_SPEECH_REGION", "eastus")
# AZURE_SPEECH_VOICE  = os.getenv("AZURE_SPEECH_VOICE", "en-US-AshleyNeural")
# AZURE_PROSODY_RATE  = os.getenv("AZURE_PROSODY_RATE", "25%")
# AZURE_PROSODY_PITCH = os.getenv("AZURE_PROSODY_PITCH", "+25%")
#
# try:
#     import azure.cognitiveservices.speech as speechsdk
#     AZURE_AVAILABLE = True
# except ImportError:
#     AZURE_AVAILABLE = False
#     print("   [TTS] azure-cognitiveservices-speech not installed. Run: pip install azure-cognitiveservices-speech")
#
# try:
#     from edge_tts import Communicate
#     EDGE_AVAILABLE = True
# except ImportError:
#     EDGE_AVAILABLE = False
#
#
# class LenaTTS:
#     def __init__(self):
#         self.is_speaking = False
#         self._stop = False
#         self.azure_synthesizer = None
#
#         try:
#             pygame.mixer.pre_init(44100, -16, 2, 2048)
#             pygame.mixer.init()
#             print("   [TTS] Audio ready.")
#         except Exception as e:
#             print(f"   [TTS] Audio init failed: {e}")
#
#         # Try Azure first
#         if AZURE_AVAILABLE and AZURE_SPEECH_KEY and AZURE_SPEECH_REGION:
#             try:
#                 speech_config = speechsdk.SpeechConfig(
#                     subscription=AZURE_SPEECH_KEY.strip(),
#                     region=AZURE_SPEECH_REGION.strip()
#                 )
#
#                 class NullCallback(speechsdk.audio.PushAudioOutputStreamCallback):
#                     def write(self, data: memoryview) -> int: return data.nbytes
#                     def close(self) -> None: pass
#
#                 stream = speechsdk.audio.PushAudioOutputStream(NullCallback())
#                 audio_config = speechsdk.audio.AudioConfig(stream=stream)
#                 self.azure_synthesizer = speechsdk.SpeechSynthesizer(
#                     speech_config=speech_config,
#                     audio_config=audio_config
#                 )
#                 print(f"   [TTS] Azure ready ({AZURE_SPEECH_VOICE}).")
#             except Exception as e:
#                 print(f"   [TTS] Azure init failed: {e} — falling back to Edge TTS.")
#                 self.azure_synthesizer = None
#         else:
#             if not AZURE_SPEECH_KEY:
#                 print("   [TTS] No AZURE_SPEECH_KEY — using Edge TTS fallback.")
#
#     async def speak(self, text: str):
#         if not text:
#             return
#
#         self._stop = False
#         self.is_speaking = True
#
#         try:
#             if self.azure_synthesizer:
#                 await self._speak_azure(text)
#             else:
#                 await self._speak_edge(text)
#         finally:
#             self.is_speaking = False
#
#     async def _speak_azure(self, text: str):
#         ssml = (
#             f'<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="en-US">'
#             f'<voice name="{AZURE_SPEECH_VOICE}">'
#             f'<prosody rate="{AZURE_PROSODY_RATE}" pitch="{AZURE_PROSODY_PITCH}">{text}</prosody>'
#             f'</voice></speak>'
#         )
#         try:
#             result = await asyncio.to_thread(self.azure_synthesizer.speak_ssml, ssml)
#             if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
#                 await self._play_audio(result.audio_data)
#             else:
#                 print(f"   [TTS] Azure failed: {result.cancellation_details.error_details}")
#                 # Fallback to Edge
#                 await self._speak_edge(text)
#         except Exception as e:
#             print(f"   [TTS] Azure error: {e}")
#             await self._speak_edge(text)
#
#     async def _speak_edge(self, text: str):
#         if not EDGE_AVAILABLE:
#             print("   [TTS] No TTS available.")
#             return
#         try:
#             voice = AZURE_SPEECH_VOICE if AZURE_SPEECH_VOICE else "en-US-AshleyNeural"
#             communicate = Communicate(text, voice)
#             buffer = b""
#             async for chunk in communicate.stream():
#                 if chunk["type"] == "audio":
#                     buffer += chunk["data"]
#             if buffer:
#                 await self._play_audio(buffer)
#         except Exception as e:
#             print(f"   [TTS] Edge error: {e}")
#
#     async def _play_audio(self, audio_bytes: bytes):
#         if self._stop or not audio_bytes:
#             return
#         try:
#             if not pygame.mixer.get_init():
#                 pygame.mixer.init()
#             pygame.mixer.stop()
#             sound = pygame.mixer.Sound(io.BytesIO(audio_bytes))
#             channel = sound.play()
#             while channel.get_busy():
#                 if self._stop:
#                     channel.stop()
#                     break
#                 await asyncio.sleep(0.05)
#         except Exception as e:
#             print(f"   [TTS] Playback error: {e}")
#
#     def stop(self):
#         self._stop = True
#         pygame.mixer.stop()










# tts.py - Kira's voice output via Azure Neural TTS + pygame

import asyncio
import io
import os
import pygame
from dotenv import load_dotenv
load_dotenv(override=True)

AZURE_SPEECH_KEY    = os.getenv("AZURE_SPEECH_KEY", "")
AZURE_SPEECH_REGION = os.getenv("AZURE_SPEECH_REGION", "eastus")
AZURE_SPEECH_VOICE  = os.getenv("AZURE_SPEECH_VOICE", "en-US-AshleyNeural")
AZURE_PROSODY_RATE  = os.getenv("AZURE_PROSODY_RATE", "25%")
AZURE_PROSODY_PITCH = os.getenv("AZURE_PROSODY_PITCH", "+25%")

try:
    import azure.cognitiveservices.speech as speechsdk
    AZURE_AVAILABLE = True
except ImportError:
    AZURE_AVAILABLE = False

try:
    from edge_tts import Communicate
    EDGE_AVAILABLE = True
except ImportError:
    EDGE_AVAILABLE = False

# Avatar integration
try:
    from avatar import avatar as _avatar
    AVATAR_AVAILABLE = True
except ImportError:
    AVATAR_AVAILABLE = False


class LenaTTS:
    def __init__(self):
        self.is_speaking = False
        self._stop = False
        self.azure_synthesizer = None

        try:
            pygame.mixer.pre_init(44100, -16, 2, 2048)
            pygame.mixer.init()
            print("   [TTS] Audio ready.")
        except Exception as e:
            print(f"   [TTS] Audio init failed: {e}")

        if AZURE_AVAILABLE and AZURE_SPEECH_KEY and AZURE_SPEECH_REGION:
            try:
                speech_config = speechsdk.SpeechConfig(
                    subscription=AZURE_SPEECH_KEY.strip(),
                    region=AZURE_SPEECH_REGION.strip()
                )
                class NullCallback(speechsdk.audio.PushAudioOutputStreamCallback):
                    def write(self, data: memoryview) -> int: return data.nbytes
                    def close(self) -> None: pass
                stream = speechsdk.audio.PushAudioOutputStream(NullCallback())
                audio_config = speechsdk.audio.AudioConfig(stream=stream)
                self.azure_synthesizer = speechsdk.SpeechSynthesizer(
                    speech_config=speech_config,
                    audio_config=audio_config
                )
                print(f"   [TTS] Azure ready ({AZURE_SPEECH_VOICE}).")
            except Exception as e:
                print(f"   [TTS] Azure init failed: {e} — falling back to Edge TTS.")
                self.azure_synthesizer = None
        else:
            if not AZURE_SPEECH_KEY:
                print("   [TTS] No AZURE_SPEECH_KEY — using Edge TTS fallback.")

    async def speak(self, text: str):
        if not text:
            return
        self._stop = False
        self.is_speaking = True
        if AVATAR_AVAILABLE:
            _avatar.set_talking(True)
        try:
            if self.azure_synthesizer:
                await self._speak_azure(text)
            else:
                await self._speak_edge(text)
        finally:
            self.is_speaking = False
            if AVATAR_AVAILABLE:
                _avatar.set_talking(False)

    async def _speak_azure(self, text: str):
        ssml = (
            f'<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="en-US">'
            f'<voice name="{AZURE_SPEECH_VOICE}">'
            f'<prosody rate="{AZURE_PROSODY_RATE}" pitch="{AZURE_PROSODY_PITCH}">{text}</prosody>'
            f'</voice></speak>'
        )
        try:
            result = await asyncio.to_thread(self.azure_synthesizer.speak_ssml, ssml)
            if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
                await self._play_audio(result.audio_data)
            else:
                print(f"   [TTS] Azure failed: {result.cancellation_details.error_details}")
                await self._speak_edge(text)
        except Exception as e:
            print(f"   [TTS] Azure error: {e}")
            await self._speak_edge(text)

    async def _speak_edge(self, text: str):
        if not EDGE_AVAILABLE:
            print("   [TTS] No TTS available.")
            return
        try:
            voice = AZURE_SPEECH_VOICE if AZURE_SPEECH_VOICE else "en-US-AshleyNeural"
            communicate = Communicate(text, voice)
            buffer = b""
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    buffer += chunk["data"]
            if buffer:
                await self._play_audio(buffer)
        except Exception as e:
            print(f"   [TTS] Edge error: {e}")

    async def _play_audio(self, audio_bytes: bytes):
        if self._stop or not audio_bytes:
            return
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()
            pygame.mixer.stop()
            sound = pygame.mixer.Sound(io.BytesIO(audio_bytes))
            channel = sound.play()
            while channel.get_busy():
                if self._stop:
                    channel.stop()
                    break
                await asyncio.sleep(0.05)
        except Exception as e:
            print(f"   [TTS] Playback error: {e}")

    def stop(self):
        self._stop = True
        pygame.mixer.stop()