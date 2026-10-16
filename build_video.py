#!/usr/bin/env python3
"""Build a presentation video part from slides + narration chunks.
Usage: python3 build_video.py 1 2 output/video_parts/part-01.mp4
Minimal style: 854x480 (480p), static slide, 0.5s fade in/out, slide crossfade via fades.
"""
import json, subprocess, sys, pathlib, re
import imageio_ffmpeg
FF = imageio_ffmpeg.get_ffmpeg_exe()

def duration(path):
    r = subprocess.run([FF, "-i", str(path)], capture_output=True, text=True)
    m = re.search(r"Duration: (\d+):(\d+):([\d.]+)", r.stderr)
    h, mnt, s = int(m.group(1)), int(m.group(2)), float(m.group(3))
    return h*3600 + mnt*60 + s

def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stderr[-3000:]); raise SystemExit(f"ffmpeg failed: {cmd[0]}")
    return r

def main():
    slides = [int(x) for x in sys.argv[1:-1]]
    out = pathlib.Path(sys.argv[-1]); out.parent.mkdir(parents=True, exist_ok=True)
    chunks = json.load(open("output/chunks.json"))
    tmp = pathlib.Path("work/tmp_segments"); tmp.mkdir(parents=True, exist_ok=True)
    segs = []
    for s in slides:
        # audio chunks for this slide, in global order
        idxs = [i for i,c in enumerate(chunks) if c["slide"]==s]
        audios = [pathlib.Path(f"output/audio/chunk-{i+1:03d}.mp3") for i in idxs]
        missing = [str(a) for a in audios if not a.exists()]
        if missing:
            raise SystemExit(f"Missing audio for slide {s}: {missing}")
        # concat audio with 0.35s silence between chunks
        slide_audio = tmp / f"slide-{s:02d}.mp3"
        if len(audios)==1:
            run([FF,"-y","-i",str(audios[0]),"-c","copy",str(slide_audio)])
        else:
            inputs=[]; filters=[]
            for j,a in enumerate(audios):
                inputs += ["-i", str(a)]
            # generate silence via anullsrc appended as filter: use concat with adelay approach - simpler: concat demuxer with re-encode
            # Use filter: each audio resampled, concat n
            fc = "".join(f"[{j}:a]aresample=24000,aformat=sample_fmts=fltp:channel_layouts=mono[a{j}];" for j in range(len(audios)))
            fc += "".join(f"[a{j}]" for j in range(len(audios))) + f"concat=n={len(audios)}:v=0:a=1[out]"
            run([FF,"-y",*inputs,"-filter_complex",fc,"-map","[out]","-c:a","libmp3lame","-q:a","3",str(slide_audio)])
        dur = duration(slide_audio) + 0.8  # breathing room
        seg = tmp / f"seg-{s:02d}.mp4"
        img = f"output/slides/slide-{s:02d}.png"
        # static image, scale to 854x480, subtle fade in/out (minimal style)
        vf = f"scale=854:480:force_original_aspect_ratio=decrease,pad=854:480:(ow-iw)/2:(oh-ih)/2,setsar=1,format=yuv420p,fade=t=in:st=0:d=0.5,fade=t=out:st={max(dur-0.5,0):.2f}:d=0.5"
        run([FF,"-y","-loop","1","-i",img,"-i",str(slide_audio),"-vf",vf,"-c:v","libx264","-preset","veryfast","-crf","23","-r","15","-c:a","aac","-b:a","128k","-t",f"{dur:.2f}","-shortest",str(seg)])
        segs.append(seg); print(f"slide {s}: audio {dur:.1f}s -> {seg}")
    # concat segments (same codec/size) via concat demuxer re-encode for safety
    lst = tmp/"concat.txt"; lst.write_text("".join(f"file '{p.resolve()}'\n" for p in segs))
    run([FF,"-y","-f","concat","-safe","0","-i",str(lst),"-c","copy",str(out)])
    print(f"BUILT {out} duration={duration(out):.1f}s")

if __name__=="__main__":
    main()
