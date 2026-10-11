import asyncio, edge_tts

VOICES = {"ar": "ar-EG-SalmaNeural", "en": "en-US-AriaNeural"}


def synth(text, path, lang="ar"):
    asyncio.run(edge_tts.Communicate(text, VOICES[lang]).save(str(path)))
    return str(path)
