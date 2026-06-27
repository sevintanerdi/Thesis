import requests

# FRED API - no key needed for basic access
def test_fred(series_id, label):
    url = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={series_id}"
    r = requests.get(url)
    if r.status_code == 200 and 'DATE' in r.text:
        lines = r.text.strip().split('\n')
        print(f"✓ {label} — {len(lines)-1} obs, sample: {lines[1]}")
    else:
        print(f"✗ {label} — {r.status_code}")

test_fred("IRLTLT01DEM156N", "Germany 10Y")
test_fred("IRLTLT01ESM156N", "Spain 10Y")
test_fred("IRLTLT01ITM156N", "Italy 10Y")
test_fred("IRLTLT01FRM156N", "France 10Y")
test_fred("IRLTLT01NLM156N", "Netherlands 10Y")
