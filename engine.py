from __future__ import annotations
import copy
import random
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Callable, Optional


import cards.cards
import states.states
import events.events
import actions.actions
import rules.rules



# --------------------------------------------------------------------------
# Engine: rules logic
# --------------------------------------------------------------------------
class Engine:
    def __init__(self, card_db: dict, rules: RulesConfig = RulesConfig()):
        self.card_db = card_db
        self.rules = rules
        self._listeners: dict[str, list[Callable]] = {}  # event name -> callbacks

        #dispatch table
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
    def new_game(self, players: Iterable[Player], seed=0) -> GameState:
    
        rng = random.Random(seed)
        s = GameState()

        #TODO: Validation check that player decks follow rule requirments

        for p in players:
            #Instanciating cards in main deck and assinging ids to main deck zone
            for def_id in p.main_deck:
                new_card = self._new_card_instance(self, s, def_id, p.id)
                s.cards[new_card.id] = new_card
                p.zone["main_deck"].append(new_card.id)
                new_card.location = [p.id, "main_deck"]
            p.zones["main_deck"] = rng.shuffle(p.zones["main_deck"])

            #Instanciating cards in rune deck and assinging ids to rune deck zone
            for def_id in p.rune_deck:
                new_card = self._new_card_instance(self, s, def_id, p.id)
                s.cards[new_card.id] = new_card
                p.zone["rune_deck"].append(new_card.id)
                new_card.location = [p.id, "rune_deck"]
            p.zones["rune_deck"] = rng.shuffle(p.zones["rune_deck"])

            #Instanciating champion card
            new_card = self._new_card_instance(self, s, p.champion, p.id)
            s.cards[new_card.id] = new_card
            p.zones["champion"] = new_card.id

        
        #battle field

            s.Battlefield[p.battlefield] =  self._new_card_instance(self, s, p.champion, p.id)


        #opening hand
            for _ in range(self.rules.starting_hand):
                card_id = p.zones["main_deck"][0]
                self.move_card()

            s.players[p.id] = p 
        return s

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
    
    def _new_card_instance(self, s, def_id, owner_id) -> CardInstance:
        id = s.next_card_id
        s.next_card_id += 1

        card = CardInstance(id, def_id, owner_id, owner_id)
        return card
    
    def _move_card(self, s, card_id, destination: [str, str]):
        

        #Find card_id location
        #Remove card_id from location
        #Add card_id to new location

    def _find_card(self, s, card_id):
        loc = s.cards[card_id].location
        if card_id in s.players[loc[0]].zones[loc[1]]:
            return loc
        else:
            for uid, p in s.players:
                for zone, cards in p.zones
            for bf in s.battlefields
                return l
            return None



    def _emit(self, s, name, **data):
        ev = Event(name, data)
        s.log.append(ev)
        for cb in self._listeners.get(name, []):
            cb(s, ev)













if __name__ == "__main__":

    CardDef('OGN-001', 'Blazing Scorcher', ["Fury"], 'Unit', None, 5, 5, None, ["Dragon", "Noxus"], "[Accelerate] (You may pay :rb_energy_1::rb_rune_fury: as an additional cost to have me enter ready.)")



    card_db = CardCatalog.from_json('cards.json')


    #engine = Engine(card_db)

    #card = engine._new_card_instance()





















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