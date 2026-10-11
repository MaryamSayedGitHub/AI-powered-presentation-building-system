"""TTS مع fallback: edge-tts (صوت مصري) -> gTTS لو edge-tts اترفض (403)."""
import asyncio, time
import edge_tts

VOICES = {"ar": "ar-EG-SalmaNeural", "en": "en-US-AriaNeural"}


def _edge(text, path, lang):
    asyncio.run(edge_tts.Communicate(text, VOICES[lang]).save(str(path)))


def _gtts(text, path, lang):
    from gtts import gTTS   # uv add gtts
    gTTS(text=text, lang=lang).save(str(path))


def synth(text, path, lang="ar"):
    for attempt in range(3):
        try:
            _edge(text, path, lang)
            return str(path)
        except Exception as e:
            print(f"[tts] edge-tts محاولة {attempt + 1} فشلت: {type(e).__name__}")
            time.sleep(1.5)
    print("[tts] بنستخدم gTTS كبديل (صوت مختلف، مش مصري)")
    _gtts(text, path, lang)
    return str(path)