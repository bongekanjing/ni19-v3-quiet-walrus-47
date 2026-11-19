#!/usr/bin/env python3
"""Build build/poster.html: a 1024x1024 newspaper front page.

Data lives here; the page is written deterministically (no timestamps, no
randomness, no dict/set ordering). All artwork is inline SVG geometry.
"""

import html
import math
import pathlib

HERE = pathlib.Path(__file__).resolve().parent

DATELINE = "Thursday 19 November 2026"

DECK_ITEMS = [
    "Three presidents in Shenzhen",
    "A drone war in the Gulf",
    "200,000 flee a cyclone",
]

REGIONS = [
    ("AMERICAS", "#1d4e8f"),
    ("EUROPE", "#157a4a"),
    ("AFRICA", "#6b2d8e"),
    ("ASIA", "#1d5468"),
    ("MIDEAST", "#8f2a1f"),
    ("OCEANIA", "#2c3b4a"),
    ("WORLD", "#12203f"),
]

REGION_OF = {
    "UNITED STATES": "AMERICAS",
    "VENEZUELA": "AMERICAS",
    "MEXICO": "AMERICAS",
    "HAITI": "AMERICAS",
    "EUROPE": "EUROPE",
    "UNITED KINGDOM": "EUROPE",
    "UKRAINE": "EUROPE",
    "RUSSIA": "EUROPE",
    "AFRICA": "AFRICA",
    "IRAN": "MIDEAST",
    "KUWAIT": "MIDEAST",
    "YEMEN": "MIDEAST",
    "ENERGY": "MIDEAST",
    "SOUTH ASIA": "ASIA",
    "EAST ASIA": "ASIA",
    "SOUTHEAST ASIA": "ASIA",
    "PACIFIC": "OCEANIA",
    "MARKETS": "WORLD",
    "CLIMATE": "WORLD",
    "TECH": "WORLD",
}

BRIEFS = [
    ("UNITED STATES", "Peltola beats Sullivan in Alaska; Senate is 56-44"),
    ("UNITED STATES", "Fed minutes: almost all saw further rate rises"),
    ("UNITED STATES", "Fed puts AI at the centre of the inflation debate"),
    ("UNITED STATES", "Waymo pulls robotaxis off freeways after state ban"),
    ("VENEZUELA", "US and Venezuela restore military ties and intelligence"),
    ("MEXICO", "Sheinbaum reports a very good meeting with Trump on trade"),
    ("EUROPE", "Berlin and London reject US criticism of Kyiv deep strikes"),
    ("EUROPE", "Magnitude 5.7 quake shakes Romania; two injured"),
    ("EUROPE", "Britain and EU near a reset deal, due Friday"),
    ("UNITED KINGDOM", "Cambridge names Human its word of the year, citing AI"),
    ("UNITED KINGDOM", "London sanctions settler leader Daniella Weiss"),
    ("UKRAINE", "Crimean Bridge struck again; traffic halted on the span"),
    ("RUSSIA", "Putin expects big potential benefits from the talks"),
    ("IRAN", "Iran says drones hit Patriot batteries at Ali Al-Salem"),
    ("IRAN", "Army chief vows a more crushing reply to any US attack"),
    ("KUWAIT", "Kuwait army says air defences engaged hostile drones"),
    ("YEMEN", "Houthis blame Saudi-led strikes for three deaths"),
    ("ENERGY", "Three tankers burn after hitting mines off Hormuz"),
    ("AFRICA", "WHO: DR Congo Ebola outbreak out of control at six months"),
    ("AFRICA", "Confirmed Ebola cases pass 11,000; deaths above 5,300"),
    ("AFRICA", "South Africa summons Nigeria's envoy over online remarks"),
    ("SOUTH ASIA", "Cyclone Akvan due to hit Andhra coast around noon Friday"),
    ("SOUTH ASIA", "Akvan to bring 120-130 km/h winds, gusting to 145"),
    ("SOUTH ASIA", "India bowl first; New Zealand 60-4 at lunch in Wellington"),
    ("EAST ASIA", "Beijing gives Japan's Takaichi a low-key welcome"),
    ("EAST ASIA", "South Korea offers $75,000 per case of exam cheating"),
    ("SOUTHEAST ASIA", "Arsenic in Mae Sai water 30 times the safe limit"),
    ("SOUTHEAST ASIA", "Bank Indonesia lifts its rate to 6% as rupiah slides"),
    ("PACIFIC", "Fiji declares a national disaster as El Nino drought bites"),
    ("PACIFIC", "Tuvalu seeks $160m for Pacific early-warning systems"),
    ("MARKETS", "S&P 500 falls 1.03% to 7,340 as rate worries bite"),
    ("MARKETS", "Gold drops 2% to about $3,787, a one-year low"),
    ("CLIMATE", "COP31 draft urges an immediate shift off fossil fuels"),
    ("HAITI", "Thousands march in Port-au-Prince for Salvadoran troops"),
    ("TECH", "Nvidia shares rise about 5% after hours on the results"),
]

LEADS = [
    {
        "region": "ASIA",
        "label": "1 - SHENZHEN - SUMMIT",
        "headline": "Trump, Xi and Putin hold first three-way summit",
        "deck": (
            "The three meet at APEC in Shenzhen on Thursday; Iran, Ukraine and "
            "arms control top the agenda, and expectations of a deal are low."
        ),
        "art": "bars",
    },
    {
        "region": "MIDEAST",
        "label": "2 - GULF - KUWAIT",
        "headline": "Iran says its drones struck a US air base in Kuwait",
        "deck": (
            "Tehran said the attack hit Patriot batteries at Ali Al-Salem, in "
            "retaliation for a US strike on Qeshm Island; Central Command said "
            "no American personnel were wounded."
        ),
        "art": "gulf",
    },
    {
        "region": "EUROPE",
        "label": "3 - UKRAINE - WAR",
        "headline": "Zelenskyy: one three-way meeting could end the war",
        "deck": (
            "He said the war could end if the leaders wanted it; the EU proposed "
            "a 45bn euro loan for Ukraine's 2027 budget gap, and the Crimean "
            "Bridge was struck again."
        ),
        "art": "market",
    },
]

NUMBERS = [
    ("\u20ac45bn", "EU loan proposed for Ukraine's 2027 budget"),
    ("11,000+", "confirmed Ebola cases in DR Congo"),
    ("5,300+", "deaths in the same outbreak"),
    ("$115.8bn", "Nvidia quarterly revenue, double a year earlier"),
    ("56-44", "Democratic majority in the US Senate"),
    ("145", "km/h gusts as Cyclone Akvan nears Andhra"),
]


def e(text):
    """Escape a story string for HTML text content."""
    return html.escape(str(text), quote=True)


# --------------------------------------------------------------- artwork


def star_points(cx, cy, r):
    """Ten alternating radii for a five-point star."""
    pts = []
    for i in range(10):
        radius = r if i % 2 == 0 else r * 0.382
        angle = -math.pi / 2 + i * math.pi / 5
        pts.append(
            "{:.2f},{:.2f}".format(
                cx + radius * math.cos(angle), cy + radius * math.sin(angle)
            )
        )
    return " ".join(pts)


def roundel_us(cx, cy, r):
    stripes = "".join(
        '<rect x="{:.2f}" y="{:.2f}" width="{:.2f}" height="1.3" fill="#b5202a"/>'.format(
            cx - r, cy - r + i * 1.9, 2 * r
        )
        for i in range(8)
    )
    return (
        "<g>"
        '<clipPath id="c_us"><circle cx="{cx:.2f}" cy="{cy:.2f}" r="{r:.2f}"/></clipPath>'
        '<circle cx="{cx:.2f}" cy="{cy:.2f}" r="{r:.2f}" fill="#fbfbf8"/>'
        '<g clip-path="url(#c_us)">'
        + stripes
        + '<rect x="{cx0:.2f}" y="{cy0:.2f}" width="{cw:.2f}" height="{ch:.2f}" fill="#1b2f5e"/>'
        '<circle cx="{d1x:.2f}" cy="{d1y:.2f}" r="0.55" fill="#fbfbf8"/>'
        '<circle cx="{d2x:.2f}" cy="{d2y:.2f}" r="0.55" fill="#fbfbf8"/>'
        '<circle cx="{d3x:.2f}" cy="{d3y:.2f}" r="0.55" fill="#fbfbf8"/>'
        "</g>"
        '<circle cx="{cx:.2f}" cy="{cy:.2f}" r="{r:.2f}" fill="none" '
        'stroke="#8e939c" stroke-width="0.8"/>'
        "</g>"
    ).format(
        cx=cx,
        cy=cy,
        r=r,
        cx0=cx - r,
        cy0=cy - r,
        cw=r * 0.95,
        ch=r * 0.95,
        d1x=cx - r * 0.62,
        d1y=cy - r * 0.66,
        d2x=cx - r * 0.28,
        d2y=cy - r * 0.34,
        d3x=cx - r * 0.66,
        d3y=cy - r * 0.16,
    )


def roundel_cn(cx, cy, r):
    return (
        '<g><circle cx="{cx:.2f}" cy="{cy:.2f}" r="{r:.2f}" fill="#d8231f"/>'
        '<polygon points="{star}" fill="#ffd83d"/>'
        '<circle cx="{cx:.2f}" cy="{cy:.2f}" r="{r:.2f}" fill="none" '
        'stroke="#8e939c" stroke-width="0.8"/></g>'
    ).format(cx=cx, cy=cy, r=r, star=star_points(cx + 0.7, cy + 0.5, r * 0.66))


def roundel_ru(cx, cy, r):
    band = 2 * r / 3.0
    return (
        "<g>"
        '<clipPath id="c_ru"><circle cx="{cx:.2f}" cy="{cy:.2f}" r="{r:.2f}"/></clipPath>'
        '<g clip-path="url(#c_ru)">'
        '<rect x="{x:.2f}" y="{y0:.2f}" width="{w:.2f}" height="{band:.2f}" fill="#f4f4f2"/>'
        '<rect x="{x:.2f}" y="{y1:.2f}" width="{w:.2f}" height="{band:.2f}" fill="#24408e"/>'
        '<rect x="{x:.2f}" y="{y1:.2f}" width="{w:.2f}" height="{band:.2f}" fill="#24408e"/>'
        '<rect x="{x:.2f}" y="{y2:.2f}" width="{w:.2f}" height="{band:.2f}" fill="#d52b1e"/>'
        "</g>"
        '<circle cx="{cx:.2f}" cy="{cy:.2f}" r="{r:.2f}" fill="none" '
        'stroke="#8e939c" stroke-width="0.8"/>'
        "</g>"
    ).format(
        cx=cx,
        cy=cy,
        r=r,
        x=cx - r,
        w=2 * r,
        band=band,
        y0=cy - r,
        y1=cy - r / 3.0,
        y2=cy + r / 3.0,
    )


SVG_OPEN = (
    '<svg viewBox="0 0 290 140" preserveAspectRatio="none" '
    'xmlns="http://www.w3.org/2000/svg">'
)


def art_bars():
    """Pale panel, grey zero line, six rising blue bars, three flag roundels."""
    base = 122.0
    heights = [26, 44, 38, 60, 54, 74]
    bw = 27.0
    step = 34.0
    x0 = (290.0 - (len(heights) * step - (step - bw))) / 2.0

    parts = ['<rect x="0" y="0" width="290" height="140" fill="#eef1f6"/>']
    for gy in (48, 78, 104):
        parts.append(
            '<line x1="0" y1="{:.1f}" x2="290" y2="{:.1f}" '
            'stroke="#dce2eb" stroke-width="0.9"/>'.format(gy, gy)
        )
    parts.append(
        '<line x1="6" y1="{:.1f}" x2="284" y2="{:.1f}" '
        'stroke="#98a2b0" stroke-width="1.1"/>'.format(base, base)
    )
    for i, hh in enumerate(heights):
        bx = x0 + i * step
        parts.append(
            '<rect x="{:.2f}" y="{:.2f}" width="{:.2f}" height="{:.2f}" '
            'fill="#41648c"/>'.format(bx, base - hh, bw, hh)
        )
    # roundels above the three tallest bars: US, China, Russia
    for idx, fn in ((3, roundel_us), (4, roundel_cn), (5, roundel_ru)):
        cx = x0 + idx * step + bw / 2.0
        cy = max(14.0, base - heights[idx] - 14.0)
        parts.append(fn(cx, cy, 9.0))
    return SVG_OPEN + "".join(parts) + "</svg>"


def art_gulf():
    """Dusk gradient sky, amber sun, dark skyline silhouette, ground bar."""
    parts = [
        "<defs>"
        '<linearGradient id="gulfsky" x1="0" y1="0" x2="0" y2="1">'
        '<stop offset="0" stop-color="#3b1d52"/>'
        '<stop offset="0.55" stop-color="#7b3a72"/>'
        '<stop offset="1" stop-color="#c2628a"/>'
        "</linearGradient>"
        "</defs>",
        '<rect x="0" y="0" width="290" height="140" fill="url(#gulfsky)"/>',
        '<circle cx="196" cy="54" r="33" fill="#f0a84e" opacity="0.15"/>',
        '<circle cx="196" cy="54" r="25" fill="#f0a84e"/>',
    ]
    towers = [
        (4, 80, 26, 46),
        (36, 92, 20, 34),
        (60, 64, 22, 62),
        (88, 86, 26, 40),
        (118, 56, 20, 70),
        (144, 84, 22, 42),
        (172, 72, 28, 54),
        (226, 90, 24, 36),
        (256, 96, 22, 30),
    ]
    body = []
    for tx, ty, tw, th in towers:
        body.append(
            '<rect x="{}" y="{}" width="{}" height="{}" fill="#22112e"/>'.format(
                tx, ty, tw, th
            )
        )
        wy = ty + 6
        while wy < ty + th - 5:
            wx = tx + 4
            while wx < tx + tw - 4:
                body.append(
                    '<rect x="{:.1f}" y="{:.1f}" width="2.2" height="2.4" '
                    'fill="#f0a84e" opacity="0.5"/>'.format(wx, wy)
                )
                wx += 7
            wy += 9
    parts.append("".join(body))
    parts.append('<rect x="0" y="124" width="290" height="16" fill="#180c22"/>')
    parts.append(
        '<line x1="0" y1="124" x2="290" y2="124" stroke="#0e0615" stroke-width="1.5"/>'
    )
    return SVG_OPEN + "".join(parts) + "</svg>"


def art_market():
    """Dark trading panel: ANT / NASDAQ, baseline, rising candles, price box."""
    parts = ['<rect x="0" y="0" width="290" height="140" fill="#123238"/>']
    parts.append(
        '<text x="10" y="26" font-family="Liberation Mono, monospace" font-size="12" '
        'font-weight="bold" letter-spacing="2" fill="#ffffff">ANT</text>'
    )
    parts.append(
        '<text x="10" y="40" font-family="Liberation Mono, monospace" font-size="6.4" '
        'letter-spacing="0.7" fill="#f0a84e">NASDAQ - FIRST TRADING DAY</text>'
    )
    base = 124.0
    parts.append(
        '<line x1="10" y1="{:.1f}" x2="280" y2="{:.1f}" stroke="#3f9b6d" '
        'stroke-width="1.1" opacity="0.9"/>'.format(base, base)
    )
    heights = [8, 12, 10, 17, 15, 23, 27, 34, 42, 51, 60]
    cw = 9.0
    step = 17.5
    x = 12.0
    up = True
    for i, hh in enumerate(heights):
        colour = "#3f9b6d" if up else "#8f3b3b"
        top = base - hh
        parts.append(
            '<line x1="{:.1f}" y1="{:.1f}" x2="{:.1f}" y2="{:.1f}" '
            'stroke="{}" stroke-width="1"/>'.format(
                x + cw / 2, top - 3, x + cw / 2, top + hh + 2, colour
            )
        )
        parts.append(
            '<rect x="{:.1f}" y="{:.1f}" width="{:.1f}" height="{:.1f}" fill="{}"/>'.format(
                x, top, cw, hh, colour
            )
        )
        up = not up
        x += step
    parts.append(
        '<rect x="214" y="66" width="64" height="28" fill="#ffffff" rx="1.5"/>'
        '<text x="246" y="85" text-anchor="middle" '
        'font-family="Liberation Mono, monospace" font-size="13" '
        'font-weight="bold" fill="#123238">$83</text>'
    )
    return SVG_OPEN + "".join(parts) + "</svg>"


ARTS = {"bars": art_bars, "gulf": art_gulf, "market": art_market}


# --------------------------------------------------------------- counting


def region_for(tag):
    if tag not in REGION_OF:
        raise SystemExit("unmapped brief tag: {!r}".format(tag))
    return REGION_OF[tag]


def tally():
    """Count stories per region from what is actually printed."""
    counts = {name: 0 for name, _colour in REGIONS}
    names = set(counts)
    for lead in LEADS:
        # leads declare their region directly, not a brief tag
        if lead["region"] not in names:
            raise SystemExit("unmapped lead region: {!r}".format(lead["region"]))
        counts[lead["region"]] += 1
    for tag, _headline in BRIEFS:
        counts[region_for(tag)] += 1
    total = len(LEADS) + len(BRIEFS)
    if sum(counts.values()) != total:
        raise SystemExit(
            "region sum {} does not equal story count {}".format(
                sum(counts.values()), total
            )
        )
    for name, _colour in REGIONS:
        if counts[name] == 0:
            raise SystemExit("region {} has no stories".format(name))
    return counts, total


# ------------------------------------------------------------------ page


def main():
    counts, total = tally()

    ears = (
        '<div class="ears">'
        '<div class="ear-left">THE WORLD TODAY</div>'
        '<div class="ear-right">{}</div>'
        "</div>".format(e("THURSDAY'S NEWS - ONE PAGE - {} STORIES".format(total)))
    )

    deck = '<div class="deck">{}</div>'.format(
        " &middot; ".join(e(item) for item in DECK_ITEMS)
    )

    tabs = "".join(
        '<div class="tab" style="background:{colour}">'
        '<div class="tab-name">{name}</div>'
        '<div class="tab-count">{count}</div>'
        "</div>".format(colour=colour, name=e(name), count=counts[name])
        for name, colour in REGIONS
    )

    numbers = "".join(
        '<div class="num"><div class="num-fig">{fig}</div>'
        '<div class="num-cap">{cap}</div></div>'.format(fig=e(fig), cap=e(cap))
        for fig, cap in NUMBERS
    )

    cards = "".join(
        '<div class="card">'
        "{svg}"
        '<div class="card-label">{label}</div>'
        '<h2 class="card-h">{head}</h2>'
        '<p class="card-deck">{deck}</p>'
        "</div>".format(
            svg=ARTS[lead["art"]](),
            label=e(lead["label"]),
            head=e(lead["headline"]),
            deck=e(lead["deck"]),
        )
        for lead in LEADS
    )

    briefs = "".join(
        '<div class="brief"><div class="brief-tag">{tag}</div>'
        '<div class="brief-h">{head}</div></div>'.format(tag=e(tag), head=e(head))
        for tag, head in BRIEFS
    )

    footer = '<div class="footer">{}</div>'.format(
        e(
            "SOURCES: AP, REUTERS, BBC, FINANCIAL TIMES, THE HINDU - "
            "{} STORIES FROM SIX CONTINENTS".format(total)
        )
    )

    doc = (
        "<!DOCTYPE html>\n"
        '<html lang="en">\n'
        "<head>\n"
        '<meta charset="utf-8">\n'
        "<title>The World Today - {dateline}</title>\n"
        '<link rel="stylesheet" href="poster.css">\n'
        "</head>\n"
        "<body>\n"
        '<div class="sheet">\n'
        "{ears}\n"
        '<div class="rule"></div>\n'
        '<h1 class="dateline">{dateline}</h1>\n'
        "{deck}\n"
        '<div class="tabs">{tabs}</div>\n'
        '<div class="numbers">{numbers}</div>\n'
        '<div class="leads">{cards}</div>\n'
        '<div class="briefs">{briefs}</div>\n'
        "{footer}\n"
        "</div>\n"
        "</body>\n"
        "</html>\n"
    ).format(
        dateline=e(DATELINE),
        ears=ears,
        deck=deck,
        tabs=tabs,
        numbers=numbers,
        cards=cards,
        briefs=briefs,
        footer=footer,
    )

    out = HERE / "poster.html"
    out.write_text(doc, encoding="utf-8")

    print("poster.html: {} stories; region sum {}".format(total, sum(counts.values())))


if __name__ == "__main__":
    main()
