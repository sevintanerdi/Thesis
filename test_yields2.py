import requests

def test_ecb(series_key, label):
    url = f"https://data-api.ecb.europa.eu/service/data/{series_key}?startPeriod=2015-01&endPeriod=2015-03&format=csvdata"
    r = requests.get(url)
    if r.status_code == 200 and 'OBS_VALUE' in r.text:
        print(f"✓ {label}")
    else:
        print(f"✗ {label} — {r.status_code}")

# Maastricht convergence criterion rates (country-specific 10Y)
test_ecb("ILM/M.DE.L.L40.CI.0.EUR.N.Z", "DE (ILM)")
test_ecb("MEI_FIN/IRLTLT01.DEU.M", "DE (MEI_FIN)")
test_ecb("MIR/M.DE.B.L22.A.2.A.I.EUR.O.Z", "DE (MIR)")

# IRTS dataset
test_ecb("IRTS/M.DE.L.L40.CI.0.EUR.N.Z", "DE (IRTS)")

# IRS - Interest Rate Statistics
test_ecb("IRS/M.DE.L.L40.CI.0.EUR.N.Z", "DE (IRS)")

# Long term interest rates
test_ecb("FM/M.DE.EUR.4F.BB.DE_10Y.YLD", "DE 10Y (FM)")
test_ecb("FM/M.ES.EUR.4F.BB.ES_10Y.YLD", "ES 10Y (FM)")
test_ecb("FM/M.IT.EUR.4F.BB.IT_10Y.YLD", "IT 10Y (FM)")
test_ecb("FM/M.FR.EUR.4F.BB.FR_10Y.YLD", "FR 10Y (FM)")
test_ecb("FM/M.NL.EUR.4F.BB.NL_10Y.YLD", "NL 10Y (FM)")
