"""Pobiera strony z listami ofert z serwisów, których nie da się czytać z chmury Claude,
i zapisuje je jako uproszczony tekst + linki w data/. Analizę robi skan Claude."""
import json, re, sys, time, datetime, pathlib
import requests
from bs4 import BeautifulSoup

OUT = pathlib.Path(__file__).resolve().parent.parent / "data"
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36"
HEADERS = {"User-Agent": UA, "Accept-Language": "pl-PL,pl;q=0.9", "Accept": "text/html,application/xhtml+xml"}

SOURCES = {
    "gratka": ["https://gratka.pl/nieruchomosci/mieszkania/gdynia/wynajem?liczba-pokoi:min=3&liczba-pokoi:max=3&cena-calkowita:max=3500"],
    "morizon": ["https://www.morizon.pl/do-wynajecia/mieszkania/gdynia/?ps%5Bnumber_of_rooms_from%5D=3&ps%5Bnumber_of_rooms_to%5D=3&ps%5Bprice_to%5D=3500"],
    "trojmiasto": ["https://ogloszenia.trojmiasto.pl/nieruchomosci-mam-do-wynajecia/mieszkanie/gdynia/ai,3_3,ri,_3500.html"],
    "okolica": ["https://www.okolica.pl/wynajem/mieszkania/gdynia"],
    "krm": ["https://krm.pl/wynajem/mieszkania/gdynia"],
}

def simplify(html, base):
    soup = BeautifulSoup(html, "html.parser")
    for t in soup(["script", "style", "noscript", "svg", "header", "footer", "nav"]):
        t.decompose()
    lines = []
    for a in soup.find_all("a", href=True):
        text = re.sub(r"\s+", " ", a.get_text(" ", strip=True))
        if len(text) < 15:
            continue
        href = requests.compat.urljoin(base, a["href"])
        img = a.find("img")
        src = (img.get("src") or img.get("data-src") or "") if img else ""
        parent = re.sub(r"\s+", " ", a.find_parent().get_text(" ", strip=True))[:400] if a.find_parent() else ""
        lines.append({"url": href, "text": text[:300], "context": parent, "img": src})
    return lines

def main():
    OUT.mkdir(exist_ok=True)
    status = {"at": datetime.datetime.utcnow().isoformat() + "Z", "sources": {}}
    for name, urls in SOURCES.items():
        items, info = [], []
        for u in urls:
            try:
                r = requests.get(u, headers=HEADERS, timeout=30)
                info.append({"url": u, "http": r.status_code, "bytes": len(r.content)})
                if r.ok:
                    items += simplify(r.text, u)
            except Exception as e:  # noqa: BLE001
                info.append({"url": u, "error": str(e)[:200]})
            time.sleep(2)
        seen, uniq = set(), []
        for it in items:
            if it["url"] not in seen:
                seen.add(it["url"]); uniq.append(it)
        (OUT / f"{name}.json").write_text(json.dumps(uniq, ensure_ascii=False, indent=1))
        status["sources"][name] = {"requests": info, "links": len(uniq)}
    (OUT / "status.json").write_text(json.dumps(status, ensure_ascii=False, indent=1))
    print(json.dumps(status, indent=1))

if __name__ == "__main__":
    sys.exit(main())
