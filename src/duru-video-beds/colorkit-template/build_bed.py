"""메이킹 롱폼 「내 영상을 아무 캐릭터로나 만들 수 있게 바꿨습니다」 바탕곡 v2 「틀 몬투노」 — 신작 1곡(2026-11-14).
v1(SLOT · 화면 사건마다 칸 화음 · 종소리 · 타격)은 ◆사용자 반려: 「음악이 아쉬움 · 이전 16곡 제작처럼 · 너무 강하게 겹치지 않게 제한하지 말고 · 음악을 효과음처럼 만들려고 하지 말기」.
→ 플레이리스트 16곡처럼 한 곡을 처음부터 끝까지 노래로 짠다: 장르 = 손 몬투노(쿠바 son) · 선율이 대사 밑에서도 계속 흐른다 · 화면 사건에 맞춘 효과 소리 없음.
4/4 ♩=150 · 1마디 = 1.6s = 76,800샘플 · 91마디 = 145.6s = 4,368f(영상 길이 그대로 · R16).
세계: 작은 작업실 손 밴드 — 피아노 몬투노가 같은 꼴로 계속 돈다(틀) · 그 위에서 마림바가 노래한다.
구성(마디): 인트로 0–4 · A1 5–20 · A2 21–32 · B 33–48 · A3 49–64 · C(클라이맥스) 65–80 · 아웃트로 81–90.
  B · C 첫 마디 = N3-7 · N6-4 다운비트(33 · 65) — 효과음이 아니라 곡의 새 단락이 시작되는 자리. 정점 = C 안(말 없는 72–75마디).
지문: 축1 MONTUNO-A I–IV–III7–V(F–B♭–A7–C7) `[+5,−1,+3,+5]` · MONTUNO-B I–iii–VI7–II7(F–Am–D7–G7) `[+4,+5,+5,−2]` — 대장 회전 · 3원 부분열 충돌 0(bgm/fp_search 계열 탐색).
     축3 SON32 = 손 클라베 3-2(2마디 8분 {0,3,6 | 10,12}) + 베이스 툼바오(2박 뒤 · 4박 = 다음 화음 미리) · 킥 {0,14}(1박 + 4박 뒤).
역할(한 자리 한 악기 · 흔드는 타악 없음): 주선율 = 마림바 · 응답 = 플루트(주선율이 쉬는 박에만) · 틀 = 업라이트 피아노 몬투노 · 저음 = 콘트라베이스 피치카토 툼바오 ·
     타악 = 클라베스 · 콩가 · 킥(1박) · 카우벨(C만) · 바탕 = 비올라 합주 여린 지속음(B만).
저수준만 공용: playlist_melty/bgm/band.py(VSCO 2 CE CC0). 화성 · 선율 · 편곡 = 신작.
사용: python build_bed.py [--tag v2] [--out-root <dir>]   (VSCO_SFZ_DIR = VSCO 2 CE SFZ 폴더 · 결과 out/<tag>/bed.wav = 영상에 쓴 곡과 같은 바이트)
"""
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "duru-zoneout-1h"))  # band.py · sfz_sampler.py (shared low-level sampler)
import band as B  # noqa: E402
from band import SR, Song, inst, line, perc, play  # noqa: E402

TAG = sys.argv[sys.argv.index("--tag") + 1] if "--tag" in sys.argv else "v2"
BAR_N = 76800
BARS = 91
SECS = [("intro", 0, 5), ("A1", 5, 16), ("A2", 21, 12), ("B", 33, 16), ("A3", 49, 16), ("C", 65, 16), ("outro", 81, 10)]
PEAK = (72, 75)
A_CH = ["F", "Bb", "A7", "C7"]
B_CH = ["F", "Am", "D7", "G7"]
KICK16 = (0, 14)   # 1박 + 4박 뒤(다음 마디로 미리 밀어 줌 · 툼바오와 같은 방향) — 첫 안 {0} 은 대장 DB · DIRGE 와 같아 교체
CLAVE = [(0, 0.0), (0, 1.5), (0, 3.0), (1, 1.0), (1, 2.0)]   # 3-2 손 클라베(2마디)

A_MEL = line("C5:.5 F5:1 A5:.5 G5:1 F5:1 | D5:.5 F5:.5 Bb5:1.5 A5:.5 G5:1 | A5:1 G5:.5 E5:.5 C#5:1 E5:1 | G5:1.5 F5:.5 E5:1 r:1 | "
             "C5:.5 F5:1 A5:.5 C6:1 A5:1 | Bb5:.5 A5:.5 G5:1 F5:.5 D5:1.5 | E5:.5 G5:.5 C#5:1 A4:1 C#5:1 | C5:1.5 Bb4:.5 C5:1 r:1", bar=4)
A_MEL2 = line("F5:1 A5:.5 C6:.5 A5:1 F5:1 | D5:1 F5:.5 Bb5:1 A5:.5 G5:1 | C#5:.5 E5:.5 A5:1 G5:1 E5:1 | C5:.5 E5:.5 G5:1.5 Bb5:.5 r:1 | "
              "A5:1.5 G5:.5 F5:1 C5:1 | D5:.5 F5:.5 G5:.5 Bb5:1 A5:.5 G5:1 | A5:.5 G5:.5 E5:.5 C#5:1 E5:1.5 | G5:1 F5:.5 E5:.5 C5:1 r:1", bar=4)
B_MEL = line("A5:2 G5:1 F5:1 | E5:3 C5:1 | F#5:2 A5:1 C6:1 | B5:2 G5:1 F5:1 | A5:1 C6:1 A5:1 F5:1 | E5:2 G5:1 E5:1 | D5:1 F#5:1 A5:1 C6:1 | B5:3 r:1", bar=4)
C_MEL = line("F5:.5 F5:.5 A5:.5 C6:1 A5:.5 F5:1 | D6:.5 C6:.5 Bb5:.5 A5:.5 G5:1 F5:1 | E5:.5 G5:.5 A5:.5 C#6:1 A5:.5 G5:1 | E5:1.5 G5:.5 C6:2 | "
             "A5:.5 G5:.5 F5:.5 C5:1 F5:.5 A5:1 | Bb5:1 D6:1 C6:.5 Bb5:.5 A5:1 | G5:.5 A5:.5 E5:.5 C#5:1.5 E5:1 | F5:2 r:2", bar=4)
FILL = {"A": line("G5:.5 A5:.5", start=3.0), "C": line("C6:.5 A5:.5 G5:.5 F5:.5", start=2.0)}   # 주선율이 쉬는 박(마디 끝)에만


def sec(bar):
    return next(n for n, a, k in SECS if a <= bar < a + k)


def chord(bar):
    n = sec(bar)
    if bar == BARS - 1:
        return "F"
    if n == "intro":
        return (A_CH + ["C7"])[bar]
    a = next(a for nn, a, k in SECS if nn == n)
    return (B_CH if n == "B" else A_CH)[(bar - a) % 4]


def bb(bar, beat=0.0):
    return bar * 4 + beat


def build():
    s = Song(TAG, "틀 몬투노", 150, 4, BARS, tail=3.0, lufs=-16.0)
    for n, a, k in SECS:
        s.section(n, a, k)
    log = {"bars": BARS, "secs": SECS, "peak": PEAK, "chords": {}}
    prev = None
    for bar in range(BARS):
        c = chord(bar)
        log["chords"][bar] = c
        n = sec(bar)
        final = bar == BARS - 1
        nxt = chord(bar + 1) if bar + 1 < BARS else "F"
        root = B.bass_note(c, 29, 43)
        v = B.voice(c, 60, 76, prev=prev, n=3)
        prev = v
        light = n in ("intro", "outro")
        loud = n == "C"
        if final:
            for m in B.voice("F", 57, 77, n=4):
                inst(s, "piano", "UprightPiano", m, bb(bar, 0), 2.0, vel=78, amp=0.9, pan=0.12, send=0.2)
            inst(s, "bass", "ContrabassPizz", 29, bb(bar, 0), 2.0, vel=90, amp=1.1, send=0.05)
            inst(s, "lead", "Marimba", 77, bb(bar, 0), 1.5, vel=92, amp=1.0, pan=-0.05, send=0.2)
            continue
        # ── 틀: 피아노 몬투노(1마디 꼴 · 화음음 위아래 번갈아 · 짧게) ───────────
        mont = [(0.5, 0), (1.0, 2), (1.5, 1), (2.5, 2), (3.0, 0), (3.5, 1)]
        for q, i in mont:
            m = v[i]
            for mm in (m, m + 12) if loud else (m,):
                inst(s, "piano", "UprightPiano", mm, bb(bar, q), 0.32, vel=70 if light else (84 if loud else 76), amp=0.75 if light else 0.9, pan=0.14, send=0.12)
        # ── 저음: 툼바오(2박 뒤 = 5음 · 4박 = 다음 화음 근음 미리) · 단락 첫 마디는 1박 근음 ───
        first = any(bar == a for nn, a, k in SECS)
        if first or n == "intro" and bar == 0:
            inst(s, "bass", "ContrabassPizz", root, bb(bar, 0), 1.0, vel=88, amp=1.0, send=0.05)
        if not (n == "intro" and bar < 2):
            inst(s, "bass", "ContrabassPizz", B.bass_note(c, 29, 43, "fifth"), bb(bar, 1.5), 1.2, vel=82, amp=0.95, send=0.05)
            if not any(bar + 1 == a for nn, a, k in SECS):          # 새 단락 바로 앞 마디는 미리 치지 않는다(단락 첫 박에 저음이 새로 들어오게 · 짧은 숨)
                inst(s, "bass", "ContrabassPizz", B.bass_note(nxt, 29, 43), bb(bar, 3.0), 1.0, vel=86, amp=1.0, send=0.05)
        # ── 타악: 클라베(3-2) · 콩가(2박 뒤 슬랩 · 4박 뒤 열린 소리 둘) · 킥 1박 · 카우벨(C) ───
        half = (bar - 0) % 2
        for side, q in CLAVE:
            if side == half:
                perc(s, 75, bb(bar, q), amp=0.42 if not light else 0.32, vel=90, pan=0.22, send=0.08)
        if not (n == "intro" and bar < 2):
            perc(s, 61, bb(bar, 1.0), amp=0.5, vel=90, pan=-0.2, send=0.06)
            perc(s, 63, bb(bar, 3.5), amp=0.55, vel=95, pan=-0.25, send=0.06)
            perc(s, 65, bb(bar, 3.75), amp=0.5, vel=95, pan=-0.3, send=0.06)
            for q in (0.5, 2.0, 2.5):
                perc(s, 60, bb(bar, q), amp=0.22, vel=70, pan=-0.2, send=0.04)
            for q in KICK16:
                perc(s, 36, bb(bar, q * 0.25), amp=(0.75 if not loud else 0.9) * (1 if q == 0 else 0.6), vel=96 if q == 0 else 80, send=0.04)
        if loud:
            for q in (0, 1, 2, 3):
                perc(s, 56, bb(bar, q), amp=0.28 if q else 0.36, vel=90, pan=0.3, send=0.06)
        # ── 바탕: 비올라 합주 여린 지속음(B 만) ───────────────────────────
        if n == "B":
            for m in B.voice(c, 55, 72, n=3):
                inst(s, "pad", "ViolaEnsSusVib-Quiet", m, bb(bar, 0), 3.9, vel=64, amp=0.5, pan=-0.1, send=0.3, attack=0.2, rel=0.5)
    # ── 주선율: 마림바(대사 밑에서도 계속) ─────────────────────────────────
    def mel(notes, bar0, amp=1.0, vel=92, octave=0):
        play(s, "lead", "Marimba", notes, at=bb(bar0), semis=octave, amp=amp, vel=vel, pan=-0.06, send=0.18)
    pick = line("A4:.5 Bb4:.5 B4:.5 C5:.5", start=2.0)                     # 인트로 끝 오르는 다리
    play(s, "lead", "Marimba", pick, at=bb(4), amp=0.8, pan=-0.06, send=0.18)
    mel(A_MEL, 5); mel(A_MEL2, 13)
    mel(A_MEL, 21, amp=1.0); mel(A_MEL[:len([x for x in A_MEL if x[0] < 16])], 29)   # A2 = 12마디(앞 8 + 뒤 4)
    mel(B_MEL, 33, amp=0.95, vel=88); mel(B_MEL, 41, amp=0.95, vel=88)
    mel(A_MEL2, 49); mel(A_MEL, 57)
    mel(C_MEL, 65, amp=1.15, vel=100); mel(C_MEL, 73, amp=1.2, vel=104)
    mel(A_MEL2, 81, amp=0.8, vel=84)
    # ── 응답: 플루트(주선율이 쉬는 마디 끝 박에만) ──────────────────────────
    for a in (21, 25, 29, 49, 53, 57, 61):
        play(s, "resp", "FluteStac", FILL["A"], at=bb(a + 3), amp=0.6, vel=84, pan=0.2, send=0.2)
    for a in (72, 80):
        play(s, "resp", "FluteStac", FILL["C"], at=bb(a), amp=0.7, vel=90, pan=0.2, send=0.2)
    return s, log


def main():
    s, log = build()
    out = Path(sys.argv[sys.argv.index("--out-root") + 1]) / TAG if "--out-root" in sys.argv else HERE / "out" / TAG
    # t2 실측(버스×단락 LUFS · --bus): lead −30 · piano −25 · bass −31 · perc −22 · pad(B) −21 → 선율이 묻힘. 목표 lead ≈ −22 · piano −25 · bass −26 · perc −27 · pad −28 · resp −29
    gains = {"lead": 2.5, "resp": 1.6, "piano": 0.85, "bass": 2.2, "perc": 0.39, "pad": 0.22}
    rep = B.master(s, gains, rev_rt=1.1, rev_wet=0.18, out_dir=out, fade_out=0.0, tp_target=-1.6)
    log["master"] = rep
    from scipy.io import wavfile
    sr, x = wavfile.read(out / "mix.wav")
    n = BARS * BAR_N
    y = x[:n].astype(np.float64)
    k = int(0.5 * SR)
    y[-k:] *= (np.linspace(1, 0, k) ** 3)[:, None]
    wavfile.write(out / "bed.wav", SR, np.round(y).astype(np.int16))
    log["bed"] = {"samples": n, "frames": n / SR * 30, "fade_s": 0.5}
    json.dump(log, open(out / "log.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)


if __name__ == "__main__":
    main()
