import json

card_db = json.load(open("riftbound/cards/cards.json").read())

class Card:
    def_id: str
    owner_id: str
    control_id: str
    might_base: int
    might_mod: int
    energy_base: int = 0
    energy_mod: int = 0
    exhausted: bool = False
    location: str

