#!/usr/bin/env python3
"""Build build/poster.html: a 1024x1024 illustrated newspaper front page.

Data lives here. Every count shown on the page is derived from the lists below,
never typed, and every story carries a flat vector illustration drawn from
inline SVG geometry. Output is byte-identical on every run: no timestamps, no
randomness, no set iteration.
"""

import html
import math
import pathlib

HERE = pathlib.Path(__file__).resolve().parent

DATE_LINE = "Thursday 19 November 2026"
KICKER = "THE DAY'S WORLD NEWS IN ONE PICTURE"

FEATURES = [
    {
        "region": "ASIA",
        "label": "1 - SHENZHEN - SUMMIT",
        "headline": "Trump, Xi and Putin hold first three-way summit",
        "dek": "The three meet at APEC in Shenzhen on Thursday; Iran, Ukraine "
               "and arms control top a low-expectation agenda.",
        "art": "flags",
    },
    {
        "region": "MIDEAST",
        "label": "2 - THE GULF - KUWAIT",
        "headline": "Iran says its drones struck a US air base in Kuwait",
        "dek": "Tehran said the attack hit Patriot batteries at Ali Al-Salem in "
               "retaliation for a US strike on Qeshm Island.",
        "art": "drone",
    },
    {
        "region": "ASIA",
        "label": "3 - ANDHRA PRADESH - CYCLONE",
        "headline": "Cyclone Akvan due to hit the Andhra coast around noon Friday",
        "dek": "Landfall expected between Machilipatnam and Puri, with winds of "
               "120-130 km/h gusting to 145.",
        "art": "spiral",
    },
]

CARDS = [
    ("EUROPE", "EU proposes a 45bn euro loan for Ukraine's 2027 budget gap", "coins"),
    ("UKRAINE", "Zelenskyy: one three-way meeting could end the war", "podium"),
    ("UKRAINE", "Crimean Bridge struck again; traffic halted on the span", "bridge"),
    ("EUROPE", "Magnitude 5.7 quake shakes Romania; two injured", "seismic"),
    ("UNITED KINGDOM", "Britain and EU near a reset deal, due Friday", "flags"),
    ("UNITED KINGDOM", "Cambridge names Human its word of the year, citing AI", "book"),
    ("UNITED STATES", "Peltola beats Sullivan in Alaska; the Senate is 56-44", "ballot"),
    ("UNITED STATES", "Fed minutes: almost all saw further rate rises", "chart_up"),
    ("UNITED STATES", "Waymo pulls robotaxis off freeways after a state ban", "car"),
    ("KUWAIT", "Kuwait army says air defences engaged hostile drones", "radar"),
    ("AFRICA", "Confirmed Ebola cases pass 11,000; deaths above 5,300", "virus"),
    ("EAST ASIA", "Beijing gives Japan's Takaichi a low-key welcome", "flags"),
]

BRIEFS = [
    ("VENEZUELA", "US and Venezuela restore military ties and intelligence"),
    ("MEXICO", "Sheinbaum reports a very good meeting with Trump on trade"),
    ("EUROPE", "Berlin and London reject US criticism of Kyiv deep strikes"),
    ("RUSSIA", "Putin expects big potential benefits from the talks"),
    ("YEMEN", "Houthis blame Saudi-led strikes for three deaths"),
    ("GULF ENERGY", "Three tankers burn after hitting mines off Hormuz"),
    ("AFRICA", "WHO: DR Congo Ebola outbreak out of control at six months"),
    ("AFRICA", "South Africa summons Nigeria's envoy over online remarks"),
    ("SOUTH ASIA", "Akvan to bring 120-130 km/h winds, gusting to 145"),
    ("SOUTH ASIA", "India bowl first; New Zealand 60-4 at lunch in Wellington"),
    ("EAST ASIA", "South Korea offers $75,000 per case of exam cheating"),
    ("SOUTHEAST ASIA", "Arsenic in Mae Sai water 30 times the safe limit"),
    ("PACIFIC", "Fiji declares a national disaster as El Nino drought bites"),
    ("PACIFIC", "Tuvalu seeks 160m dollars for Pacific early-warning systems"),
    ("MARKETS", "S&P 500 falls 1.03% to 7,340 as rate worries bite"),
]

NUMBERS = [
    ("45bn euros", "EU loan proposed for Ukraine's 2027 budget"),
    ("11,000+", "confirmed Ebola cases in DR Congo"),
    ("5,300+", "deaths in the same outbreak"),
    ("56-44", "Democratic majority in the US Senate"),
    ("145", "km/h gusts as Cyclone Akvan nears Andhra"),
    ("7,340", "S&P 500 close, down 1.03 per cent"),
]

REGIONS = [
    ("ASIA", "#1d4e8f"),
    ("MIDEAST", "#8f2a1f"),
    ("EUROPE", "#157a4a"),
    ("AMERICAS", "#7a2f6b"),
    ("AFRICA", "#a8641c"),
    ("OCEANIA", "#1d5468"),
    ("WORLD", "#4a3b6b"),
]

REGION_OF = {
    "SOUTH ASIA": "ASIA", "EAST ASIA": "ASIA", "SOUTHEAST ASIA": "ASIA",
    "IRAN": "MIDEAST", "KUWAIT": "MIDEAST", "YEMEN": "MIDEAST",
    "GULF ENERGY": "MIDEAST",
    "EUROPE": "EUROPE", "UNITED KINGDOM": "EUROPE", "UKRAINE": "EUROPE",
    "RUSSIA": "EUROPE",
    "UNITED STATES": "AMERICAS", "VENEZUELA": "AMERICAS", "MEXICO": "AMERICAS",
    "AFRICA": "AFRICA",
    "PACIFIC": "OCEANIA",
    "MARKETS": "WORLD",
}

TOTAL = len(FEATURES) + len(CARDS) + len(BRIEFS)
COLOUR = dict(REGIONS)
NAMES = [name for name, _ in REGIONS]


def resolve(tag):
    """Map a story tag to a region name, refusing anything unknown."""
    if tag in REGION_OF:
        return REGION_OF[tag]
    if tag in COLOUR:
        return tag
    raise ValueError("tag %r has no region in REGION_OF" % (tag,))


def region_counts():
    """Count stories per region; raise on unmapped tags and empty regions."""
    counts = dict((name, 0) for name in NAMES)
    for item in FEATURES:
        counts[resolve(item["region"])] += 1
    for tag, _headline, _art in CARDS:
        counts[resolve(tag)] += 1
    for tag, _headline in BRIEFS:
        counts[resolve(tag)] += 1
    for name in NAMES:
        if counts[name] == 0:
            raise ValueError("region %r has no stories" % (name,))
    if sum(counts.values()) != 30:
        raise ValueError("story total is %d, expected 30" % sum(counts.values()))
    return counts


# ------------------------------------------------------------------ geometry

def n(value):
    """Format a coordinate deterministically, without trailing zeros."""
    text = "%.1f" % value
    if text.endswith(".0"):
        text = text[:-2]
    if text == "-0":
        text = "0"
    return text


def esc(text):
    return html.escape(text, quote=False)


def mix(first, second, t):
    """Flat blend of two #rrggbb colours, no alpha channel involved."""
    a = [int(first[i:i + 2], 16) for i in (1, 3, 5)]
    b = [int(second[i:i + 2], 16) for i in (1, 3, 5)]
    return "#%02x%02x%02x" % tuple(
        int(round(a[i] + (b[i] - a[i]) * t)) for i in range(3)
    )


PAPER = "#efe9dd"

TINT = {
    "flags": "#c3d2ea",
    "drone": "#e3c2ba",
    "spiral": "#bfd8df",
    "coins": "#f0e0b6",
    "podium": "#d9d2c2",
    "podium_cn": "#d9d2c2",
    "bridge": "#bcd6df",
    "seismic": "#e6c8c2",
    "book": "#e6dfcc",
    "ballot": "#c6d1e6",
    "chart_up": "#c4d5ea",
    "chart_down": "#c4d5ea",
    "car": "#c3d2e8",
    "radar": "#bcd6de",
    "virus": "#e0c6d8",
}


def wrap(uid, w, h, body):
    """Wrap primitives in a clipped SVG box of exactly w x h pixels."""
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" '
        'viewBox="0 0 %d %d" preserveAspectRatio="xMidYMid meet">'
        '<defs><clipPath id="%s"><rect x="0" y="0" width="%d" height="%d"/>'
        '</clipPath></defs><g clip-path="url(#%s)">%s</g></svg>'
    ) % (w, h, w, h, uid, w, h, uid, body)


def sw(w, base=1.0, k=0.010):
    """Stroke width that stays legible at 46px wide and at 317px wide."""
    return max(base, w * k)


def a_flags(w, h, uid):
    top = h * 0.16
    bot = h * 0.93
    fh = min(h * 0.38, h * 0.38)
    fw = w * 0.21
    ink = "#26324a"
    bands = (
        ("#b5202a", "#f7f3e8"),
        ("#f7f3e8", "#1d4e8f"),
        ("#1d4e8f", "#b5202a"),
    )
    out = []
    for x, (first, second) in zip((w * 0.14, w * 0.47, w * 0.80), bands):
        out.append('<line x1="%s" y1="%s" x2="%s" y2="%s" stroke="%s" stroke-width="%s"/>'
                   % (n(x), n(top), n(x), n(bot), ink, n(sw(w, 1.2))))
        out.append('<rect x="%s" y="%s" width="%s" height="%s" fill="%s"/>'
                   % (n(x), n(top), n(fw), n(fh * 0.5), first))
        out.append('<rect x="%s" y="%s" width="%s" height="%s" fill="%s" stroke="%s" stroke-width="%s"/>'
                   % (n(x), n(top + fh * 0.5), n(fw), n(fh * 0.5), second, ink,
                      n(sw(w, 0.7, 0.005))))
    out.append('<line x1="0" y1="%s" x2="%s" y2="%s" stroke="%s" stroke-width="%s"/>'
               % (n(bot), n(w), n(bot), ink, n(sw(w, 1.0))))
    return wrap(uid, w, h, "".join(out))


def a_drone(w, h, uid):
    cx = w * 0.46
    cy = h * 0.46
    arm = min(w * 0.30, h * 0.34)
    rotor = min(w, h) * 0.13
    ink = "#1d2230"
    out = [
        '<line x1="%s" y1="%s" x2="%s" y2="%s" stroke="%s" stroke-width="%s"/>'
        % (n(cx - arm), n(cy), n(cx + arm), n(cy), ink, n(sw(w, 1.6))),
        '<line x1="%s" y1="%s" x2="%s" y2="%s" stroke="%s" stroke-width="%s"/>'
        % (n(cx), n(cy - arm * 0.60), n(cx), n(cy + arm * 0.60), ink, n(sw(w, 1.6))),
    ]
    for ex, ey in ((cx - arm, cy), (cx + arm, cy),
                   (cx, cy - arm * 0.60), (cx, cy + arm * 0.60)):
        out.append('<circle cx="%s" cy="%s" r="%s" fill="#8f2a1f" stroke="%s" '
                   'stroke-width="%s"/>'
                   % (n(ex), n(ey), n(rotor), ink, n(sw(w, 1.0))))
    out.append('<rect x="%s" y="%s" width="%s" height="%s" rx="%s" fill="#1d2230"/>'
               % (n(cx - w * 0.065), n(cy - h * 0.075), n(w * 0.13), n(h * 0.15),
                  n(min(w, h) * 0.03)))
    out.append('<rect x="%s" y="%s" width="%s" height="%s" fill="#f7f3e8"/>'
               % (n(cx - w * 0.030), n(cy - h * 0.030), n(w * 0.060), n(h * 0.060)))
    out.append('<line x1="%s" y1="%s" x2="%s" y2="%s" stroke="#7d2318" '
               'stroke-width="%s" stroke-dasharray="%s %s"/>'
               % (n(cx + arm * 0.5), n(cy + arm * 0.95), n(w * 0.92), n(h * 0.96),
                  n(sw(w, 1.4)), n(max(3.0, w * 0.035)), n(max(2.5, w * 0.025))))
    return wrap(uid, w, h, "".join(out))


def a_spiral(w, h, uid):
    cx = w * 0.46
    cy = h * 0.50
    r = min(w, h) * 0.40
    ink = "#1d5468"
    out = [
        '<circle cx="%s" cy="%s" r="%s" fill="none" stroke="%s" stroke-width="%s"/>'
        % (n(cx), n(cy), n(r), ink, n(sw(w, 1.6))),
        '<circle cx="%s" cy="%s" r="%s" fill="none" stroke="%s" stroke-width="%s"/>'
        % (n(cx), n(cy), n(r * 0.70), ink, n(sw(w, 1.2))),
        '<circle cx="%s" cy="%s" r="%s" fill="none" stroke="%s" stroke-width="%s"/>'
        % (n(cx), n(cy), n(r * 0.40), ink, n(sw(w, 1.2))),
        '<circle cx="%s" cy="%s" r="%s" fill="%s"/>'
        % (n(cx), n(cy), n(r * 0.12), ink),
        '<path d="M %s %s A %s %s 0 0 1 %s %s" fill="none" stroke="#a8641c" '
        'stroke-width="%s" stroke-dasharray="%s %s"/>'
        % (n(cx - r * 0.98), n(cy - r * 0.30), n(r * 1.05), n(r * 1.05),
           n(cx + r * 0.55), n(cy - r * 1.02), n(sw(w, 1.0)),
           n(max(2.5, w * 0.035)), n(max(2.0, w * 0.02))),
        '<path d="M %s %s A %s %s 0 0 0 %s %s" fill="none" stroke="#a8641c" '
        'stroke-width="%s" stroke-dasharray="%s %s"/>'
        % (n(cx + r * 0.95), n(cy + r * 0.55), n(r * 0.9), n(r * 0.9),
           n(cx - r * 0.90), n(cy + r * 0.62), n(sw(w, 1.0)),
           n(max(2.5, w * 0.035)), n(max(2.0, w * 0.02))),
        '<polygon points="%s,%s %s,%s %s,%s" fill="#a8641c" opacity="0.85"/>'
        % (n(w * 0.72), n(h * 0.86), n(w), n(h * 0.66), n(w), n(h * 0.98)),
    ]
    return wrap(uid, w, h, "".join(out))


def a_coins(w, h, uid):
    rx = min(w * 0.27, h * 0.46)
    ry = rx * 0.32
    cx = w * 0.44
    out = []
    for i in range(4):
        cy = h * 0.82 - i * h * 0.16
        out.append('<ellipse cx="%s" cy="%s" rx="%s" ry="%s" fill="#d9a93c" '
                   'stroke="#7d5a12" stroke-width="%s"/>'
                   % (n(cx), n(cy), n(rx), n(ry), n(sw(w, 0.8, 0.006))))
        out.append('<ellipse cx="%s" cy="%s" rx="%s" ry="%s" fill="none" '
                   'stroke="#7d5a12" stroke-width="%s"/>'
                   % (n(cx), n(cy - ry * 0.35), n(rx * 0.62), n(ry * 0.55),
                      n(sw(w, 0.6, 0.004))))
    return wrap(uid, w, h, "".join(out))


def a_podium(w, h, uid):
    ink = "#2b3446"
    out = [
        '<rect x="%s" y="%s" width="%s" height="%s" fill="#ded3bd" stroke="%s" '
        'stroke-width="%s"/>'
        % (n(w * 0.16), n(h * 0.06), n(w * 0.68), n(h * 0.50), ink, n(sw(w, 0.8))),
        '<polygon points="%s,%s %s,%s %s,%s %s,%s" fill="#b5202a"/>'
        % (n(w * 0.42), n(h * 0.52), n(w * 0.58), n(h * 0.52),
           n(w * 0.64), n(h * 0.94), n(w * 0.36), n(h * 0.94)),
        '<line x1="%s" y1="%s" x2="%s" y2="%s" stroke="%s" stroke-width="%s"/>'
        % (n(w * 0.50), n(h * 0.30), n(w * 0.50), n(h * 0.52), ink, n(sw(w, 0.9))),
        '<circle cx="%s" cy="%s" r="%s" fill="%s"/>'
        % (n(w * 0.50), n(h * 0.27), n(min(w, h) * 0.075), ink),
    ]
    return wrap(uid, w, h, "".join(out))


def a_bridge(w, h, uid):
    ink = "#2b3446"
    deck = h * 0.62
    out = [
        '<rect x="0" y="%s" width="%s" height="%s" fill="#9fc4cf"/>'
        % (n(deck), n(w), n(h - deck)),
        '<line x1="0" y1="%s" x2="%s" y2="%s" stroke="%s" stroke-width="%s"/>'
        % (n(deck), n(w), n(deck), ink, n(sw(w, 1.4))),
        '<rect x="%s" y="%s" width="%s" height="%s" fill="%s"/>'
        % (n(w * 0.28), n(h * 0.22), n(w * 0.055), n(deck - h * 0.22), ink),
        '<rect x="%s" y="%s" width="%s" height="%s" fill="%s"/>'
        % (n(w * 0.68), n(h * 0.22), n(w * 0.055), n(deck - h * 0.22), ink),
    ]
    for tx in (w * 0.3075, w * 0.7075):
        out.append('<line x1="%s" y1="%s" x2="%s" y2="%s" stroke="%s" stroke-width="%s"/>'
                   % (n(tx), n(h * 0.30), n(w * 0.06), n(deck), ink, n(sw(w, 0.7))))
        out.append('<line x1="%s" y1="%s" x2="%s" y2="%s" stroke="%s" stroke-width="%s"/>'
                   % (n(tx), n(h * 0.30), n(w * 0.94), n(deck), ink, n(sw(w, 0.7))))
    return wrap(uid, w, h, "".join(out))


def a_seismic(w, h, uid):
    base = h * 0.58
    pts = [(0.00, 0.58), (0.12, 0.58), (0.18, 0.34), (0.24, 0.84), (0.30, 0.20),
           (0.37, 0.90), (0.44, 0.44), (0.50, 0.74), (0.57, 0.28), (0.63, 0.68),
           (0.70, 0.50), (0.78, 0.58), (1.00, 0.58)]
    line = " ".join("%s,%s" % (n(x * w), n(y * h)) for x, y in pts)
    out = [
        '<line x1="0" y1="%s" x2="%s" y2="%s" stroke="#cfc7b6" stroke-width="%s"/>'
        % (n(base), n(w), n(base), n(sw(w, 1.0))),
        '<polyline points="%s" fill="none" stroke="#8f2a1f" stroke-width="%s" '
        'stroke-linejoin="round"/>' % (line, n(sw(w, 1.6))),
    ]
    return wrap(uid, w, h, "".join(out))


def a_book(w, h, uid):
    ink = "#2b3446"
    out = [
        '<polygon points="%s,%s %s,%s %s,%s %s,%s" fill="#f7f3e8" stroke="%s" '
        'stroke-width="%s"/>'
        % (n(w * 0.08), n(h * 0.26), n(w * 0.49), n(h * 0.20),
           n(w * 0.49), n(h * 0.84), n(w * 0.08), n(h * 0.76), ink, n(sw(w, 0.9))),
        '<polygon points="%s,%s %s,%s %s,%s %s,%s" fill="#efe9dd" stroke="%s" '
        'stroke-width="%s"/>'
        % (n(w * 0.51), n(h * 0.20), n(w * 0.92), n(h * 0.26),
           n(w * 0.92), n(h * 0.76), n(w * 0.51), n(h * 0.84), ink, n(sw(w, 0.9))),
        '<line x1="%s" y1="%s" x2="%s" y2="%s" stroke="%s" stroke-width="%s"/>'
        % (n(w * 0.50), n(h * 0.19), n(w * 0.50), n(h * 0.85), ink, n(sw(w, 1.0))),
    ]
    for i, y in enumerate((0.38, 0.50, 0.62)):
        dy = y * h
        out.append('<line x1="%s" y1="%s" x2="%s" y2="%s" stroke="%s" stroke-width="%s"/>'
                   % (n(w * 0.16), n(dy + i * h * 0.01), n(w * 0.42),
                      n(dy + i * h * 0.01), "#7b7361", n(sw(w, 0.8))))
        out.append('<line x1="%s" y1="%s" x2="%s" y2="%s" stroke="%s" stroke-width="%s"/>'
                   % (n(w * 0.58), n(dy + i * h * 0.01), n(w * 0.84),
                      n(dy + i * h * 0.01), "#7b7361", n(sw(w, 0.8))))
    return wrap(uid, w, h, "".join(out))


def a_ballot(w, h, uid):
    ink = "#2b3446"
    out = [
        '<polygon points="%s,%s %s,%s %s,%s %s,%s" fill="#f7f3e8" stroke="%s" '
        'stroke-width="%s"/>'
        % (n(w * 0.30), n(h * 0.10), n(w * 0.66), n(h * 0.10),
           n(w * 0.60), n(h * 0.52), n(w * 0.24), n(h * 0.52), ink, n(sw(w, 0.9))),
        '<rect x="%s" y="%s" width="%s" height="%s" fill="#c9d2e4" stroke="%s" '
        'stroke-width="%s"/>'
        % (n(w * 0.14), n(h * 0.50), n(w * 0.72), n(h * 0.36), ink, n(sw(w, 1.0))),
        '<line x1="%s" y1="%s" x2="%s" y2="%s" stroke="%s" stroke-width="%s"/>'
        % (n(w * 0.38), n(h * 0.56), n(w * 0.62), n(h * 0.56), ink, n(sw(w, 1.4))),
        '<polyline points="%s,%s %s,%s %s,%s" fill="none" stroke="#157a4a" '
        'stroke-width="%s" stroke-linejoin="round"/>'
        % (n(w * 0.36), n(h * 0.32), n(w * 0.45), n(h * 0.41),
           n(w * 0.62), n(h * 0.20), n(sw(w, 1.8))),
    ]
    return wrap(uid, w, h, "".join(out))


def _bars(w, h, uid, up):
    ink = "#1d4e8f"
    base = h * 0.88
    out = ['<line x1="%s" y1="%s" x2="%s" y2="%s" stroke="#cfc7b6" stroke-width="%s"/>'
           % (n(w * 0.06), n(base), n(w * 0.94), n(base), n(sw(w, 1.0)))]
    count = 7
    span = w * 0.80 / count
    barw = span * 0.62
    for i in range(count):
        frac = 0.20 + 0.68 * (i + 1) / float(count) if up else 0.88 - 0.68 * (i + 1) / float(count)
        top = base - frac * h * 0.72
        x = w * 0.08 + i * span
        out.append('<rect x="%s" y="%s" width="%s" height="%s" fill="%s"/>'
                   % (n(x), n(top), n(barw), n(base - top), ink))
    if up:
        arrow = [(0.10, 0.80), (0.86, 0.22)]
    else:
        arrow = [(0.10, 0.26), (0.86, 0.78)]
    (x1, y1), (x2, y2) = arrow
    out.append('<line x1="%s" y1="%s" x2="%s" y2="%s" stroke="#b5202a" '
               'stroke-width="%s"/>'
               % (n(x1 * w), n(y1 * h), n(x2 * w), n(y2 * h), n(sw(w, 1.6))))
    out.append('<polyline points="%s,%s %s,%s %s,%s" fill="none" stroke="#b5202a" '
               'stroke-width="%s" stroke-linecap="round"/>'
               % (n(x2 * w - w * 0.09), n(y2 * h - h * 0.02 * (1 if up else -1)),
                  n(x2 * w), n(y2 * h),
                  n(x2 * w - w * 0.02), n(y2 * h + h * 0.12 * (1 if up else -1)),
                  n(sw(w, 1.6))))
    return wrap(uid, w, h, "".join(out))


def a_chart_up(w, h, uid):
    return _bars(w, h, uid, True)


def a_chart_down(w, h, uid):
    return _bars(w, h, uid, False)


def a_car(w, h, uid):
    ink = "#2b3446"
    out = [
        '<polygon points="%s,%s %s,%s %s,%s %s,%s %s,%s %s,%s" fill="#1d4e8f"/>'
        % (n(w * 0.06), n(h * 0.66), n(w * 0.17), n(h * 0.66),
           n(w * 0.28), n(h * 0.40), n(w * 0.70), n(h * 0.40),
           n(w * 0.86), n(h * 0.66), n(w * 0.94), n(h * 0.66)),
        '<rect x="%s" y="%s" width="%s" height="%s" fill="#2b3446"/>'
        % (n(w * 0.36), n(h * 0.20), n(w * 0.20), n(h * 0.12)),
        '<circle cx="%s" cy="%s" r="%s" fill="%s"/>'
        % (n(w * 0.28), n(h * 0.70), n(min(w, h) * 0.12), ink),
        '<circle cx="%s" cy="%s" r="%s" fill="%s"/>'
        % (n(w * 0.72), n(h * 0.70), n(min(w, h) * 0.12), ink),
        '<circle cx="%s" cy="%s" r="%s" fill="#cfc7b6"/>'
        % (n(w * 0.28), n(h * 0.70), n(min(w, h) * 0.05)),
        '<circle cx="%s" cy="%s" r="%s" fill="#cfc7b6"/>'
        % (n(w * 0.72), n(h * 0.70), n(min(w, h) * 0.05)),
    ]
    return wrap(uid, w, h, "".join(out))


def a_radar(w, h, uid):
    cx = w * 0.50
    cy = h * 0.50
    r = min(w, h) * 0.42
    ink = "#1d5468"
    out = [
        '<circle cx="%s" cy="%s" r="%s" fill="none" stroke="%s" stroke-width="%s"/>'
        % (n(cx), n(cy), n(r), ink, n(sw(w, 1.3))),
        '<circle cx="%s" cy="%s" r="%s" fill="none" stroke="%s" stroke-width="%s"/>'
        % (n(cx), n(cy), n(r * 0.66), ink, n(sw(w, 1.1))),
        '<circle cx="%s" cy="%s" r="%s" fill="none" stroke="%s" stroke-width="%s"/>'
        % (n(cx), n(cy), n(r * 0.33), ink, n(sw(w, 1.1))),
        '<polygon points="%s,%s %s,%s %s,%s" fill="#8f2a1f" opacity="0.35"/>'
        % (n(cx), n(cy), n(cx + r), n(cy - r * 0.55), n(cx + r * 0.55), n(cy + r * 0.55)),
        '<line x1="%s" y1="%s" x2="%s" y2="%s" stroke="%s" stroke-width="%s"/>'
        % (n(cx - r), n(cy), n(cx + r), n(cy), ink, n(sw(w, 0.7))),
        '<line x1="%s" y1="%s" x2="%s" y2="%s" stroke="%s" stroke-width="%s"/>'
        % (n(cx), n(cy - r), n(cx), n(cy + r), ink, n(sw(w, 0.7))),
        '<circle cx="%s" cy="%s" r="%s" fill="#b5202a"/>'
        % (n(cx + r * 0.34), n(cy - r * 0.40), n(max(1.8, min(w, h) * 0.055))),
    ]
    return wrap(uid, w, h, "".join(out))


def a_virus(w, h, uid):
    cx = w * 0.50
    cy = h * 0.50
    r = min(w, h) * 0.27
    ink = "#7a2f6b"
    spikes = []
    for i in range(12):
        ang = math.radians(i * 30.0)
        x1 = cx + math.cos(ang) * r
        y1 = cy + math.sin(ang) * r
        x2 = cx + math.cos(ang) * r * 1.62
        y2 = cy + math.sin(ang) * r * 1.62
        spikes.append("M %s %s L %s %s" % (n(x1), n(y1), n(x2), n(y2)))
    out = [
        '<path d="%s" stroke="%s" stroke-width="%s" stroke-linecap="round" fill="none"/>'
        % (" ".join(spikes), ink, n(sw(w, 1.2))),
        '<circle cx="%s" cy="%s" r="%s" fill="%s"/>' % (n(cx), n(cy), n(r), ink),
    ]
    for dx, dy in ((-0.38, -0.10), (0.30, -0.34), (0.12, 0.36)):
        out.append('<circle cx="%s" cy="%s" r="%s" fill="#f7f3e8"/>'
                   % (n(cx + dx * r), n(cy + dy * r), n(r * 0.19)))
    return wrap(uid, w, h, "".join(out))


ART = {
    "flags": a_flags,
    "drone": a_drone,
    "spiral": a_spiral,
    "coins": a_coins,
    "podium": a_podium,
    "podium_cn": a_podium,
    "bridge": a_bridge,
    "seismic": a_seismic,
    "book": a_book,
    "ballot": a_ballot,
    "chart_up": a_chart_up,
    "chart_down": a_chart_down,
    "car": a_car,
    "radar": a_radar,
    "virus": a_virus,
}


def art(name, w, h, uid):
    try:
        draw = ART[name]
    except KeyError:
        raise ValueError("no illustration named %r" % (name,))
    svg = draw(w, h, uid)
    # Every illustration sits on a flat tint panel so the artwork reads as a
    # picture, not as a line drawing on newsprint, at 46px and at thumbnail.
    opener = '<g clip-path="url(#%s)">' % uid
    panel = '<rect x="0" y="0" width="%d" height="%d" fill="%s"/>' % (
        w, h, TINT[name])
    return svg.replace(opener, opener + panel, 1)


# ---------------------------------------------------------------------- page

FEAT_ART_W = 317
FEAT_ART_H = 118
CARD_ART_W = 46
CARD_ART_H = 40


def card_region(tag):
    return resolve(tag)


def build():
    counts = region_counts()

    mast = [
        '<header class="mast">',
        '<div class="kicker">%s</div>' % esc(KICKER),
        '<div class="dateline">%s</div>' % esc(DATE_LINE),
        '<div class="mastrow">',
        '<div class="count">%d STORIES</div>' % TOTAL,
        '<div class="sub">%d LEADS &#183; %d CARDS &#183; %d BRIEFS</div>'
        % (len(FEATURES), len(CARDS), len(BRIEFS)),
        '</div>',
        '<div class="maststat">',
    ]
    stats = [
        (TOTAL, "STORIES"),
        (TOTAL, "PICTURES"),
        (len(REGIONS), "REGIONS"),
        (len(BRIEFS), "BRIEFS"),
    ]
    for value, label in stats:
        mast.append('<div class="mcell"><b>%d</b><span>%s</span></div>'
                    % (value, label))
    mast.extend(['</div>', '<div class="deck">'])
    for item in FEATURES:
        colour = COLOUR[resolve(item["region"])]
        mast.append('<div class="dcell"><i class="dot" style="background:%s"></i>%s</div>'
                    % (colour, esc(item["label"])))
    mast.extend(['</div>', '</header>'])

    key = ['<div class="key">']
    for name, colour in REGIONS:
        key.append('<span class="k"><i class="dot" style="background:%s"></i>%s %d</span>'
                   % (colour, name, counts[name]))
    key.append('</div>')

    feat = ['<section class="feat">']
    for i, item in enumerate(FEATURES):
        colour = COLOUR[resolve(item["region"])]
        feat.append('<article class="fcard">')
        feat.append('<div class="art">%s</div>'
                    % art(item["art"], FEAT_ART_W, FEAT_ART_H, "f%d" % (i + 1)))
        feat.append('<div class="flabel"><i class="dot" style="background:%s"></i>%s</div>'
                    % (colour, esc(item["label"])))
        feat.append('<div class="fh">%s</div>' % esc(item["headline"]))
        feat.append('<div class="fd">%s</div>' % esc(item["dek"]))
        feat.append('</article>')
    feat.append('</section>')

    cards = ['<section class="cards">']
    for i, (tag, headline, name) in enumerate(CARDS):
        colour = COLOUR[card_region(tag)]
        cards.append('<article class="ccard">')
        cards.append('<div class="art">%s</div>'
                     % art(name, CARD_ART_W, CARD_ART_H, "c%d" % (i + 1)))
        cards.append('<div class="ch"><b class="cn" style="background:%s">%d</b>%s</div>'
                     % (colour, i + 4, esc(headline)))
        cards.append('</article>')
    cards.append('</section>')

    briefs = ['<section class="briefs">']
    for tag, headline in BRIEFS:
        colour = COLOUR[resolve(tag)]
        briefs.append('<div class="b"><div class="bk"><i class="dot" '
                      'style="background:%s"></i><span class="tag">%s</span></div>'
                      '<span class="bt">%s</span></div>'
                      % (colour, esc(tag), esc(headline)))
    briefs.append('</section>')

    nums = ['<div class="num">']
    for value, caption in NUMBERS:
        nums.append('<div class="ncell"><b>%s</b><i>%s</i></div>'
                    % (esc(value), esc(caption)))
    nums.append('</div>')

    foot = ('<div class="foot">THE WORLD TODAY &#183; %s &#183; %d STORIES, '
            'ALL ILLUSTRATED</div>' % (esc(DATE_LINE.upper()), TOTAL))

    page = [
        '<!DOCTYPE html>',
        '<html lang="en">',
        '<head>',
        '<meta charset="utf-8">',
        '<title>The World Today - %s</title>' % esc(DATE_LINE),
        '<link rel="stylesheet" href="poster.css">',
        '</head>',
        '<body>',
        '<div class="sheet">',
    ]
    page.extend(mast)
    page.extend(key)
    page.extend(feat)
    page.extend(cards)
    page.extend(briefs)
    page.extend(nums)
    page.append(foot)
    page.extend(['</div>', '</body>', '</html>', ''])

    return "\n".join(page)


def main():
    counts = region_counts()
    print("counts " + "  ".join("%s %d" % (name, counts[name]) for name in NAMES))
    print("total %d" % TOTAL)
    (HERE / "poster.html").write_text(build(), encoding="utf-8")


if __name__ == "__main__":
    main()
