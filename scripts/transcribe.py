"""Word-level transcript with faster-whisper (CPU, int8)."""
import sys, json, os
from faster_whisper import WhisperModel

def transcribe(path, out_json, model_name="small", language="hi"):
    model = WhisperModel(model_name, device="cpu", compute_type="int8")
    segs, _ = model.transcribe(path, language=language, word_timestamps=True,
                               vad_filter=True, beam_size=5)
    words = []
    for s in segs:
        for w in s.words or []:
            words.append({"word": w.word.strip(), "start": w.start, "end": w.end})
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(words, f, ensure_ascii=False, indent=1)
    return words

if __name__ == "__main__":
    transcribe(sys.argv[1], sys.argv[2],
               os.environ.get("WHISPER_MODEL", "small"), os.environ.get("LANGUAGE", "hi"))
