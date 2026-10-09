card_db = json.load(open("riftbound/cards/cards.json").read())

@dataclass(frozen=True)
class CardDef:  # static, shared by every copy of a card
    id: str
    name: str
    kind: str = "unit"  # unit / spell / gear / rune ...
    energy: int = 1  # energy cost
    might: int = 1


