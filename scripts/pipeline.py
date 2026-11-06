"""Orchestrator: for each raw video -> edit -> transcribe -> captions -> burn -> outputs."""
import os, sys, json, subprocess, pathlib
sys.path.insert(0, os.path.dirname(__file__))
from edit import edit, probe_duration
from transcribe import transcribe
from captions import build

def process(src, outdir):
    name = pathlib.Path(src).stem
    od = pathlib.Path(outdir) / name
    od.mkdir(parents=True, exist_ok=True)
    edited = od / "edited.mp4"
    edit(src, str(edited))
    words = transcribe(str(edited), str(od / "words.json"),
                       os.environ.get("WHISPER_MODEL", "small"), os.environ.get("LANGUAGE", "hi"))
    dur = probe_duration(str(edited))
    ass = od / "captions.ass"
    ass.write_text(build(words, dur, os.environ.get("HOOK_TEXT", ""), os.environ.get("CTA_TEXT", "")),
                   encoding="utf-8")
    final = od / f"{name}_final.mp4"
    subprocess.run(["ffmpeg", "-y", "-i", str(edited), "-vf", f"ass={ass}",
                    "-c:v", "libx264", "-crf", "20", "-preset", "veryfast", "-c:a", "copy",
                    "-movflags", "+faststart", str(final)], check=True)
    (od / "transcript.txt").write_text(" ".join(w["word"] for w in words), encoding="utf-8")
    (od / "metadata_TODO.md").write_text(
        "# Title / description / hashtags\n"
        "Paste transcript.txt to Claude and ask: 'iska title, description, hashtags, cover text do'.\n",
        encoding="utf-8")
    for f in ("edited.mp4",):  # keep outputs small
        (od / f).unlink(missing_ok=True)
    print("done:", final)

if __name__ == "__main__":
    indir, outdir = sys.argv[1], sys.argv[2]
    vids = [str(p) for p in sorted(pathlib.Path(indir).glob("*")) if p.suffix.lower() in (".mp4", ".mov")]
    if not vids:
        sys.exit("No videos in Drive inbox (AIBABA/inbox).")
    for v in vids:
        process(v, outdir)
