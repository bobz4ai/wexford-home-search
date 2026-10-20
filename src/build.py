"""Assemble the Wexford Home Search page.
Outputs:
  out/index.html     full HTML document for GitHub Pages
  out/artifact.html  page fragment for the Claude artifact preview
"""
import json, pathlib, sys, datetime

here = pathlib.Path(__file__).parent
updated = sys.argv[1] if len(sys.argv) > 1 else datetime.date.today().strftime("%B %-d, %Y")
nxt = sys.argv[2] if len(sys.argv) > 2 else ""

listings = json.loads((here / "data_listings.json").read_text())
comm = json.loads((here / "data_communities.json").read_text())
groups = {
    "senior": comm.get("senior", []),
    "rental": comm.get("rental", []),
    "owner": comm.get("owner", []),
    "listing": listings["rentals"],
    "sale": listings["sales"],
}
ids = [x["id"] for g in groups.values() for x in g]
assert len(ids) == len(set(ids)), "duplicate ids"
data = json.dumps({"groups": groups}, ensure_ascii=False)

tpl = (here / "template.html").read_text()
lp = here / "package/dist/leaflet.css"
leaflet_css = lp.read_text() if lp.exists() else (here / "leaflet.css").read_text()
page = (tpl.replace("/*__DATA__*/null", data)
           .replace("/*__LEAFLET_CSS__*/", leaflet_css)
           .replace("__UPDATED__", updated)
           .replace("__NEXT__", nxt))

out = here / "out"; out.mkdir(exist_ok=True)
(out / "artifact.html").write_text(page)
gh = page.replace(leaflet_css, "").replace('<link rel="preconnect" href="https://fonts.googleapis.com">', '<link rel="preconnect" href="https://fonts.googleapis.com">\n<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.css">')
head_end = gh.index("</style>") + len("</style>")
full = ("<!doctype html>\n<html lang=\"en\">\n<head>\n<meta charset=\"utf-8\">\n"
        "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1, viewport-fit=cover\">\n"
        + gh[:head_end] + "\n</head>\n<body>\n" + gh[head_end:] + "\n</body>\n</html>\n")
(out / "index.html").write_text(full)
print("ok", len(ids), "places;", len(full), "bytes")
