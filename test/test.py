import random


#Cards
class Card:
    def_id: int
    name: str
    owner_id: int 
    might: int
    energy: int
    health: int
    location: str
    exausted : bool = False





#State

class PlayerState:
    score: int = 0
    main_deck: list = []
    rune_deck: list = []
    runes: list = []
    hand: list = []
    base: list = []
    trash: list = []


class Player:
    name: str
    id: str
    agent_type: str
    main_deck: list
    rune_deck: list
    battlefields: list
    state: PlayerState

class Battlefield: 
    id: str
    cards: list = []

class GameState:
    players: dict
    active: str
    seed : int
    cards : dict
    phase : int
    turn : int
    winner : bool = False
    battlefield : list



    



#Actions
class Action:
    pass

class MoveUnit(Action):
    id: str
    dest: str

class PlayCard(Action):
    id: str

class EndTurn(Action):
    pass




#Events

class Event:
    name: str
    data: dict


class EventBus:
    pass












#Engine

class Phase():
    AWAKEN: int = 1
    BEGINNING: int = 2
    CHANNEL: int = 3
    DRAW: int = 4
    ACTION: int = 5
    END: int = 6

class Engine:

    def __init__(self, card_db):
        self.card_db = card_db
        self._listeners = {}




        self._phase_handler = {
            Phase.AWAKEN: self._phase_awaken,
            Phase.BEGINNING: self._phase_beginning,
            Phase.CHANNEL: self._phase_channel,
            Phase.DRAW: self._phase_draw,
            Phase.ACTION: self._phase_action,
            Phase.END: self._phase_end,
        }

        self._action_handler = {
            PlayCard: self._do_play_card,
            MoveUnit: self._do_move_unit,
            EndTurn: self._do_end_turn,

        }








    ### API
    def new_game():
        return


    def apply(s: GameState, a: Action):
        #validate
        #check if action is in 

        #mutate
        return

    def legal_moves():
        return










    #Phases


    def _phase_awaken(self, s: GameState):
        me = s.player[s.active]
        
        s.phase = Phase.BEGINNING
        return

    def _phase_beginning(self, s: GameState):

        s.phase = Phase.CHANNEL

    
    def _phase_channel(self, s: GameState):

        s.phase = Phase.DRAW

    def _phase_draw(self, s: GameState):

        s.phase = Phase.ACTION

    def _phase_action(self, s: GameState):

        s.phase = Phase.END

    def _phase_end(self, s: GameState):
        return




    #Actions
    def _do_move_unit():
        return

    def _do_play_card():
        return
    
    def _do_end_turn():
        return








    #Helper Functions
    def new_card(def_id, owner_id) -> Card:
        data  = card_db['def_id']
        card = Card
        card.def_id = def_id
        card.name = data.name
        card.owner_id = owner_id
        card.might = data.might
        card.energy = data.energy
        card.health = data.health
        return card

    def _emit(self, s, name, **data):
        ev = Event(name, data)
        s.log.append(ev)
        for cb in self._listeners.get(name, []):
            cb(s, ev)







if __name__ == "__main__":
    card_db = { "1": {
                "name": "goblin",
                "might": 5,
                "energy": 5
                },
                "2": {
                "name": "elf",
                "might": 6,
                "energy": 6
            }}


    deck1 = [1, 1, 2]

    deck2 = [2, 1, 1]

    player1 = Player
    player1.main_deck = deck1

    player2 = Player
    player2.main_deck = deck2

    s = GameState

    def new_game(s: GameState, players: list):
        player_id = 0
        for p in players:
            p

    
        active: str
        seed : int
        cards : dict
        phase : int
        turn : int
    winner : bool = False
    battlefield : list

    cards = 
    