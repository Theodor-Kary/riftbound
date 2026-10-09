import copy
import random
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Callable, Optional
import json



# --------------------------------------------------------------------------
# State: data only
# --------------------------------------------------------------------------
class Phase(Enum):
    AWAKEN = auto()
    BEGINNING = auto()  # scoring step (hold)
    CHANNEL = auto()
    DRAW = auto()
    ACTION = auto()  # <- the only phase where a player is asked to choose
    END = auto()


@dataclass
class CardInstance:  # runtime object; many can share one CardDef
    id: int
    def_id: str
    owner_id: str
    control_id: str
    might_mod: int = 0
    energy_mod: int = 0
    damage: int = 0
    exhausted: bool = False
    location: str = None


@dataclass
class Player:
    name: str
    id: str
    agent_type: str
    main_deck: list
    rune_deck: list
    legend : list
    champion : list
    battlefields: list




@dataclass
class PlayerState:
    score: int = 0
    # Zones hold card ids, not objects, so cloning stays cheap and cycle-free.
    zones = {
        "main_deck": [],
        "rune_deck": [],
        "hand": [],
        "runes": [],
        "trash": [],
        "base": [],
        "legend": [],
        "champion": []
    }


@dataclass
class Battlefield:
    id: str
    units: list = field(default_factory=list)


@dataclass
class GameState:
    card_registry: dict
    players: list
    battlefields: list
    rng: random.Random
    active: int = 0
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

    def show():
        return