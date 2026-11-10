"""음악 형식 게이트 — 측정만 한다. 귀 판정은 ◆사용자(이 스크립트를 쓴 Claude 는 소리를 들을 수 없다).

G1 지문: 이 곡의 루트운동(모든 회전)이 대장(스키마·hyak 대장 문서 파싱)과 불일치 · 킥 세트 {0,8,12} 가 대장의 킥 세트와 불일치
G2 3중 정수: 92마디 × 76,800샘플 = 길이 · 48f/마디 · 총 프레임이 timeline 과 같음
G3 말미: 마지막 100ms 피크 ≤ 0.01
G4 아크(마디별 K-가중 라우드니스): 전곡 최대 마디가 합주(74–77) 안 · 막 평균이 정점 합주 > 놀기 > 선물 > 낯가림 · 돌봄 < 놀기 · 6막 < 선물 · 숨 멈춤 구간 = 완전 무음
G5 누르는 순간마다 소리: 손짓(종류별) 시각마다 그 소리를 내는 버스에 온셋이 있고 오차 ≤ 1프레임
G6 클립 0 · 트루피크 ≤ −1.5 dBTP · 통합 라우드니스 −14 ± 0.5 LUFS
G7 음역: 스펙트럼 무게중심 ≤ 950 Hz · 1~2.5kHz 비중 ≤ 20% (승인곡 747Hz·13% / 반려곡 1245Hz·35% — feedback-bgm-register-not-too-high)
G8 역할당 한 명: 합주 4마디의 16분 창마다 「가장 큰 버스 −18dB 안」 버스 수 평균 ≤ 6 (ep38 승인판 드롭 첫 마디 5.0 — feedback-climax-one-per-role)
G9 슬램 온셋: 다운비트 오차 ≤ 1프레임(R4)
G10 소리 색이 튀는 폭: 0.4초 창마다 스펙트럼 무게중심이 이웃 창과 몇 옥타브 다른가(중앙값) — 음악이 깔리는 막(2·3·5막)에서 ≤ 0.8옥타브.
    근거 = 사용자 「음악이 좀 난잡한 것 같아」(v1 · 2026-11-09): v1 2막 1.19 · 3막 1.20 / 승인곡 ep38 v2.1 0.475. ⚠임계 0.8 은 승인 1 · 반려 1 표본의 중간값(가설)
사용: <site-factory venv> bgm/gate_music.py [--tag v1]
"""
import json
import math
import re
import sys
from pathlib import Path

import numpy as np
import pyloudnorm as pyln
from scipy.io import wavfile
from scipy.signal import butter, resample_poly, sosfilt, welch

HERE = Path(__file__).resolve().parent
EP = HERE.parent
ROOT = next(d for d in [HERE, *HERE.parents] if (d / ".akashic-root").exists())
TL = json.loads((EP / "timeline.json").read_text(encoding="utf-8"))
M, C = TL["meta"], TL["cues"]
SR, FPS = M["sr"], M["fps"]
BAR_N = M["spb"] * M["bpb"]
BARS = M["bars"]
SPB = M["spb"]
MINE = {"HOME I–II–IV–I": [2, 3, -5], "HOME(4칸)": [2, 3, -5, 0], "SHY i–iv–♭II–V7": [5, -4, 6, 5], "PLAY vi–II–IV–I": [5, 3, -5, -3],
        "CARE I–iii–ii–IV": [4, -2, 3, -5], "BUILD 베이스 IV–#IV°–I/V–V7": [1, 1, 0, 5], "SORRY 다리 iv–i/V–V–V": [-5, -5, 0, 5]}
MY_KICK = {0, 8, 12}
# 손짓 → 소리를 내는 버스(온셋을 찾을 스템)
SOUND_BUS = {"knock": ["fx"], "tap": ["cur"], "poke": ["cur"], "bow": ["cur"], "drag": ["cur", "fx"], "pat": ["cur"], "tickle": ["cur", "duru"],
             "grab": ["cur"], "drop": ["cur"], "land": ["fx", "duru"], "hold": ["cur", "kick"], "meet": ["fx", "cur"], "startle": ["cur"], "click": ["fx"],
             "fan": ["fx"], "d_knock": ["fx"], "wiggle": ["cur"]}


def doc_text():
    docs = list((ROOT / "projects/duru/스키마").glob("*지문*.md")) + list((ROOT / "projects/hyak").rglob("*지문*대장*.md"))
    # 이 곡 자신의 등재 행(「| poke_long」으로 시작)은 대조에서 뺀다 — 등재 뒤에 게이트를 다시 돌려도 자기 자신과 충돌하지 않게
    return docs, {p.name: chr(10).join(l for l in p.read_text(encoding="utf-8").splitlines() if not l.startswith("| poke_long")) for p in docs}


def doc_vectors(texts):
    out = {}
    for name, t in texts.items():
        for m in re.finditer(r"\[([−+\-]?\d+(?:\s*,\s*[−+\-]?\d+){1,})\]", t):
            v = [int(x.strip().replace("−", "-").replace("+", "")) for x in m.group(1).split(",")]
            out.setdefault(tuple(v), name)
    return out


def doc_kicks(texts):
    out = set()
    for t in texts.values():
        for m in re.finditer(r"\{(\d+(?:\s*,\s*\d+)*)\}", t):
            out.add(frozenset(int(x) for x in m.group(1).split(",")))
    return out


def rotations(v):
    return [v[i:] + v[:i] for i in range(len(v))]


def events():
    """(종류, 박) — 소리가 붙어야 하는 손짓 시각 전부."""
    ev = []
    for t in TL["touch"]:
        k = t["kind"]
        if k in ("knock", "poke", "bow", "meet", "startle", "click", "grab"):
            ev.append((k, t["b"]))
        elif k == "tap":
            ev.append(("tap", t["b"]))
        elif k == "drag":
            ev.append(("drag", t["b0"]))
        elif k in ("pat", "tickle", "fan"):
            b = t["b0"]
            while b < t["b1"] - 1e-6:
                ev.append((k, b))
                b += t["every"]
        elif k == "drop":
            ev.append(("drop", t["b"]))
            ev.append(("land", t["land"]))
        elif k == "hold":
            ev.append(("hold", t["b0"]))
        elif k == "wiggle":
            ev.append(("wiggle", t["b0"]))
    ev += [("d_knock", b) for b in TL["d_knocks"]]
    return sorted(ev, key=lambda e: e[1])


def onset_err(y, t0, win=0.05):
    """온셋 시각 − t0 (초) · 앞 30ms 대비 뒤 30ms 에너지 비 · 근처 포락선 최대값.
    온셋 = t0−30ms 부터 훑어, 포락선이 「앞 바닥 + (근처 최대 − 앞 바닥)의 절반」을 처음 넘는 지점.
    (처음엔 「가장 가파르게 오르는 지점」으로 쟀는데, 음이 울리는 중의 잔물결이 실제 어택보다 가파르게 잡혀
     쓰담 24번 중 1번을 1.23프레임 늦다고 오판했다 — 파형을 직접 보니 어택은 박 위에 있었다. 2026-11-09)"""
    a = max(0, int((t0 - win) * SR))
    b = int((t0 + win) * SR)
    w = int(0.002 * SR)
    env = np.sqrt(np.convolve(y[a:b] ** 2, np.ones(w) / w, mode="same"))[::w]
    tt = (a + np.arange(len(env)) * w) / SR - t0
    pre = float(np.median(env[tt < -0.02])) if (tt < -0.02).any() else 0.0
    near = env[(tt >= -0.01)]
    pk = float(near.max())
    thr = pre + 0.5 * (pk - pre)
    idx = [i for i in range(len(env)) if tt[i] >= -0.03 and env[i] >= thr]
    t = tt[idx[0]] if idx else 9.0
    i0 = int(t0 * SR)
    p0 = np.sqrt((y[max(0, i0 - int(0.03 * SR)):i0] ** 2).mean() + 1e-12)
    p1 = np.sqrt((y[i0:i0 + int(0.03 * SR)] ** 2).mean() + 1e-12)
    return float(t), p1 / p0, pk


def main():
    tag = sys.argv[sys.argv.index("--tag") + 1] if "--tag" in sys.argv else "v2"
    out = HERE / "out" / tag
    x = wavfile.read(out / "mix.wav")[1].astype(np.float64) / 32768.0
    res = {}
    docs, texts = doc_text()
    parsed, kicks = doc_vectors(texts), doc_kicks(texts)
    hits = {k: [f"{parsed[t]}{list(t)}" for t in parsed if list(t) in rotations(v)] for k, v in MINE.items()}
    res["G1_fingerprint"] = {"docs": [p.name for p in docs], "parsed_vectors": len(parsed), "parsed_kick_sets": len(kicks), "axis1_collisions": hits,
                             "kick_collision": frozenset(MY_KICK) in kicks, "pass": not any(hits.values()) and frozenset(MY_KICK) not in kicks}
    res["G2_grid"] = {"samples": len(x), "expect": BARS * BAR_N, "frames": len(x) / SR * FPS, "timeline_frames": M["total_frames"],
                      "pass": len(x) == BARS * BAR_N and len(x) / SR * FPS == M["total_frames"]}
    tail = float(np.abs(x[-int(0.1 * SR):]).max())
    res["G3_tail"] = {"last100ms_peak": round(tail, 4), "pass": tail <= 0.01}
    meter = pyln.Meter(SR)
    L = {}
    for b in range(BARS):
        seg = x[b * BAR_N:(b + 1) * BAR_N]
        v = meter.integrated_loudness(seg) if np.abs(seg).max() > 1e-4 else -99.0
        L[b] = round(float(v), 2) if math.isfinite(v) else -99.0
    acts = {a["name"]: (a["bar0"], a["bar1"]) for a in TL["acts"]}

    def seg_l(b0, b1):
        return round(float(meter.integrated_loudness(x[b0 * BAR_N:b1 * BAR_N])), 2)

    AL = {k: seg_l(*v) for k, v in acts.items()}
    tutti = seg_l(74, 78)
    a_, b_ = int(round(C["breath"] * SPB)), int(round(C["slam"] * SPB))
    breath_peak = float(np.abs(x[a_:b_]).max())
    mx = max(L, key=L.get)
    res["G4_arc"] = {"max_bar": mx, "act_lufs": AL, "tutti_74_77": tutti, "breath_peak": breath_peak,
                     "pass": 74 <= mx < 78 and tutti > AL["play"] > AL["gifts"] > AL["shy"] and AL["care"] < AL["play"] and AL["turn"] < AL["gifts"] and breath_peak == 0.0}
    res["bar_lufs"] = L
    # G5 — 스템에서 온셋
    st = {}
    for p in (out / "stems").glob("*.wav"):
        st[p.stem] = wavfile.read(p)[1].astype(np.float64).mean(1) / 32768.0
    hp = butter(2, 120, btype="highpass", fs=SR, output="sos")
    sth = {k: sosfilt(hp, v) if k != "kick" else v for k, v in st.items()}
    rows, bad = [], []
    for kind, b in events():
        t0 = b * SPB / SR
        best = None
        for bus in SOUND_BUS[kind]:
            if bus not in sth:
                continue
            err, ratio, pk = onset_err(sth[bus], t0)
            ok = abs(err) * FPS <= 1.0 and (ratio >= 1.5 or pk > 0.02) and pk > 0.004
            cand = (ok, -abs(err), bus, round(err * FPS, 2), round(ratio, 2), round(pk, 4))
            if best is None or cand > best:
                best = cand
        rows.append((kind, round(b, 3), *best[2:]))
        if not best[0]:
            bad.append((kind, round(b, 3), *best[2:]))
    by = {}
    for r in rows:
        by.setdefault(r[0], []).append(abs(r[3]))
    res["G5_touch_sound"] = {"events": len(rows), "missing": bad, "max_abs_err_f_by_kind": {k: max(v) for k, v in by.items()}, "count_by_kind": {k: len(v) for k, v in by.items()}, "pass": not bad}
    tp = 20 * math.log10(np.abs(resample_poly(x, 4, 1, axis=0)).max() + 1e-12)
    I = float(meter.integrated_loudness(x))
    res["G6_level"] = {"true_peak_db": round(tp, 2), "clip_samples": int((np.abs(x) >= 32767 / 32768).sum()), "integrated_lufs": round(I, 2), "pass": tp <= -1.5 and abs(I + 14) <= 0.5}
    fq, p = welch(x.mean(1), SR, nperseg=8192)
    cen = float((fq * p).sum() / p.sum())
    hi = float(p[(fq >= 1000) & (fq <= 2500)].sum() / p.sum())
    res["G7_register"] = {"centroid_hz": round(cen, 1), "share_1k_2k5": round(hi, 4), "limit": [950, 0.20], "ref_approved": [747, 0.13], "ref_rejected": [1245, 0.35], "pass": cen <= 950 and hi <= 0.20}
    gains = json.loads((out / "report.json").read_text(encoding="utf-8"))["gains"]
    # 스템은 버스별로 0.9 정규화돼 있어 크기 비교에 못 쓴다 → 빌더가 남긴 버스×막 값 대신, 정규화 전 상대 크기를 스템 최대값 표에서 복원할 수 없으므로 master 의 layers 를 그대로 쓰고 합주 구간만 다시 센다.
    peaks = json.loads((out / "stem_peaks.json").read_text(encoding="utf-8")) if (out / "stem_peaks.json").exists() else None
    lay = None
    if peaks:
        cnt = []
        step = SPB // 4
        for q in range(74 * BAR_N, 78 * BAR_N, step):
            r = [np.sqrt(np.mean((st[k][q:q + step] * peaks[k] / 0.9 * gains[k]) ** 2)) + 1e-12 for k in st if k in gains and k in peaks]
            mxr = max(r)
            cnt.append(sum(1 for v in r if 20 * math.log10(v / mxr) > -18))
        lay = round(float(np.mean(cnt)), 2)
    res["G8_one_per_role"] = {"tutti_layers_mean": lay, "limit": 6, "ref_ep38_drop": 5.0, "pass": lay is not None and lay <= 6}
    err, ratio, _ = onset_err(sosfilt(hp, x.mean(1)), C["slam"] * SPB / SR)
    res["G9_slam"] = {"err_f": round(err * FPS, 2), "post_pre_ratio": round(ratio, 1) if ratio < 1e6 else "앞이 무음", "slam_frame": M["slam_frame"], "pass": abs(err * FPS) <= 1.0}
    def jump(seg, win=0.4):
        n = int(win * SR)
        c = []
        for i in range(0, len(seg) - n, n):
            sp = np.abs(np.fft.rfft(seg[i:i + n] * np.hanning(n))) ** 2
            c.append((np.fft.rfftfreq(n, 1 / SR) * sp).sum() / sp.sum() if sp.sum() > 1e-6 else np.nan)
        d = np.abs(np.diff(np.log2(np.array(c))))
        return round(float(np.nanmedian(d)), 3)

    mono = x.mean(1)
    J = {k: jump(mono[v[0] * BAR_N:v[1] * BAR_N]) for k, v in acts.items()}
    J2 = {k: jump(mono[v[0] * BAR_N:v[1] * BAR_N], 0.8) for k, v in acts.items()}      # 참고: 2박(0.8초) 창 — 쿵·짝이 번갈아 드러나는 것을 빼고 본 값
    res["G10_timbre_jump"] = {"median_octaves_by_act": J, "two_beat_window_info": J2, "limit": 0.8, "ref_approved_ep38": 0.475, "ref_rejected_v1": {"gifts": 1.194, "play": 1.202},
                              "pass": all(J[k] <= 0.8 for k in ("gifts", "play", "peak"))}
    res["info"] = {"below60Hz_share": round(float(p[fq < 60].sum() / p.sum()), 4), "duration_s": len(x) / SR}
    res["ALL_PASS"] = all(v["pass"] for k, v in res.items() if k.startswith("G"))
    (out / "gate.json").write_text(json.dumps(res, ensure_ascii=False, indent=1, default=lambda o: o.item() if hasattr(o, "item") else str(o)), encoding="utf-8")
    for k, v in res.items():
        if k != "bar_lufs":
            print(k, json.dumps(v, ensure_ascii=False, default=lambda o: o.item() if hasattr(o, "item") else str(o)))


if __name__ == "__main__":
    main()
