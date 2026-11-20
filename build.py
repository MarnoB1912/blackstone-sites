#!/usr/bin/env python3
"""Generate one preview site per prospect from prospects/*.json into site/<slug>/index.html."""
import json, html, pathlib, urllib.parse, re

ROOT = pathlib.Path(__file__).parent
OUT = ROOT / "site"
TEMPLATE = (ROOT / "template.html").read_text()
BOOKING = (ROOT / "booking.html").read_text()
PRICE = "R2,500"
U = "https://images.unsplash.com/photo-"
Q = "?auto=format&fit=crop&q=70"
STOCK = {
    "mechanic": [U + "1625047509248-ec889cbff17f" + Q, U + "1615906655593-ad0386982a0f" + Q, U + "1530124566582-a618bc2615dc" + Q, U + "1552656967-7a0991a13906" + Q],
    "electrical": [U + "1615906655593-ad0386982a0f" + Q, U + "1625047509248-ec889cbff17f" + Q, U + "1527383418406-f85a3b146499" + Q, U + "1530124566582-a618bc2615dc" + Q],
    "plumbing": [U + "1676210134188-4c05dd172f89" + Q, U + "1676210134190-3f2c0d5cf58d" + Q, U + "1542013936693-884638332954" + Q, U + "1530124566582-a618bc2615dc" + Q],
}

P = '<svg class="i" viewBox="0 0 24 24">{}</svg>'
ICONS = {
    "wrench": '<path d="M14.7 6.3a4 4 0 0 0-5.4 5.2L3 17.8V21h3.2l6.3-6.3a4 4 0 0 0 5.2-5.4l-2.6 2.6-2.4-.6-.6-2.4z"/>',
    "bolt": '<path d="M13 2 4 14h7l-1 8 9-12h-7z"/>',
    "snow": '<path d="M12 2v20M4.9 4.9l14.2 14.2M2 12h20M4.9 19.1 19.1 4.9"/>',
    "battery": '<rect x="2" y="7" width="18" height="12" rx="2"/><path d="M22 11v4M7 13h4M9 11v4M14 13h3"/>',
    "car": '<path d="M5 17h14M3 13l2-6h14l2 6v4H3z"/><circle cx="7" cy="17" r="2"/><circle cx="17" cy="17" r="2"/>',
    "drop": '<path d="M12 2s7 7.5 7 12a7 7 0 0 1-14 0c0-4.5 7-12 7-12z"/>',
    "fire": '<path d="M12 22a7 7 0 0 0 7-7c0-4-3-6-4-10-2 2-3 4-3 6-1-1-2-2-2-4-2 2-5 5-5 8a7 7 0 0 0 7 7z"/>',
    "truck": '<path d="M1 6h13v10H1zM14 10h4l3 3v3h-7"/><circle cx="5" cy="18" r="2"/><circle cx="17" cy="18" r="2"/>',
    "gauge": '<path d="M12 14l4-4M3.3 17a10 10 0 1 1 17.4 0"/><circle cx="12" cy="14" r="1"/>',
    "shield": '<path d="M12 2l8 4v6c0 5-3.5 8.5-8 10-4.5-1.5-8-5-8-10V6z"/><path d="m9 12 2 2 4-4"/>',
    "clock": '<circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/>',
    "tool": '<path d="M3 21l6-6M14 4l6 6-9 9-6-6z"/>',
    "paint": '<path d="M19 11H5V3h14zM12 11v4M10 15h4v6h-4z"/>',
    "calendar": '<rect x="3" y="4" width="18" height="18" rx="2"/><path d="M16 2v4M8 2v4M3 10h18"/>',
    "phone": '<path d="M22 16.9v3a2 2 0 0 1-2.2 2 19.8 19.8 0 0 1-8.6-3.1 19.5 19.5 0 0 1-6-6A19.8 19.8 0 0 1 2.1 4.2 2 2 0 0 1 4.1 2h3a2 2 0 0 1 2 1.7c.1 1 .4 1.9.7 2.8a2 2 0 0 1-.5 2.1L8 9.9a16 16 0 0 0 6 6l1.3-1.3a2 2 0 0 1 2.1-.4c.9.3 1.8.6 2.8.7a2 2 0 0 1 1.7 2z"/>',
    "pin": '<path d="M21 10c0 7-9 13-9 13S3 17 3 10a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/>',
    "map": '<path d="M1 6v16l7-4 8 4 7-4V2l-7 4-8-4z"/><path d="M8 2v16M16 6v16"/>',
    "star": '<path d="m12 2 3.1 6.3 6.9 1-5 4.9 1.2 6.8L12 17.8 5.8 21l1.2-6.8-5-4.9 6.9-1z"/>',
    "chat": '<path d="M21 11.5a8.4 8.4 0 0 1-12.4 7.4L3 21l2.1-5.6A8.4 8.4 0 1 1 21 11.5z"/>',
}
EMOJI = {"⚡": "bolt", "❄️": "snow", "🔋": "battery", "💡": "bolt", "🔧": "wrench", "🖥️": "gauge", "🛑": "shield", "🚐": "truck",
         "⚙️": "tool", "🚗": "car", "🆘": "phone", "🚿": "drop", "🔥": "fire", "🌀": "drop", "🛠️": "tool", "🎨": "paint", "📋": "calendar",
         "🧰": "tool", "📅": "calendar", "🚚": "truck", "🛞": "car"}
WA_SVG = '<svg viewBox="0 0 24 24"><path d="M17.5 14.4c-.3-.1-1.8-.9-2-1-.3-.1-.5-.1-.7.1-.2.3-.8 1-.9 1.2-.2.2-.3.2-.6.1-.3-.1-1.3-.5-2.4-1.5-.9-.8-1.5-1.8-1.7-2.1-.2-.3 0-.5.1-.6l.4-.5c.2-.2.2-.3.3-.5.1-.2 0-.4 0-.5l-.9-2.2c-.2-.6-.5-.5-.7-.5h-.6c-.2 0-.5.1-.8.4-.3.3-1 1-1 2.5s1.1 2.9 1.2 3.1c.1.2 2.1 3.2 5.1 4.5.7.3 1.3.5 1.7.6.7.2 1.4.2 1.9.1.6-.1 1.8-.7 2-1.4.2-.7.2-1.3.2-1.4-.1-.1-.3-.2-.6-.3zM12 21.8c-1.8 0-3.5-.5-5-1.4l-.4-.2-3.7 1 1-3.6-.2-.4A9.8 9.8 0 1 1 12 21.8zm0-21.6A11.8 11.8 0 0 0 1.9 18L.2 24l6.2-1.6A11.8 11.8 0 1 0 12 .2z"/></svg>'


def ic(k):
    return P.format(ICONS.get(k, ICONS["wrench"]))


def e(s):
    return html.escape(str(s or ""), quote=True)


def wa_link(phone, text):
    d = "".join(c for c in phone if c.isdigit())
    if d.startswith("0"):
        d = "27" + d[1:]
    return f"https://wa.me/{d}?text={urllib.parse.quote(text)}"


def initials(name):
    words = [w for w in re.split(r"[\s'’&-]+", name) if w and w[0].isalnum()]
    return "".join(w[0] for w in words[:2]).upper()


def sized(url, w):
    return url + f"&w={w}" if "unsplash" in url else url


def render(p):
    kind = p.get("kind") or ("plumbing" if "plumb" in p["slug"] else "electrical" if ("electric" in p["slug"] or "cool" in p["slug"]) else "mechanic")
    photos = (p.get("photos") or []) + STOCK[kind]
    hero, ph2, ph3, ph4 = photos[0], photos[1], photos[2], photos[3]
    services = "".join(
        f'<div class="card"><div class="ic">{ic(EMOJI.get(s.get("icon",""), s.get("icon","wrench")))}</div><h3>{e(s["name"])}</h3><p>{e(s.get("desc",""))}</p></div>'
        for s in p["services"])
    reviews = "".join(
        f'<figure class="review"><div class="stars">{"★"*int(r.get("stars",5))}</div><blockquote>“{e(r["text"])}”</blockquote>'
        f'<div class="who"><div class="av">{e(r["name"][0])}</div><div><b>{e(r["name"])}</b><small>Google review</small></div></div></figure>'
        for r in p.get("reviews", []))
    hours = "".join(f"<li><span>{e(d)}</span><span>{e(h)}</span></li>" for d, h in p.get("hours", []))
    areas = p.get("areas", [])
    phone = p.get("phone", "")
    wa = wa_link(phone, f'Hi {p["name"]}, I found you online and would like a quote.')
    rating, count = p.get("rating"), p.get("review_count")
    proof = ""
    if rating:
        proof += f'<span><span class="stars">★★★★★</span> {e(rating)} on Google</span><span>{ic("chat")} {e(count)} reviews</span>'
    proof += f'<span>{ic("shield")} Workmanship you can trust</span>'
    strip = [("star", f"{rating}/5" if rating else "Trusted", f"from {count} Google reviews" if count else "by local customers"),
             ("pin", p.get("town", "").split(",")[0], "local and owner-run"),
             ("chat", "WhatsApp", "quick replies and quotes"),
             ("clock", p["hours"][0][1] if p.get("hours") else "Call today", p["hours"][0][0] if p.get("hours") else "for an appointment")]
    strip_html = "".join(f"<div>{ic(i)}<span><b>{e(a)}</b><small>{e(b)}</small></span></div>" for i, a, b in strip)
    gscore = (f'<div class="gscore"><b>{e(rating)}</b><div><div class="stars">★★★★★</div><small>{e(count)} reviews on Google</small></div></div>' if rating else "")
    badge = (f'{ic("star")}<div><b>{e(rating)}</b><small>{e(count)} Google reviews</small></div>' if rating else f'{ic("shield")}<div><b>Local</b><small>owner-run</small></div>')
    tag = p["tagline"]
    words = tag.split()
    tag_html = e(" ".join(words[:-2])) + " <em>" + e(" ".join(words[-2:])) + "</em>" if len(words) > 3 else e(tag)
    logo = p.get("logo")
    mark = f'<img src="{e(logo)}" alt="{e(p["name"])} logo" style="height:44px;width:auto;max-width:140px;border-radius:8px;object-fit:contain;background:#fff">' if logo else f'<span class="mark">{e(initials(p["name"]))}</span>'
    subs = {
        "NAME": e(p["name"]), "TAGLINE": e(tag), "TAGLINE_HTML": tag_html, "INTRO": e(p["intro"]),
        "TOWN": e(p.get("town", "").split(",")[0]), "AREAS": e(", ".join(areas)), "AREAS_SHORT": e(", ".join(areas[1:3]) if len(areas) > 2 else ", ".join(areas)),
        "PHONE": e(phone), "TEL": e("".join(c for c in phone if c.isdigit())), "WA": e(wa),
        "SERVICES": services, "SERVICES_TITLE": e(p.get("services_title") or "Services we offer"),
        "REVIEWS": reviews, "REVIEWS_STYLE": "" if reviews else "display:none", "GSCORE": gscore, "BADGE": badge,
        "HOURS": hours, "HOURS_STYLE": "" if hours else "display:none", "ADDRESS": e(p.get("address", "")),
        "MAP_Q": urllib.parse.quote(p.get("map_query") or p["name"]), "ACCENT": e(p.get("accent", "#0f766e")), "ACCENT_INK": e(p.get("accent_ink", "#fff")), "EM_FILTER": "none" if p.get("accent_ink") else "brightness(1.35) saturate(1.2)",
        "HERO_1800": e(sized(hero, 1800)), "HERO_1000": e(sized(hero, 1000)), "HERO_1200": e(sized(hero, 1200)),
        "PHOTO2": e(sized(ph2, 1100)), "PHOTO3": e(sized(ph3, 600)), "PHOTO4": e(sized(ph4, 600)),
        "PROOF": proof, "STRIP": strip_html, "SLUG": e(p["slug"]), "PRICE": PRICE, "YEAR": "2026", "MARK": mark,
        "FORM_HINT": e(p.get("form_hint") or "What's the problem? Vehicle make and model?"),
        "I_PHONE": ic("phone"), "I_WA": ic("chat"), "I_PIN": ic("pin"), "I_CLOCK": ic("clock"), "I_MAP": ic("map"), "WA_SVG": WA_SVG,
    }
    bk = p.get("booking", {})
    bk_html = BOOKING
    bsubs = {"BK_SERVICES": "".join(f'<button type="button" class="chip">{e(s["name"])}</button>' for s in p["services"]) + '<button type="button" class="chip">Something else</button>',
             "BK_PHONE": wa.split("wa.me/")[1].split("?")[0], "BK_NAME_JS": p["name"].replace('"', "").replace("\\", ""),
             "BK_DAYS": json.dumps(bk.get("days", [1, 2, 3, 4, 5])), "BK_OPEN": bk.get("open", "08:00"), "BK_CLOSE": bk.get("close", "17:00"),
             "BK_STEP": str(bk.get("step", 60)), "BK_EXTRA": e(p.get("form_hint") or "Vehicle make and model? Anything we should know?")}
    for k, v in bsubs.items():
        bk_html = bk_html.replace("{{" + k + "}}", v)
    out = TEMPLATE.replace('<section id="find">', bk_html + '\n<section id="find">', 1).replace('<a class="l" href="#find">Contact</a>', '<a class="l" href="#book">Book online</a><a class="l" href="#find">Contact</a>')
    for k, v in subs.items():
        out = out.replace("{{" + k + "}}", v)
    left = re.findall(r"{{\w+}}", out)
    assert not left, left
    return out


def main():
    OUT.mkdir(exist_ok=True)
    built, names = [], {}
    for f in sorted((ROOT / "prospects").glob("*.json")):
        p = json.loads(f.read_text())
        if p.get("skip"):
            continue
        if p.get("custom"):
            names[p["slug"]] = p["name"]
            continue
        d = OUT / p["slug"]
        d.mkdir(parents=True, exist_ok=True)
        (d / "index.html").write_text(render(p))
        built.append(p["slug"])
        names[p["slug"]] = p["name"]
    (OUT / "claim" / "names.js").write_text("window.NAMES=" + json.dumps(names) + ";")
    print("built:", len(built), ", ".join(built))


if __name__ == "__main__":
    main()
