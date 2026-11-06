"""ffmpeg cleanup: cut silences, alternating punch-in zoom, colour grade, loudnorm."""
import subprocess, re, sys, json

def run(cmd):
    subprocess.run(cmd, check=True)

def probe_duration(path):
    out = subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration",
                                   "-of","default=nw=1:nk=1",path]).decode().strip()
    return float(out)

def speech_segments(path, noise="-35dB", min_sil=0.4, pad=0.12):
    p = subprocess.run(["ffmpeg","-i",path,"-af",f"silencedetect=n={noise}:d={min_sil}",
                        "-f","null","-"],capture_output=True,text=True)
    total = probe_duration(path)
    starts = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", p.stderr)]
    ends = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", p.stderr)]
    segs, cur = [], 0.0
    for i, s in enumerate(starts):
        if s - cur > 0.25:
            segs.append((max(0, cur - pad), min(total, s + pad)))
        cur = ends[i] if i < len(ends) else total
    if total - cur > 0.25:
        segs.append((max(0, cur - pad), total))
    return segs or [(0, total)]

def edit(src, dst):
    segs = speech_segments(src)
    parts, vlabels, alabels = [], [], []
    for i, (a, b) in enumerate(segs):
        z = 1.0 if i % 2 == 0 else 1.14
        crop = f"crop=iw/{z}:ih/{z}" if z != 1.0 else "null"
        parts.append(f"[0:v]trim={a:.3f}:{b:.3f},setpts=PTS-STARTPTS,{crop},"
                     f"scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1[v{i}]")
        parts.append(f"[0:a]atrim={a:.3f}:{b:.3f},asetpts=PTS-STARTPTS,"
                     f"afade=t=in:d=0.03,afade=t=out:st={max(0,b-a-0.03):.3f}:d=0.03[a{i}]")
        vlabels.append(f"[v{i}]"); alabels.append(f"[a{i}]")
    n = len(segs)
    inter = "".join(f"{v}{a}" for v, a in zip(vlabels, alabels))
    parts.append(f"{inter}concat=n={n}:v=1:a=1[vc][ac]")
    parts.append("[vc]eq=contrast=1.08:saturation=1.18:brightness=0.02,unsharp=5:5:0.6,fade=t=in:d=0.2[vo]")
    parts.append("[ac]highpass=f=80,afftdn=nf=-30,acompressor=threshold=-18dB:ratio=3,"
                 "loudnorm=I=-14:TP=-1.5:LRA=9[ao]")
    run(["ffmpeg","-y","-i",src,"-filter_complex",";".join(parts),"-map","[vo]","-map","[ao]",
         "-c:v","libx264","-crf","20","-preset","veryfast","-pix_fmt","yuv420p",
         "-c:a","aac","-b:a","192k","-movflags","+faststart",dst])

if __name__ == "__main__":
    edit(sys.argv[1], sys.argv[2])
