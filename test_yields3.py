import requests

def test_ecb(series_key, label):
    url = f"https://data-api.ecb.europa.eu/service/data/{series_key}?startPeriod=2015-01&endPeriod=2015-03&format=csvdata"
    r = requests.get(url)
    if r.status_code == 200 and 'OBS_VALUE' in r.text:
        print(f"✓ {label}")
    else:
        print(f"✗ {label} — {r.status_code}")

# Maastricht long-term interest rates - country level
test_ecb("ILM/M.DE.L.L40.CI.0.EUR.N.Z", "DE (ILM v1)")
test_ecb("ILM/M.AT.L.L40.CI.0.EUR.N.Z", "AT (ILM v1)")

# Alternative format
test_ecb("ILM/M.DE.L.CI.0.EUR.N.Z.L40", "DE (ILM v2)")

# RTD dataset
test_ecb("RTD/M.S0.N.I10.SV.U2.EUR09.DE.10Y.YLD.A.N", "DE (RTD)")

# SAFE dataset  
test_ecb("BSP/Q.DE._Z.W._Z.R.A.A.F.I._T.EUR.Q.A", "DE (BSP)")

# Long-term rates from IRS
test_ecb("IRS/M.AT.L.L40.CI.0.EUR.N.Z", "AT test (IRS)")
test_ecb("IRS/M.DE.L.L40.CI.0.EUR.N.Z", "DE test (IRS)")

# Try without country - EA aggregate benchmark by country
test_ecb("FM/M.DE.EUR.4F.BB.DE_10Y.YLD", "DE FM v2")
test_ecb("FM/M.U2.EUR.4F.BB.DE_10Y.YLD", "DE FM v3")
