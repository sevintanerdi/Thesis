import requests

def test_fred(sid, label):
    r = requests.get(f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={sid}")
    ok = 'observation_date' in r.text[:50] or 'DATE' in r.text[:50]
    print(f"{'✓' if ok else '✗'} {label} ({sid})")

# Domestic credit / loans outstanding - FRED
test_fred("LOANSDEPDE", "DE loans")
test_fred("QDES628BIS", "ES BIS credit")
test_fred("QITS628BIS", "IT BIS credit")
test_fred("QFRS628BIS", "FR BIS credit")
test_fred("QNLS628BIS", "NL BIS credit")
test_fred("DDDI01DEA156NWDB", "DE credit WB")
test_fred("DDDI01ESA156NWDB", "ES credit WB")
test_fred("DDDI01ITA156NWDB", "IT credit WB")
test_fred("DDDI01FRA156NWDB", "FR credit WB")
test_fred("DDDI01NLA156NWDB", "NL credit WB")
