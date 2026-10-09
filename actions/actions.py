# --------------------------------------------------------------------------
# Actions: only decision the player makes
# --------------------------------------------------------------------------
@dataclass(frozen=True)
class Action:
    pass


@dataclass(frozen=True)
class EndTurn(Action):
    pass


@dataclass(frozen=True)
class PlayCard(Action):
    card_id: int  # TODO: targets, payment choices


@dataclass(frozen=True)
class MoveUnit(Action):
    unit_id: int
    destination: str  # battlefield id


class IllegalAction(Exception):
    pass