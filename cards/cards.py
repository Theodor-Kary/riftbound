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

    def __init__(self, cards: Mapping[str, CardDef]):
        self.cards = cards

    def from_json(path) -> CardCatalog:
        data = json.load(open(path).read())
        cards = {}
        for key, d in data:
            effect = _effect_from_text(d['effect'])
            card = CardDef(key, d['name'], d['domain'], d['type'], d['supertype'], d['energy'], d['might'], d['power'], d['tags'], effect)
            cards[key] = card

        return CardCatalog(cards)
    
    def __repr__(self):
        return f'CardCatalog len {len(self.cards)}'

    #def _effect_from_text(text: str) -> dict:
    #    return {}
