"""Build an ASS subtitle file: word-by-word highlighted captions, hook card, CTA card."""
import json, sys

FONT = "Noto Sans"          # fonts-noto-core covers Latin + Devanagari
def t(sec):
    h = int(sec // 3600); m = int(sec % 3600 // 60); s = sec % 60
    return f"{h}:{m:02d}:{s:05.2f}"

HEADER = f"""[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920

[V4+ Styles]
Format: Name,Fontname,Fontsize,PrimaryColour,SecondaryColour,OutlineColour,BackColour,Bold,Italic,Underline,StrikeOut,ScaleX,ScaleY,Spacing,Angle,BorderStyle,Outline,Shadow,Alignment,MarginL,MarginR,MarginV,Encoding
Style: Cap,{FONT},84,&H00FFFFFF,&H00FFFFFF,&H00000000,&H80000000,1,0,0,0,100,100,0,0,1,6,2,2,60,60,520,1
Style: Hook,{FONT},96,&H0000E5FF,&H0000E5FF,&H00000000,&H80000000,1,0,0,0,100,100,0,0,1,7,3,8,70,70,260,1
Style: CTA,{FONT},80,&H0000E5FF,&H0000E5FF,&H00000000,&H80000000,1,0,0,0,100,100,0,0,1,6,3,2,70,70,260,1

[Events]
Format: Layer,Start,End,Style,Name,MarginL,MarginR,MarginV,Effect,Text
"""

def build(words, duration, hook="", cta="", chunk=3):
    ev = []
    if hook:
        ev.append(f"Dialogue: 1,{t(0.1)},{t(min(2.6, duration))},Hook,,0,0,0,,{{\\fad(150,200)\\fscx60\\fscy60\\t(0,200,\\fscx100\\fscy100)}}{hook}")
    for i in range(0, len(words), chunk):
        grp = words[i:i + chunk]
        for j, w in enumerate(grp):
            start = w["start"]
            end = grp[j + 1]["start"] if j + 1 < len(grp) else w["end"] + 0.15
            line = []
            for k, x in enumerate(grp):
                if k == j:
                    line.append(f"{{\\c&H0000E5FF&\\fscx115\\fscy115}}{x['word']}{{\\r}}")
                else:
                    line.append(x["word"])
            ev.append(f"Dialogue: 0,{t(start)},{t(end)},Cap,,0,0,0,,{' '.join(line)}")
    if cta and duration > 4:
        ev.append(f"Dialogue: 1,{t(duration-2.5)},{t(duration)},CTA,,0,0,0,,{{\\fad(200,0)}}{cta}")
    return HEADER + "\n".join(ev) + "\n"

if __name__ == "__main__":
    words = json.load(open(sys.argv[1], encoding="utf-8"))
    open(sys.argv[2], "w", encoding="utf-8").write(build(words, float(sys.argv[3]), sys.argv[4], sys.argv[5]))
