import requests

def test_ecb(series_key, label):
    url = f"https://data-api.ecb.europa.eu/service/data/{series_key}?startPeriod=2015-Q1&endPeriod=2015-Q2&format=csvdata"
    r = requests.get(url)
    ok = r.status_code == 200 and 'OBS_VALUE' in r.text
    print(f"{'✓' if ok else '✗'} {label} ({r.status_code})")

# IT GDP deflator
test_ecb("MNA/Q.Y.IT.W2.S1.S1.B.B1GQ._Z._Z._Z.EUR.LR.G1", "IT GDP growth ECB")
test_ecb("MNA/Q.Y.IT.W0.S1.S1.D.B1GQ.D._Z._Z.EUR.V.N", "IT GDP deflator ECB")
test_ecb("ICP/M.IT.N.000000.4.ANR", "IT HICP")

# 1Y government yields ECB
test_ecb("ILM/M.DE.L.L10.CI.0.EUR.N.Z", "DE 1Y ECB")
test_ecb("ILM/M.ES.L.L10.CI.0.EUR.N.Z", "ES 1Y ECB")
test_ecb("ILM/M.IT.L.L10.CI.0.EUR.N.Z", "IT 1Y ECB")
test_ecb("ILM/M.FR.L.L10.CI.0.EUR.N.Z", "FR 1Y ECB")
test_ecb("ILM/M.NL.L.L10.CI.0.EUR.N.Z", "NL 1Y ECB")

# Alternative: FM dataset for yields
test_ecb("FM/M.DE.EUR.4F.BB.DE_1YR.YLD", "DE 1Y FM")
test_ecb("YC/B.U2.EUR.4F.G_N_A.SV_C_YM.SR_1Y", "EA 1Y spot rate YC")
