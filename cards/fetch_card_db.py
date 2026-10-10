import requests
import json


cards = {}

page = 1
while False:
    print(page)
    resp = requests.get("https://api.riftcodex.com/cards", params={"page": page, "size": 100})
    data = resp.json()

    for i in data["items"]:
        print(i)
        cards[i["riftbound_id"]] = {
            "name": i["name"],
            "set": i["set"]["set_id"],
            "domain" : i["classification"]["domain"],
            "type" : i["classification"]["type"] ,
            "supertype" : i["classification"]["supertype"],
            "energy" : i["attributes"]["energy"],
            "might" : i["attributes"]["might"],
            "power" : i["attributes"]["power"],
            "tags" : i["tags"],
            "rarity" : i["classification"]["rarity"],
            "effect" : i["text"]["plain"],
            "image_url" : i["media"]["image_url"]
        }



    if data["page"] == data["pages"]:
        break

    page += 1

resp = requests.get("https://api.riftcodex.com/cards", params={"page": 1, "size": 1})
print(resp.json())

#with open('cards.json', 'w') as fp:
#    json.dump(cards, fp)




