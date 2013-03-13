from Card import Card
import random
from game import Agent

class LearningAgent(Agent):
    def __init__(self, epsilon, alpha):
        Agent.__init__(self)
        self.epsilon = epsilon
        self.cardsWeights={}
        self.cardsFeat={}
        self.discount = 1
        self.alpha = alpha

    def getActionCard(self, state):
        legalActions = self.getLegalActions(state)
        if self.flip(self.epsilon):
            action = random.choice(legalActions)
        else:
            action = self.getCardPolicy(state, legalActions)
        return action

    def getActionCall(self, state):
        return False

    def getLegalActions(self, state):
        legalActions = []
        for card in state.agentCards:
            for value in self.legalValues(state):
                for i in range(4):
                    newAction = (card, Card(value, i))
                    legalActions.append(newAction)
        return legalActions

    def getCardPolicy(self, state, legalActions):
        bestActions = []
        bestVal = None
        for action in legalActions:
            actionVal = self.getCardQValue(state, action)
            if bestVal == None: bestVal = actionVal
            if actionVal == bestVal:
                bestActions.append(action)
            if actionVal > bestVal:
                bestActions = [action]
                bestVal = actionVal
        if len(bestActions) == 0:
            assert True,"no actions"
        finalAction = random.choice(bestActions)
        return finalAction

    def getCardQValue(self, state, action):
        QVal = 0
        stateFeat = self.getCardFeatures(state, action)
        if len(self.cardsWeights) == 0:
            self.cardsWeights = self.cardsWeights.fromkeys(stateFeat,1)
        for feature in stateFeat:
            featVal = stateFeat[feature]*self.cardsWeights[feature]
            QVal += featVal
        return QVal

    def getCardValue(self, state):
        bestVal = None
        for action in self.getLegalActions(state):
            actionVal = self.getCardQValue(state, action)
            if bestVal == None: bestVal = actionVal
            bestVal = max(actionVal, bestVal)
        assert bestVal != None, "no actions in value calculating"
        return bestVal

    def flip(self, p):
        return True if random.random() < p else False

    def getCardFeatures(self, state, action):
        features = {}
        features['numOfMyCards'] = state.cardLengths[state.agentNum]
        features['numOfCardsInDeck'] = state.cardLengths[0]
        features['timeSinceLastCall'] = state.turnsSinceLastLie
        features['amILying'] = action[0].isSameValue(action[1])
        for i in range(state.numOfPlayers+1):
            if i != state.agentNum and i != 0:
                playerNum = 'player' + str(i)
                features[playerNum] = state.cardLengths[i]
        return features

    def inform(self, oldState,action,newState):
        reward = 0
        agentNum = oldState.agentNum
        myDeckChange = oldState.cardLengths[agentNum] - newState.cardLengths[agentNum]
        playersDeckChange = 0
        for i in range(oldState.numOfPlayers):
            if i != agentNum and i != 0:
                playersDeckChange = playersDeckChange + oldState.cardLengths[i] - newState.cardLengths[i]
        reward = -myDeckChange + playersDeckChange/oldState.numOfPlayers
        self.update(oldState, action, newState, reward)

    def update(self, state, action, nextState, reward):
        stateFeat = self.getCardFeatures(state, action)
        correction = reward + self.discount*self.getCardValue(nextState) - self.getCardQValue(state, action)
        for feature in stateFeat:
            adding = self.alpha*correction*stateFeat[feature]
            self.cardsWeights[feature] += adding