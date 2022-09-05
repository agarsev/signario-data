import sys
from subprocess import run
from pathlib import Path
import json

if len(sys.argv)!=3:
    print(f"Usage: {sys.argv[0]} cut_dir vid_id")
    exit(1)

out_path = Path(sys.argv[1])
vid_path = Path(sys.argv[2])

base_command = ['ffmpeg', '-hide_banner', '-loglevel', 'error', '-stats']

info = json.loads((vid_path / 'info.json').read_text())
cuts = info.get('cuts')
failed = []
if cuts is None or len(cuts) == 0:
    out_path.mkdir(parents=True, exist_ok=True)
    (out_path / 'no_cuts').write_text('')
    exit(0)

for cut in cuts:
    try:
        number = str(cut['number'])
    except KeyError:
        print(f'Cut without number in video {sys.argv[2]}')
        continue
    major = number[:-2]
    minor = number[-2:]
    dest = out_path / major
    dest.mkdir(parents=True, exist_ok=True)
    in_vid = 'lowq.mp4' if cut['gloss'] != 'Toma falsa' else 'raw.mp4'
    dest = (dest / minor).with_suffix('.mp4')
    if not dest.exists():
        r = run(base_command + [
            '-ss', str(cut['start']), '-to', str(cut['end']),
            '-i', vid_path / in_vid,
            '-an', '-vcodec', 'libx264',
            dest])
        if r.returncode != 0:
            failed.append(str(dest))

flog = out_path / 'failed.txt'
if len(failed) > 0:
    flog.write_text('\n'.join(failed)+'\n')
else:
    flog.unlink(missing_ok=True)
