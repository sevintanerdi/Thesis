import requests
from io import StringIO
import pandas as pd

def test_ecb(series_key, label):
    url = f"https://data-api.ecb.europa.eu/service/data/{series_key}?startPeriod=2015-Q2&endPeriod=2015-Q4&format=csvdata"
    r = requests.get(url)
    if r.status_code == 200 and 'OBS_VALUE' in r.text:
        print(f"✓ {label}")
    else:
        print(f"✗ {label} — {r.status_code}")

# NIM - yeni ülkeler
test_ecb("SUP/Q.IT.W0._Z.I2120._T.SII._Z._Z._Z.PCT.C", "NIM Italy")
test_ecb("SUP/Q.FR.W0._Z.I2120._T.SII._Z._Z._Z.PCT.C", "NIM France")
test_ecb("SUP/Q.NL.W0._Z.I2120._T.SII._Z._Z._Z.PCT.C", "NIM Netherlands")

# CET1 - yeni ülkeler
test_ecb("SUP/Q.IT.W0._Z.I4008._T.SII._Z._Z._Z.PCT.C", "CET1 Italy")
test_ecb("SUP/Q.FR.W0._Z.I4008._T.SII._Z._Z._Z.PCT.C", "CET1 France")
test_ecb("SUP/Q.NL.W0._Z.I4008._T.SII._Z._Z._Z.PCT.C", "CET1 Netherlands")

# 10Y Government bond yields
test_ecb("IRS/M.DE.L.L40.CI.0.EUR.N.Z", "10Y Yield Germany")
test_ecb("IRS/M.ES.L.L40.CI.0.EUR.N.Z", "10Y Yield Spain")
test_ecb("IRS/M.IT.L.L40.CI.0.EUR.N.Z", "10Y Yield Italy")
test_ecb("IRS/M.FR.L.L40.CI.0.EUR.N.Z", "10Y Yield France")
test_ecb("IRS/M.NL.L.L40.CI.0.EUR.N.Z", "10Y Yield Netherlands")
