"""T11 「우유 한 잔 녹턴」 — E 4/4 ♩=66 · DREAM 구간(따뜻한 우유 같은 느린 녹턴).

지문: 축1 MAJIII-iv — I–iiim–IV–ivm (E–G#m–A–Am) `[+4,+1,0,−5]` IV에서 같은 근음 단조로 꺼지는 한숨 (대장 미사용)
      축3 ALB8-NODRUM — 타악 없음 · 피아노 알베르티 8분(저-고-중-고) + 왼손 온음표 베이스 (대장에 타악 없는 격자 없음)
음색: 리드 = 클라리넷 지속 → 바이올린 솔로(A2) → 플루트(B) / 화음·저음 = 업라이트 피아노 / 끝 = 컵 '팅'(글로켄).
구성: 인트로2 · A16 · B8 · A16 · B8 · A8 · 아웃트로4 = 62마디.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import band as B  # noqa: E402
from band import Song, inst, line, play  # noqa: E402

TAG, TITLE = "t11_nocturne", "우유 한 잔 녹턴"
A_CH = ["E", "G#m", "A", "Am", "E", "G#m", "A", "Am", "E", "E7", "A", "Am", "E", "C#m", "F#m7", "B7"]
B_CH = ["C#m", "G#m", "A", "E", "C#m", "F#7", "A", "B7"]
A_MEL = line("G#4:2 B4:1 E5:1 | D#5:3 B4:1 | C#5:2 E5:1 A5:1 | C5:3 E5:1 | B4:2 E5:1 G#5:1 | F#5:2 D#5:2 | E5:1 C#5:1 A4:2 | C5:4 | "
             "G#4:2 B4:1 E5:1 | D5:3 B4:1 | C#5:2 E5:1 A5:1 | C6:2 B5:1 A5:1 | G#5:2 E5:2 | E5:2 C#5:2 | A4:2 C#5:1 E5:1 | D#5:3 r:1", bar=4)
B_MEL = line("E5:2 G#5:2 | B5:3 G#5:1 | A5:2 E5:1 C#5:1 | B4:4 | C#5:2 E5:1 G#5:1 | A#5:2 F#5:2 | E5:2 C#5:1 A4:1 | B4:2 D#5:2", bar=4)
SECS = [("intro", 2), ("A1", 16), ("B1", 8), ("A2", 16), ("B2", 8), ("A3", 8), ("outro", 4)]


def build():
    bars = sum(n for _, n in SECS)
    s = Song(TAG, TITLE, bpm=66, bar=4, bars=bars, swing=0.5, tail=5.0, lufs=-16.5)
    s.meta = {"fingerprint": "MAJIIIiv×ALB8-NODRUM", "key": "E", "stage": "DREAM"}
    plan, b0 = [], 0
    for name, n in SECS:
        s.section(name, b0, n)
        plan.append((name, b0, n))
        b0 += n
    st = {nm: x for nm, x, n in plan}
    chords = []
    for name, x, n in plan:
        if name == "intro":
            chords += ["E", "B7"]
        elif name == "outro":
            chords += ["A", "Am", "E", "E"]
        elif name == "A3":
            chords += A_CH[:6] + ["A", "Am"]
        else:
            chords += B_CH if name[0] == "B" else A_CH
    prev = None
    for bar, sym in enumerate(chords):
        b = s.B(bar)
        last = bar == len(chords) - 1
        inst(s, "bass", "UprightPiano", B.bass_note(sym, 28, 43), b, 3.8 if not last else 6.0, vel=70, amp=0.8, pan=-0.15, send=0.2, rel=0.6)
        v = B.voice(sym, 52, 67, prev=prev, n=3)
        prev = v
        if last:
            for i, m in enumerate(v + [v[0] + 12]):
                inst(s, "chord", "UprightPiano", m, b + i * 0.25, 5.0, vel=64, amp=1.0, pan=0.1, send=0.3, rel=1.0)
            continue
        lo, mid, hi = v
        for i, m in enumerate([lo, hi, mid, hi, lo, hi, mid, hi]):
            inst(s, "chord", "UprightPiano", m, b + i * 0.5, 0.9, vel=62 if i % 2 else 70, amp=0.9, pan=0.12, send=0.25, rel=0.3, human=0.01)
    play(s, "lead", "ClarinetSus", A_MEL, at=s.B(st["A1"]), amp=0.42, pan=-0.05, send=0.3, stac=0.97, rel=0.3, vel=70)
    play(s, "lead", "FluteSusVib", B_MEL, at=s.B(st["B1"]), amp=1.0, pan=-0.05, send=0.32, stac=0.97, rel=0.3, vel=70)
    play(s, "lead", "SViolinVib-Quiet", A_MEL, at=s.B(st["A2"]), semis=12, amp=1.2, pan=-0.05, send=0.32, stac=0.98, rel=0.35, vel=70, attack=0.04)
    play(s, "resp", "ClarinetSus", [(b, d, m) for b, d, m in A_MEL if d >= 3], at=s.B(st["A2"]), semis=-12, amp=0.22, pan=0.25, send=0.3, rel=0.3, vel=60)
    play(s, "lead", "ClarinetSus", B_MEL, at=s.B(st["B2"]), amp=0.42, pan=-0.05, send=0.3, stac=0.97, rel=0.3, vel=70)
    play(s, "lead", "FluteSusVib", [n for n in A_MEL if n[0] < 32], at=s.B(st["A3"]), amp=1.7, pan=-0.05, send=0.32, stac=0.97, rel=0.3, vel=64)
    ob = s.B(st["outro"])
    inst(s, "color", "Glockenspiel", 88, ob + 13, 2.0, vel=70, amp=3.0, pan=0.35, send=0.45, rel=1.6)      # 컵 '팅'
    inst(s, "color", "Glockenspiel", 95, ob + 13.08, 1.5, vel=60, amp=1.5, pan=0.35, send=0.45, rel=1.2)
    gains = {"bass": 1.0, "chord": 0.9, "lead": 1.0, "resp": 0.9, "color": 0.8}
    return B.master(s, gains, rev_rt=2.0, rev_wet=0.34)


if __name__ == "__main__":
    build()
