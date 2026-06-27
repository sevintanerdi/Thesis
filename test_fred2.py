import requests

url = "https://fred.stlouisfed.org/graph/fredgraph.csv?id=IRLTLT01DEM156N"
r = requests.get(url)
print(r.text[:300])
