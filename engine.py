from __future__ import annotations
 
import copy
import random
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Callable, Optional




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



class Phase(Enum):
    awaken = auto()
    beginning = auto()
    channel = auto()
    draw = auto()
    action = auto()
    end = auto()














class GameState:
    players: list
    cards: dict
    battlefield: list
    rng = int
    phase: Phase.awaken
    turn: int = 1
    log: list
    winner: str = None





class Player:
    name: str
    id: str
    type: str
    main_deck: list
    rune_deck: list
    battlefield: list
    champion: list






class PlayerState:
    score: int = 0
    id: str
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





class CardDef:
    id: str
    name: str
    type: str
    might: int
    energy: int
    legend: bool













































if __name__ == "__main__":
    print("Hello World!")

















"""
TODO:

Starting Sequence:
Pick Battlefield
Draw 4
Mulligan

Event Log

Demo replay




Showdown
    non combat
    combat

Champions


Reaction
Chain


Gear
Spells



"""