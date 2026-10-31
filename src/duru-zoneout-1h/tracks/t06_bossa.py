"""T06 「졸린 보사」 — D 4/4 ♩=120 · DEEP 구간(나른한 보사노바).

지문: 축1 BOSSA-II7 — Imaj7–II7–iim7–V7 (Dmaj7–E7–Em7–A7) `[+2,0,+5,+5]` 같은 근음에서 장→단으로 꺾이는 II(대장 미사용)
      브리지 IVmaj7–iv6–iiim7–VI7 (Gmaj7–Gm6–F#m7–B7)
      축3 BOSSA-CLV — 베이스 {0,6,8}(1박·2박 뒤16분 앞당김·3박) + 림 클라베 2마디 보사 3-2 + 나일론 기타 당김 코드 (대장 전무)
음색: 리드 = 플루트 → 마림바(B) → 나일론 기타 선율(A3, 카플러스-스트롱 합성) / 화음 = 나일론 기타 / 저음 = 콘트라베이스.
구성: 인트로4 · A16 · A16 · B8 · A16 · B8 · A16 · A16 · 아웃트로4 = 104마디.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import band as B  # noqa: E402
from band import Song, inst, line, perc, play  # noqa: E402

TAG, TITLE = "t06_bossa", "졸린 보사"
A_CH = ["Dmaj7", "Dmaj7", "E7", "E7", "Em7", "A7", "Dmaj7", "A7", "Dmaj7", "Dmaj7", "E7", "E7", "Em7", "A7", "D6", "D6"]
B_CH = ["Gmaj7", "Gm6", "F#m7", "B7", "Em7", "A7", "Dmaj7", "A7"]
A_MEL = line("F#5:1.5 E5:.5 F#5:2 | r:.5 E5:.5 F#5:.5 A5:.5 C#5:2 | G#5:1.5 F#5:.5 G#5:2 | r:.5 F#5:.5 G#5:.5 B5:.5 D5:2 | "
             "G5:1.5 F#5:.5 E5:1 D5:1 | C#5:1 E5:1 G5:2 | F#5:4 | r:2 E5:.5 F#5:.5 G5:.5 G#5:.5 | "
             "A5:1.5 F#5:.5 A5:2 | r:.5 G5:.5 F#5:.5 E5:.5 C#5:2 | B5:1.5 G#5:.5 B5:2 | r:.5 A5:.5 G#5:.5 F#5:.5 D5:2 | "
             "G5:1 B5:1 D6:1 B5:1 | C#6:1.5 A5:.5 G5:2 | F#5:2 B4:2 | D5:4", bar=4)
B_MEL = line("B5:1.5 A5:.5 F#5:2 | Bb5:1.5 A5:.5 E5:2 | A5:1 F#5:1 C#5:2 | D#5:1.5 F#5:.5 A5:2 | "
             "G5:1.5 F#5:.5 E5:1 B4:1 | C#5:1 E5:1 A5:1 G5:1 | F#5:4 | E5:2 r:2", bar=4)
SECS = [("intro", 4), ("A1", 16), ("A2", 16), ("B1", 8), ("A3", 16), ("B2", 8), ("A4", 16), ("A5", 16), ("outro", 4)]
GTR_HITS = [0.5, 1.5, 3.0, 4.5, 6.0, 7.5]          # 2마디(8박) 당김 코드 자리
CLAVE = [0, 1.5, 3.0, 5.0, 6.0]                     # 보사 3-2 림 클라베(8박)


def nylon(s, m, b, dur_b, amp, pan, bus="chord", bright=0.35, send=0.18):
    y = B.ks_pluck(m, max(0.4, dur_b * s.beat + 0.3), bright=bright, decay=0.9965)
    s.add(bus, y * amp, s.pos(b) + (B.h01(b, m, 11) - 0.5) * 0.008, pan=pan, send=send)


def build():
    bars = sum(n for _, n in SECS)
    s = Song(TAG, TITLE, bpm=120, bar=4, bars=bars, swing=0.5, tail=4.0, lufs=-16.0)
    s.meta = {"fingerprint": "BOSSAII7×BOSSA-CLV", "key": "D", "stage": "DEEP"}
    plan, b0 = [], 0
    for name, n in SECS:
        s.section(name, b0, n)
        plan.append((name, b0, n))
        b0 += n
    st = {nm: x for nm, x, n in plan}
    chords = []
    for name, x, n in plan:
        if name == "intro":
            chords += ["Dmaj7", "E7", "Em7", "A7"]
        elif name == "outro":
            chords += ["Dmaj7", "Gm6", "D6", "Dmaj9"]
        else:
            chords += B_CH if name[0] == "B" else A_CH
    prev = None
    for bar, sym in enumerate(chords):
        name = next(nm for nm, x, n in plan if x <= bar < x + n)
        b = s.B(bar)
        last = bar == len(chords) - 1
        r = B.bass_note(sym, 33, 48)
        f5 = B.bass_note(sym, 33, 48, "fifth")
        for q, m, a in ((0, r, 1.0), (1.5, f5, 0.7), (2.0, f5, 0.85)) if not last else ((0, r, 1.0),):
            inst(s, "bass", "ContrabassPizz", m, b + q, 1.0 if q != 1.5 else 0.45, vel=90, amp=2.25 * a, pan=-0.05, send=0.1, human=0.01)
        v = B.voice(sym, 52, 67, prev=prev)
        prev = v
        if last:
            for i, m in enumerate(v + [v[-1] + 5]):
                nylon(s, m, b + i * 0.12, 3.5, 0.32, 0.15)
            continue
        half = bar % 2
        for h in GTR_HITS:
            if half * 4 <= h < half * 4 + 4:
                for i, m in enumerate(v):
                    nylon(s, m, b + (h - half * 4) + 0.01 * i, 0.9, 0.135, 0.18 + 0.03 * i)
        if name != "intro":
            for c in CLAVE:
                if half * 4 <= c < half * 4 + 4:
                    perc(s, 75, b + (c - half * 4), amp=1.1, pan=0.3, vel=70)
            for q in range(8):
                perc(s, 53, b + q * 0.5, amp=0.55 if q % 2 else 0.38, pan=-0.35, vel=60, dur=0.2)
    play(s, "lead", "FluteSusVib", A_MEL, at=s.B(st["A1"]), amp=1.0, pan=-0.05, send=0.25, stac=0.95, rel=0.2, vel=72)
    play(s, "lead", "FluteSusVib", A_MEL, at=s.B(st["A2"]), amp=1.0, pan=-0.05, send=0.25, stac=0.95, rel=0.2, vel=72)
    fills = [(b, d, m) for b, d, m in A_MEL if d <= 0.5]
    play(s, "resp", "Marimba", fills, at=s.B(st["A2"]), semis=-12, amp=1.5, pan=0.3, send=0.2, rel=0.3)
    play(s, "lead", "Marimba", B_MEL, at=s.B(st["B1"]), amp=3.8, pan=-0.05, send=0.22, rel=0.4)
    for b, d, m in A_MEL:
        nylon(s, m, s.B(st["A3"]) + b, d, 0.72, -0.1, bus="lead", bright=0.55, send=0.22)
    play(s, "resp", "FluteSusVib", [(b, d, m) for b, d, m in A_MEL if d >= 2], at=s.B(st["A3"]), semis=-12, amp=1.3, pan=0.25, send=0.3, rel=0.3, vel=64)
    play(s, "lead", "FluteSusVib", B_MEL, at=s.B(st["B2"]), amp=1.0, pan=-0.05, send=0.25, stac=0.95, rel=0.2, vel=72)
    play(s, "lead", "FluteSusVib", A_MEL, at=s.B(st["A4"]), amp=1.0, pan=-0.05, send=0.25, stac=0.95, rel=0.2, vel=72)
    play(s, "resp", "Marimba", fills, at=s.B(st["A4"]), semis=-12, amp=1.4, pan=0.3, send=0.2, rel=0.3)
    play(s, "lead", "Marimba", A_MEL[:len(A_MEL) // 2], at=s.B(st["A5"]), amp=3.2, pan=-0.05, send=0.25, rel=0.4)   # 졸려서 앞 반만
    gains = {"bass": 1.0, "perc": 0.8, "chord": 0.9, "lead": 1.0, "resp": 0.9}
    return B.master(s, gains, rev_rt=1.5, rev_wet=0.3)


if __name__ == "__main__":
    build()
