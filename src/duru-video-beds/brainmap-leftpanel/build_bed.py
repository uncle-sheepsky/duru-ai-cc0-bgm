"""폴리곤 뇌 메이킹 롱폼 「검사는 다 통과했는데, 왼쪽 화면이 2분 넘게 그대로였습니다」 바탕곡 — 신작 1곡(2026-11-14).
4/4 ♩=112.5 · 1마디 = 2.1333s = 64f = 102,400샘플@48k · 8분음표 = 8f = 12,800샘플 · 16분 = 4f(3중 정수).
마디·강조·말 없는 구간은 tools/l2_timeline.py place()(TTS 실측 반영)에서 읽는다 — 손으로 적지 않는다.

생각 = 「왼쪽은 멈춰 있고 오른쪽만 움직인다」를 소리로.
  · 왼쪽(팬 −0.55) 플루트 스타카토가 D 한 음을 같은 꼴(8분 0·3·6칸)로 되풀이한다 = 2분 넘게 같은 그림.
  · 오른쪽(팬 +0.45) 하프가 화음을 풀어 움직인다 = 바뀌는 결과 화면.
  · 모든 화음이 D 를 품게 골라서 멈춘 음이 틀린 음이 되지는 않는다(STILL) — 다만 들킨 뒤(4·5장)엔 마지막 화음을 A♭maj7♯11 로 바꿔
    같은 D 가 ♯11 로 걸린다(ODD = 「맞는 줄 알았는데 어긋나 있다」).
  · 4장 슬램(「한 번도 안 나왔어요」)에서 다른 소리가 다 빠지고 왼쪽 D 만 남는다. 6장 「검사를 새로 만들었어요」에서 C 장조로 올라가며
    왼쪽 플루트가 처음으로 움직인다(화음음 8분 아르페지오) = 정점. 7장은 B♭ 로 돌아와 D 가 화음의 3음으로 길게 놓이며 끝난다.
지문: STILL B♭maj7–Gm9–E♭maj7–Dm7 `[−3,−4,−1,−4]` · ODD B♭maj7–Gm9–E♭maj7–A♭maj7♯11 `[−3,−4,+5,+2]` ·
     16분 킥 {0,6,9} + 클라베스 {4,12} = STILL×K069. 회전 전부 대장과 불일치(bgm/fp_search.py · gate_bed.py G1).
역할(한 자리 한 악기): 멈춘 왼쪽 = 플루트 스타카토 · 오른쪽 화음 = 하프 · 바탕 = 비올라 합주 여린 지속음 · 저음 = 콘트라베이스 피치카토 ·
     선율(말 없는 구간만) = 클라리넷 지속음 · 박 = 큰북 + 클라베스(흔드는 타악 없음) · 강조 = 트럼펫·트롬본 스타카토 한 방 / 팀파니.
저수준만 공용: playlist_melty/bgm/band.py(VSCO 2 CE CC0 샘플러·마스터). 화성·편곡·선율은 신작.
Rebuild: VSCO_SFZ_DIR=/path/to/VSCO-2-CE-SFZ python build_bed.py --tag v7   (writes out/v7/bed.wav · CC0)
"""
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "duru-zoneout-1h"))  # band.py · sfz_sampler.py (shared low-level sampler)
import band  # noqa: E402
from band import SR, Song, inst, perc  # noqa: E402

import types  # noqa: E402
_t = json.loads((HERE / "timing.json").read_text(encoding="utf-8"))  # measured narration timing (values only)
T = types.SimpleNamespace(BAR=_t["BAR"], place=lambda: _t["place"], MEAS=True)
TAG = sys.argv[sys.argv.index("--tag") + 1] if "--tag" in sys.argv else "v1"
BAR_N = 102400
P = T.place()
BARS = round(P[-1]["t1"] / T.BAR)
ROWS = {r["id"]: r for c in P for r in c["rows"] if r["id"] != "[X]"}
BAR_OF = lambda i: int(round(ROWS[i]["t0"] / T.BAR))
CH = [(c["ch"].split()[0], round(c["t0"] / T.BAR), round(c["t1"] / T.BAR)) for c in P]
XS = [(c["ch"].split()[0], r["text"], round(r["t0"] / T.BAR), round(r["t1"] / T.BAR)) for c in P for r in c["rows"] if r["id"] == "[X]"]
SL = {"N3-7": BAR_OF("N3-7"), "N4-3": BAR_OF("N4-3")}          # 강조(통과) · 슬램(한 번도 안 나왔어요)
X_Q = next((x[2], x[3]) for x in XS if x[0] == "H")              # 두루 갸웃
X_BRAIN = next((x[2], x[3]) for x in XS if x[0] == "2")          # 완성 뇌
X_PASS = next((x[2], x[3]) for x in XS if x[0] == "3")           # 통과 표
X_LEFT = next((x[2], x[3]) for x in XS if x[0] == "4")           # 열두 장 왼쪽만 — 멈춘 D 만
X_PEAK = next((x[2], x[3]) for x in XS if x[0] == "6")           # 고친 판 = 정점
END0 = next(x[2] for x in XS if x[1].startswith("엔드"))
CHA = {k: (a, b) for k, a, b in CH}
UNSTUCK = CHA["6"][0]                                             # 「검사를 새로 만들었어요」 = 왼쪽이 처음 움직인다 + C 장조
HOME = CHA["7"][0]

# 화음: (이름, 근음 midi(저음), 패드 보이싱, 하프 화음음)
B = {
    "B♭maj7": (34, [58, 62, 65, 69], [58, 62, 65, 69, 72]),
    "Gm9": (31, [55, 58, 62, 65, 69], [55, 58, 62, 65, 69]),
    "E♭maj7": (39, [51, 55, 58, 62], [51, 55, 58, 62, 67]),
    "Dm7": (38, [50, 53, 57, 60], [50, 53, 57, 60, 62]),
    "A♭maj7♯11": (32, [56, 60, 63, 67], [56, 60, 63, 67, 62]),
    "Cmaj7": (36, [60, 64, 67, 71], [60, 64, 67, 71, 74]),
    "Am9": (33, [57, 60, 64, 67, 71], [57, 60, 64, 67, 71]),
    "Fmaj7": (29, [53, 57, 60, 64], [53, 57, 60, 64, 69]),
    "Em7": (28, [52, 55, 59, 62], [52, 55, 59, 62, 64]),
}
STILL = ["B♭maj7", "Gm9", "E♭maj7", "Dm7"]
ODD = ["B♭maj7", "Gm9", "E♭maj7", "A♭maj7♯11"]
UP = ["Cmaj7", "Am9", "Fmaj7", "Em7"]                             # 같은 꼴 장2도 위(6장)
D5 = 74
KICK16 = (0, 6, 9)
TAP16 = (4, 12)


def chap(bar):
    return next(k for k, a, b in CH if a <= bar < b)


def chord(bar):
    if bar >= BARS - 1:
        return "B♭maj7"
    k = chap(bar)
    a = CHA[k][0]
    if k in ("4", "5"):
        return ODD[(bar - a) % 4]
    if k == "6":
        return UP[(bar - a) % 4]
    return STILL[(bar - a) % 4]


def bb(bar, beat=0.0):
    return bar * 4 + beat


def build():
    song = Song(TAG, "폴리곤 뇌 메이킹 바탕곡", 112.5, 4, BARS, tail=3.0, lufs=-16.0)
    for k, a, b in CH:
        song.section(k, a, b - a)
    log = {"bars": BARS, "slam_bars": SL, "x": {"q": X_Q, "brain": X_BRAIN, "pass": X_PASS, "left": X_LEFT, "peak": X_PEAK}, "unstuck_bar": UNSTUCK, "home_bar": HOME, "end0": END0, "chords": {}}
    for bar in range(BARS):
        c = chord(bar)
        log["chords"][bar] = c
        root, pad, harp = B[c]
        k = chap(bar)
        silent_left = X_LEFT[0] <= bar < X_LEFT[1]
        after_slam = SL["N4-3"] <= bar < X_LEFT[1]
        final = bar == BARS - 1

        # ── 멈춘 왼쪽: 플루트 스타카토 D5 · 8분 0·3·6칸(2분 넘게 같은 꼴) ─────────────
        if bar < UNSTUCK and not final:
            vel = 72 if silent_left or after_slam else 58
            amp = 1.0 if silent_left or after_slam else 0.82
            for e in (0, 3, 6):
                inst(song, "left", "FluteStac", D5, bb(bar, e * 0.5), 0.42, vel=vel, amp=amp, pan=-0.55, send=0.10, human=0.0)
        elif UNSTUCK <= bar < HOME:
            # 처음 움직인다 — 화음음 8분 아르페지오(위로 갔다 내려옴). 정점(말 없는 구간)에선 클라리넷이 머무는 박에만 움직인다.
            pcs = sorted({t % 12 for t in pad + harp})
            pool = sorted({m for pc in pcs for m in range(64, 82) if m % 12 == pc})
            tones = [pool[i * len(pool) // 4] for i in range(4)]
            seq = tones + tones[-2:0:-1]
            peak = X_PEAK[0] <= bar < X_PEAK[1]
            for e in range(8):
                if peak and e in (0, 4):
                    continue                                  # 선율이 새 음을 치는 박은 비운다(대선율 규칙)
                inst(song, "left", "FluteStac", seq[e % len(seq)], bb(bar, e * 0.5), 0.42, vel=66, amp=0.9, pan=-0.55, send=0.12, human=0.0)
        elif bar >= HOME and not final:
            # 집으로 — D 가 다시 한 음이지만 이번엔 화음의 일부로 길게(멈춤이 아니라 놓임)
            if bar < END0 or (bar - END0) % 2 == 0:
                inst(song, "left", "FluteStac", D5, bb(bar, 0), 0.42, vel=56, amp=0.7, pan=-0.55, send=0.16, human=0.0)

        # ── 오른쪽 화음: 하프 8분 풀어치기 ─────────────────────────────────────
        harp_on = (bar >= CHA["1"][0]) and not (SL["N4-3"] <= bar < X_LEFT[1]) and not final
        if k == "H":
            harp_on = False
        if harp_on:
            up = harp + [harp[-2], harp[-3]]
            pat = up[:8] if len(up) >= 8 else (up * 2)[:8]
            for e in range(8):
                pk = X_PEAK[0] <= bar < X_PEAK[1]
                dur = min(1.2, (8 - e) * 0.5 - 0.1) if bar == SL["N4-3"] - 1 else 1.2
                inst(song, "right", "Harp", pat[e], bb(bar, e * 0.5), dur, vel=82 if pk else 70, amp=1.0 if pk else 0.75, pan=0.45, send=0.18, rel=0.05 if bar == SL["N4-3"] - 1 else 0.08)

        # ── 바탕: 비올라 합주 여린 지속음(2장부터 · 슬램~왼쪽만 구간은 빠짐 · 마지막 마디는 B♭add9) ──
        pad_on = bar >= CHA["1"][0] and not (SL["N4-3"] <= bar < X_LEFT[1])
        pad_v = 56 if k == "1" else (84 if X_PEAK[0] <= bar < X_PEAK[1] else 64)
        pad_a = 0.45 if k == "1" else (1.0 if X_PEAK[0] <= bar < X_PEAK[1] else 0.62)
        if final:
            for m in (58, 62, 65, 72):
                inst(song, "pad", "ViolaEnsSusVib-Quiet", m, bb(bar, 0), 3.6, vel=70, amp=0.8, pan=0.05, send=0.3, attack=0.25, rel=1.2)
        elif pad_on:
            for m in pad:
                pre = bar == SL["N4-3"] - 1
                inst(song, "pad", "ViolaEnsSusVib-Quiet", m, bb(bar, 0), 3.55 if pre else 3.95, vel=pad_v, amp=pad_a, pan=0.05, send=0.28, attack=0.18, rel=0.1 if pre else 0.5)

        # ── 저음: 콘트라베이스 피치카토 ────────────────────────────────────────
        if final:
            inst(song, "bass", "ContrabassPizz", 34, bb(bar, 0), 2.0, vel=80, amp=1.0, pan=0.0, send=0.05)
        elif k == "H" or silent_left:
            if bar < X_Q[0] or silent_left:
                inst(song, "bass", "ContrabassPizz", root if not silent_left else 34, bb(bar, 0), 1.0, vel=60, amp=0.7, pan=0.0, send=0.05)
        elif not after_slam:
            busy = k in ("2", "3", "6")
            inst(song, "bass", "ContrabassPizz", root, bb(bar, 0), 1.0, vel=78, amp=1.0, pan=0.0, send=0.05)
            inst(song, "bass", "ContrabassPizz", root + 7, bb(bar, 2), 0.9, vel=70, amp=0.85, pan=0.0, send=0.05)
            if busy:
                nxt = B[chord(bar + 1)][0] if bar + 1 < BARS else root
                inst(song, "bass", "ContrabassPizz", nxt - 1 if nxt - 1 >= 28 else nxt + 11, bb(bar, 3.5), 0.4, vel=64, amp=0.7, pan=0.0, send=0.05)

        # ── 박: 큰북 {0,6,9}/16 + 클라베스 {4,12}/16 ─────────────────────────────
        drums = (CHA["2"][0] <= bar < CHA["4"][0]) or (UNSTUCK + 2 <= bar < HOME)
        drums_light = CHA["5"][0] + 4 <= bar < UNSTUCK                # 「검사는 바뀌는지만 봤어요」부터 큰북만 돌아옴
        if drums or drums_light:
            for s in KICK16:
                perc(song, 36, bb(bar, s * 0.25), amp=0.9 if s == 0 else 0.6, vel=90 if s == 0 else 70, send=0.05)
            if drums:
                for s in TAP16:
                    perc(song, 75, bb(bar, s * 0.25), amp=0.32, vel=80, send=0.08, pan=0.12)

    # ── 강조 1: 「전부 통과했어요」 — 하프 위로 쓸고(앞 마디 4박) 트럼펫·트롬본 스타카토 한 방 ─────────
    b0 = SL["N3-7"]
    for i, m in enumerate([58, 62, 65, 69, 72, 74, 77, 81]):
        inst(song, "right", "Harp", m, bb(b0 - 1, 3 + i * 0.125), 0.8, vel=74, amp=0.7, pan=0.45, send=0.2)
    for m in (70, 74, 77):
        inst(song, "hit", "TrumpetStac", m, bb(b0, 0), 0.5, vel=96, amp=0.9, pan=0.15, send=0.2)
    inst(song, "hit", "TromboneStac", 46, bb(b0, 0), 0.5, vel=96, amp=0.9, pan=-0.1, send=0.2)
    perc(song, 36, bb(b0, 0), amp=1.0, vel=110, send=0.08)

    # ── 슬램: 「한 번도 안 나왔어요」 — 다른 소리 전부 빠지고 팀파니 + 콘트라베이스 낮은 B♭ · 왼쪽 D 만 남는다 ───
    b1 = SL["N4-3"]
    inst(song, "hit", "Timpani", 46, bb(b1, 0), 2.0, vel=110, amp=1.0, pan=0.0, send=0.15)
    inst(song, "hit", "Timpani", 41, bb(b1, 0), 2.0, vel=100, amp=0.8, pan=0.0, send=0.15)
    inst(song, "bass", "ContrabassPizz", 34, bb(b1, 0), 1.5, vel=100, amp=1.1, pan=0.0, send=0.05)

    # ── 선율(말 없는 구간만): 클라리넷 지속음 ───────────────────────────────
    def mel(notes, bar0, vel=80, amp=0.8):
        for beat, dur, m in notes:
            inst(song, "mel", "ClarinetSus", m, bb(bar0, beat), dur, vel=vel, amp=amp, pan=-0.05, send=0.22, attack=0.04, rel=0.3)
    mel([(0, 2, 74), (2, 2, 75)], X_Q[0])                                      # 갸웃: D → E♭(반음 올라가며 묻는다)
    mel([(0, 3, 70), (3, 1, 72), (4, 4, 74)], X_BRAIN[0], vel=74, amp=0.55)                      # 완성 뇌: B♭ → C → D(멈춘 그 음이 선율이 된다)
    mel([(0, 1, 77), (1, 1, 74), (2, 1, 72), (3, 1, 69), (4, 2, 70)], X_PASS[0], vel=70, amp=0.5)   # 통과 표: 내려오는 폭포 F–D–C–A(Dm7 화음음) → B♭
    p0 = X_PEAK[0]
    mel([(0, 2, 69), (2, 2, 72), (4, 4, 71), (8, 2, 67), (10, 2, 76), (12, 4, 72)], p0, vel=100, amp=1.3)   # 정점(C 장조): 긴 음 위주 — 사이를 왼쪽이 채운다
    e0 = END0
    mel([(0, 4, 74), (4, 2, 72), (6, 2, 70), (8, 4, 67), (12, 4, 69), (16, 4, 70), (20, 4, 74)], e0, vel=66, amp=0.45)  # 끝: D 로 시작해 D 로 놓인다
    return song, log


def onset_lead(y):
    return int(np.argmax(np.abs(y) > 0.15 * np.abs(y).max())) / SR


def main():
    song, log = build()
    out = HERE / "out" / TAG
    # v1 실측(버스×장 LUFS): left −33 · right −27 · pad −17 · bass −29 · mel −17 → 멈춘 왼쪽이 들려야 이 곡의 생각이 선다
    gains = {"left": 2.6, "right": 1.15, "pad": 0.3, "bass": 1.6, "mel": 1.0, "hit": 0.9, "perc": 0.55}
    rep = band.master(song, gains, rev_rt=1.3, rev_wet=0.22, out_dir=out, fade_out=0.0, tp_target=-1.6)
    mix = out / "mix.wav"
    from scipy.io import wavfile
    sr, x = wavfile.read(mix)
    N = BARS * BAR_N
    x = x[:N]
    k = int(0.6 * SR)
    x = x.astype(np.float64)
    x[-k:] *= np.linspace(1, 0, k)[:, None] ** 2
    wavfile.write(out / "bed.wav", SR, x.astype(np.int16))
    log["samples"] = int(len(x))
    log["frames"] = len(x) / SR * 30
    (out / "build_log.json").write_text(json.dumps(log, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps({k: log[k] for k in ("bars", "slam_bars", "x", "unstuck_bar", "home_bar", "samples")}, ensure_ascii=False))


if __name__ == "__main__":
    main()
