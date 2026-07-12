import requests
r = requests.get("https://fred.stlouisfed.org/graph/fredgraph.csv?id=CLVMDEEA02DEQ")
print(r.text[:500])
