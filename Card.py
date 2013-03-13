__author__ = 'Yotam'

class Card:
    def __init__(self, value, shape):
        self.shape = shape
        self.value = value

    def getValue(self):
        return self.value

    def getShape(self):
        return self.shape

    def isSameValue(self, card):
        if card.value == self.value:
            return True;
        return False