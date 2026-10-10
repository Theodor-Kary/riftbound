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
    control_id: str = owner_id
    might_mod: int = 0
    energy_mod: int = 0
    damage: int = 0
    exhausted: bool = False
    location: list = []







@dataclass
class PlayerState:
    
    # Zones hold card_instance.id



@dataclass
class Player:
    id: int
    name: str
    agent_type: str
    main_deck: Iterable[str]
    rune_deck: Iterable[str]
    champion : str
    battlefields: str
    legend : str
    score: int = 0
    zones = {
        "main_deck": [],
        "rune_deck": [],
        "hand": [],
        "runes": [],
        "trash": [],
        "base": [],
        "champion": []
    }

@dataclass
class Battlefield:
    id: str
    units: list = field(default_factory=list)


@dataclass
class GameState:
    cards: dict = {}
    players: dict = {}
    battlefields: dict = {}
    rng: int = random.Random()
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