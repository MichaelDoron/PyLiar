import random
import Card

"""
This Class is the main engine beyond the game mechanics.
It receives a list of agents,
and handles the rules of the game.
"""
class Game:
    def __init__( self, agents):
        self.numOfPlayers = len(agents)
        self.state = self.createStartState(self.numOfPlayers)
        self.agents = agents
        self.states = [self.state]

#   This method creates the first state of the game
    def createStartState(self, numOfPlayers):
        return  gameState(numOfPlayers)

    #   This method resets the game
    def newGame(self):
        state = self.createStartState(self.numOfPlayers)

    #   This method handles the actual mechanics of the game.
    #   It ends when one of the players wins
    def play(self):
        turnOfPlayer = 0
        while(True):
            newState = self.state.copy()

            #   selecting a player to play, and receiving the card and declaration of Card from the player
            currAgentState = agentState(self.state, turnOfPlayer+1)
            stateBeforeCardPlacement = newState.copy()
            card, declare = self.agents[turnOfPlayer].getActionCard(currAgentState)

            #print("the card which was played was ",card.value," of shape ",card.shape)
            #print("the card which was declared was ",declare.value, " of shape ", declare.shape)

            #   updating the game state after the play
            newState.isLie = self.isLie(card, declare)
            newState.cards[turnOfPlayer+1].remove(card)
            newState.cards[0].append(card)
            newState.lastPlayed = declare.value
            newState.turnsSinceLastLie = newState.turnsSinceLastLie + 1

            #   Checking each player if he calls for bluff
            call = False
            suspectingPlayer = turnOfPlayer
            while (True):
                suspectingPlayer = (suspectingPlayer+1) % self.numOfPlayers
                if suspectingPlayer == turnOfPlayer:
                    break
                currAgentState = agentState(newState, suspectingPlayer+1)
                stateBeforeCallPlacement = newState.copy()
                call = self.agents[suspectingPlayer].getActionCall(currAgentState)
                if call == True:
                    print("called a liar!")
                    break
                #self.agents[suspectingPlayer].inform(agentState(stateBeforeCallPlacement, suspectingPlayer), call, agentState(newState.copy(), suspectingPlayer))

            #   deciding repercussions for the call
            if call == True:
                if newState.isLie == True:
                    newState.cards[turnOfPlayer] = newState.cards[turnOfPlayer] + newState.cards[0]
                    newState.cards[0] = []
                    newState.lastPlayed = 0
                    newState.turnsSinceLastLie = 0
                    print("A liar was caught! ")
                else:
                    newState.cards[suspectingPlayer] = newState.cards[suspectingPlayer] + newState.cards[0]
                    newState.cards[0] = []
                    print("A dirty name-caller was shamed! ")
                #self.agents[suspectingPlayer].inform(agentState(stateBeforeCallPlacement,suspectingPlayer), call, agentState(newState.copy(),suspectingPlayer))
            self.agents[turnOfPlayer].inform(agentState(stateBeforeCardPlacement,turnOfPlayer+1), (card, declare), agentState(newState.copy(), turnOfPlayer+1))

            #   if someone wins, the game ends
            if len(newState.cards[turnOfPlayer+1]) == 0:
                print("the winner is player ", turnOfPlayer+1)
                break

            #   updating the state
            self.states.append(self.state)
            self.state = newState

            #   calling the next player to play
            turnOfPlayer = (turnOfPlayer+1) % self.numOfPlayers

#   This method checks if the declaration was a lie
    def isLie(self, card, declare):
        if card.value == declare.value and card.shape == declare.shape:
            return False
        else:
            return True

"""
This is the state of the agent, whose values are harvested from the state of the game
"""
class agentState:
    def __init__( self, state, agentNum):
        self.agentNum = agentNum
        self.numOfPlayers = state.numOfPlayers
        self.agentCards = state.cards[agentNum]
        self.lastPlayed = state.lastPlayed
        self.turnsSinceLastLie = state.turnsSinceLastLie
        self.cardLengths = {}
        for player in range(state.numOfPlayers+1):
            self.cardLengths[player] = len(state.cards[player])

    def copy( self ):
        state = agentState(self, self.agentNum)
        self.agentCards = self.agentCards
        self.lastPlayed = self.lastPlayed
        self.cardLengths = self.cardLengths
        return state

"""
This is the state of the game, where all the information concerning the game is kept.
"""
class gameState:
    def __init__( self, numOfPlayers):
        self.numOfPlayers = numOfPlayers
        self.cards = self.dealDeck(numOfPlayers)
        self.lastPlayed = 0
        self.isLie = False
        self.turnsSinceLastLie = 0

    def copy( self ):
        state = gameState(self.numOfPlayers)
        state.cards = self.cards
        state.lastPlayed = self.lastPlayed
        state.isLie = self.isLie
        return state

#   This method deals the cards to the players at the beginning of the game
    def dealDeck(self, numOfPlayers):
        cards = {}
        cards[0] = self.createDeck()
        for player in range(numOfPlayers):
            cards[player+1] = []
        while len(cards[0]) != 0:
            for player in range(numOfPlayers):
                if (len(cards[0]) == 0): break
                cardIndex = random.randint(0,len(cards[0])) -1
                card = cards[0][cardIndex]
                cards[0].remove(card)
                cards[player+1].append(card)
        return cards

#   This method deals the cards to the deck
    def createDeck(self):
        cards = []
        i = 0
        for shape in range(4):
            for value in range(13):
                cards.append(Card.Card(value+1, shape))
                i = i + 1
        random.shuffle(cards)
        return cards

"""
This is an interface of a player in the game
it gets a state and returns two actions:
which action to pick and declaration to declare
and whether to lie or not
"""
class Agent:
    def __init__(self): pass

    def update(self, agentState):
        pass

    def getActionCard(self, agentState):
        raise NotImplementedError("Implemented in the inheriting classes")

    def getActionCall(self, agentState):
        raise NotImplementedError("Implemented in the inheriting classes")

#   This method returns the legal values of cards that the player can return
    def legalValues(self, agentState):
        lastPlayed = agentState.lastPlayed
        if lastPlayed == 0:
            return [0]
        if lastPlayed == 13:
            return [1]
        return [lastPlayed + 1]

#   This method returns the cards that the agent can return without lying
    def myLegalCards(self, state):
        legalValues = self.legalValues(state)
        if legalValues[0] == 0:
            return state.agentCards
        legalCards = []
        for card in state.agentCards:
            cardValue = card.getValue()
            if (cardValue in legalValues):
                legalCards.append(card)
        return legalCards