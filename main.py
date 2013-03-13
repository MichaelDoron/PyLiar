from game import Game
from NaiveAgent import NaiveAgent
from LearningAgent import LearningAgent

def main():
    num = 2
    agents = [NaiveAgent() for i in range(num-1)]
    agents.append(LearningAgent(0.5, 1))
    game = Game(agents)
    game.play()

if __name__  == "__main__":
    main()