from dataclasses import dataclass, field
import json

@dataclass(frozen=True)
class CardDef:  # static, shared by every copy of a card
    id: str
    name: str
    domain: list
    type: str
    supertype: str
    energy: int
    might: int
    power: int
    tags: list
    effect: str




class CardCatalog:
    cards: Mapping[str, CardDef]

    def _from_json(path) -> CardCatalog:
        data = json.load(open(path).read())
        next_id = 0
        cards = {}
        for key, card_data in data:
            

        return CardCatalog()