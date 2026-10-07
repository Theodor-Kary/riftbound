import requests

resp = requests.get("https://api.riftcodex.com/cards", params={"page": 1, "size": 100})
data = resp.json()
print(data.keys())
print(data["total"], data["pages"])
print(data["items"][0])