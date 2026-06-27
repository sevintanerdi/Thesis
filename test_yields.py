import requests

def test_ecb(series_key, label):
    url = f"https://data-api.ecb.europa.eu/service/data/{series_key}?startPeriod=2015-01&endPeriod=2015-03&format=csvdata"
    r = requests.get(url)
    if r.status_code == 200 and 'OBS_VALUE' in r.text:
        print(f"✓ {label}")
    else:
        print(f"✗ {label} — {r.status_code}")

# ECB long-term interest rates (Maastricht criterion)
test_ecb("ILM/M.DE.L.L40.CI.0.EUR.N.Z", "10Y Germany (ILM)")
test_ecb("ILM/M.ES.L.L40.CI.0.EUR.N.Z", "10Y Spain (ILM)")
test_ecb("ILM/M.IT.L.L40.CI.0.EUR.N.Z", "10Y Italy (ILM)")
test_ecb("ILM/M.FR.L.L40.CI.0.EUR.N.Z", "10Y France (ILM)")
test_ecb("ILM/M.NL.L.L40.CI.0.EUR.N.Z", "10Y Netherlands (ILM)")

# Alternative: FM dataset
test_ecb("FM/M.DE.EUR.FR.BB.U2.10Y.R.A.A._Z._Z.A", "10Y Germany (FM)")
test_ecb("FM/M.ES.EUR.FR.BB.U2.10Y.R.A.A._Z._Z.A", "10Y Spain (FM)")
test_ecb("FM/M.IT.EUR.FR.BB.U2.10Y.R.A.A._Z._Z.A", "10Y Italy (FM)")
