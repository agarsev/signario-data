from pathlib import Path
import json
import random

random.seed()

def get_next(number):
    number = number+1
    while str(number).endswith("0") or random.random()>0.96:
        number = number+1
    return number

def assign_to_cut(cut, normal, out):
    try:
        gloss = cut['gloss']
        if gloss == 'Toma falsa':
            number = get_next(out)
            out = number
        else:
            number = get_next(normal)
            normal = number
        cut['number'] = number
    except KeyError:
        pass
    return normal, out

def assign_numbers(data_dir, start_normal, start_out):
    data_dir = Path(data_dir)
    normal = int(start_normal)
    out = int(start_out)
    for info_file in data_dir.glob('**/*.json'):
        info = json.loads(info_file.read_text())
        for cut in info.get('cuts', []):
            normal, out = assign_to_cut(cut, normal, out)
        info_file.write_text(json.dumps(info))
    return normal, out


if __name__ == '__main__':
    import sys
    if len(sys.argv) != 4:
        print(f"Use: {sys.argv[0]} data_dir start_normal start_outtake")
        exit(1)
    last_normal, last_outtake = assign_numbers(*sys.argv[1:])
    print(f"last normal: {last_normal}\nlast outtake: {last_outtake}")
