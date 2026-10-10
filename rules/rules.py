from dataclasses import dataclass, field

# --------------------------------------------------------------------------
# Config and static card data
# --------------------------------------------------------------------------
@dataclass(frozen=True)
class RulesConfig:
    number_of_players: int = 2
    formation_of_players: str = "1v1"
    victory_score: int = 8
    battlefield_count: int = 2
    best_of: int = 1
    runes_per_turn: int = 2
    first_player_skips_draw: bool = False
    last_player_channels_extra_rune: bool = True
    starting_hand = 4