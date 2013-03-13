from Card import Card
import random
from game import Agent


class NaiveAgent(Agent):

    def __init__(self):
        Agent.__init__(self)

    def getActionCard(self, state):
        legalCards = self.myLegalCards(state)
        if len(legalCards) != 0:
            returnCard = legalCards[0]
            return (returnCard, returnCard)
        else:
            legalValues = self.legalValues(state)
            returnCard = state.agentCards[0]
            randomShape = random.randint(0,3)
            fakeCard = Card(legalValues[0], randomShape)
            return (returnCard, fakeCard)

    def getActionCall(self, agentState):
        return False

    def inform(self, oldState, newState, action):
        pass