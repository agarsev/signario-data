import cv2
import pandas as pd
from sklearn.mixture import GaussianMixture as GMM

FPS = 50
PROC_SIZE = (200, 200)
SMOOTH_WIN = 10
BASELINE_WIN = 100
MARGIN_START = 0.6
MARGIN_END = 0.4

def reduce(frame, new_size=PROC_SIZE):
    frame = cv2.resize(frame, new_size)
    return frame

def get_rest_frame(cap, start=1.0*FPS, end=3.0*FPS):
    all_frames = []
    nframe = 0
    while cap.isOpened():
        ret, frame = cap.read()
        nframe += 1
        if ret != True or nframe > end:
            break
        if nframe < start:
            continue
        all_frames.append(reduce(frame))
    avg = all_frames[0]
    for i in range(len(all_frames)):
        if i > 0:
            alpha = 1.0/(i + 1)
            beta = 1.0 - alpha
            avg = cv2.addWeighted(all_frames[i], alpha, avg, beta, 0.0)
    return avg

RENORM = 1/(32*PROC_SIZE[0]*PROC_SIZE[1])
def difference(a, b):
    dist = cv2.norm(a, b, cv2.NORM_L1)
    return dist*RENORM

def get_scores(cap, rest):
    scores = []
    times = []
    while cap.isOpened():
        ret, frame = cap.read()
        if ret != True:
            break
        frame = reduce(frame)
        scores.append(difference(frame, rest))
        times.append(cap.get(cv2.CAP_PROP_POS_MSEC)/1000)
    return pd.Series(scores), times

def get_cut_times(source_vid):

    cap = cv2.VideoCapture(source_vid)
    rest = get_rest_frame(cap)
    scores, times = get_scores(cap, rest)
    cap.release()

    baseline = scores.rolling(BASELINE_WIN).min().fillna(0)
    smooth = (scores-baseline).rolling(SMOOTH_WIN).median().fillna(0)
    model = GMM(2).fit(smooth.values.reshape(-1, 1))
    cutoff = model.means_.mean()

    cuts = []
    start = None
    in_frame = False
    for i in range(SMOOTH_WIN, len(smooth)):
        if smooth[i] > cutoff:
            if not in_frame:
                start = times[i-SMOOTH_WIN] - MARGIN_START
                in_frame = True
        elif smooth[i] < cutoff:
            if in_frame:
                end = times[i-SMOOTH_WIN] + MARGIN_END
                cuts.append((f'{start:2.2f}', f'{end:2.2f}'))
                in_frame = False

    if in_frame:
        print('\nUnfinished last clip!')
        end = times[-1]
        cuts.append((f'{start:2.2f}', f'{end:2.2f}'))
    return cuts

if __name__ == '__main__':
    import sys
    cuts = get_cut_times(sys.argv[1])
    for i in range(len(cuts)):
        print(f'{i} {cuts[i][0]} {cuts[i][1]}')
