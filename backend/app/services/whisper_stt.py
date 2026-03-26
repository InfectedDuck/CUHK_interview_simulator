"""
Local Whisper speech-to-text using faster-whisper,
with AI-powered context-aware transcript correction.
"""
import tempfile
import os
from ..config import settings
from . import ollama

_model = None


def _get_model():
    global _model
    if _model is None:
        from faster_whisper import WhisperModel
        _model = WhisperModel(
            settings.whisper_model,
            device="cpu",
            compute_type="int8",
        )
    return _model


async def transcribe(audio_bytes: bytes, language: str | None = None) -> str:
    """Transcribe audio bytes to text using Whisper."""
    import asyncio

    lang = language or settings.whisper_language

    def _run():
        # Write to temp file (faster-whisper needs a file path)
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            f.write(audio_bytes)
            temp_path = f.name

        try:
            model = _get_model()
            segments, _info = model.transcribe(
                temp_path,
                language=lang,
                beam_size=5,
                vad_filter=True,
            )
            return " ".join(seg.text.strip() for seg in segments)
        finally:
            os.unlink(temp_path)

    # Run in a thread pool so we don't block the async event loop
    return await asyncio.get_event_loop().run_in_executor(None, _run)


CLEANUP_SYSTEM = """You are a transcript correction assistant. You fix speech-to-text errors using context clues.
You must return ONLY the corrected transcript text — nothing else. No explanations, no quotes, no preamble."""

CLEANUP_PROMPT = """Fix any speech-to-text errors in this transcript using the context provided.

RULES:
1. Fix words that don't make sense in context (e.g., "producer" → "produced" if talking about coding)
2. Fix proper nouns — names, university names, company names, project names — using the context below
3. Fix technical terms that were misheard (e.g., "reacts" → "React", "pie torch" → "PyTorch")
4. Do NOT change the meaning, add new content, or rephrase. Only fix obvious mishearings.
5. If the transcript seems correct, return it unchanged.
6. Keep the same sentence structure and length.

CONTEXT (use this to understand what the speaker is likely saying):
{context}

RAW TRANSCRIPT TO FIX:
{transcript}

Return ONLY the corrected transcript:"""


async def clean_transcript(raw_text: str, context: str = "") -> str:
    """Use the LLM to fix speech-to-text errors based on context."""
    if not raw_text.strip():
        return raw_text

    prompt = CLEANUP_PROMPT.format(
        context=context or "No additional context provided.",
        transcript=raw_text,
    )
    corrected = await ollama.generate(prompt, system=CLEANUP_SYSTEM)

    # Safety: if the LLM returned something wildly different length, keep original
    cleaned = corrected.strip().strip('"').strip("'")
    if len(cleaned) < len(raw_text) * 0.5 or len(cleaned) > len(raw_text) * 2:
        return raw_text

    return cleaned
