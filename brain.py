# # brain.py - Lena's brain via Ollama (local, no API key, no quota)
#
# import asyncio
# import os
# import re
# import json
# import urllib.request
# from dotenv import load_dotenv
# load_dotenv(override=True)
#
# OLLAMA_URL   = "http://localhost:11434/api/chat"
# OLLAMA_MODEL = "llama3.2:3b"
#
# SYSTEM_PROMPT = """You are Lena, a 22-year-old German woman from Munich. You are helping your friend learn German through natural conversation. Your friend speaks English to you.
#
# Your job:
# 1. Always respond FIRST in German (natural, conversational — like a real person, not a textbook)
# 2. Then on a new line, add a brief English translation in brackets so they understand
# 3. Keep responses short — 2-3 sentences max. This is a conversation, not a lecture.
# 4. Be warm, a little sarcastic, genuinely encouraging.
# 5. Occasionally weave in a simple German word or phrase they can learn from context.
#
# Example:
# Friend says: "Hello Lena, how are you?"
# Lena responds:
# Na, endlich meldest du dich! Mir geht's gut, danke — und dir?
# [Well, you finally show up! I'm doing well, thanks — and you?]"""
#
#
# class LenaBrain:
#     def __init__(self):
#         self.history = []
#         self.ready = False
#
#         # Check Ollama is running
#         try:
#             req = urllib.request.urlopen("http://localhost:11434", timeout=2)
#             self.ready = True
#             print(f"   [Brain] Ollama ready ({OLLAMA_MODEL}).")
#         except Exception:
#             print("   [Brain] ERROR: Ollama not running.")
#             print("   [Brain] Start it with: ollama serve")
#             print(f"  [Brain] Pull model with: ollama pull {OLLAMA_MODEL}")
#
#     async def chat(self, user_text: str) -> str:
#         if not self.ready:
#             return "Ollama läuft nicht. Starte: ollama serve"
#
#         # Add user message
#         self.history.append({"role": "user", "content": user_text})
#
#         # Keep last 20 messages to save memory
#         if len(self.history) > 20:
#             self.history = self.history[-20:]
#
#         messages = [{"role": "system", "content": SYSTEM_PROMPT}] + self.history
#
#         def _run():
#             payload = json.dumps({
#                 "model": OLLAMA_MODEL,
#                 "messages": messages,
#                 "stream": False,
#                 "options": {
#                     "temperature": 0.8,
#                     "num_predict": 150,  # short responses
#                 }
#             }).encode("utf-8")
#
#             req = urllib.request.Request(
#                 OLLAMA_URL,
#                 data=payload,
#                 headers={"Content-Type": "application/json"},
#                 method="POST",
#             )
#             with urllib.request.urlopen(req, timeout=30) as resp:
#                 data = json.loads(resp.read().decode("utf-8"))
#                 return data["message"]["content"].strip()
#
#         try:
#             result = await asyncio.to_thread(_run)
#             self.history.append({"role": "assistant", "content": result})
#             return result
#         except Exception as e:
#             print(f"   [Brain] Error: {e}")
#             return "Entschuldigung, da ist was schiefgelaufen."
#
#     def clear_history(self):
#         self.history = []
#         print("   [Brain] Conversation history cleared.")















# # brain.py - Lena's brain via Groq (free, fast, 70B Llama)  best version currently
#
# import asyncio
# import os
# import re
# from dotenv import load_dotenv
# load_dotenv(override=True)
#
# from groq import AsyncGroq
#
# GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
# print(f"   [Brain] Groq key loaded: '{GROQ_API_KEY[:8]}...'" if GROQ_API_KEY else "   [Brain] ERROR: GROQ_API_KEY not set in .env")
#
# SYSTEM_PROMPT = """You are Lena, a 22-year-old German woman from Munich. You are helping your friend learn German through natural conversation. Your friend speaks English to you.
#
# Your job:
# 1. Always respond FIRST in German (natural, conversational — like a real person, not a textbook)
# 2. Then on a new line, add a brief English translation in brackets so they understand
# 3. Keep responses short — 2-3 sentences max. This is a conversation, not a lecture.
# 4. Be warm, a little sarcastic, genuinely encouraging.
# 5. Occasionally weave in a simple German word or phrase they can learn from context.
#
# Example:
# Friend says: "Hello Lena, how are you?"
# Lena responds:
# Na, endlich meldest du dich! Mir geht's gut, danke — und dir?
# [Well, you finally show up! I'm doing well, thanks — and you?]"""
#
#
# class LenaBrain:
#     def __init__(self):
#         self.history = []
#         self.ready = False
#
#         if not GROQ_API_KEY:
#             print("   [Brain] ERROR: GROQ_API_KEY not set in .env")
#             return
#
#         try:
#             self.client = AsyncGroq(api_key=GROQ_API_KEY)
#             self.ready = True
#             print("   [Brain] Groq ready (llama-3.3-70b).")
#         except Exception as e:
#             print(f"   [Brain] Init failed: {e}")
#
#     async def chat(self, user_text: str) -> str:
#         if not self.ready:
#             return "Ich kann gerade nicht denken. Check the API key."
#
#         self.history.append({"role": "user", "content": user_text})
#
#         # Keep last 20 messages to save tokens
#         if len(self.history) > 20:
#             self.history = self.history[-20:]
#
#         messages = [{"role": "system", "content": SYSTEM_PROMPT}] + self.history
#
#         try:
#             response = await self.client.chat.completions.create(
#                 model="llama-3.3-70b-versatile",
#                 messages=messages,
#                 max_tokens=150,
#                 temperature=0.8,
#             )
#             result = response.choices[0].message.content.strip()
#             self.history.append({"role": "assistant", "content": result})
#             return result
#         except Exception as e:
#             err = str(e)
#             if "429" in err:
#                 match = re.search(r'try again in (\d+)', err)
#                 wait = match.group(1) if match else "a moment"
#                 print(f"   [Brain] Rate limited — retry in {wait}s")
#                 return f"Kurze Pause — versuch es in {wait} Sekunden nochmal."
#             print(f"   [Brain] Error: {e}")
#             return "Entschuldigung, da ist was schiefgelaufen."
#
#     def clear_history(self):
#         self.history = []
#         print("   [Brain] Conversation history cleared.")
























# BEST ONE SO FAR
#
# # brain.py - Lena's brain via Groq
#
# import asyncio
# import os
# import re
# from dotenv import load_dotenv
# load_dotenv(override=True)
#
# from groq import AsyncGroq
#
# GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
# print(f"   [Brain] Groq key loaded: '{GROQ_API_KEY[:8]}...'" if GROQ_API_KEY else "   [Brain] ERROR: GROQ_API_KEY not set in .env")
#
# SYSTEM_PROMPT = """You are Lena, a warm, witty, and slightly sarcastic AI companion. You talk like a real person — casual, natural, never robotic.
#
# Keep responses short and conversational — 2-3 sentences max unless the user asks for something detailed.
# Be genuinely helpful, a little funny, and always honest.
# When given screen context in brackets, you CAN see the screen and should reference what you see naturally and confidently."""
#
#
# class LenaBrain:
#     def __init__(self):
#         self.history = []
#         self.ready = False
#
#         if not GROQ_API_KEY:
#             print("   [Brain] ERROR: GROQ_API_KEY not set in .env")
#             return
#
#         try:
#             self.client = AsyncGroq(api_key=GROQ_API_KEY)
#             self.ready = True
#             print("   [Brain] Groq ready (llama-3.3-70b).")
#         except Exception as e:
#             print(f"   [Brain] Init failed: {e}")
#
#     async def chat(self, user_text: str, vision_context: str = "") -> str:
#         if not self.ready:
#             return "I can't think right now. Check the API key."
#
#         # Build message — inject vision context if present
#         message = user_text
#         if vision_context:
#             message = f"[You can currently see the user's screen. Here is what is on it: {vision_context}]\n\nUser says: {user_text}"
#
#         self.history.append({"role": "user", "content": message})
#
#         # Keep last 20 messages
#         if len(self.history) > 20:
#             self.history = self.history[-20:]
#
#         messages = [{"role": "system", "content": SYSTEM_PROMPT}] + self.history
#
#         try:
#             response = await self.client.chat.completions.create(
#                 model="llama-3.3-70b-versatile",
#                 messages=messages,
#                 max_tokens=150,
#                 temperature=0.8,
#             )
#             result = response.choices[0].message.content.strip()
#             self.history.append({"role": "assistant", "content": result})
#             return result
#         except Exception as e:
#             err = str(e)
#             if "429" in err:
#                 match = re.search(r'try again in (\d+)', err)
#                 wait = match.group(1) if match else "a moment"
#                 print(f"   [Brain] Rate limited — retry in {wait}s")
#                 return f"Rate limited — try again in {wait} seconds."
#             print(f"   [Brain] Error: {e}")
#             return "Sorry, something went wrong."
#
#     def clear_history(self):
#         self.history = []
#         print("   [Brain] Conversation history cleared.")





# # brain.py - Lena's brain via Groq
#
# import asyncio
# import os
# import re
# from dotenv import load_dotenv
# load_dotenv(override=True)
#
# from groq import AsyncGroq
#
# GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
# print(f"   [Brain] Groq key loaded: '{GROQ_API_KEY[:8]}...'" if GROQ_API_KEY else "   [Brain] ERROR: GROQ_API_KEY not set in .env")
#
# # Load personality from file
# def _load_personality() -> str:
#     personality_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "personality.txt")
#     try:
#         with open(personality_path, "r", encoding="utf-8") as f:
#             content = f.read().strip()
#             print("   [Brain] Personality loaded from personality.txt")
#             return content
#     except FileNotFoundError:
#         print("   [Brain] WARNING: personality.txt not found — using default.")
#         return "You are Lena, a 22-year-old German woman from Munich. You are warm, witty, and help your friend learn German naturally."
#
# SYSTEM_PROMPT = _load_personality()
#
#
# class LenaBrain:
#     def __init__(self):
#         self.history = []
#         self.ready = False
#
#         if not GROQ_API_KEY:
#             print("   [Brain] ERROR: GROQ_API_KEY not set in .env")
#             return
#
#         try:
#             self.client = AsyncGroq(api_key=GROQ_API_KEY)
#             self.ready = True
#             print("   [Brain] Groq ready (llama-3.3-70b).")
#         except Exception as e:
#             print(f"   [Brain] Init failed: {e}")
#
#     async def chat(self, user_text: str, vision_context: str = "") -> str:
#         if not self.ready:
#             return "I can't think right now. Check the API key."
#
#         message = user_text
#         if vision_context:
#             message = (
#                 f"[You can currently see the user's screen. Here is what is on it: {vision_context}]\n\n"
#                 f"User says: {user_text}"
#             )
#
#         self.history.append({"role": "user", "content": message})
#
#         if len(self.history) > 20:
#             self.history = self.history[-20:]
#
#         messages = [{"role": "system", "content": SYSTEM_PROMPT}] + self.history
#
#         try:
#             response = await self.client.chat.completions.create(
#                 model="llama-3.3-70b-versatile",
#                 messages=messages,
#                 max_tokens=150,
#                 temperature=0.85,
#             )
#             result = response.choices[0].message.content.strip()
#             self.history.append({"role": "assistant", "content": result})
#             return result
#         except Exception as e:
#             err = str(e)
#             if "429" in err:
#                 match = re.search(r'try again in (\d+)', err)
#                 wait = match.group(1) if match else "a moment"
#                 print(f"   [Brain] Rate limited — retry in {wait}s")
#                 return f"Rate limited — try again in {wait} seconds."
#             print(f"   [Brain] Error: {e}")
#             return "Sorry, something went wrong."
#
#     def clear_history(self):
#         self.history = []
#         print("   [Brain] Conversation history cleared.")


















# # brain.py - Lena's brain via Groq with memory support
#
# import asyncio
# import os
# import re
# from dotenv import load_dotenv
# load_dotenv(override=True)
#
# from groq import AsyncGroq
#
# GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
# print(f"   [Brain] Groq key loaded: '{GROQ_API_KEY[:8]}...'" if GROQ_API_KEY else "   [Brain] ERROR: GROQ_API_KEY not set in .env")
#
# def _load_personality() -> str:
#     path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "personality.txt")
#     try:
#         with open(path, "r", encoding="utf-8") as f:
#             content = f.read().strip()
#             print("   [Brain] Personality loaded from personality.txt")
#             return content
#     except FileNotFoundError:
#         print("   [Brain] WARNING: personality.txt not found — using default.")
#         return "You are Lena, a warm and helpful AI companion."
#
# SYSTEM_PROMPT = _load_personality()
#
#
# class LenaBrain:
#     def __init__(self):
#         self.history = []
#         self.ready = False
#
#         if not GROQ_API_KEY:
#             print("   [Brain] ERROR: GROQ_API_KEY not set in .env")
#             return
#
#         try:
#             self.client = AsyncGroq(api_key=GROQ_API_KEY)
#             self.ready = True
#             print("   [Brain] Groq ready (llama-3.3-70b).")
#         except Exception as e:
#             print(f"   [Brain] Init failed: {e}")
#
#     async def chat(self, user_text: str, vision_context: str = "", memory_context: str = "") -> str:
#         if not self.ready:
#             return "I can't think right now. Check the API key."
#
#         # Build system prompt with memory injected
#         system = SYSTEM_PROMPT
#         if memory_context:
#             system += f"\n\n[MEMORY — what you know about your friend, use naturally]\n{memory_context}"
#
#         # Build user message with vision context if present
#         message = user_text
#         if vision_context:
#             message = (
#                 f"[You can currently see the user's screen: {vision_context}]\n\n"
#                 f"User says: {user_text}"
#             )
#
#         self.history.append({"role": "user", "content": message})
#
#         if len(self.history) > 20:
#             self.history = self.history[-20:]
#
#         messages = [{"role": "system", "content": system}] + self.history
#
#         try:
#             response = await self.client.chat.completions.create(
#                 model="llama-3.3-70b-versatile",
#                 messages=messages,
#                 max_tokens=150,
#                 temperature=0.85,
#             )
#             result = response.choices[0].message.content.strip()
#             self.history.append({"role": "assistant", "content": result})
#             return result
#         except Exception as e:
#             err = str(e)
#             if "429" in err:
#                 match = re.search(r'try again in (\d+)', err)
#                 wait = match.group(1) if match else "a moment"
#                 print(f"   [Brain] Rate limited — retry in {wait}s")
#                 return f"Rate limited — try again in {wait} seconds."
#             print(f"   [Brain] Error: {e}")
#             return "Sorry, something went wrong."
#
#     def clear_history(self):
#         self.history = []
#         print("   [Brain] Conversation history cleared.")




















# # brain.py - Lena's brain via Groq with memory support
#
# import asyncio
# import os
# import re
# from dotenv import load_dotenv
# load_dotenv(override=True)
#
# from groq import AsyncGroq
#
# GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
# print(f"   [Brain] Groq key loaded: '{GROQ_API_KEY[:8]}...'" if GROQ_API_KEY else "   [Brain] ERROR: GROQ_API_KEY not set in .env")
#
#
# def _load_personality(filename: str = "personality_english.txt") -> str:
#     path = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)
#     try:
#         with open(path, "r", encoding="utf-8") as f:
#             content = f.read().strip()
#             print(f"   [Brain] Personality loaded from {filename}")
#             return content
#     except FileNotFoundError:
#         print(f"   [Brain] WARNING: {filename} not found — using default.")
#         return "You are Lena, a warm and helpful AI companion."
#
#
# class LenaBrain:
#     def __init__(self, personality_file: str = "personality_english.txt"):
#         self.history = []
#         self.ready = False
#         self.system_prompt = _load_personality(personality_file)
#
#         if not GROQ_API_KEY:
#             print("   [Brain] ERROR: GROQ_API_KEY not set in .env")
#             return
#
#         try:
#             self.client = AsyncGroq(api_key=GROQ_API_KEY)
#             self.ready = True
#             print("   [Brain] Groq ready (llama-3.3-70b).")
#         except Exception as e:
#             print(f"   [Brain] Init failed: {e}")
#
#     async def chat(self, user_text: str, vision_context: str = "", memory_context: str = "") -> str:
#         if not self.ready:
#             return "I can't think right now. Check the API key."
#
#         system = self.system_prompt
#         if memory_context:
#             system += f"\n\n[MEMORY — what you know about your friend, use naturally]\n{memory_context}"
#
#         message = user_text
#         if vision_context:
#             message = (
#                 f"[You can currently see the user's screen: {vision_context}]\n\n"
#                 f"User says: {user_text}"
#             )
#
#         self.history.append({"role": "user", "content": message})
#
#         if len(self.history) > 20:
#             self.history = self.history[-20:]
#
#         messages = [{"role": "system", "content": system}] + self.history
#
#         try:
#             response = await self.client.chat.completions.create(
#                 model="llama-3.3-70b-versatile",
#                 messages=messages,
#                 max_tokens=150,
#                 temperature=0.85,
#             )
#             result = response.choices[0].message.content.strip()
#             self.history.append({"role": "assistant", "content": result})
#             return result
#         except Exception as e:
#             err = str(e)
#             if "429" in err:
#                 match = re.search(r'try again in (\d+)', err)
#                 wait = match.group(1) if match else "a moment"
#                 print(f"   [Brain] Rate limited — retry in {wait}s")
#                 return f"Rate limited — try again in {wait} seconds."
#             print(f"   [Brain] Error: {e}")
#             return "Sorry, something went wrong."
#
#     def clear_history(self):
#         self.history = []
#         print("   [Brain] Conversation history cleared.")








# # brain.py - Lena's brain via Groq with memory support
#
# import asyncio
# import os
# import re
# from dotenv import load_dotenv
# load_dotenv(override=True)
#
# from groq import AsyncGroq
#
# GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
# print(f"   [Brain] Groq key loaded: '{GROQ_API_KEY[:8]}...'" if GROQ_API_KEY else "   [Brain] ERROR: GROQ_API_KEY not set in .env")
#
#
# def _load_personality(filename: str = "personality_english.txt") -> str:
#     path = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)
#     try:
#         with open(path, "r", encoding="utf-8") as f:
#             content = f.read().strip()
#             print(f"   [Brain] Personality loaded from {filename}")
#             return content
#     except FileNotFoundError:
#         print(f"   [Brain] WARNING: {filename} not found — using default.")
#         return "You are Lena, a warm and helpful AI companion."
#
#
# class LenaBrain:
#     def __init__(self, personality_file: str = "personality_english.txt"):
#         self.history = []
#         self.ready = False
#         self.system_prompt = _load_personality(personality_file)
#
#         if not GROQ_API_KEY:
#             print("   [Brain] ERROR: GROQ_API_KEY not set in .env")
#             return
#
#         try:
#             self.client = AsyncGroq(api_key=GROQ_API_KEY)
#             self.ready = True
#             print("   [Brain] Groq ready (llama-3.3-70b).")
#         except Exception as e:
#             print(f"   [Brain] Init failed: {e}")
#
#     async def chat(self, user_text: str, vision_context: str = "", memory_context: str = "") -> str:
#         if not self.ready:
#             return "I can't think right now. Check the API key."
#
#         system = self.system_prompt
#         if memory_context:
#             system += f"\n\n[MEMORY — what you know about your friend, use naturally]\n{memory_context}"
#
#         message = user_text
#         if vision_context:
#             message = (
#                 f"[You can currently see the user's screen: {vision_context}]\n\n"
#                 f"User says: {user_text}"
#             )
#
#         self.history.append({"role": "user", "content": message})
#
#         if len(self.history) > 8:
#             self.history = self.history[-8:]
#
#         # Only send full system prompt on first 2 turns — saves ~600 tokens per message after that
#         if len(self.history) <= 2:
#             messages = [{"role": "system", "content": system}] + self.history
#         else:
#             messages = [{"role": "system", "content": "Continue naturally."}] + self.history
#
#         try:
#             response = await self.client.chat.completions.create(
#                 model="llama-3.3-70b-versatile",
#                 messages=messages,
#                 max_tokens=150,
#                 temperature=0.85,
#             )
#             result = response.choices[0].message.content.strip()
#             self.history.append({"role": "assistant", "content": result})
#             return result
#         except Exception as e:
#             err = str(e)
#             if "429" in err:
#                 match = re.search(r'try again in (\d+)', err)
#                 wait = match.group(1) if match else "a moment"
#                 print(f"   [Brain] Rate limited — retry in {wait}s")
#                 return f"Rate limited — try again in {wait} seconds."
#             print(f"   [Brain] Error: {e}")
#             return "Sorry, something went wrong."
#
#     def clear_history(self):
#         self.history = []
#         print("   [Brain] Conversation history cleared.")






# brain.py - Kira's brain via Groq with auto key rotation

import asyncio
import os
import re
from dotenv import load_dotenv
load_dotenv(override=True)

from groq import AsyncGroq

# Multiple keys — rotates when one hits quota
GROQ_KEYS = [
    k for k in [
        os.getenv("GROQ_API_KEY", ""),
        os.getenv("GROQ_API_KEY_2", ""),
        os.getenv("GROQ_API_KEY_3", ""),
    ] if k
]

if not GROQ_KEYS:
    print("   [Brain] ERROR: No GROQ_API_KEY set in .env")
else:
    print(f"   [Brain] {len(GROQ_KEYS)} Groq key(s) loaded.")


def _load_personality(filename: str = "personality_english.txt") -> str:
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)
    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read().strip()
            print(f"   [Brain] Personality loaded from {filename}")
            return content
    except FileNotFoundError:
        print(f"   [Brain] WARNING: {filename} not found — using default.")
        return "You are Kira, a sharp witty AI companion. Be short. One sentence. Stay in character."


class LenaBrain:
    def __init__(self, personality_file: str = "personality_english.txt"):
        self.history      = []
        self.ready        = False
        self.system_prompt = _load_personality(personality_file)
        self._key_index   = 0
        self._clients     = []

        if not GROQ_KEYS:
            print("   [Brain] ERROR: No Groq keys available.")
            return

        for key in GROQ_KEYS:
            self._clients.append(AsyncGroq(api_key=key))

        self.ready = True
        print(f"   [Brain] Groq ready (llama-3.3-70b) — {len(self._clients)} key(s).")

    def _current_client(self) -> AsyncGroq:
        return self._clients[self._key_index]

    def _rotate_key(self):
        """Switch to next available key."""
        next_index = (self._key_index + 1) % len(self._clients)
        if next_index == self._key_index:
            return False  # only one key, can't rotate
        self._key_index = next_index
        print(f"   [Brain] Rotated to key {self._key_index + 1}/{len(self._clients)}")
        return True

    async def chat(self, user_text: str, vision_context: str = "", memory_context: str = "") -> str:
        if not self.ready:
            return "I can't think right now. Check the API key."

        # Build system — full on first 2 turns, short rules after
        if len(self.history) <= 2:
            system = self.system_prompt
            if memory_context:
                system += f"\n\n[MEMORY]\n{memory_context[:400]}"
        else:
            system = "BE SHORT. One sentence max. No explaining. Stay in character as Kira."

        # Build message
        message = user_text
        if vision_context:
            message = f"[Screen: {vision_context[:300]}]\nUser: {user_text}"

        self.history.append({"role": "user", "content": message})
        if len(self.history) > 8:
            self.history = self.history[-8:]

        messages = [{"role": "system", "content": system}] + self.history

        # Try current key, rotate on 429
        for attempt in range(len(self._clients)):
            try:
                response = await self._current_client().chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=messages,
                    max_tokens=120,
                    temperature=0.85,
                )
                result = response.choices[0].message.content.strip()
                self.history.append({"role": "assistant", "content": result})
                return result

            except Exception as e:
                err = str(e)
                if "429" in err:
                    print(f"   [Brain] Key {self._key_index + 1} rate limited.")
                    if self._rotate_key():
                        print(f"   [Brain] Retrying with key {self._key_index + 1}...")
                        continue
                    else:
                        # Extract wait time
                        match = re.search(r'try again in (\d+)', err)
                        wait = match.group(1) if match else "60"
                        return f"Rate limited — try again in {wait} seconds."
                else:
                    print(f"   [Brain] Error: {e}")
                    return "Sorry, something went wrong."

        return "All API keys are rate limited. Try again later."

    def clear_history(self):
        self.history = []
        print("   [Brain] History cleared.")