#!/usr/bin/env python3
"""Generate one preview site per prospect from prospects/*.json into site/<slug>/index.html."""
import json, html, pathlib, urllib.parse

ROOT = pathlib.Path(__file__).parent
OUT = ROOT / "site"
TEMPLATE = (ROOT / "template.html").read_text()
PRICE = "R2,500"


def e(s):
    return html.escape(str(s or ""), quote=True)


def wa_link(phone, text):
    digits = "".join(c for c in phone if c.isdigit())
    if digits.startswith("0"):
        digits = "27" + digits[1:]
    return f"https://wa.me/{digits}?text={urllib.parse.quote(text)}"


def render(p):
    services = "".join(
        f'<div class="card"><div class="icon">{e(s.get("icon","✓"))}</div><h3>{e(s["name"])}</h3><p>{e(s.get("desc",""))}</p></div>'
        for s in p["services"]
    )
    reviews = "".join(
        f'<figure class="review"><div class="stars">{"★"*int(r.get("stars",5))}</div><blockquote>{e(r["text"])}</blockquote><figcaption>— {e(r["name"])}</figcaption></figure>'
        for r in p.get("reviews", [])
    )
    hours = "".join(f"<li><span>{e(d)}</span><span>{e(h)}</span></li>" for d, h in p.get("hours", []))
    areas = ", ".join(p.get("areas", []))
    map_q = urllib.parse.quote(p.get("map_query") or f'{p["name"]} {p.get("town","")}')
    phone = p.get("phone", "")
    wa = wa_link(phone, f'Hi {p["name"]}, I found you online and would like a quote.') if phone else "#contact"
    rating = p.get("rating")
    rating_html = (
        f'<div class="rating"><b>{e(rating)}★</b> from {e(p.get("review_count",""))} Google reviews</div>' if rating else ""
    )
    subs = {
        "NAME": e(p["name"]),
        "TAGLINE": e(p["tagline"]),
        "INTRO": e(p["intro"]),
        "TOWN": e(p.get("town", "")),
        "AREAS": e(areas),
        "PHONE": e(phone),
        "TEL": e("".join(c for c in phone if c.isdigit() or c == "+")),
        "WA": e(wa),
        "SERVICES": services,
        "REVIEWS": reviews,
        "REVIEWS_STYLE": "" if reviews else "display:none",
        "HOURS": hours,
        "HOURS_STYLE": "" if hours else "display:none",
        "ADDRESS": e(p.get("address", "")),
        "MAP_Q": map_q,
        "ACCENT": e(p.get("accent", "#0f766e")),
        "HERO_IMG": e(p.get("hero_img", "")),
        "RATING": rating_html,
        "SLUG": e(p["slug"]),
        "PRICE": PRICE,
        "YEAR": "2026",
    }
    out = TEMPLATE
    for k, v in subs.items():
        out = out.replace("{{" + k + "}}", v)
    return out


def main():
    OUT.mkdir(exist_ok=True)
    built = []
    for f in sorted((ROOT / "prospects").glob("*.json")):
        p = json.loads(f.read_text())
        d = OUT / p["slug"]
        d.mkdir(parents=True, exist_ok=True)
        (d / "index.html").write_text(render(p))
        built.append(p["slug"])
    names={json.loads(f.read_text())["slug"]:json.loads(f.read_text())["name"] for f in (ROOT/"prospects").glob("*.json")}
    (OUT/"claim"/"names.js").write_text("window.NAMES="+json.dumps(names)+";")
    print("built:", ", ".join(built))


if __name__ == "__main__":
    main()
