import copy
import random
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Callable, Optional
import json

import cards.cards

# --------------------------------------------------------------------------
# State: data only
# --------------------------------------------------------------------------
@dataclass(frozen=True)
class Phase(Enum):
    AWAKEN = auto()
    BEGINNING = auto()  # scoring step (hold)
    CHANNEL = auto()
    DRAW = auto()
    ACTION = auto()  # <- the only phase where a player is asked to choose
    END = auto()



@dataclass(frozen=True)
class CardInstance:  # runtime object; many can share one CardDef
    id: int
    def_id: str
    owner_id: str
    control_id: str = None
    might_mod: int = 0
    energy_mod: int = 0
    damage: int = 0
    exhausted: bool = False
    address: tuple = field(default_factory=tuple)
    




@dataclass(frozen=True)
class Player:
    id: int
    name: str
    agent_type: str
    main_deck: list
    rune_deck: list
    champion : str
    battlefields: str
    legend : str
    score: int = 0



@dataclass(frozen=True)
class Battlefield:
    id: str
    units: list = field(default_factory=list)





@dataclass(frozen=True)
class GameState:
    cards: dict = field(default_factory=dict)
    players: dict = field(default_factory=dict)
    zones: dict = field(default_factory=dict)
    rng: None
    turn_order: list = field(default_factory=list)
    active_player: str = None
    turn: int = 1
    phase: Phase = Phase.AWAKEN
    scored_this_turn: set = field(default_factory=set)
    winner: Optional[int] = None
    log: list = field(default_factory=list)
    next_card_id = 0

    def clone(self) -> "GameState":
        # deepcopy is fine to start with; replace with a hand-written copy
        # once profiling says so. It also copies the RNG state.
        return copy.deepcopy(self)