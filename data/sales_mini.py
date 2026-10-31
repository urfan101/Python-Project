"""sales_mini.py - kiçik data app + Git PR axını.
İstifadə: python sales_mini.py [test | demo | fayl.csv]"""
import csv, io, subprocess as sp, sys, tempfile, unittest
from collections import defaultdict
from pathlib import Path

DATA = "region,amount\nbaku,100\nGanja,50\n baku ,25\nGanja,abc\n,10\nBaku,-5\n"

def clean(rows):
    """Yararsız sətirləri atır, (təmiz_siyahı, atılan_say) qaytarır."""
    out = []
    for r in rows:
        try: amt = float(r["amount"])
        except (ValueError, KeyError, TypeError): continue
        reg = (r.get("region") or "").strip().title()
        if reg and amt > 0: out.append((reg, amt))
    return out, len(rows) - len(out)

def report(sales):
    t = defaultdict(float)
    for reg, amt in sales: t[reg] += amt
    return dict(t), (sum(t.values()) / len(sales) if sales else 0.0)  # boş data üçün qoruma

class T(unittest.TestCase):
    def test_clean(self):
        s, bad = clean(list(csv.DictReader(io.StringIO(DATA))))
        self.assertEqual((s, bad), ([("Baku", 100), ("Ganja", 50), ("Baku", 25)], 3))
    def test_report(self):
        self.assertEqual(report([("A", 10), ("A", 20)]), ({"A": 30}, 15))
    def test_empty(self):
        self.assertEqual(report([]), ({}, 0.0))

def demo():
    d = Path(tempfile.mkdtemp()); g = lambda *a: sp.run(["git", *a], cwd=d, check=True, capture_output=True)
    g("init", "-b", "main"); g("config", "user.name", "Dev"); g("config", "user.email", "d@x.az")
    (d / "README.md").write_text("# demo\n"); g("add", "."); g("commit", "-m", "init")
    for n, msg in [(1, "feat: data"), (2, "feat: report")]:
        g("switch", "-c", f"feature/{n}"); (d / f"{n}.txt").write_text(msg); g("add", ".")
        g("commit", "-m", msg); g("switch", "main")
        g("merge", "--no-ff", f"feature/{n}", "-m", f"Merge pull request #{n} (approved)")
    print(sp.run(["git", "log", "--graph", "--oneline"], cwd=d, capture_output=True, text=True).stdout)

if __name__ == "__main__":
    a = sys.argv[1] if len(sys.argv) > 1 else "test"
    if a == "test": unittest.main(argv=["x"])
    elif a == "demo": demo()
    else:
        s, bad = clean(list(csv.DictReader(open(a, encoding="utf-8"))))
        print(*report(s), f"atılan: {bad}")
