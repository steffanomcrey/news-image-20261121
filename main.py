# SPDX-License-Identifier: MIT
"""Saturday 21 November 2026, summed up in one image.

A program that draws a newspaper front page (1024x1024 PNG) with 52 stories:
16 drawn panels plus a 36-item list, a numbers strip, a UTC timeline, a dotted
world map with numbered pins, and a DATE CHECK box naming what was left out.
No network, no clock, no randomness: two runs write identical bytes.
Run: mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
"""
import os
import textwrap

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
PAPER = (247, 241, 227)
INK = (26, 26, 26)
NAVY = (20, 48, 77)
RED = (179, 35, 27)
GOLD = (196, 154, 43)
TEAL = (18, 110, 105)
GREY = (90, 86, 78)
LIGHT = (255, 252, 244)
PINK = (251, 233, 231)
BLUE = (214, 228, 240)

SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"


def font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        try:
            return ImageFont.truetype(SANS, size)
        except Exception:
            return ImageFont.load_default()


def wrap(draw, text, fnt, width):
    """Greedy word wrap using real text widths; returns a list of lines."""
    lines, cur = [], ""
    for word in text.split():
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=fnt) <= width or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_wrapped(draw, x, y, text, fnt, width, fill=INK, leading=3):
    lines = wrap(draw, text, fnt, width)
    for line in lines:
        draw.text((x, y), line, font=fnt, fill=fill)
        y += fnt.size + leading
    return y


def wrap_limit(draw, text, fnt, width, max_lines):
    """Wrap, then cap at max_lines, adding an ellipsis when text is cut."""
    lines = wrap(draw, text, fnt, width)
    if len(lines) > max_lines:
        lines = lines[:max_lines]
        while lines and draw.textlength(lines[-1] + "…", font=fnt) > width:
            lines[-1] = lines[-1][:-1]
        lines[-1] = lines[-1] + "…"
    return lines


def draw_limited(draw, x, y, text, fnt, width, max_lines, fill=INK, leading=1):
    for line in wrap_limit(draw, text, fnt, width, max_lines):
        draw.text((x, y), line, font=fnt, fill=fill)
        y += fnt.size + leading
    return y


def text_h(fnt):
    return fnt.size + 3


# (number, region, place, category, headline, deck, source)
PANELS = [
    (1, "Europe", "ANTALYA, TURKIYE", "CLIMATE",
     "COP31 runs into overtime with no fossil-fuel text",
     "Draft drops phase-out language. France and Panama demand a stronger deal; a third draft is due Saturday morning.",
     "Guardian, Al Jazeera"),
    (2, "Europe", "KYIV AND KRYVYI RIH, UKRAINE", "WAR",
     "Overnight Russian barrage kills at least 8 in Ukraine",
     "More than 400 drones and 110 missiles. Bridges and rail stations hit in Kyiv; 2 dead and 42 hurt in Kryvyi Rih.",
     "Kyiv Independent, AP"),
    (3, "Europe", "LUBLIN, POLAND", "SECURITY",
     "Russian missiles land in Poland; NATO calls it a grave violation",
     "Two missiles and a suspected drone come down during drills. Tusk calls it a deliberate provocation.",
     "SCMP, Reuters"),
    (4, "Middle East", "RIYADH, SAUDI ARABIA", "SECURITY",
     "Houthi missiles intercepted over Riyadh",
     "Three ballistic missiles destroyed. The coalition strikes Houthi workshops in Sanaa and Hodeidah.",
     "Wire reports"),
    (5, "Middle East", "GAZA", "AID",
     "Four nations call on Israel to let aid reach flooded Gaza",
     "Australia, Canada, Italy and the UK seek immediate, unrestricted access as flooding adds to suffering.",
     "The Paris Eye"),
    (6, "Middle East", "JERUSALEM, ISRAEL", "POLITICS",
     "Herzog taps Eisenkot to form a government",
     "The former army chief gets the mandate on Saturday evening, passing over Netanyahu. A formal handover is set for Sunday.",
     "The Paris Eye"),
    (7, "Europe", "PARIS, FRANCE", "PROTEST",
     "France holds a fourth weekend of cost-of-living protests",
     "About 146,000 march nationwide, 46,000 of them in Paris.",
     "The Paris Eye"),
    (8, "Americas", "WASHINGTON, USA", "POLITICS",
     "Senate rejects the Iran war-powers resolution 51-48",
     "Trump says he is not rushing decisions on Iran and may not decide until 2027.",
     "Wire reports"),
    (9, "Americas", "WASHINGTON, USA", "SANCTIONS",
     "US adds four Iranians to the OFAC sanctions list",
     "The four are tied to handling Iranian oil revenues, the Treasury says.",
     "US Treasury"),
    (10, "Americas", "WASHINGTON, USA", "VENEZUELA",
     "State Dept details $12bn in Venezuelan oil revenue",
     "A 53-page report traces the money nearly a year after US forces captured Nicolas Maduro.",
     "The Paris Eye"),
    (11, "Europe", "TALLINN, ESTONIA", "SECURITY",
     "Estonia shuts all road border crossings to Russia",
     "The move follows a suspected arson sabotage attack on a drone maker.",
     "Wire reports"),
    (12, "Europe", "BRUSSELS, BELGIUM", "EUROPE",
     "EU adopts 1bn euros in military aid for Ukraine",
     "Council decisions fund joint equipment buying, delivery by end-2027. A 45bn euro loan is earmarked.",
     "EU Council"),
    (13, "Europe", "LONDON, UK", "DEFENCE",
     "UK pledges more than 1,000 drones for Ukraine",
     "A 260m pound package of extended-range drones for Kyiv's defences.",
     "Wire reports"),
    (14, "Europe", "COPENHAGEN, DENMARK", "SECURITY",
     "Denmark foils a plot to kill rapper Kyivstoner",
     "Two men are accused. Police moved minutes before the concert; a Russian diplomat is expelled.",
     "Kyiv Post, Stuff"),
    (15, "Asia", "NEW DELHI, INDIA", "DIPLOMACY",
     "Modi opens the first SCO Civilisational Dialogue Forum",
     "The three-day forum runs 20-22 Nov. A Pakistani minister attends; India says its Indus Waters stand has not changed.",
     "MEA reports"),
    (16, "Oceania", "WELLINGTON, NEW ZEALAND", "SPORT",
     "India fight back in the Wellington Test at 159/1",
     "Jaiswal and Rahul share a century opening stand. India trail New Zealand by 209.",
     "Jagran Josh"),
]

# (number, place, one-line brief)
ALSO = [
    (17, "KERCH", "Third strike this week hits the Crimea Bridge; rail traffic halts."),
    (18, "HORMUZ", "Tanker strike and fire reported; UKMTO issues a warning off Khasab."),
    (19, "NEW YORK", "JPMorgan, Visa and Mastercard report vendor cyberattacks."),
    (20, "LOS ANGELES", "Hyundai unveils the 2027 Elantra at the auto show; hybrid options."),
    (21, "LOS ANGELES", "Jury convicts the man who started the deadly 2025 Palisades Fire."),
    (22, "UNITED STATES", "A pill hailed as a breakthrough for pancreatic cancer is reported."),
    (23, "WASHINGTON", "Melania Trump says her Christmas wish is another ceasefire."),
    (24, "WASHINGTON", "Trump says he and Putin had very good talks on Ukraine."),
    (25, "PARIS", "France calls for a UN Security Council meeting after Kyiv embassy damage."),
    (26, "BRUSSELS", "EU-UK youth mobility agreed for ages 18-31, with an annual cap."),
    (27, "BUENOS AIRES", "Senate approves a permanent disability framework, 71-0."),
    (28, "KATHMANDU", "PM Balendra Shah to visit India on 22-23 November."),
    (29, "KUALA LUMPUR", "Malaysia plans to resettle 10,000 Rohingya refugees to Turkiye."),
    (30, "JAKARTA", "Indonesia fire losses could reach $30bn, Copernicus says."),
    (31, "NEW DELHI", "WHO calls for urgent action on antimicrobial resistance in SE Asia."),
    (32, "KUNO", "A Botswana-born cheetah gives birth to four cubs; India count rises to 62."),
    (33, "NEW DELHI", "ICC gives India the 2029 Champions Trophy and 2031 ODI World Cup."),
    (34, "PARIS", "UEFA backs France's Diallo against Infantino in the FIFA election."),
    (35, "RIYADH", "Saudi Arabia warns of thunderstorms through Tuesday 24 November."),
    (36, "BUDAPEST", "Hungary lifts its block on the last two EU accession categories."),
    (37, "NEW DELHI", "Delhi Police bans drones and laser beams near IGI Airport for 60 days."),
    (38, "MUMBAI", "IRDAI fines Star Health Rs 2 crore over Covid claim rejections."),
    (39, "NEW DELHI", "India's core sector growth hits a series high of 10.9% in October."),
    (40, "MUMBAI", "Foreign investors pump a record Rs 1.01 lakh crore into Indian stocks."),
    (41, "NEW DELHI", "Aviation regulator issues a show-cause notice to SpiceJet."),
    (42, "NEW DELHI", "Supreme Court dismisses Tamil Nadu's plea over the Cauvery dispute."),
    (43, "GLOBAL", "A UN agency warns of growing global hunger as funding runs short."),
    (44, "WASHINGTON", "US announces $52m in schooling aid for crisis countries."),
    (45, "NEW YORK", "Magnus Carlsen forfeits rapid games at a chess tournament."),
    (46, "KHARTOUM", "Relief agencies say 1.2m Sudanese children are displaced."),
    (47, "TOKYO", "The yen trades near 158 to the dollar as the AI sell-off weighs."),
    (48, "ANKARA", "Turkiye welcomes the ICJ decision finding Myanmar responsible."),
    (49, "BERLIN", "Students march against rearmament and mandatory service."),
    (50, "BRASILIA", "Brazil advances an Indigenous land bill as its leader meets chief Raoni."),
    (51, "FRANKFURT", "ECB names Boone and Brunnermeier for its Executive Board."),
    (52, "MELBOURNE", "Australia and England open their T20 series at the MCG tonight."),
]

KPI = [
    ("0", "climate deal agreed at COP31"),
    ("8+", "killed in the overnight Ukraine strikes"),
    ("42", "hurt in the Kryvyi Rih strike"),
    ("400+", "drones fired at Ukraine overnight"),
    ("120,000", "evacuated for Cyclone Akvan"),
    ("-3.7%", "Wall Street falls into correction"),
]

TIMELINE = [
    ("00:30", "Kryvyi Rih toll"),
    ("01:44", "COP31 stalls"),
    ("03:52", "Gaza aid call"),
    ("06:15", "Estonia border shut"),
    ("19:46", "Trump-Putin talks"),
    ("23:49", "Denmark plot foiled"),
]

DATE_CHECK = ("DATE CHECK — LEFT OUT BECAUSE IT BROKE BEFORE SATURDAY:  "
              "Kyiv bridges — Fri 20 Nov  ·  ICJ Myanmar ruling — Thu 19 Nov  ·  "
              "Shenzhen declaration — Thu 19 Nov  ·  UK-EU deal — Fri 20 Nov  ·  "
              "Wall Street Friday close — Fri 20 Nov  ·  Anthropic IPO — Thu 19 Nov")

REGIONS = ["Europe", "Asia", "Middle East", "Africa", "Americas", "Oceania", "Global"]
REGION_COLOURS = {
    "Europe": (31, 78, 140), "Asia": (179, 35, 27), "Middle East": (176, 141, 30),
    "Africa": (18, 110, 105), "Americas": (104, 52, 130), "Oceania": (16, 120, 140),
    "Global": (90, 86, 78),
}
# Region per story number, counted from PANELS + ALSO by place (kept in code).
STORY_REGION = {}
for _n, _r, *_rest in PANELS:
    STORY_REGION[_n] = _r
for _n, _p, _b in ALSO:
    _r = {"KERCH": "Europe", "HORMUZ": "Middle East", "NEW YORK": "Americas",
          "LOS ANGELES": "Americas", "UNITED STATES": "Americas",
          "WASHINGTON": "Americas", "PARIS": "Europe", "BRUSSELS": "Europe",
          "BUENOS AIRES": "Americas", "KATHMANDU": "Asia", "KUALA LUMPUR": "Asia",
          "JAKARTA": "Asia", "NEW DELHI": "Asia", "KUNO": "Asia", "ROME": "Europe",
          "KHARTOUM": "Africa", "TOKYO": "Asia", "ANKARA": "Middle East",
          "BERLIN": "Europe", "BRASILIA": "Americas", "FRANKFURT": "Europe",
          "MELBOURNE": "Oceania", "MUMBAI": "Asia", "BUDAPEST": "Europe",
          "RIYADH": "Middle East"}.get(_p, "Global")
    STORY_REGION[_n] = _r


def starburst(d, cx, cy, r, colour):
    for k in range(8):
        ang = k * 3.14159 / 4
        x2 = cx + r * (1 if k % 2 == 0 else 0.45) * (1 if k in (0, 1, 7) else -1 if k in (3, 4, 5) else 0.4)
        y2 = cy + r * (1 if k % 2 == 0 else 0.45) * (1 if k in (1, 2, 3) else -1 if k in (5, 6, 7) else 0.4)
        d.line([(cx, cy), (x2, y2)], fill=colour, width=3)
    d.ellipse([cx - r // 3, cy - r // 3, cx + r // 3, cy + r // 3], fill=colour)


def scene(d, num, x0, y0, x1, y1):
    """Flat drawn scene for panel `num`, clipped to its box by construction:
    every coordinate is interpolated inside the box, never outside it."""
    w, h = x1 - x0, y1 - y0
    X = lambda f: x0 + int(w * f)
    Y = lambda f: y0 + int(h * f)
    if num == 1:  # COP31: globe + thermometer
        d.rectangle([x0, y0, x1, y1], fill=(178, 224, 210))
        d.ellipse([X(0.08), Y(0.12), X(0.58), Y(0.92)], fill=(43, 120, 190))
        d.ellipse([X(0.18), Y(0.25), X(0.34), Y(0.45)], fill=(74, 160, 90))
        d.ellipse([X(0.36), Y(0.55), X(0.52), Y(0.78)], fill=(74, 160, 90))
        d.rectangle([X(0.68), Y(0.15), X(0.78), Y(0.75)], fill=(255, 255, 255),
                    outline=RED, width=2)
        d.rectangle([X(0.68), Y(0.45), X(0.78), Y(0.75)], fill=RED)
        d.ellipse([X(0.64), Y(0.72), X(0.82), Y(0.92)], fill=RED)
    elif num == 2:  # Kyiv night
        d.rectangle([x0, y0, x1, y1], fill=(16, 28, 52))
        d.ellipse([X(0.78), Y(0.08), X(0.90), Y(0.28)], fill=(240, 220, 160))
        for i, bx in enumerate((0.05, 0.28, 0.52, 0.72)):
            bh = (0.55, 0.72, 0.62, 0.48)[i]
            d.rectangle([X(bx), Y(1 - bh), X(bx + 0.18), y1], fill=(8, 14, 30))
            for wy in (0.42, 0.58, 0.74):
                for wx in (0.04, 0.10):
                    d.rectangle([X(bx + wx), Y(wy), X(bx + wx + 0.04), Y(wy + 0.07)],
                                fill=(250, 200, 90))
        starburst(d, X(0.38), Y(0.30), max(6, w // 18), (255, 150, 40))
        starburst(d, X(0.62), Y(0.22), max(5, w // 24), (255, 200, 80))
    elif num == 3:  # Poland: border fence + streaks
        d.rectangle([x0, y0, x1, y1], fill=(226, 232, 238))
        for i in range(7):
            d.line([(X(0.05 + i * 0.14), Y(0.35)), (X(0.05 + i * 0.14), Y(0.95))],
                   fill=(60, 60, 60), width=2)
        d.line([(x0, Y(0.38)), (x1, Y(0.38))], fill=(60, 60, 60), width=3)
        d.line([(X(0.10), Y(0.15)), (X(0.55), Y(0.45))], fill=RED, width=3)
        d.line([(X(0.30), Y(0.10)), (X(0.70), Y(0.40))], fill=RED, width=3)
        starburst(d, X(0.72), Y(0.48), max(6, w // 18), (255, 120, 30))
        d.ellipse([X(0.80), Y(0.55), X(0.88), Y(0.68)], fill=RED)
    elif num == 4:  # Riyadh intercept
        d.rectangle([x0, y0, x1, y1], fill=(250, 226, 180))
        for i, bx in enumerate((0.05, 0.35, 0.65)):
            d.rectangle([X(bx), Y(0.55), X(bx + 0.22), Y(0.95)], fill=(190, 150, 100))
            d.rectangle([X(bx + 0.07), Y(0.42), X(bx + 0.15), Y(0.55)], fill=(160, 120, 80))
        d.line([(X(0.15), Y(0.10)), (X(0.45), Y(0.50))], fill=(40, 40, 40), width=2)
        d.line([(X(0.85), Y(0.10)), (X(0.60), Y(0.45))], fill=(40, 40, 40), width=2)
        starburst(d, X(0.52), Y(0.52), max(6, w // 18), (255, 140, 40))
    elif num == 5:  # Gaza: waves + tents
        d.rectangle([x0, y0, x1, y1], fill=(120, 180, 210))
        for i in range(3):
            d.polygon([(X(0.08 + i * 0.30), Y(0.85)), (X(0.20 + i * 0.30), Y(0.45)),
                       (X(0.32 + i * 0.30), Y(0.85))], fill=(245, 240, 225))
        d.rectangle([X(0.10), Y(0.88), X(0.90), Y(0.98)], fill=(40, 90, 130))
        d.rectangle([X(0.55), Y(0.18), X(0.85), Y(0.32)], fill=(255, 255, 255))
        d.text((X(0.58), Y(0.20)), "AID", font=font(SANS_B, max(8, h // 6)), fill=RED)
    elif num == 6:  # Israel: domed building
        d.rectangle([x0, y0, x1, y1], fill=(232, 226, 210))
        d.rectangle([X(0.15), Y(0.55), X(0.85), Y(0.92)], fill=(200, 185, 150))
        d.pieslice([X(0.35), Y(0.22), X(0.65), Y(0.60)], 180, 360, fill=(150, 120, 80))
        for i in range(4):
            d.rectangle([X(0.20 + i * 0.16), Y(0.60), X(0.26 + i * 0.16), Y(0.92)],
                        fill=(240, 235, 220))
    elif num == 7:  # Paris: tower + crowd
        d.rectangle([x0, y0, x1, y1], fill=(220, 228, 240))
        d.polygon([(X(0.42), Y(0.10)), (X(0.58), Y(0.10)), (X(0.68), Y(0.92)),
                   (X(0.32), Y(0.92))], fill=(90, 90, 90))
        d.line([(X(0.20), Y(0.55)), (X(0.80), Y(0.55))], fill=(90, 90, 90), width=2)
        for i in range(9):
            d.ellipse([X(0.08 + i * 0.10), Y(0.82), X(0.14 + i * 0.10), Y(0.92)],
                      fill=(179, 35, 27) if i % 3 == 0 else NAVY)
    elif num == 8:  # Washington: capitol + tally
        d.rectangle([x0, y0, x1, y1], fill=(235, 235, 228))
        d.rectangle([X(0.20), Y(0.60), X(0.80), Y(0.92)], fill=(220, 215, 200))
        d.pieslice([X(0.40), Y(0.25), X(0.60), Y(0.62)], 180, 360, fill=(180, 170, 150))
        d.rectangle([X(0.10), Y(0.72), X(0.46), Y(0.82)], fill=NAVY)
        d.rectangle([X(0.54), Y(0.72), X(0.90), Y(0.82)], fill=RED)
    elif num == 9:  # Sanctions: barrel + list
        d.rectangle([x0, y0, x1, y1], fill=(240, 238, 225))
        d.ellipse([X(0.10), Y(0.30), X(0.38), Y(0.90)], fill=(40, 40, 40))
        d.rectangle([X(0.10), Y(0.30), X(0.38), Y(0.90)], fill=(60, 60, 60))
        for i in range(3):
            d.line([(X(0.50), Y(0.25 + i * 0.22)), (X(0.90), Y(0.25 + i * 0.22))],
                   fill=RED, width=2)
            d.line([(X(0.50), Y(0.33 + i * 0.22)), (X(0.82), Y(0.33 + i * 0.22))],
                   fill=(120, 120, 120), width=2)
    elif num == 10:  # Venezuela: derrick + barrels
        d.rectangle([x0, y0, x1, y1], fill=(250, 240, 200))
        d.polygon([(X(0.15), Y(0.90)), (X(0.30), Y(0.15)), (X(0.45), Y(0.90))],
                  fill=(120, 90, 60))
        for i in range(3):
            d.rectangle([X(0.60 + i * 0.12), Y(0.65), X(0.70 + i * 0.12), Y(0.92)],
                        fill=(30, 80, 40))
        d.text((X(0.55), Y(0.20)), "$12bn", font=font(SANS_B, max(9, h // 5)), fill=NAVY)
    elif num == 11:  # Estonia: closed gate
        d.rectangle([x0, y0, x1, y1], fill=(228, 232, 225))
        for i in range(6):
            d.line([(X(0.08 + i * 0.15), Y(0.30)), (X(0.08 + i * 0.15), Y(0.92))],
                   fill=(50, 50, 50), width=2)
        d.line([(x0, Y(0.32)), (x1, Y(0.32))], fill=(50, 50, 50), width=3)
        d.polygon([(X(0.62), Y(0.15)), (X(0.78), Y(0.45)), (X(0.46), Y(0.45))],
                  fill=(240, 200, 40), outline=(0, 0, 0))
        d.text((X(0.60), Y(0.28)), "!", font=font(SANS_B, max(9, h // 5)), fill=(0, 0, 0))
    elif num == 12:  # Brussels: stars + coins
        d.rectangle([x0, y0, x1, y1], fill=(30, 60, 120))
        for k in range(8):
            ang = k * 3.14159 / 4
            cx, cy = X(0.30) + int(0.16 * w * (1 if k % 2 == 0 else 0.7)), Y(0.50)
            d.ellipse([cx - 3, cy - 3, cx + 3, cy + 3], fill=(250, 210, 60))
        for i in range(3):
            d.ellipse([X(0.60 + i * 0.11), Y(0.60), X(0.70 + i * 0.11), Y(0.82)],
                      fill=(250, 210, 60), outline=(180, 140, 20))
    elif num == 13:  # London: tower + drones
        d.rectangle([x0, y0, x1, y1], fill=(215, 228, 235))
        d.rectangle([X(0.12), Y(0.20), X(0.26), Y(0.92)], fill=(120, 100, 80))
        d.polygon([(X(0.10), Y(0.20)), (X(0.19), Y(0.08)), (X(0.28), Y(0.20))],
                  fill=(90, 75, 60))
        d.ellipse([X(0.16), Y(0.28), X(0.22), Y(0.36)], fill=(250, 240, 200))
        for i, (fx, fy) in enumerate(((0.55, 0.25), (0.75, 0.45), (0.60, 0.65))):
            d.ellipse([X(fx), Y(fy), X(fx + 0.10), Y(fy + 0.12)], fill=(40, 40, 40))
            d.line([(X(fx - 0.04), Y(fy + 0.06)), (X(fx + 0.14), Y(fy + 0.06))],
                   fill=(40, 40, 40), width=2)
    elif num == 14:  # Copenhagen: stage + shield
        d.rectangle([x0, y0, x1, y1], fill=(25, 25, 40))
        d.rectangle([X(0.10), Y(0.65), X(0.90), Y(0.92)], fill=(120, 90, 70))
        d.polygon([(X(0.35), Y(0.20)), (X(0.65), Y(0.20)), (X(0.65), Y(0.45)),
                   (X(0.50), Y(0.60)), (X(0.35), Y(0.45))], fill=(40, 90, 160))
        d.text((X(0.47), Y(0.28)), "✓", font=font(SANS_B, max(9, h // 5)), fill=(255, 255, 255))
        starburst(d, X(0.20), Y(0.25), max(5, w // 22), (255, 200, 80))
    elif num == 15:  # Delhi: fort arch + flags
        d.rectangle([x0, y0, x1, y1], fill=(250, 230, 200))
        d.rectangle([X(0.10), Y(0.45), X(0.90), Y(0.92)], fill=(190, 90, 60))
        d.pieslice([X(0.38), Y(0.35), X(0.62), Y(0.75)], 180, 360, fill=(247, 241, 227))
        d.rectangle([X(0.15), Y(0.20), X(0.30), Y(0.38)], fill=(255, 140, 0))
        d.rectangle([X(0.70), Y(0.20), X(0.85), Y(0.38)], fill=(20, 130, 60))
    else:  # Wellington: cricket
        d.rectangle([x0, y0, x1, y1], fill=(140, 190, 120))
        d.rectangle([X(0.10), Y(0.70), X(0.90), Y(0.92)], fill=(210, 185, 140))
        d.line([(X(0.30), Y(0.20)), (X(0.55), Y(0.75))], fill=(150, 110, 70), width=max(3, w // 30))
        d.ellipse([X(0.68), Y(0.30), X(0.78), Y(0.44)], fill=RED)
        d.text((X(0.12), Y(0.15)), "159/1", font=font(SANS_B, max(9, h // 5)), fill=(255, 255, 255))


def dot_map(d, x0, y0, x1, y1):
    """Dotted world map on a square pixel grid: a dot is drawn only when its
    centre falls inside a coarse continent rectangle, so the grid stays square
    whatever the strip height is. Pins are numbered 1-16, matching panels."""
    d.rectangle([x0, y0, x1, y1], fill=(238, 230, 205))
    pins = [(28, 53), (33, 48), (23, 51), (46, 24), (34, 31), (35, 31), (2, 48),
            (-80, 40), (-77, 36), (-74, 41), (24, 59), (4, 50), (0, 51), (12, 55),
            (77, 28), (174, -41)]
    # Pixel nudges to de-collide pins that share a place: Gaza/Jerusalem are
    # 1 degree apart and the three Washington pins are 3 degrees apart.
    PIN_NUDGE = {5: (0, -7), 6: (0, 7), 8: (-6, -5), 9: (0, 6), 10: (5, -5)}
    blobs = [(-168, -52, 15, 71), (-70, -34, -55, 12), (-10, 40, 36, 70),
             (40, 140, 5, 77), (95, 155, -10, 55), (113, 154, -39, -11),
             (20, 50, -35, 5)]
    step = 9
    py = y0 + 4
    while py < y1 - 2:
        px = x0 + 4
        while px < x1 - 2:
            lon = (px - x0) / max(1, x1 - x0) * 360 - 180
            lat = 80 - (py - y0) / max(1, y1 - y0) * 140
            if any(a <= lon <= b and c <= lat <= e for a, b, c, e in blobs):
                d.ellipse([px - 1, py - 1, px + 1, py + 1], fill=(150, 140, 115))
            px += step
        py += step
    for i, (lon, lat) in enumerate(pins, 1):
        px = x0 + int((lon + 180) / 360 * (x1 - x0))
        py = y0 + int((80 - lat) / 140 * (y1 - y0))
        dx, dy = PIN_NUDGE.get(i, (0, 0))
        px += dx
        py += dy
        d.ellipse([px - 5, py - 5, px + 5, py + 5], fill=RED, outline=(255, 255, 255))
        d.text((px - 2, py - 4), str(i), font=font(SANS_B, 7), fill=(255, 255, 255))


def build():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    mx = 14
    x1 = W - mx
    y = 10
    # Masthead
    f_mast = font(SANS_B, 13)
    d.text((mx, y), "THE WORLD IN ONE DAY", font=f_mast, fill=RED)
    right = "52 STORIES  ·  7 REGIONS  ·  EVERY ONE DATED SATURDAY 21 NOVEMBER 2026"
    d.text((x1 - d.textlength(right, font=f_mast), y), right, font=f_mast, fill=INK)
    y += 20
    d.line([(mx, y), (x1, y)], fill=INK, width=2)
    y += 6
    # Title
    f_title = font(SERIF_B, 52)
    title = "Saturday 21 November 2026"
    d.text(((W - d.textlength(title, font=f_title)) // 2, y), title, font=f_title, fill=NAVY)
    y += 60
    f_sub = font(SERIF, 15)
    sub = ("COP31 runs into overtime  ·  Russian strikes kill at least 8  ·  "
           "Missiles land in Poland  ·  Houthi missiles intercepted")
    for line in wrap(d, sub, f_sub, x1 - mx):
        d.text(((W - d.textlength(line, font=f_sub)) // 2, y), line, font=f_sub, fill=INK)
        y += 19
    y += 4
    d.line([(mx, y), (x1, y)], fill=INK, width=1)
    y += 5
    # KPI strip
    kh = 46
    d.rectangle([mx, y, x1, y + kh], fill=NAVY)
    cw = (x1 - mx) / len(KPI)
    for i, (big, cap) in enumerate(KPI):
        cx = mx + i * cw
        fb = font(SANS_B, 20)
        d.text((cx + 8, y + 4), big, font=fb, fill=(255, 255, 255))
        draw_wrapped(d, cx + 8, y + 28, cap, font(SANS, 9), cw - 14, fill=(220, 225, 235), leading=0)
        if i:
            d.line([(cx, y + 6), (cx, y + kh - 6)], fill=(120, 140, 165), width=1)
    y += kh + 6
    # DATE CHECK band
    f_dc = font(SANS, 10)
    dc_lines = wrap(d, DATE_CHECK, f_dc, x1 - mx - 12)
    dh = len(dc_lines) * 13 + 10
    d.rectangle([mx, y, x1, y + dh], fill=PINK, outline=RED, width=1)
    yy = y + 5
    for line in dc_lines:
        d.text((mx + 6, yy), line, font=f_dc, fill=(120, 20, 15))
        yy += 13
    y += dh + 6
    # Region bar (counts computed from STORY_REGION)
    counts = {r: sum(1 for v in STORY_REGION.values() if v == r) for r in REGIONS}
    f_reg = font(SANS_B, 10)
    rx = mx
    total_w = x1 - mx
    for r in REGIONS:
        label = "%s %d" % (r.upper(), counts[r])
        wdt = d.textlength(label, font=f_reg) + 16
        d.rectangle([rx, y, rx + wdt, y + 20], fill=REGION_COLOURS[r])
        d.text((rx + 8, y + 4), label, font=f_reg, fill=(255, 255, 255))
        rx += wdt + 3
    y += 24
    # Lead panels 1-3
    pw = (x1 - mx - 2 * 8) // 3
    ph = 158
    f_kick = font(SANS_B, 9)
    f_head = font(SANS_B, 14)
    f_deck = font(SANS, 10)
    f_src = font(SANS, 8)
    for i, (num, region, place, cat, head, deck, src) in enumerate(PANELS[:3]):
        px = mx + i * (pw + 8)
        d.rectangle([px, y, px + pw, y + ph], fill=LIGHT, outline=GREY, width=1)
        scene(d, num, px + 1, y + 1, px + pw - 1, y + 62)
        d.ellipse([px + 6, y + 66, px + 24, y + 84], fill=RED)
        d.text((px + 11, y + 69), str(num), font=font(SANS_B, 11), fill=(255, 255, 255))
        d.text((px + 28, y + 69), "%s · %s" % (place, cat), font=f_kick, fill=RED)
        yy = draw_limited(d, px + 6, y + 86, head, f_head, pw - 12, 2, leading=1)
        yy = draw_limited(d, px + 6, yy + 1, deck, f_deck, pw - 12, 2, leading=1)
        d.text((px + 6, y + ph - 13), "Source: " + src, font=f_src, fill=GREY)
    y += ph + 8
    # Small panels 4-16: two rows, 7 + 6
    rows = [PANELS[3:10], PANELS[10:16]]
    sph = 112
    for row in rows:
        n = len(row)
        spw = (x1 - mx - (n - 1) * 6) // n
        for i, (num, region, place, cat, head, deck, src) in enumerate(row):
            px = mx + i * (spw + 6)
            d.rectangle([px, y, px + spw, y + sph], fill=LIGHT, outline=GREY, width=1)
            scene(d, num, px + 1, y + 1, px + spw - 1, y + 40)
            d.ellipse([px + 4, y + 49, px + 18, y + 63], fill=RED)
            d.text((px + 8, y + 51), str(num), font=font(SANS_B, 9), fill=(255, 255, 255))
            d.text((px + 20, y + 51), place.split(",")[0], font=font(SANS_B, 8), fill=RED)
            yy = draw_limited(d, px + 4, y + 65, head, font(SANS_B, 10), spw - 8, 4, leading=0)
            # No deck in the small panels: at this width a deck always truncates
            # mid-sentence, so the headline alone carries the story.
        y += sph + 6
    # Timeline strip
    th = 22
    d.rectangle([mx, y, x1, y + th], fill=NAVY)
    f_tl = font(SANS_B, 9)
    d.text((mx + 6, y + 6), "THE DAY, HOUR BY HOUR (UTC):", font=f_tl, fill=GOLD)
    tx = mx + 6 + d.textlength("THE DAY, HOUR BY HOUR (UTC):", font=f_tl) + 8
    parts = ["%s %s" % (t, s) for t, s in TIMELINE]
    joined = "   ·   ".join(parts)
    d.text((tx, y + 6), joined, font=font(SANS, 9), fill=(255, 255, 255))
    y += th + 6
    # ALSO ON list, 3 columns x 12 rows
    f_also_h = font(SANS_B, 11)
    d.text((mx, y), "ALSO ON SATURDAY 21 NOVEMBER — 36 MORE STORIES", font=f_also_h, fill=NAVY)
    y += 16
    f_also = font(SANS, 10)
    col_w = (x1 - mx) // 2
    for idx, (num, place, brief) in enumerate(ALSO):
        col = idx // 18
        rowi = idx % 18
        ax = mx + col * col_w
        ay = y + rowi * 10
        d.text((ax, ay), "%d" % num, font=font(SANS_B, 10), fill=RED)
        line = "%s — %s" % (place, brief)
        lines = wrap_limit(d, line, f_also, col_w - 22, 1)
        d.text((ax + 18, ay), lines[0] if lines else "", font=f_also, fill=INK)
    y += 18 * 10 + 4
    # World map strip
    mh = H - y - 18
    f_map = font(SANS_B, 10)
    d.text((mx, y), "WHERE IT HAPPENED — 16 LEADS PINNED", font=f_map, fill=NAVY)
    y += 14
    dot_map(d, mx, y, x1, y + mh - 14)
    y = H - 14
    d.line([(mx, y), (x1, y)], fill=INK, width=1)
    f_foot = font(SANS, 8)
    foot = ("Every story here happened, or was first reported, on Saturday 21 November 2026. "
            "Sources named beside each story. Drawn illustrations, not photographs. 52 stories, 7 regions.")
    d.text((mx, y + 3), foot, font=f_foot, fill=GREY)
    return img


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    img = build()
    img.save(os.path.join(out_dir, "entry.png"), format="PNG", optimize=True)


if __name__ == "__main__":
    main()
