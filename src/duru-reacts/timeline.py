"""「건드리면 반응하는 두루」 롱폼 애니메이션 — 단일 값 파일(타임라인) 생성기.

화면(comp)과 소리(bgm/build_music.py)가 같은 사건표를 읽는다. 시간 단위 = 박(beat). 여기 말고 다른 곳에 시각 상수를 쓰지 않는다.
♩150 · 4/4 · 30fps → 1박 = 12프레임 = 19,200샘플@48k · 16분음표 = 3프레임(정수) · 1마디 = 48프레임 = 1.6초.
막 구성 = 장면표.md(사용자 확정 2026-11-09: 초안 + 1막 끝 서로 사과 + 3막 쓰담 녹아내림 · 기본 자세 얼굴은 1막 또렷한 판 idle / 2막부터 순한 판 calm).

출력: timeline.json(파이썬용) · timeline.js(window.TL — 컴포지션용)
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent

BPM, FPS, SR, BPB = 150, 30, 48000, 4
FPB = FPS * 60 / BPM              # 12 프레임/박
SPB = SR * 60 // BPM              # 19,200 샘플/박
assert FPB == int(FPB) and SR * 60 % BPM == 0

# ── 막(마디 범위) · 배경(하루의 시간) ──────────────────────────────────────────
ACTS = [
    dict(id=0, name="knock",   title="노크",          bar0=0,  bar1=4,  bg="night"),
    dict(id=1, name="shy",     title="낯가림",        bar0=4,  bar1=20, bg="dawn"),
    dict(id=2, name="gifts",   title="선물 공세",     bar0=20, bar1=36, bg="morning"),
    dict(id=3, name="play",    title="같이 놀기",     bar0=36, bar1=56, bg="day"),
    dict(id=4, name="care",    title="돌봐 주기",     bar0=56, bar1=68, bg="sunset"),
    dict(id=5, name="peak",    title="정점",          bar0=68, bar1=80, bg="pink"),
    dict(id=6, name="turn",    title="이번엔 두루가", bar0=80, bar1=92, bg="night2"),
]
BARS = ACTS[-1]["bar1"]
TOTAL_BEATS = BARS * BPB


def B(bar, beat=0.0):
    """(마디, 마디 안 박) → 절대 박."""
    return bar * BPB + beat


# 배경색이 다음 색으로 넘어가는 구간(박) — 막 경계 앞뒤로 천천히. 4막 안에서 노을 → 보라(해가 짐).
BG = [
    dict(b=B(0), name="night"), dict(b=B(4), name="dawn", fade=4), dict(b=B(19), name="morning", fade=8),
    dict(b=B(35), name="day", fade=8), dict(b=B(55), name="sunset", fade=8), dict(b=B(61), name="dusk", fade=6),
    dict(b=B(68), name="pink", fade=4), dict(b=B(79, 2), name="night2", fade=8), dict(b=B(90), name="dark", fade=2),
]

# ── 무대(1920×1080) ───────────────────────────────────────────────────────────
STAGE = (1920, 1080)
# 세이프존: 읽는 요소(낱말 · 손짓 이름 · 게이지)는 가장자리 10% 안쪽 = x 192~1728 · y 108~972 에만 둔다(제작 계약 11단계). 두루 그림과 배경은 밖으로 나가도 된다.
SAFE = (192, 108, 1728, 972)
FACE = (960, 480)          # 두루 얼굴 중심(스티커 기준점이 여기 온다)
HEAD = (960, 295)          # 정수리(쓰담)
CHEEK = (1085, 545)        # 볼(콕 찌르는 자리 — 화면 오른쪽 볼)
CHEST = (960, 755)
BELLY = (960, 825)
FRONT = (960, 905)         # 두루 앞(물건이 놓이는 자리)
HOOF = (1205, 785)         # 5막 발굽을 내미는 자리(스팟 프레임에서 잰 값)
KNOCK_AT = (1200, 690)     # 6막 두루가 화면을 두드리는 자리(스팟 프레임에서 잰 값)
# ★두루 세계(스티커 · 소품 · 커서 · 두루에 붙는 이펙트)는 화면에서 WORLD_DX 만큼 왼쪽으로 옮겨 그린다 — 오른쪽에 낱말 기둥을 비우기 위해.
#   위의 FACE~KNOCK_AT 와 아래 손짓 좌표는 전부 「옮기기 전」 좌표다. 낱말 · 손짓 이름 · 게이지 자리는 화면 좌표(옮기지 않음).
WORLD_DX = -150
EDGE = (1925, 585)         # 0막 빼꼼 — 옮긴 뒤 x 1775: 스티커 안의 벽이 화면 오른쪽 끝에 걸친다
LAMP = (400, 860)          # 6막 스탠드(옮긴 뒤 x 250 · 0.8배로 그림)
REST = (700, 960)          # 커서가 쉬는 자리(옮긴 뒤 x 550 — 스탠드 오른쪽 아래)
WORD_SLOT = (1475, 330)    # [화면 좌표] 두루의 말(큰 낱말) — 읽는 자리 한 곳(오른쪽 기둥). 낱말 폭 ≤ 420(외곽선 포함 ≤ 492) → x 1232~1724
WORD_PEEK = (1300, 400)    # [화면 좌표] 0막 빼꼼 때만 — 두루가 오른쪽 끝에 있으므로 낱말을 그 왼쪽에
LABEL_SLOT = (420, 912)    # [화면 좌표] 손짓 이름(작은 낱말) — 왼쪽 아래 한 곳
GAUGE_POS = (810, 150)     # [화면 좌표] 게이지 중심 = 옮긴 두루의 머리 위(높이 80 → y 110~190)

# ── 이야기 큐(이름 → 박) — 화면·소리가 같이 읽는 닻 ────────────────────────────
C = dict(
    # 0막 노크
    enter=B(0), knock1=B(1), knock2=B(2), peek=B(2, 2), hide=B(3, 2),
    # 1막 낯가림
    tap_edge=B(4), peek2=B(4, 1), come_out=B(6), poke1=B(8), back1=B(9, 2), poke2=B(10), back2=B(12),
    poke3=B(13), puff_max=B(13, 1.5), puff_out=B(14, 2.5), back3=B(15), bow=B(16), sorry=B(17), back4=B(19),
    # 2막 선물 공세
    leave=B(20), cup_drag=B(21), cup_arrive=B(22), coffee=B(23), soften=B(25), bun_drag=B(26), bun_arrive=B(27), eat=B(27, 1),
    back5=B(29), shy=B(30, 2), thanks=B(32), back6=B(34),
    # 3막 같이 놀기
    pat0=B(36, 2), pat1=B(40), melt_max=B(41), melt_end=B(43), tickle0=B(44), tickle1=B(46, 2), back7=B(47),
    grab=B(48), lift_top=B(48, 2), drop=B(50), land=B(50, 1), back8=B(51, 2), cheer=B(52), love=B(54),
    # 4막 돌봐 주기
    hot=B(56), fan_drag=B(58), fan0=B(59), fan1=B(61), cold=B(61, 2), blanket_drag=B(63), cozy=B(64), hug=B(66, 2),
    # 5막 정점
    settle=B(68), hold0=B(69), clap=B(70), breath=B(73, 2), slam=B(74), gift_word=B(75), back9=B(77),
    hoof0=B(77, 2), hoof_touch=B(78), hoof_back=B(79), hoof_end=B(80),
    # 6막 이번엔 두루가
    still=B(80), look=B(81, 2), d_knock=B(82, 2), startle=B(83), wave=B(84), sleepy=B(86), sleep=B(88), lamp_off=B(90), end=B(92),
)

# ── 씬: 어느 컷이 [b0, b1) 동안 보이나 ─────────────────────────────────────────
# mode: loop = 승인 GIF 를 제 속도(ms)로 반복 · seq = 장 번호를 박에 맞춰 지정([[씬 시작부터 박, 장 번호(0부터)], …])
#       breathe = 쉬는 몸(6장 숨쉬기·깜빡 8박 주기) · none = 두루 없음
# at = 스티커 기준점이 놓이는 무대 좌표(기본 FACE)
BREATHE = [[0, 0], [3, 1], [5.5, 2], [5.75, 3], [6.25, 4], [6.5, 5]]   # 8박 주기 안의 [박, 장]


def seq(*pairs):
    return [list(p) for p in pairs]


S = []


def scene(cut, b0, b1, mode="loop", at=None, **kw):
    S.append(dict(cut=cut, b0=b0, b1=b1, mode=mode, at=list(at or FACE), **kw))


scene(None, C["enter"], C["peek"], mode="none")
scene("32_peek", C["peek"], B(4), mode="seq", at=EDGE, anchor="raw",
      seq=seq((0, 0), (0.5, 1), (1, 2), (1.5, 3), (2.5, 4), (3, 5), (4, 6), (5, 7), (5.5, -1)))   # 나왔다가 눈 마주치고 쏙(−1 = 안 보임)
scene("32_peek", C["peek2"], C["come_out"], mode="seq", at=EDGE, anchor="raw",
      seq=seq((0, 0), (0.5, 1), (1, 2), (1.5, 3), (3, 4), (4, 5), (5, 6), (6, 3), (6.5, 7)))
scene("idle", C["come_out"], C["poke1"], mode="breathe", enter="pop")
scene("13_surprise", C["poke1"], C["back1"])
scene("idle", C["back1"], C["poke2"], mode="breathe")
scene("05_no", C["poke2"], C["back2"])
scene("idle", C["back2"], C["poke3"], mode="breathe")
scene("puff", C["poke3"], C["back3"], mode="seq", seq=seq((0, 0), (0.5, 1), (1.5, 2), (3.5, 3), (4, 2), (4.5, 3), (5, 2), (5.5, 3), (6.5, 4), (7.25, 5)))
scene("idle", C["back3"], C["sorry"], mode="breathe")
scene("03_sorry", C["sorry"], C["back4"])
scene("idle", C["back4"], C["coffee"], mode="breathe")
scene("31_coffee", C["coffee"], C["soften"])
scene("calm", C["soften"], C["eat"], mode="breathe")              # ★ 여기서 처음 순한 얼굴
scene("30_eat", C["eat"], C["back5"])
scene("calm", C["back5"], C["shy"], mode="breathe")
scene("18_shy", C["shy"], C["thanks"])
scene("02_thanks", C["thanks"], C["back6"])
scene("calm", C["back6"], C["pat0"], mode="breathe")
scene("pat", C["pat0"], C["pat1"], mode="seq", seq=seq((0, 0), (1, 1), (2.5, 2), (5, 3), (8, 4), (9.5, 2), (11, 3), (12.5, 4), (13.5, 2)))
scene("melt", C["pat1"], C["melt_end"], mode="seq", seq=seq((0, 0), (1.5, 1), (3, 2), (4, 3), (8, 4), (10, 5)))
scene("calm", C["melt_end"], C["tickle0"], mode="breathe")
scene("tickle", C["tickle0"], C["back7"], mode="seq",
      seq=seq((0, 0), (0.5, 1), (1.5, 2), (2.5, 3), (3.5, 1), (4.5, 2), (5.5, 3), (6.5, 1), (7.5, 2), (8.5, 3), (10, 4), (11.25, 5)))
scene("calm", C["back7"], C["grab"], mode="breathe")
scene("lift", C["grab"], C["back8"], mode="seq",
      seq=seq((0, 0), (1.5, 1), (2.5, 2), (3.5, 1), (4.5, 2), (5.5, 1), (6.5, 2), (7.5, 1), (8, 3), (9, 4), (11.5, 5)))
scene("calm", C["back8"], C["cheer"], mode="breathe")
scene("11_cheer", C["cheer"], C["love"])
scene("06_love", C["love"], C["hot"])
scene("29_hot", C["hot"], C["fan0"])
scene("calm", C["fan0"], C["cold"], mode="hold", frame=3, sway=True)   # 눈 감고 바람 맞음(감은 눈 장 고정 + 살랑)
scene("28_cold", C["cold"], C["cozy"])
scene("cozy", C["cozy"], C["hug"], mode="seq", seq=seq((0, 0), (1.5, 1), (3, 2), (5, 3), (6.5, 4), (8, 3), (9, 5)))
scene("08_hug", C["hug"], C["settle"])
scene("calm", C["settle"], C["clap"], mode="breathe")
scene("12_congrats", C["clap"], C["breath"])
scene("12_congrats", C["breath"], C["slam"], mode="hold", frame=0)      # 숨 멈춤 — 정지
scene("35_gift", C["slam"], C["back9"])
scene("calm", C["back9"], C["hoof0"], mode="breathe")
scene("hoof", C["hoof0"], C["hoof_end"], mode="seq", seq=seq((0, 0), (1, 1), (2, 2), (3.5, 3), (6, 4), (8, 5)))
scene("calm", C["still"], C["look"], mode="breathe")
scene("knock", C["look"], C["wave"], mode="seq",
      seq=seq((0, 0), (2, 1), (4, 2), (4.25, 3), (4.5, 4), (4.75, 3), (6, 1), (8, 2), (8.25, 3), (8.5, 4), (8.75, 3), (9, 2), (9.25, 3), (9.5, 5)))
scene("01_wave", C["wave"], C["sleepy"])
scene("sleepy", C["sleepy"], C["sleep"], mode="seq", seq=seq((0, 0), (1.5, 1), (3.5, 2), (5, 3), (6, 4), (7, 5)))
scene("23_sleep", C["sleep"], C["end"], anchor="raw")

# ── 손짓(커서) ───────────────────────────────────────────────────────────────
# kind: move(이동만) · knock/tap/poke(순간) · drag(물건 끌어오기) · pat(쓸기) · tickle(빠른 문지르기) · grab(잡고 들기) · drop(놓기)
#       hold(누르고 기다림) · fan(부채질) · bow(꾸벅) · startle(움찔) · wiggle(흔들) · click(스탠드) · still(멈춤)
T = []


def touch(kind, b=None, **kw):
    T.append(dict(kind=kind, **({"b": b} if b is not None else {}), **kw))


touch("move", b0=C["enter"], b1=B(0, 3), frm=(-60, 1140), to=(1500, 620))
touch("knock", C["knock1"], x=1500, y=620)
touch("knock", C["knock1"] + 0.5, x=1500, y=620)
touch("knock", C["knock2"], x=1500, y=620)
touch("knock", C["knock2"] + 0.5, x=1500, y=620)
touch("knock", C["knock2"] + 1, x=1500, y=620)
touch("tap", C["tap_edge"], x=1560, y=640)
touch("move", b0=B(5), b1=C["come_out"], frm=(1560, 640), to=(1360, 760))
touch("poke", C["poke1"], x=CHEEK[0], y=CHEEK[1], n=1)
touch("poke", C["poke2"], x=CHEEK[0], y=CHEEK[1], n=2)
touch("wiggle", b0=B(12, 2), b1=B(13), x=1250, y=560)                  # 또 누를까 망설임
touch("poke", C["poke3"], x=CHEEK[0], y=CHEEK[1], n=3)
touch("move", b0=C["back3"], b1=B(15, 3), frm=(1250, 560), to=(1420, 800))   # 물러남
touch("bow", C["bow"], x=1420, y=800)
touch("bow", C["bow"] + 2, x=1420, y=800)
touch("move", b0=C["leave"], b1=B(20, 3), frm=(1420, 800), to=(-80, 760))    # 화면 밖으로
touch("drag", b0=C["cup_drag"], b1=C["cup_arrive"], item="cup", frm=(-140, 780), to=(FRONT[0] - 10, FRONT[1]))
touch("move", b0=C["cup_arrive"], b1=B(22, 2), frm=(FRONT[0] + 60, FRONT[1]), to=(560, 800))
touch("move", b0=B(25, 2), b1=B(25, 3.5), frm=(560, 800), to=(2000, 780))
touch("drag", b0=C["bun_drag"], b1=C["bun_arrive"], item="bun", frm=(2060, 800), to=(FRONT[0] + 10, FRONT[1]))
touch("move", b0=C["bun_arrive"], b1=B(27, 2), frm=(FRONT[0] + 60, FRONT[1]), to=(1400, 800))
touch("still", b0=C["back5"], b1=C["shy"], x=1400, y=800)
touch("wiggle", b0=C["back6"], b1=B(35), x=1400, y=760)                # 기뻐서 폴짝
touch("move", b0=B(35, 2), b1=C["pat0"], frm=(1400, 760), to=(HEAD[0] + 150, HEAD[1] - 20))
touch("pat", b0=C["pat0"], b1=C["melt_end"] - 2, path=[(HEAD[0] + 150, HEAD[1] - 10), (HEAD[0] - 150, HEAD[1] - 10)], every=1.0)   # 1박마다 한 번 쓸기
touch("move", b0=C["melt_end"] - 1, b1=C["tickle0"], frm=(HEAD[0], HEAD[1]), to=(BELLY[0] - 90, BELLY[1]))
touch("tickle", b0=C["tickle0"], b1=C["tickle1"], x=BELLY[0], y=BELLY[1], w=200, every=0.5)   # 8분마다 방향 바꿈
touch("move", b0=C["tickle1"], b1=C["back7"], frm=(BELLY[0], BELLY[1]), to=(1300, 700))
touch("grab", C["grab"], x=CHEST[0] + 40, y=CHEST[1] - 60)
touch("lift", b0=C["grab"], b1=C["lift_top"], dy=-105)               # 스티커가 통째로 들림(머리가 게이지를 가리지 않는 높이)
touch("carry", b0=C["lift_top"], b1=C["drop"], dy=-105, sway=40)
touch("drop", C["drop"], land=C["land"])
touch("move", b0=C["land"], b1=C["back8"], frm=(CHEST[0] + 40, CHEST[1] - 60), to=(1400, 760))
touch("wiggle", b0=C["cheer"], b1=C["love"], x=1400, y=700)
touch("move", b0=C["hot"], b1=B(57, 2), frm=(1400, 700), to=(1300, 620))
touch("move", b0=B(57, 2), b1=C["fan_drag"], frm=(1300, 620), to=(-80, 700))
touch("drag", b0=C["fan_drag"], b1=C["fan0"], item="fan", frm=(-140, 700), to=(640, 520), keep=True)
touch("fan", b0=C["fan0"], b1=C["fan1"], x=640, y=520, every=1.0)
touch("move", b0=C["fan1"], b1=C["cold"], frm=(640, 520), to=(-120, 620), item="fan")     # 부채를 치움
touch("drag", b0=C["blanket_drag"], b1=C["cozy"], item="blanket", frm=(2060, 760), to=(FACE[0], FACE[1] + 160))
touch("move", b0=C["cozy"], b1=B(64, 2), frm=(FACE[0] + 60, FACE[1] + 160), to=(1420, 780))
touch("move", b0=C["settle"], b1=C["hold0"], frm=(1420, 780), to=(CHEST[0], CHEST[1]))
touch("hold", b0=C["hold0"], b1=C["clap"], x=CHEST[0], y=CHEST[1])
# 박수 빌드 — 손끝이 점점 빨라진다(4분 → 8분 → 16분) · 숨 멈춤 직전까지
_build = [B(70) + k for k in (0, 1, 2, 3)] + [B(71) + k * 0.5 for k in range(8)] + [B(72) + k * 0.5 for k in range(8)] + [B(73) + k * 0.25 for k in range(8)]
_ring = [(560, 420), (1360, 420), (600, 760), (1320, 760), (960, 210), (480, 600), (1440, 600), (760, 880), (1160, 880), (700, 300), (1220, 300), (960, 930)]
for i, b in enumerate(_build):
    touch("tap", b, x=_ring[i % len(_ring)][0], y=_ring[i % len(_ring)][1], build=i)
touch("still", b0=C["breath"], b1=C["slam"], x=CHEST[0], y=CHEST[1])
touch("tap", C["slam"], x=CHEST[0], y=CHEST[1], slam=True)
touch("move", b0=B(76, 2), b1=C["hoof0"], frm=(1400, 760), to=(HOOF[0] + 200, HOOF[1] + 60))
touch("move", b0=C["hoof0"], b1=C["hoof_touch"], frm=(HOOF[0] + 200, HOOF[1] + 60), to=(HOOF[0] + 16, HOOF[1]))
touch("meet", C["hoof_touch"], x=HOOF[0], y=HOOF[1])                  # 커서와 발굽이 닿는 순간
touch("still", b0=C["hoof_touch"], b1=C["hoof_back"], x=HOOF[0] + 16, y=HOOF[1])
touch("move", b0=C["hoof_back"], b1=C["hoof_end"], frm=(HOOF[0] + 16, HOOF[1]), to=REST)
touch("still", b0=C["still"], b1=C["startle"], x=REST[0], y=REST[1])
touch("startle", C["startle"], x=REST[0], y=REST[1])
touch("move", b0=B(83, 2), b1=C["wave"], frm=REST, to=(1380, 640))
touch("wiggle", b0=C["wave"] + 2, b1=C["sleepy"], x=1380, y=640)        # 커서도 손 흔듦
touch("move", b0=C["sleep"], b1=B(89, 2), frm=(1380, 640), to=(LAMP[0] + 30, LAMP[1] - 120))
touch("click", C["lamp_off"], x=LAMP[0] + 30, y=LAMP[1] - 120)
touch("move", b0=B(90, 2), b1=C["end"], frm=(LAMP[0] + 30, LAMP[1] - 120), to=(LAMP[0] + 30, LAMP[1] - 120), fade=True)

# 두루 쪽 사건(커서가 아닌 것) — 6막 두루의 노크
D_KNOCKS = [C["d_knock"], C["d_knock"] + 0.5, B(83, 2), B(83, 2.5), B(83, 3)]     # 0막 커서의 2번 + 3번과 같은 박 모양

# ── 화면 낱말(영어 짧은 낱말만) ───────────────────────────────────────────────
# 큰 낱말 = 두루의 말(WORD_SLOT) · style: pop(통통) · stamp(도장) · soft(조용) · float(떠오름)
WORDS = [
    dict(text="...?",      b0=B(3),        b1=C["hide"] + 1,   style="soft",  color="moon", at=WORD_PEEK),
    dict(text="!?",        b0=C["poke1"],  b1=C["back1"],      style="pop",   color="tang"),
    dict(text="NOPE",      b0=C["poke2"],  b1=C["back2"],      style="stamp", color="ink"),
    dict(text="HMPH",      b0=C["puff_max"], b1=C["back3"],    style="stamp", color="ink"),
    dict(text="sorry...",  b0=C["sorry"],  b1=C["back4"],      style="soft",  color="ink"),
    dict(text="YUM",       b0=C["eat"],    b1=C["back5"],      style="pop",   color="red"),
    dict(text="THANK YOU", b0=C["thanks"], b1=C["back6"],      style="pop",   color="green"),
    dict(text="MELT",      b0=C["melt_max"], b1=C["melt_end"] - 1, style="float", color="ink"),
    dict(text="HEHE",      b0=C["tickle0"] + 1, b1=C["tickle1"] + 1, style="pop", color="red"),
    dict(text="WHEE",      b0=C["lift_top"], b1=C["drop"],     style="pop",   color="tang"),
    dict(text="OOF",       b0=C["land"],   b1=C["back8"],      style="stamp", color="ink"),
    dict(text="AGAIN!",    b0=C["cheer"],  b1=C["love"],       style="pop",   color="red"),
    dict(text="HOT...",    b0=C["hot"],    b1=C["fan_drag"],   style="soft",  color="tang"),
    dict(text="COLD...",   b0=C["cold"],   b1=C["blanket_drag"], style="soft", color="ice"),
    dict(text="WARM",      b0=C["cozy"] + 3, b1=C["hug"],      style="float", color="red"),
    dict(text="MAX!",      b0=C["slam"],   b1=C["gift_word"],  style="pop",   color="red", big=True),
    dict(text="FOR YOU",   b0=C["gift_word"], b1=C["back9"],   style="pop",   color="red", big=True),
    dict(text="HIGH FIVE", b0=C["hoof_touch"], b1=C["hoof_back"] + 2, style="pop", color="green"),
    dict(text="knock knock", b0=C["d_knock"], b1=C["startle"] + 3, style="pop", color="moon"),
    dict(text="HI",        b0=C["wave"],   b1=C["sleepy"],     style="pop",   color="moon", big=True),
    dict(text="zzz",       b0=C["sleep"] + 1, b1=C["end"],     style="float", color="moon"),
]
# 작은 낱말 = 커서의 손짓 이름(LABEL_SLOT)
LABELS = [
    dict(text="knock knock",   b0=C["knock1"], b1=C["knock1"] + 3),
    dict(text="knock knock knock", b0=C["knock2"], b1=C["knock2"] + 3),
    dict(text="tap",           b0=C["tap_edge"], b1=C["tap_edge"] + 2),
    dict(text="poke",          b0=C["poke1"], b1=C["poke1"] + 2),
    dict(text="poke again",    b0=C["poke2"], b1=C["poke2"] + 2),
    dict(text="poke again?",   b0=B(12, 2),   b1=C["poke3"] + 2),
    dict(text="sorry",         b0=C["bow"],   b1=C["sorry"]),
    dict(text="FOR YOU?",      b0=C["cup_drag"], b1=C["coffee"]),
    dict(text="one more",      b0=C["bun_drag"], b1=C["eat"]),
    dict(text="pat pat",       b0=C["pat0"],  b1=C["pat1"]),
    dict(text="pat pat pat pat", b0=C["pat1"], b1=C["melt_end"] - 2),
    dict(text="tickle tickle", b0=C["tickle0"], b1=C["tickle1"]),
    dict(text="lift",          b0=C["grab"],  b1=C["drop"]),
    dict(text="fan",           b0=C["fan0"],  b1=C["fan1"]),
    dict(text="blanket",       b0=C["blanket_drag"], b1=C["cozy"] + 2),
    dict(text="hold",          b0=C["hold0"], b1=C["clap"]),
]

# ── 친해짐 게이지(0..10) — 값이 바뀌는 박만. show = 보이기 시작 / hide = 사라짐 ────
GAUGE = dict(show=C["come_out"], hide=C["lamp_off"], steps=[
    (C["come_out"], 2), (C["poke1"], 1.5), (C["poke2"], 1), (C["poke3"], 0), (C["sorry"], 1),
    (C["coffee"], 2), (C["eat"], 3), (C["shy"], 3.5), (C["thanks"], 4),
    (C["pat0"] + 2, 5), (C["melt_max"], 5.5), (C["tickle0"] + 1, 6), (C["land"], 6.5), (C["cheer"], 7),
    (C["fan0"] + 2, 7.5), (C["cozy"] + 3, 8), (C["hug"], 8.5),
    (C["hold0"], 8.5), (C["clap"], 9), (C["breath"], 9.9), (C["slam"], 10),
], ramp=[(C["hold0"], C["clap"], 8.5, 9.0), (C["clap"], C["breath"], 9.0, 9.9)])

# ── 화면 효과 큐(캐릭터에 붙는 이펙트·배경 동심원·빛망울 — 방사형 빛줄기 없음) ───────────
FX = [
    dict(kind="ripple", b=C["knock1"]), dict(kind="ripple", b=C["knock1"] + 0.5),
    dict(kind="ripple", b=C["knock2"]), dict(kind="ripple", b=C["knock2"] + 0.5), dict(kind="ripple", b=C["knock2"] + 1),
    dict(kind="ripple", b=C["tap_edge"]),
    dict(kind="shake", b=C["poke1"], amp=10), dict(kind="shake", b=C["poke2"], amp=12), dict(kind="shake", b=C["poke3"], amp=14),
    dict(kind="dust", b=C["poke2"]), dict(kind="steamhead", b0=C["puff_max"], b1=C["puff_out"]), dict(kind="puffcloud", b=C["puff_out"]),
    dict(kind="drops", b=C["sorry"]),
    dict(kind="steam", b0=C["coffee"], b1=C["soften"]), dict(kind="sparkle", b=C["soften"]), dict(kind="crumbs", b=C["eat"] + 1),
    dict(kind="blush", b=C["shy"]), dict(kind="sparkle", b=C["thanks"]),
    dict(kind="patlines", b0=C["pat0"], b1=C["melt_end"] - 2), dict(kind="floathearts", b0=C["melt_max"], b1=C["melt_end"]),
    dict(kind="giggle", b0=C["tickle0"], b1=C["tickle1"]),
    dict(kind="whoosh", b=C["grab"]), dict(kind="thud", b=C["land"]), dict(kind="shake", b=C["land"], amp=16),
    dict(kind="rings", b0=C["cheer"], b1=C["love"], every=2.0, strength=0.5), dict(kind="hearts", b=C["love"]),
    dict(kind="heat", b0=C["hot"], b1=C["fan0"]), dict(kind="breeze", b0=C["fan0"], b1=C["fan1"]),
    dict(kind="snow", b0=C["cold"], b1=C["cozy"]), dict(kind="warmglow", b0=C["cozy"], b1=C["settle"]),
    dict(kind="rings", b0=C["clap"], b1=B(72), every=2.0, strength=0.5),
    dict(kind="rings", b0=B(72), b1=C["breath"], every=1.0, strength=0.75),
    dict(kind="flash", b=C["slam"]), dict(kind="confetti", b=C["slam"]), dict(kind="shock", b=C["slam"]),
    dict(kind="rings", b0=C["slam"], b1=C["back9"], every=1.0, strength=1.0), dict(kind="bokeh", b0=C["slam"], b1=C["hoof_end"]),
    dict(kind="meetring", b=C["hoof_touch"]), dict(kind="sparkle", b=C["hoof_touch"]),
    dict(kind="stars", b0=C["still"], b1=C["end"]),
    dict(kind="glass", b=C["d_knock"]), dict(kind="glass", b=C["d_knock"] + 0.5),
    dict(kind="glass", b=B(83, 2)), dict(kind="glass", b=B(83, 2.5)), dict(kind="glass", b=B(83, 3)),
    dict(kind="lampglow", b0=C["still"], b1=C["lamp_off"]), dict(kind="zzz", b0=C["sleep"], b1=C["end"]),
]

# 박자 펀치(카메라) — 이 구간에서만 매 박 살짝 들어간다
PUNCH = [(B(36), B(40), 0.008), (B(44), B(47), 0.012), (B(52), B(56), 0.012), (B(74), B(77), 0.022)]
BREATH = (C["breath"], C["slam"])      # 숨 멈춤(무음·정지)

# 물건(소품) — 끌려온 뒤 어디에 얼마나 놓여 있나
PROPS = [
    dict(item="cup", b0=C["cup_drag"], b1=C["coffee"], rest=(FRONT[0] - 10, FRONT[1])),
    dict(item="bun", b0=C["bun_drag"], b1=C["eat"], rest=(FRONT[0] + 10, FRONT[1])),
    dict(item="fan", b0=C["fan_drag"], b1=C["cold"]),
    dict(item="blanket", b0=C["blanket_drag"], b1=C["cozy"]),
    dict(item="blanket", b0=C["hug"], b1=C["hold0"], rest=(470, 915)),          # 포옹할 때 옆에 개어 놓임
    dict(item="lamp_on", b0=C["still"] - 2, b1=C["lamp_off"], rest=LAMP),
    dict(item="lamp_off", b0=C["lamp_off"], b1=C["end"], rest=LAMP),
]


def frame(b):
    return int(round(b * FPB))


def build():
    for s in S:
        assert s["b0"] < s["b1"], s
    for a, b in zip(S, S[1:]):
        assert a["b1"] <= b["b0"], (a["cut"], a["b1"], b["cut"], b["b0"])
    return dict(
        meta=dict(bpm=BPM, fps=FPS, sr=SR, bpb=BPB, bars=BARS, fpb=FPB, spb=SPB, total_beats=TOTAL_BEATS,
                  total_frames=frame(TOTAL_BEATS), total_samples=TOTAL_BEATS * SPB, total_s=TOTAL_BEATS * 60 / BPM,
                  slam_beat=C["slam"], slam_frame=frame(C["slam"]), breath=list(BREATH), stage=list(STAGE),
                  face=list(FACE), head=list(HEAD), cheek=list(CHEEK), chest=list(CHEST), belly=list(BELLY), front=list(FRONT),
                  hoof=list(HOOF), knock_at=list(KNOCK_AT), edge=list(EDGE), safe=list(SAFE), world_dx=WORLD_DX, lamp=list(LAMP), rest=list(REST),
                  word_slot=list(WORD_SLOT), label_slot=list(LABEL_SLOT), gauge_pos=list(GAUGE_POS), breathe=BREATHE),
        acts=ACTS, bg=BG, cues=C, scenes=S, touch=T, d_knocks=D_KNOCKS, words=WORDS, labels=LABELS,
        gauge=dict(show=GAUGE["show"], hide=GAUGE["hide"], steps=[dict(b=b, v=v) for b, v in GAUGE["steps"]],
                   ramp=[dict(b0=a, b1=b, v0=v0, v1=v1) for a, b, v0, v1 in GAUGE["ramp"]]),
        fx=FX, punch=[dict(b0=a, b1=b, k=k) for a, b, k in PUNCH], props=PROPS,
    )


if __name__ == "__main__":
    tl = build()
    s = json.dumps(tl, ensure_ascii=False, indent=1)
    (HERE / "timeline.json").write_text(s, encoding="utf-8")
    (HERE / "timeline.js").write_text("window.TL = " + s + ";\n", encoding="utf-8")
    m = tl["meta"]
    print(f"bpm {m['bpm']} · fps {m['fps']} · {m['bars']}마디 · {m['total_frames']}f · {m['total_s']:.3f}s · slam f{m['slam_frame']} · 씬 {len(S)} · 손짓 {len(T)} · 낱말 {len(WORDS)}+{len(LABELS)}")
    for a in ACTS:
        print(f"  {a['id']} {a['title']:8s} {a['bar0']:2d}–{a['bar1']:2d}마디  {a['bar0'] * 1.6:6.1f}s–{a['bar1'] * 1.6:6.1f}s")
