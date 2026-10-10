from dataclasses import dataclass, field
import json

@dataclass(frozen=True)
class CardDef:  # static, shared by every copy of a card
    id: str
    name: str
    domain: list
    c_type: str
    supertype: str
    energy: int
    might: int
    power: int
    tags: list
    effect: dict




class CardCatalog:
    cards: Mapping[str, CardDef]

    def _from_json(path) -> CardCatalog:
        data = json.load(open(path).read())
        next_id = 0
        cards = {}
        for key, d in data:
            effect = _effect_from_text(d['effect'])
            card = CardDef(key, d['name'], d['domain'], d['type'], d['supertype'], d['energy'], d['might'], d['power'], d['tags'], effect)
            cards[next_id] = card

        return CardCatalog(cards)

    def _effect_from_text(text: str) -> dict:
        return {}
