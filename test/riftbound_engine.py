from __future__ import annotations

import copy
import random
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Callable, Optional


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


@dataclass(frozen=True)
class CardDef:  # static, shared by every copy of a card
    id: str
    name: str
    kind: str = "unit"  # unit / spell / gear / rune ...
    cost: int = 1  # energy cost
    might: int = 1


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


# --------------------------------------------------------------------------
# Events: for logging/replays now, triggered abilities later
# --------------------------------------------------------------------------
@dataclass
class Event:
    name: str
    data: dict = field(default_factory=dict)


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
    owner: int
    exhausted: bool = False
    damage: int = 0




@dataclass
class Player:
    name: str
    id: str
    agent_type: str
    main_deck: list
    rune_deck: list
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
    cards: dict
    players: list
    battlefields: list
    rng: random.Random
    active: int = 0
    turn: int = 1
    phase: Phase = Phase.AWAKEN
    scored_this_turn: set = field(default_factory=set)
    winner: Optional[int] = None
    log: list = field(default_factory=list)

    def clone(self) -> "GameState":
        # deepcopy is fine to start with; replace with a hand-written copy
        # once profiling says so. It also copies the RNG state.
        return copy.deepcopy(self)


# --------------------------------------------------------------------------
# Engine: rules logic
# --------------------------------------------------------------------------
class Engine:
    def __init__(self, card_db: dict, rules: RulesConfig = RulesConfig()):
        self.card_db = card_db
        self.rules = rules
        self._listeners: dict[str, list[Callable]] = {}  # event name -> callbacks

        # dispatch tables keep apply() and _advance() free of big if-chains
        self._action_handlers = {
            EndTurn: self._do_end_turn,
            PlayCard: self._do_play_card,
            MoveUnit: self._do_move_unit,
        }
        self._phase_handlers = {
            Phase.AWAKEN: self._phase_awaken,
            Phase.BEGINNING: self._phase_beginning,
            Phase.CHANNEL: self._phase_channel,
            Phase.DRAW: self._phase_draw,
            Phase.END: self._phase_end,
        }

    # ---- public API (this is all agents and bots ever touch) -------------
    def new_game(self, players: list, seed=0) -> GameState:
        rng = random.Random(seed)
        cards = {}
        next_id = 0
        for p in players:
            state = PlayerState()
            state.zones["main_deck"] = rng.shuffle(p.main_deck)
            state.zones["rune_deck"] = rng.shuffle()

        players = [PlayerState() for p in players]

        cards, players, next_id = {}, [Player(), Player()], 0
        for p, (deck, runes) in enumerate(zip(decks, rune_decks)):
            for zone, def_ids in (("deck", deck), ("rune_deck", runes)):
                for d in def_ids:
                    cards[next_id] = CardInstance(next_id, d, p)
                    players[p].zones[zone].append(next_id)
                    next_id += 1
            rng.shuffle(players[p].zones["deck"])
            rng.shuffle(players[p].zones["rune_deck"])
            for _ in range(self.rules.opening_hand):
                players[p].zones["hand"].append(players[p].zones["deck"].pop())
        state = GameState(cards, players, [Battlefield(b) for b in battlefield_ids], rng)
        self._advance(state)
        return state

    def legal_actions(self, s: GameState) -> list:
        if s.winner is not None:
            return []
        me = s.players[s.active]
        ready_runes = sum(1 for r in me.zones["runes"] if not s.cards[r].exhausted)
        acts: list[Action] = [EndTurn()]
        for cid in me.zones["hand"]:
            if self.card_db[s.cards[cid].def_id].cost <= ready_runes:
                acts.append(PlayCard(cid))
        for uid in me.zones["base"]:
            if not s.cards[uid].exhausted:
                for bf in s.battlefields:
                    # TODO: combat/showdown. For now, only empty or own battlefields.
                    if self._controller(s, bf) in (None, s.active):
                        acts.append(MoveUnit(uid, bf.id))
        return acts

    def apply(self, state: GameState, action: Action, *, inplace=False, validate=True) -> GameState:
        if validate and action not in self.legal_actions(state):
            raise IllegalAction(action)
        s = state if inplace else state.clone()
        self._action_handlers[type(action)](s, action)
        self._advance(s)
        return s

    def is_terminal(self, s: GameState) -> bool:
        return s.winner is not None

    def observation_for(self, s: GameState, player: int) -> GameState:
        # TODO: hide opponent hand, deck order and rune deck order.
        return s

    def on(self, event_name: str, callback: Callable) -> None:
        """Register a listener. Card abilities will use this later."""
        self._listeners.setdefault(event_name, []).append(callback)

    # ---- turn flow --------------------------------------------------------
    def _advance(self, s: GameState) -> None:
        """Run automatic phases until a player has to decide something."""
        while s.winner is None and s.phase is not Phase.ACTION:
            self._phase_handlers[s.phase](s)

    def _phase_awaken(self, s):
        for c in s.cards.values():
            if c.owner == s.active:
                c.exhausted = False
        s.phase = Phase.BEGINNING

    def _phase_beginning(self, s):
        for bf in s.battlefields:
            if self._controller(s, bf) == s.active:
                s.scored_this_turn.add(bf.id)
                self._award_point(s, s.active, "hold", bf.id)
                if s.winner is not None:
                    return
        s.phase = Phase.CHANNEL

    def _phase_channel(self, s):
        n = self.rules.runes_per_turn
        if s.turn == 2:  # second player's first turn (1v1)
            n = self.rules.second_player_first_channel
        me = s.players[s.active]
        for _ in range(n):
            if me.zones["rune_deck"]:
                me.zones["runes"].append(me.zones["rune_deck"].pop())
        s.phase = Phase.DRAW

    def _phase_draw(self, s):
        skip = self.rules.first_player_skips_first_draw and s.turn == 1
        me = s.players[s.active]
        if not skip and me.zones["deck"]:  # TODO: empty-deck rules
            me.zones["hand"].append(me.zones["deck"].pop())
        s.phase = Phase.ACTION

    def _phase_end(self, s):
        for c in s.cards.values():
            c.damage = 0
        self._emit(s, "turn_ended", player=s.active)
        s.active = 1 - s.active
        s.turn += 1
        s.scored_this_turn.clear()
        s.phase = Phase.AWAKEN

    # ---- action handlers --------------------------------------------------
    def _do_end_turn(self, s, a: EndTurn):
        s.phase = Phase.END

    def _do_play_card(self, s, a: PlayCard):
        me = s.players[s.active]
        card = s.cards[a.card_id]
        cost = self.card_db[card.def_id].cost
        # TODO: Power costs (recycle runes), player-chosen payment.
        for rid in me.zones["runes"]:
            if cost == 0:
                break
            if not s.cards[rid].exhausted:
                s.cards[rid].exhausted = True
                cost -= 1
        me.zones["hand"].remove(a.card_id)
        me.zones["base"].append(a.card_id)  # TODO: spells/gear go elsewhere
        card.exhausted = True  # units enter exhausted
        self._emit(s, "card_played", player=s.active, card=a.card_id)

    def _do_move_unit(self, s, a: MoveUnit):
        bf = next(b for b in s.battlefields if b.id == a.destination)
        before = self._controller(s, bf)
        s.players[s.active].zones["base"].remove(a.unit_id)  # TODO: moves from other locations
        bf.units.append(a.unit_id)
        s.cards[a.unit_id].exhausted = True
        self._emit(s, "unit_moved", unit=a.unit_id, to=bf.id)
        if before is None and bf.id not in s.scored_this_turn:
            s.scored_this_turn.add(bf.id)
            self._award_point(s, s.active, "conquer", bf.id)

    # ---- helpers ----------------------------------------------------------
    def _controller(self, s, bf: Battlefield) -> Optional[int]:
        owners = {s.cards[u].owner for u in bf.units}
        return owners.pop() if len(owners) == 1 else None

    def _award_point(self, s, player, reason, bf_id):
        # TODO: the final-point rule (conquering for the last point has extra
        # conditions). Check the Core Rules before implementing.
        s.players[player].score += 1
        self._emit(s, "point_scored", player=player, reason=reason, battlefield=bf_id)
        if s.players[player].score >= self.rules.points_to_win:
            s.winner = player

    def _emit(self, s, name, **data):
        ev = Event(name, data)
        s.log.append(ev)
        for cb in self._listeners.get(name, []):
            cb(s, ev)


# --------------------------------------------------------------------------
# Demo: two random agents play a full game
# --------------------------------------------------------------------------
if __name__ == "__main__":
    db = {
        "grunt": CardDef("grunt", "Grunt", "unit", cost=1, might=2),
        "rune": CardDef("rune", "Rune", "rune", cost=0, might=0),
    }
    engine = Engine(db)
    wins = [0, 0]
    for seed in range(200):
        picker = random.Random(seed)
        state = engine.new_game(
            decks=[["grunt"] * 20] * 2,
            rune_decks=[["rune"] * 12] * 2,
            battlefield_ids=["bf_a", "bf_b"],
            seed=seed,
        )
        steps = 0
        while not engine.is_terminal(state) and steps < 5000:
            state = engine.apply(state, picker.choice(engine.legal_actions(state)), inplace=True)
            steps += 1
        if state.winner is not None:
            wins[state.winner] += 1
    print("games finished, wins by player:", wins)
