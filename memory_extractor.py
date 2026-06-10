# # memory_extractor.py — Extracts German learning progress and user facts
# import json
# import re
#
# EXTRACTOR_SYSTEM = """You are a language learning memory archivist for an AI German companion named Lena. Your job is to extract TWO types of durable information from conversation:
#
# 1. LANGUAGE PROGRESS — things about the user's German ability that will matter next session
# 2. PERSONAL FACTS — durable facts about the user as a person (same bar as before)
#
# THE BAR IS HIGH. Most turns produce NO memories. Reject:
# - Temporary states ("I'm tired today")
# - Trivial filler ("okay", "yeah", "thanks")
# - One-off mistakes that happen once and are immediately corrected
# - Vague generalizations
#
# SAVE language progress memories when:
# - The user consistently makes the same grammar mistake (worth remembering to address again)
# - The user successfully uses a construction correctly for the first time ("used accusative case correctly")
# - The user learns and correctly uses a new word or phrase
# - The user's current approximate level is clear ("mostly A2, struggles with word order")
# - The user expresses specific difficulty ("I always forget where to put the verb")
#
# SAVE personal facts when:
# - The user states concrete preferences, life facts, goals, or strong opinions about themselves
#
# Output STRICT JSON. No prose before or after. Schema:
# {
#   "memories": [
#     {
#       "subject": "User",
#       "category": "grammar_struggle | vocabulary_learned | grammar_success | language_level | personal_fact | goal",
#       "fact": "natural sentence stating the fact in clean English",
#       "confidence": 0.0-1.0
#     }
#   ]
# }
#
# If nothing meets the bar, output: {"memories": []}
#
# Use natural English in the "fact" field. Never use snake_case or underscores in the fact text.
# """
#
#
# def _extract_json(text: str) -> dict | None:
#     try:
#         match = re.search(r"\{.*\}", text, re.DOTALL)
#         if not match:
#             return None
#         return json.loads(match.group(0))
#     except Exception:
#         return None
#
#
# async def extract_memories(ai_core, user_text: str, conversation_history: list) -> list[dict]:
#     """Extracts German learning progress and personal facts from a conversation turn."""
#
#     if len(user_text) < 8:
#         return []
#
#     if not getattr(ai_core, "anthropic_client", None):
#         return []
#
#     context = "\n".join(
#         f"{'User' if m['role'] == 'user' else 'Lena'}: {m['content'][:300]}"
#         for m in conversation_history[-3:]
#     )
#
#     user_msg = (
#         f"Recent context:\n{context}\n\n"
#         f"User's latest message: \"{user_text}\"\n\n"
#         f"Extract durable language progress facts or personal facts. Return JSON."
#     )
#
#     try:
#         raw = await ai_core.claude_chat_inference(
#             messages=[{"role": "user", "content": user_msg}],
#             system_prompt=EXTRACTOR_SYSTEM,
#             max_tokens=400,
#         )
#         if not raw:
#             return []
#         data = _extract_json(raw)
#         if not data or "memories" not in data:
#             return []
#
#         valid = []
#         for mem in data["memories"]:
#             confidence = float(mem.get("confidence", 0))
#             if confidence < 0.7:
#                 continue
#             fact = mem.get("fact", "").strip()
#             if not fact or len(fact) < 10 or "_" in fact:
#                 continue
#
#             category = mem.get("category", "personal_fact")
#             memory_type = "language_progress" if category in (
#                 "grammar_struggle", "vocabulary_learned", "grammar_success", "language_level"
#             ) else "profile_fact"
#
#             valid.append({
#                 "subject": mem.get("subject", "User"),
#                 "category": category,
#                 "fact": fact,
#                 "confidence": confidence,
#                 "memory_type": memory_type,
#                 "predicate": category,
#                 "object": fact,
#                 "salience": confidence,
#             })
#             print(f"   [Memory] Extracted: {fact} (conf: {confidence})")
#
#         return valid
#
#     except Exception as e:
#         print(f"   [Memory Extractor] Error: {e}")
#         return []




























# memory_extractor.py - Extracts durable facts from conversation using Groq

import json
import re
import os
from dotenv import load_dotenv
load_dotenv(override=True)

from groq import AsyncGroq

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

EXTRACTOR_SYSTEM = """You are a memory archivist for an AI companion named Lena. Extract DURABLE facts about her friend from conversation — facts that will still matter next week.

THE BAR IS HIGH. Most turns produce NO memories. Reject:
- Temporary states ("I'm tired", "I'm busy")
- Questions the user asks
- Trivial reactions ("that's cool", "thanks")
- Filler ("okay", "yeah", "hmm")
- Vague generalizations

ONLY save:
- Concrete preferences explicitly stated ("my favorite anime is X")
- Life facts ("I study medicine", "I live in Berlin")
- Strong opinions ("I think X is the best because...")
- Goals or plans ("I want to learn German for travel")
- Significant personal details ("I have a German test next week")

Output STRICT JSON only. No prose before or after:
{
  "memories": [
    {
      "subject": "user",
      "category": "preference | life_fact | opinion | plan | personal_detail",
      "fact": "natural sentence stating the fact in clean English",
      "confidence": 0.0-1.0
    }
  ]
}

If nothing meets the bar: {"memories": []}
"""


async def extract_memories(user_text: str, conversation_history: list) -> list:
    """Extracts durable facts from a conversation turn using Groq."""
    if len(user_text) < 8 or not GROQ_API_KEY:
        return []

    client = AsyncGroq(api_key=GROQ_API_KEY)

    context = "\n".join(
        f"{'User' if m['role'] == 'user' else 'Lena'}: {m['content'][:200]}"
        for m in conversation_history[-3:]
    )

    user_msg = (
        f"Recent context:\n{context}\n\n"
        f"User's latest message: \"{user_text}\"\n\n"
        f"Extract durable facts. Return JSON only."
    )

    try:
        response = await client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": EXTRACTOR_SYSTEM},
                {"role": "user", "content": user_msg},
            ],
            max_tokens=300,
            temperature=0.1,
        )
        raw = response.choices[0].message.content.strip()

        match = re.search(r"\{.*\}", raw, re.DOTALL)
        if not match:
            return []
        data = json.loads(match.group(0))
        if "memories" not in data:
            return []

        valid = []
        for mem in data["memories"]:
            confidence = float(mem.get("confidence", 0))
            if confidence < 0.7:
                continue
            fact = mem.get("fact", "").strip()
            if not fact or len(fact) < 10:
                continue
            valid.append({
                "fact": fact,
                "category": mem.get("category", "general"),
                "confidence": confidence,
                "memory_type": "profile_fact" if mem.get("category") in ("life_fact", "preference") else "episodic",
                "predicate": mem.get("category", "fact"),
            })
            print(f"   [Memory] Extracted: {fact} (conf: {confidence})")
        return valid

    except Exception as e:
        print(f"   [Memory Extractor] Error: {e}")
        return []


