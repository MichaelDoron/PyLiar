from Card import Card
import random
from game import Agent

class LearningAgent(Agent):
    def __init__(self, epsilon, alpha):
        Agent.__init__(self)
        self.epsilon = epsilon
        self.cardsWeights={}
        self.callWeights = {}
        self.discount = 1
        self.alpha = alpha
        self.legalCalls = [True, False]

    def getActionCard(self, state):
        legalActions = self.getLegalCardActions(state)
        return self.chooseActionWisely(state, legalActions)

    def getActionCall(self, state):
        return self.chooseActionWisely(state, self.legalCalls)

    def getLegalCardActions(self, state):
        legalActions = []
        for card in state.agentCards:
            for value in self.legalValues(state):
                for i in range(4):
                    newAction = (card, Card(value, i))
                    legalActions.append(newAction)
        return legalActions

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

    def informCard(self, oldState,action,newState):
        reward = 0
        agentNum = oldState.agentNum
        myDeckChange = oldState.cardLengths[agentNum] - newState.cardLengths[agentNum]
        playersDeckChange = 0
        for i in range(oldState.numOfPlayers):
            if i != agentNum and i != 0:
                playersDeckChange = playersDeckChange + oldState.cardLengths[i] - newState.cardLengths[i]
        reward = -myDeckChange + playersDeckChange/oldState.numOfPlayers
        legalActions = self.getLegalCardActions(newState)
        self.update(oldState, action, newState, reward, legalActions)

    def getCallFeatures(self, state, action):
        features = {}
        features['numOfMyCards'] = state.cardLengths[state.agentNum]
        features['numOfCardsInDeck'] = state.cardLengths[0]
        features['timeSinceLastCall'] = state.turnsSinceLastLie
        features['suspectNumOfCards']= state.cardLengths[state.turnNum]
        features['doIHaveThisCard'] = self.checkIfIHaveThisCard(state)
        features['haveISeenThisCard'] = self.haveISeenThisCard(state)
        return features

    def informCall(self, oldState ,action, newState):
        reward = 0
        agentNum = oldState.agentNum
        myDeckChange = oldState.cardLengths[agentNum] - newState.cardLengths[agentNum]
        playersDeckChange = 0
        for i in range(oldState.numOfPlayers):
            if i != agentNum and i != 0:
                playersDeckChange = playersDeckChange + oldState.cardLengths[i] - newState.cardLengths[i]
        reward = -myDeckChange + playersDeckChange/oldState.numOfPlayers
        self.update(oldState, action, newState, reward, self.legalCalls)

    def haveISeenThisCard(self, state):
        return False

    def featuresSwitch(self, state, action):
        return self.getCardFeatures(state, action) if state.agentNum == state.turnNum else\
               self.getCallFeatures(state, action)

    def weightSwitch(self, state):
        return self.cardsWeights if state.agentNum == state.turnNum else\
        self.callWeights

    def chooseActionWisely(self, state, legalActions):
        if self.flip(self.epsilon):
            action = random.choice(legalActions)
        else:
            action = self.getPolicy(state, legalActions)
        return action

    def getPolicy(self, state, legalActions):
        bestActions = []
        bestVal = None
        for action in legalActions:
            actionVal = self.getQValue(state, action)
            if bestVal is None: bestVal = actionVal
            if actionVal == bestVal:
                bestActions.append(action)
            if actionVal > bestVal:
                bestActions = [action]
                bestVal = actionVal
        assert len(bestActions) > 0, "no legal card calls"
        finalAction = random.choice(bestActions)
        return finalAction

    def getQValue(self, state, action):
        QVal = 0
        stateFeat = self.featuresSwitch(state, action)
        weights = self.weightSwitch(state)
        if len(weights) == 0:
            weights = weights.fromkeys(stateFeat,1)
        for feature in stateFeat:
            featVal = stateFeat[feature]*weights[feature]
            QVal += featVal
        return QVal

    def getValue(self, state, legalActions):
        if len(state.agentCards) == 0:
            return 100
        bestVal = None
        for action in legalActions:
            actionVal = self.getQValue(state, action)
            if bestVal is None: bestVal = actionVal
            bestVal = max(actionVal, bestVal)
        return bestVal

    def update(self, state, action, nextState, reward, legalActions):
        stateFeat = self.featuresSwitch(state, action)
        weights = self.weightSwitch(state)
        correction = reward + self.discount*self.getValue(nextState, legalActions) - self.getQValue(state, action)
        for feature in stateFeat:
            adding = self.alpha*correction*stateFeat[feature]
            weights[feature] += adding

    def flip(self, p):
        return True if random.random() < p else False


