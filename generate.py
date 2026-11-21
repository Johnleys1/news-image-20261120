#!/usr/bin/env python3
"""Draw THE WORLD — Friday 20 November 2026, one 1024x1024 broadsheet page.
37 verified stories, 7 regions. Deterministic: same bytes every run.
Run: python3 generate.py  ->  writes entry.png next to this file.
"""
import math
import os
from PIL import Image, ImageDraw, ImageFont

W = H = 1024
PAPER = (247, 242, 231)
PAPER2 = (238, 231, 214)
INK = (26, 26, 46)
RED = (185, 28, 28)
NAVY = (30, 58, 95)
GREY = (96, 96, 104)
MIDGREY = (150, 148, 138)
TEAL = (23, 94, 106)
ORANGE = (214, 110, 30)
GOLD = (176, 141, 42)
GREEN = (46, 110, 62)
SKY = (58, 84, 120)

SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SERIF_I = "/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def F(path, size):
    return ImageFont.truetype(path, size)


def wrap(d, text, font, max_w):
    words = text.split()
    lines, cur = [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if d.textlength(t, font=font) <= max_w:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def para(d, x, y, text, font, color, max_w, lh, align="left"):
    """Draw wrapped paragraph; return y after last line."""
    for line in wrap(d, text, font, max_w):
        if align == "center":
            lx = x + (max_w - d.textlength(line, font=font)) / 2
        elif align == "right":
            lx = x + max_w - d.textlength(line, font=font)
        else:
            lx = x
        d.text((lx, y), line, font=font, fill=color)
        y += lh
    return y


def hline(d, x0, x1, y, color=INK, width=1):
    d.line([(x0, y), (x1, y)], fill=color, width=width)


def vline(d, x, y0, y1, color=INK, width=1):
    d.line([(x, y0), (x, y1)], fill=color, width=width)


def tag(d, x, y, label, color):
    """Certainty tag: small filled chip with white bold text."""
    f = F(SANS_B, 8)
    tw = d.textlength(label, font=f)
    d.rectangle([x, y, x + tw + 8, y + 12], fill=color)
    d.text((x + 4, y + 2), label, font=f, fill=(255, 255, 255))
    return tw + 8


def starburst(d, cx, cy, r1, r2, color, n=12):
    pts = []
    for i in range(n * 2):
        r = r1 if i % 2 == 0 else r2
        a = math.pi * i / n
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    d.polygon(pts, fill=color)


# ---------------------------------------------------------------- data
STATS = [
    ("400+", "drones fired\nat Ukraine"),
    ("110+", "missiles fired,\n27 ballistic"),
    ("300,000+", "evacuated\nin Odisha"),
    ("-8%", "MSCI Asia-Pacific\nworst week since 2020"),
    ("3", "Kyiv bridges\nhit overnight"),
    ("£5.1bn", "UK-EU reset deal\nbenefit by 2028"),
    ("70-80", "km/h at landfall,\ngusting to 90"),
]

REGIONS = "EUROPE 6   ·   ASIA 7   ·   MIDDLE EAST 7   ·   AFRICA 3   ·   AMERICAS 9   ·   OCEANIA 1   ·   GLOBAL 4"

HEROES = [
    dict(n=1, kicker="UKRAINE — KYIV", art="kyiv",
         head="Kyiv's bridges hit in Russia's biggest barrage of the war",
         deck="Ballistic missiles strike three Dnipro bridges; 3 killed in Kyiv, 9 across Ukraine; "
              "400+ drones fired.",
         src="Reuters · AP", tag="REPORTED", tagc=GREEN),
    dict(n=2, kicker="INDIA — ODISHA", art="akvan",
         head="Cyclone Akvan makes landfall; 300,000 moved to safety",
         deck="The storm crosses near Gopalpur at 70-80 km/h. No deaths reported; "
              "heavy rain floods Bengal.",
         src="India Meteorological Dept.", tag="REPORTED", tagc=GREEN),
    dict(n=3, kicker="MARKETS — ASIA", art="market",
         head="Asia's AI sell-off deepens; worst week since 2020",
         deck="Nikkei -4.8%, KOSPI -5.2%, TAIEX -6.6% as AI doubts swamp Nvidia's "
              "$115.8bn quarter.",
         src="Reuters · FXStreet", tag="REPORTED", tagc=GREEN),
]

GRID = [
    dict(n=4, kicker="BRUSSELS", art="table",
         head="UK-EU reset deal agreed; tuition row unresolved",
         deck="Burnham, von der Leyen, Costa seal food, youth and carbon deals; the fees row is unresolved.",
         src="Reuters", tag="REPORTED", tagc=GREEN),
    dict(n=5, kicker="ANTALYA — COP31", art="climate",
         head="Climate talks deadlocked; summit into overtime",
         deck="Final day fails on fossil-fuel phase-out, clean power by 2035 and finance. Talks run into the weekend.",
         src="Euronews", tag="REPORTED", tagc=GREEN),
    dict(n=6, kicker="POLAND", art="missile",
         head="Russian missiles crash in Poland during barrage",
         deck="A Kh-101 missile and a drone fall in south-east Poland, reports say; Warsaw calls it a provocation.",
         src="Fox News · Euronews", tag="CLAIM", tagc=ORANGE),
    dict(n=7, kicker="GAZA", art="fence",
         head="Israeli troops cross the Yellow Line in Gaza",
         deck="First ground operation beyond the ceasefire line since the truce, the army says, to dismantle a tunnel.",
         src="One Turn", tag="REPORTED", tagc=GREEN),
    dict(n=8, kicker="RIYADH", art="tower",
         head="Houthi missile damages Riyadh wealth-fund tower",
         deck="Reports say a missile hit the PIF tower in the financial district; no casualty toll given.",
         src="One Turn", tag="CLAIM", tagc=ORANGE),
    dict(n=9, kicker="SUDAN", art="gold",
         head="Drone strike kills 10 at Sudan gold mine",
         deck="At least 10 die at the Bajoun mining site as Sudan's war grinds on into its fourth year.",
         src="One Turn", tag="REPORTED", tagc=GREEN),
    dict(n=10, kicker="HAITI", art="shield",
         head="Haiti forces kill 34 gang suspects in raid",
         deck="Forces storm Martissant in Port-au-Prince in the latest push against gangs holding much of the capital.",
         src="One Turn", tag="REPORTED", tagc=GREEN),
    dict(n=11, kicker="SENEGAL", art="boat",
         head="Migrant boat capsizes off Yenne; dozens missing",
         deck="Reports say a boat carrying migrants went down off the coast near Dakar; a search is under way.",
         src="One Turn", tag="CLAIM", tagc=ORANGE),
    dict(n=12, kicker="EL SALVADOR", art="ballot",
         head="Bukele registers for a third term",
         deck="Nayib Bukele files to run again, testing term limits in a country where he remains widely popular.",
         src="One Turn", tag="REPORTED", tagc=GREEN),
    dict(n=13, kicker="VENEZUELA", art="handshake",
         head="US and Venezuela sign military deal",
         deck="Caracas and Washington agree a military cooperation pact, a sharp turn after years of open hostility.",
         src="One Turn", tag="REPORTED", tagc=GREEN),
]

BRIEFS = [
    (14, "BERLIN", "Ukraine's allies meet, say Europe is ready to talk with Russia.", "One Turn"),
    (15, "HORMUZ", "Iran war enters its ninth month; tanker attacks intensify.", "One Turn"),
    (16, "DHAKA", "Violence ahead of Hasina's planned return.", "One Turn"),
    (17, "JURF AL-NASR", "Iraq orders Iran-backed militia out.", "One Turn"),
    (18, "NORTHERN ISRAEL", "Mosque set on fire.", "One Turn"),
    (19, "HAITI", "Two Salvadoran soldiers killed handling explosives.", "Media Alert Press"),
    (20, "BELGRADE", "Mayor charged with assaulting opposition politician.", "Media Alert Press"),
    (21, "WASHINGTON", "Indian man sentenced to 19 years in US Sikh separatist plot.", "Media Alert Press"),
    (22, "KATHMANDU", "Nepal cricket fans celebrate their team's global rise.", "Media Alert Press"),
    (23, "GAZA", "Displaced children mark World Children's Day.", "Media Alert Press"),
    (24, "SUDAN", "War leaves disabled children out of education.", "Media Alert Press"),
    (25, "WASHINGTON", "Trump defends Putin ties; warns AI data centres must stay in US.", "Media Alert Press"),
    (26, "GAZA", "Palestinian anti-Hamas groups accused of role in Gaza operation.", "Media Alert Press"),
    (27, "HOUSTON", "NASA: Artemis III stays in orbit; first landing moves to Artemis IV.", "Tickline"),
    (28, "SPACE", "Google's Project Suncatcher books New Glenn for a 2029 test flight.", "Tickline"),
    (29, "NEW YORK", "SpaceX shares slide below IPO price, down 5% to $131.16.", "Tickline"),
    (30, "SCIENCE", "Space radiation changes brain immune cells, not behaviour — mouse study.", "Phys.org"),
    (31, "NEW YORK", "Anthropic shares slide below $90 after record IPO debut fades.", "CNBC TV18"),
    (32, "SANTA CLARA", "Nvidia's $115.8bn quarter fails to stop the AI sell-off.", "Coinpaper"),
    (33, "SEOUL", "KOSPI sidecars halt trading twice, first dual halt since 6 Nov.", "Aju Press"),
    (34, "TAIPEI", "TAIEX worst week since 1991, down about 17%.", "Aju Press"),
    (35, "ODISHA", "47 trains cancelled, 28 rescheduled as Akvan hits.", "The Watchers"),
    (36, "KYIV", "Three nuclear plants cut power; emergency outages in 11 regions.", "NY Post"),
    (37, "SHENZHEN", "Xi tells Albanese China-Australia ties have turned around, on APEC sidelines.", "Xinhua via EIN"),
]

HOURS = [
    ("02:00", "Akvan crosses the coast near Gopalpur"),
    ("03:00", "Russian missiles strike Kyiv's three bridges"),
    ("05:06", "Asian markets open to the AI sell-off"),
    ("11:54", "KOSPI sidecar halt as Seoul plunges 5.2%"),
    ("13:40", "Burnham calls the reset deal 'probably the limit'"),
    ("16:30", "COP31 talks pushed into weekend overtime"),
    ("18:00", "Akvan's remnant fades to a low over Odisha"),
]

DATECHECK = [
    "ICJ rules Myanmar committed genocide (Thu 19 Nov)",
    "Trump, Xi & Putin three-way Shenzhen summit (Thu 19 Nov)",
    "Anthropic's $83 IPO pricing; debut closed $97.17 (Thu 19 Nov)",
    "Voyager 1 reaches one light-day from Earth (Thu 19 Nov)",
    "Suneung: 551,864 sit Korea's college exam (Thu 19 Nov)",
    "Australia beats NZ 32-12, Rugby League World Cup final (Sun 15 Nov)",
    "Vulcan Centaur fails; 40 Amazon Leo satellites lost (Sun 15 Nov)",
]


# ---------------------------------------------------------------- art
def art_kyiv(d, x, y, w, h):
    """Night sky over the Dnipro: bridges, missile bursts, smoke."""
    d.rectangle([x, y, x + w, y + h], fill=(28, 38, 66))
    d.rectangle([x, y, x + w, y + 14], fill=(44, 56, 92))
    # skyline silhouettes
    for bx, bw, bh in [(6, 26, 26), (38, 18, 34), (60, 30, 20), (96, 16, 30),
                       (118, 24, 24), (150, 20, 36), (176, 26, 22), (206, 18, 30),
                       (232, 28, 26), (264, 20, 32)]:
        d.rectangle([x + bx, y + h - 26 - bh, x + bx + bw, y + h - 26], fill=(16, 22, 40))
        for wy in range(y + h - 26 - bh + 5, y + h - 30, 8):
            d.rectangle([x + bx + 4, wy, x + bx + 8, wy + 3], fill=(232, 190, 90))
    # river band
    d.polygon([(x, y + h - 26), (x + w, y + h - 34), (x + w, y + h), (x, y + h)],
              fill=(58, 84, 120))
    d.line([(x, y + h - 20), (x + w, y + h - 28)], fill=(120, 150, 180), width=2)
    # three bridges: arched spans across the river
    for bx in (30, 125, 220):
        d.arc([x + bx, y + h - 52, x + bx + 62, y + h - 8], 180, 360, fill=(220, 220, 210), width=3)
        d.line([(x + bx, y + h - 30), (x + bx + 62, y + h - 30)], fill=(220, 220, 210), width=2)
        for px in range(bx + 6, bx + 58, 12):
            d.line([(x + px, y + h - 30), (x + px, y + h - 44)], fill=(220, 220, 210), width=1)
    # missile bursts over bridges 1 and 3
    starburst(d, x + 52, y + 34, 16, 7, ORANGE)
    starburst(d, x + 52, y + 34, 9, 4, (255, 220, 120))
    starburst(d, x + 252, y + 30, 13, 6, ORANGE)
    starburst(d, x + 252, y + 30, 7, 3, (255, 220, 120))
    # smoke plumes
    for sx, sy, sr in [(44, 52, 9), (56, 60, 12), (244, 48, 8), (256, 56, 11)]:
        d.ellipse([x + sx - sr, y + sy - sr, x + sx + sr, y + sy + sr], fill=(110, 110, 118))
    # falling missile trails
    d.line([(x + 130, y + 6), (x + 150, y + 40)], fill=(255, 200, 120), width=2)
    d.line([(x + 200, y + 2), (x + 214, y + 30)], fill=(255, 200, 120), width=2)


def art_akvan(d, x, y, w, h):
    """Cyclone spiral over the Bay of Bengal coast."""
    d.rectangle([x, y, x + w, y + h], fill=(18, 68, 92))
    # spiral arms
    for k in range(5):
        r0 = 6 + k * 9
        pts = []
        for a in range(0, 300, 12):
            rad = math.radians(a + k * 72)
            r = r0 + a * 0.16
            pts.append((x + w * 0.42 + r * math.cos(rad), y + h * 0.46 + r * math.sin(rad) * 0.8))
        d.line(pts, fill=(230, 240, 245), width=3)
    d.ellipse([x + w * 0.42 - 10, y + h * 0.46 - 8, x + w * 0.42 + 10, y + h * 0.46 + 8],
              fill=(247, 242, 231))
    # rain streaks
    for i in range(26):
        rx = x + (i * 37) % w
        ry = y + (i * 53) % h
        d.line([(rx, ry), (rx - 5, ry + 12)], fill=(180, 210, 225), width=1)
    # coastline + waves at the bottom
    d.polygon([(x, y + h - 18), (x + w, y + h - 26), (x + w, y + h), (x, y + h)], fill=(214, 186, 130))
    for wx in range(0, w, 26):
        d.arc([x + wx, y + h - 16, x + wx + 24, y + h - 2], 180, 360, fill=(255, 255, 255), width=2)
    # bent palm
    d.line([(x + w - 34, y + h - 18), (x + w - 22, y + h - 46)], fill=(90, 60, 30), width=3)
    for a in range(-50, 60, 25):
        rad = math.radians(a)
        d.line([(x + w - 22, y + h - 46),
                (x + w - 22 + 16 * math.cos(rad), y + h - 46 + 8 * math.sin(rad))],
               fill=(46, 110, 62), width=2)


def art_market(d, x, y, w, h):
    """Falling market: red candles and a plunging line."""
    d.rectangle([x, y, x + w, y + h], fill=(24, 28, 48))
    # grid
    for gy in range(y + 10, y + h - 6, 14):
        d.line([(x + 6, gy), (x + w - 6, gy)], fill=(44, 50, 74), width=1)
    # candlesticks, descending
    tops = [18, 24, 22, 32, 30, 42, 40, 52, 50, 62]
    for i, t in enumerate(tops):
        cx = x + 14 + i * 28
        col = RED if i % 2 == 0 else (200, 60, 50)
        d.rectangle([cx, y + t, cx + 12, y + t + 16], fill=col)
        d.line([(cx + 6, y + t - 5), (cx + 6, y + t + 21)], fill=col, width=1)
    # plunging line
    pts = [(x + 8, y + 16), (x + 60, y + 26), (x + 110, y + 24), (x + 160, y + 40),
           (x + 210, y + 48), (x + 260, y + 62), (x + w - 8, y + h - 12)]
    d.line(pts, fill=(255, 90, 70), width=3)
    # down arrow
    d.polygon([(x + w - 30, y + h - 26), (x + w - 14, y + h - 26), (x + w - 22, y + h - 8)],
              fill=(255, 90, 70))
    d.text((x + 10, y + h - 22), "NIKKEI -4.8%  ·  KOSPI -5.2%",
           font=F(SANS_B, 10), fill=(255, 220, 120))


def art_strip(d, x, y, w, h, kind):
    """Small illustration strip for grid cards 4-13."""
    bg = {"table": (58, 84, 120), "climate": (23, 94, 106), "missile": (90, 40, 44),
          "fence": (120, 100, 60), "tower": (52, 52, 78), "gold": (140, 110, 40),
          "shield": (46, 90, 70), "boat": (23, 94, 106), "ballot": (90, 60, 110),
          "handshake": (140, 70, 40)}[kind]
    d.rectangle([x, y, x + w, y + h], fill=bg)
    if kind == "table":
        d.rectangle([x + 30, y + h - 12, x + w - 30, y + h - 8], fill=(220, 210, 190))
        d.rectangle([x + 30, y + h - 8, x + w - 30, y + h], fill=(90, 60, 40))
        d.rectangle([x + 44, y + 6, x + 74, y + 22], fill=(30, 58, 95))
        d.rectangle([x + 74, y + 6, x + 104, y + 22], fill=(200, 200, 200))
        d.rectangle([x + 104, y + 6, x + 134, y + 22], fill=(185, 28, 28))
        d.ellipse([x + 84, y + h - 20, x + 96, y + h - 10], fill=(240, 220, 160))
    elif kind == "climate":
        d.ellipse([x + w // 2 - 14, y + 4, x + w // 2 + 14, y + h - 4], fill=(90, 160, 120))
        d.arc([x + w // 2 - 14, y + 4, x + w // 2 + 14, y + h - 4], 200, 340, fill=(240, 240, 220), width=2)
        starburst(d, x + 18, y + 10, 8, 3, (255, 220, 120), n=8)
        d.line([(x + w - 40, y + h - 6), (x + w - 10, y + h - 6)], fill=(255, 255, 255), width=2)
    elif kind == "missile":
        d.line([(x + 8, y + h - 8), (x + w - 60, y + 10)], fill=(255, 200, 120), width=2)
        starburst(d, x + w - 44, y + 12, 10, 4, ORANGE)
        d.ellipse([x + w - 52, y + 4, x + w - 36, y + 20], fill=(255, 220, 120))
        d.rectangle([x + 10, y + h - 12, x + w - 10, y + h - 6], fill=(40, 40, 56))
    elif kind == "fence":
        d.line([(x + 6, y + h - 8), (x + w - 6, y + h - 8)], fill=(230, 220, 190), width=2)
        for px in range(14, w - 8, 22):
            d.line([(x + px, y + 8), (x + px, y + h - 8)], fill=(230, 220, 190), width=2)
        d.line([(x + 6, y + 12), (x + w - 6, y + 12)], fill=(230, 220, 190), width=1)
        d.rectangle([x + w - 60, y + 4, x + w - 30, y + h - 10], fill=(185, 28, 28))
    elif kind == "tower":
        d.rectangle([x + w // 2 - 10, y + 6, x + w // 2 + 10, y + h - 4], fill=(200, 200, 210))
        d.line([(x + w // 2, y + 2), (x + w // 2, y + 6)], fill=(255, 220, 120), width=2)
        for wy in range(y + 10, y + h - 6, 7):
            d.rectangle([x + w // 2 - 7, wy, x + w // 2 + 7, wy + 3], fill=(255, 220, 120))
        d.rectangle([x + 12, y + h - 10, x + 44, y + h - 4], fill=(140, 140, 150))
        d.rectangle([x + w - 44, y + h - 14, x + w - 12, y + h - 4], fill=(140, 140, 150))
    elif kind == "gold":
        d.polygon([(x + 20, y + 8), (x + 60, y + 8), (x + 44, y + h - 8), (x + 28, y + h - 8)],
                  fill=(90, 70, 40))
        d.line([(x + 30, y + 6), (x + 70, y + h - 6)], fill=(220, 200, 160), width=2)
        starburst(d, x + w - 40, y + h - 12, 7, 3, (255, 220, 120), n=6)
        starburst(d, x + w - 70, y + 12, 5, 2, (255, 220, 120), n=6)
    elif kind == "shield":
        d.polygon([(x + w // 2 - 16, y + 4), (x + w // 2 + 16, y + 4), (x + w // 2 + 16, y + 16),
                   (x + w // 2, y + h - 4), (x + w // 2 - 16, y + 16)], fill=(240, 240, 230))
        d.line([(x + w // 2 - 8, y + 16), (x + w // 2 - 2, y + 24), (x + w // 2 + 10, y + 10)],
               fill=GREEN, width=3)
    elif kind == "boat":
        d.polygon([(x + 30, y + h - 12), (x + w - 30, y + h - 12), (x + w - 44, y + h - 4),
                   (x + 44, y + h - 4)], fill=(140, 70, 40))
        d.line([(x + w // 2, y + h - 12), (x + w // 2, y + 6)], fill=(230, 220, 190), width=2)
        d.polygon([(x + w // 2, y + 6), (x + w // 2 + 22, y + h - 14), (x + w // 2, y + h - 14)],
                  fill=(240, 240, 230))
        for wx in range(0, w, 24):
            d.arc([x + wx, y + h - 6, x + wx + 22, y + h + 4], 180, 360, fill=(255, 255, 255), width=2)
    elif kind == "ballot":
        d.rectangle([x + w // 2 - 18, y + 8, x + w // 2 + 18, y + h - 6], fill=(240, 240, 230))
        d.rectangle([x + w // 2 - 18, y + 8, x + w // 2 + 18, y + 14], fill=RED)
        d.line([(x + w // 2 - 10, y + 22), (x + w // 2 - 2, y + 28), (x + w // 2 + 12, y + 14)],
               fill=GREEN, width=3)
    elif kind == "handshake":
        d.rectangle([x + 16, y + 6, x + w // 2, y + h - 6], fill=(30, 58, 95))
        d.rectangle([x + w // 2, y + 6, x + w - 16, y + h - 6], fill=(200, 60, 50))
        d.ellipse([x + w // 2 - 14, y + h // 2 - 8, x + w // 2 + 14, y + h // 2 + 8],
                  fill=(240, 220, 180))
        d.arc([x + w // 2 - 14, y + h // 2 - 8, x + w // 2 + 14, y + h // 2 + 8], 0, 360,
              fill=(120, 80, 40), width=2)


# ---------------------------------------------------------------- map
# Rough equirectangular continent outlines (lon, lat).
CONTINENTS = [
    [(-168, 66), (-150, 70), (-140, 70), (-128, 71), (-115, 73), (-100, 73), (-90, 74),
     (-85, 70), (-80, 73), (-76, 62), (-70, 58), (-65, 60), (-60, 55), (-65, 50),
     (-70, 44), (-75, 38), (-76, 34), (-80, 32), (-81, 26), (-84, 30), (-89, 29),
     (-90, 21), (-94, 18), (-97, 16), (-92, 14), (-87, 13), (-83, 9), (-79, 9),
     (-83, 15), (-88, 16), (-92, 15), (-97, 16), (-105, 20), (-110, 23), (-114, 28),
     (-117, 33), (-122, 37), (-124, 42), (-124, 48), (-130, 55), (-140, 60), (-150, 59),
     (-158, 58), (-165, 60), (-168, 66)],
    [(-55, 60), (-45, 60), (-40, 64), (-32, 68), (-22, 70), (-25, 74), (-32, 76),
     (-45, 76), (-55, 74), (-58, 70), (-55, 64)],
    [(-80, 10), (-77, 7), (-80, 3), (-81, -3), (-80, -10), (-77, -15), (-70, -18),
     (-70, -25), (-68, -32), (-70, -40), (-70, -48), (-68, -54), (-66, -55), (-65, -50),
     (-62, -42), (-58, -35), (-52, -33), (-48, -28), (-41, -23), (-39, -15), (-35, -8),
     (-38, -5), (-44, -3), (-50, 0), (-52, 4), (-58, 6), (-62, 9), (-68, 11),
     (-72, 12), (-77, 8), (-80, 10)],
    [(-10, 35), (-6, 36), (-2, 36), (3, 37), (10, 37), (15, 38), (20, 32), (25, 32),
     (30, 31), (33, 27), (37, 22), (39, 18), (43, 12), (46, 11), (51, 11), (48, 6),
     (44, 2), (41, -2), (40, -8), (39, -15), (36, -20), (33, -26), (28, -33), (20, -35),
     (17, -32), (15, -27), (12, -18), (13, -12), (12, -6), (9, -1), (9, 4), (4, 6),
     (-2, 5), (-8, 5), (-13, 8), (-16, 12), (-17, 15), (-16, 21), (-15, 27), (-10, 31)],
    [(-10, 36), (-5, 36), (-2, 37), (0, 39), (3, 42), (7, 44), (10, 44), (13, 45),
     (16, 44), (19, 42), (22, 40), (23, 37), (26, 36), (28, 38), (30, 36), (28, 41),
     (26, 40), (23, 40), (19, 42), (15, 44), (12, 46), (8, 48), (4, 49), (0, 49),
     (-2, 48), (-4, 48), (-2, 46), (-5, 44), (-8, 43), (-10, 39), (-10, 36)],
    [(30, 36), (35, 36), (40, 37), (44, 39), (48, 38), (50, 41), (54, 44), (58, 45),
     (62, 45), (66, 44), (70, 46), (74, 50), (78, 55), (82, 60), (86, 64), (90, 66),
     (95, 68), (100, 70), (105, 72), (110, 73), (115, 73), (120, 72), (125, 71),
     (130, 70), (135, 71), (140, 72), (145, 72), (150, 70), (155, 68), (160, 66),
     (165, 64), (170, 66), (173, 64), (170, 62), (162, 60), (158, 56), (155, 52),
     (150, 48), (145, 44), (142, 40), (140, 38), (136, 35), (132, 33), (129, 33),
     (127, 35), (124, 31), (122, 30), (120, 27), (116, 23), (112, 21), (109, 18),
     (108, 13), (105, 9), (103, 7), (100, 6), (98, 10), (97, 15), (94, 17), (92, 21),
     (89, 22), (87, 21), (84, 19), (82, 17), (80, 15), (77, 8), (76, 10), (73, 16),
     (72, 20), (68, 23), (65, 25), (61, 25), (58, 26), (56, 27), (54, 27), (52, 28),
     (50, 29), (48, 30), (45, 29), (43, 29), (40, 31), (38, 34), (36, 36), (33, 36),
     (30, 36)],
    [(129, 32), (130, 34), (132, 34), (134, 35), (136, 35), (138, 36), (140, 38),
     (141, 40), (141, 42), (140, 44), (138, 42), (136, 40), (134, 38), (132, 36),
     (130, 33)],
    [(113, -22), (114, -28), (115, -32), (116, -35), (120, -34), (124, -33), (129, -32),
     (132, -32), (135, -35), (138, -35), (140, -38), (144, -38), (147, -39), (150, -37),
     (153, -32), (153, -27), (151, -24), (149, -20), (146, -19), (143, -15), (142, -11),
     (139, -14), (136, -12), (135, -15), (132, -12), (130, -13), (127, -14), (124, -15),
     (121, -17), (118, -20), (114, -22), (113, -22)],
    [(167, -45), (169, -43), (172, -41), (174, -40), (177, -38), (178, -37), (176, -38),
     (174, -40), (171, -42), (168, -44), (167, -45)],
    [(-5, 48), (-3, 50), (-1, 51), (1, 51), (1, 50), (-3, 49), (-5, 48)],
]

# (lon, lat) of numbered stories 1-13 and grey brief dots.
RED_DOTS = [(30.5, 50.4), (84.9, 19.3), (139.7, 35.7), (4.35, 50.85), (30.7, 36.9),
            (22.5, 50.5), (34.5, 31.5), (46.7, 24.6), (30.0, 11.0), (-72.3, 18.5),
            (-17.2, 14.7), (-89.2, 13.7), (-66.9, 10.5)]
GREY_DOTS = [(13.4, 52.5), (56.5, 26.5), (90.4, 23.8), (44.3, 32.8), (35.3, 32.9),
             (20.5, 44.8), (-77.0, 38.9), (85.3, 27.7), (32.5, 15.5), (-95.4, 29.8),
             (-74.0, 40.7), (127.0, 37.5), (121.5, 25.0), (114.0, 22.5)]


def draw_map(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(214, 226, 236))
    d.rectangle([x, y, x + w, y + h], outline=INK, width=1)

    def px(lon, lat):
        return x + (lon + 170) / 360.0 * w, y + (75 - lat) / 130.0 * h

    for poly in CONTINENTS:
        pts = [px(lon, lat) for lon, lat in poly]
        d.polygon(pts, fill=(232, 226, 210), outline=(120, 120, 110))
    # graticule
    for lon in range(-150, 181, 30):
        gx, _ = px(lon, 0)
        d.line([(gx, y), (gx, y + h)], fill=(190, 205, 220), width=1)
    for n, (lon, lat) in enumerate(RED_DOTS, start=1):
        cx, cy = px(lon, lat)
        d.ellipse([cx - 7, cy - 7, cx + 7, cy + 7], fill=RED, outline=(255, 255, 255), width=1)
        d.text((cx - 2.5 if n < 10 else cx - 5, cy - 5), str(n), font=F(SANS_B, 8),
               fill=(255, 255, 255))
    for lon, lat in GREY_DOTS:
        cx, cy = px(lon, lat)
        d.ellipse([cx - 2.5, cy - 2.5, cx + 2.5, cy + 2.5], fill=GREY)


# ---------------------------------------------------------------- page
def draw_page():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    MX = 26
    CW = W - 2 * MX

    # ---- masthead
    f_kick = F(SANS_B, 11)
    d.text((MX, 16), "THE WORLD IN ONE DAY", font=f_kick, fill=INK)
    right = "37 STORIES  ·  7 REGIONS  ·  ALL FROM THIS ONE DAY"
    d.text((W - MX - d.textlength(right, font=f_kick), 16), right, font=f_kick, fill=INK)
    hline(d, MX, W - MX, 34, INK, 2)
    title = "THE WORLD"
    f_title = F(SERIF_B, 66)
    d.text(((W - d.textlength(title, font=f_title)) / 2, 38), title, font=f_title, fill=INK)
    hline(d, MX, W - MX, 112, INK, 1)
    date_line = "Friday 20 November 2026"
    f_date = F(SERIF_I, 17)
    d.text(((W - d.textlength(date_line, font=f_date)) / 2, 118), date_line, font=f_date, fill=INK)
    deck = "Kyiv's bridges hit  ·  Cyclone Akvan lands  ·  Asia's AI sell-off deepens"
    f_deck = F(SERIF_I, 16)
    d.text(((W - d.textlength(deck, font=f_deck)) / 2, 140), deck, font=f_deck, fill=RED)
    hline(d, MX, W - MX, 164, INK, 2)

    # ---- big-number stat strip
    y0 = 172
    col_w = CW / 7
    for i, (num, lab) in enumerate(STATS):
        cx = MX + i * col_w
        f_num = F(SERIF_B, 21)
        d.text((cx + (col_w - d.textlength(num, font=f_num)) / 2, y0), num, font=f_num,
               fill=RED if i % 2 == 0 else NAVY)
        f_lab = F(SANS, 9)
        yy = y0 + 26
        for ln in lab.split("\n"):
            d.text((cx + (col_w - d.textlength(ln, font=f_lab)) / 2, yy), ln, font=f_lab,
                   fill=INK)
            yy += 11
        if i:
            vline(d, cx, y0 + 2, y0 + 46, MIDGREY, 1)
    hline(d, MX, W - MX, 222, INK, 1)

    # ---- region strip
    f_reg = F(SANS_B, 11)
    d.text(((W - d.textlength(REGIONS, font=f_reg)) / 2, 228), REGIONS, font=f_reg, fill=NAVY)
    hline(d, MX, W - MX, 246, INK, 2)

    # ---- heroes
    hy, hh = 254, 148
    hw = int((CW - 24) / 3)
    arts = {"kyiv": art_kyiv, "akvan": art_akvan, "market": art_market}
    for i, s in enumerate(HEROES):
        x = MX + i * (hw + 12)
        d.rectangle([x, hy, x + hw, hy + hh], outline=INK, width=1)
        arts[s["art"]](d, x + 1, hy + 1, hw - 2, 64)
        tx = x + 8
        ty = hy + 68
        d.text((tx, ty), f"{s['n']}  ·  {s['kicker']}", font=F(SANS_B, 9), fill=RED)
        ty += 13
        ty = para(d, tx, ty, s["head"], F(SERIF_B, 13), INK, hw - 16, 14)
        ty = para(d, tx, ty + 2, s["deck"], F(SERIF, 10), INK, hw - 16, 11)
        d.text((tx, hy + hh - 16), s["src"], font=F(SANS, 8), fill=GREY)
        tag(d, x + hw - 62, hy + hh - 17, s["tag"], s["tagc"])

    # ---- grid 4-13
    gy, gh = 410, 106
    gw = int((CW - 40) / 5)
    for i, s in enumerate(GRID):
        row, col = divmod(i, 5)
        x = MX + col * (gw + 10)
        y = gy + row * (gh + 8)
        d.rectangle([x, y, x + gw, y + gh], outline=INK, width=1)
        art_strip(d, x + 1, y + 1, gw - 2, 32, s["art"])
        tx = x + 7
        ty = y + 37
        d.text((tx, ty), f"{s['n']}  ·  {s['kicker']}", font=F(SANS_B, 8), fill=RED)
        ty += 11
        ty = para(d, tx, ty, s["head"], F(SERIF_B, 11), INK, gw - 14, 12)
        ty = para(d, tx, ty + 1, s["deck"], F(SERIF, 8), INK, gw - 14, 10)
        d.text((tx, y + gh - 13), s["src"], font=F(SANS, 7), fill=GREY)
        tag(d, x + gw - 54, y + gh - 14, s["tag"], s["tagc"])
    return img, d


def finish_page(img, d):
    MX = 26
    CW = W - 2 * MX

    # ---- map + hours
    my = 630
    d.text((MX, my), "WHERE IT HAPPENED", font=F(SANS_B, 12), fill=INK)
    map_x, map_y, map_w, map_h = MX, my + 20, 600, 100
    draw_map(d, map_x, map_y, map_w, map_h)
    d.text((map_x, map_y + map_h + 4),
           "Red numbers mark stories 1–13; grey dots mark the briefs. Positions approximate.",
           font=F(SANS, 9), fill=GREY)
    # hours column
    hx = MX + 612
    d.text((hx, my), "THE DAY BY HOURS  (UTC)", font=F(SANS_B, 12), fill=INK)
    hyy = my + 20
    for t, ev in HOURS:
        d.text((hx, hyy), t, font=F(SANS_B, 10), fill=RED)
        d.text((hx + 44, hyy), ev, font=F(SANS, 10), fill=INK)
        hyy += 15
    hline(d, MX, W - MX, my + 132, INK, 1)

    # ---- briefs 14-37
    by = my + 140
    d.text((MX, by), "ALSO ON FRIDAY 20 NOVEMBER", font=F(SANS_B, 12), fill=INK)
    d.text((W - MX - d.textlength("One line each — place, headline, source.", font=F(SANS, 9)), by + 2),
           "One line each — place, headline, source.", font=F(SANS, 9), fill=GREY)
    col_w = (CW - 20) / 2
    f_b = F(SERIF, 10)
    f_bb = F(SANS_B, 9)
    left = BRIEFS[:12]
    right = BRIEFS[12:]
    yy = by + 20
    for col, items in ((MX, left), (MX + col_w + 20, right)):
        y = yy
        for n, place, head, src in items:
            pre = f"{n}. {place} — "
            tw = d.textlength(pre, font=f_bb)
            d.text((col, y), pre, font=f_bb, fill=INK)
            rest = head + " " + src + "."
            # shrink to fit one line
            size = 10
            f = F(SERIF, size)
            while d.textlength(rest, font=f) > col_w - tw and size > 8:
                size -= 1
                f = F(SERIF, size)
            d.text((col + tw, y), rest, font=f, fill=INK)
            y += 11
    hline(d, MX, W - MX, by + 20 + 12 * 11 + 4, INK, 1)

    # ---- date check + certainty legend
    dy = by + 20 + 12 * 11 + 12
    box_w = 620
    d.rectangle([MX, dy, MX + box_w, dy + 58], outline=RED, width=2)
    d.text((MX + 8, dy + 5), "DATE CHECK  ✓ — these are NOT 20 November news", font=F(SANS_B, 11),
           fill=RED)
    f_dc = F(SERIF, 9)
    lines = [
        "ICJ rules Myanmar committed genocide  ·  Trump, Xi & Putin Shenzhen summit  ·  Anthropic $83 IPO (all Thu 19 Nov)",
        "Voyager 1 reaches one light-day  ·  Suneung: 551,864 sit Korea's exam (Thu 19 Nov)",
        "Australia beats NZ 32-12, Rugby League World Cup final  ·  Vulcan Centaur fails (Sun 15 Nov)",
    ]
    yy = dy + 22
    for ln in lines:
        d.text((MX + 8, yy), ln, font=f_dc, fill=INK)
        yy += 11
    lx = MX + box_w + 14
    d.text((lx, dy + 2), "HOW SURE ARE WE?", font=F(SANS_B, 11), fill=INK)
    yy = dy + 20
    for lab, col in (("REPORTED", GREEN), ("CLAIM", ORANGE), ("FORECAST", NAVY)):
        tw = tag(d, lx, yy, lab, col)
        desc = {"REPORTED": "confirmed by officials / agencies",
                "CLAIM": "attributed, not independently verified",
                "FORECAST": "expected, not yet happened"}[lab]
        d.text((lx + tw + 6, yy + 1), desc, font=F(SANS, 9), fill=INK)
        yy += 14

    # ---- footer
    fy = dy + 66
    hline(d, MX, W - MX, fy, INK, 2)
    foot = ("Every story here happened, or was first reported, on Friday 20 November 2026; disputed "
            "claims are attributed. Sources: Reuters · AP · IMD · Euronews · One Turn · FXStreet · "
            "Aju Press · Xinhua · Tickline. Original drawings.")
    para(d, MX, fy + 6, foot, F(SERIF_I, 9), INK, CW, 11, align="center")


def main():
    img, d = draw_page()
    finish_page(img, d)
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")
    img.save(out, "PNG", optimize=True)
    print("wrote", out, os.path.getsize(out), "bytes", img.size)


if __name__ == "__main__":
    main()
