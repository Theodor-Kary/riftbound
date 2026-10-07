from __future__ import annotations
 
import copy
import random
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Callable, Optional




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



def Phase():
    awaken = 1
    beginning = 2
    channel = 3
    draw = 4
    action = 5
    end = 6




@dataclass
class GameState():
    players: list
    battlefield: list
    rng = random.random
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
        "base": []
    }

    
    

class CardDef:
    id: str
    name: str
    type: str
    might: int
    energy: int
    legend: bool



class CardInstance:
    id: str
    def_id: str
    owner_id: str
    exhausted: bool = False




# Actions

class PlayCard():
    id: str

class ActivateCard():
    id: str

class MoveCard():
    id: str
    destination: str

class EndTrun():
    pass














class Battlefield:
    id: str
    units: list


class Rune:
    id: str
    type: str

















class Engine:
    def __init__(self, cards_db: dict, rules: RulesConfig = RulesConfig()):
        self.cards_db = cards_db
        self.rules = rules


    def newGame(self, players, seed=0) -> GameState:
        rng = random.Random(seed)
        player_states = []
        for p in players:




        def newPlayer(player) -> PlayerState:
            state = PlayerState()
            state.id = player.id










    def gameTurn():

        print(game_turn)
        #Awaken:

        #Beginning

        #











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