class generator:
    def __init__(self,ID,l,price_multiply=0.5):
        self.ID = ID
        self.l = l
        self.bid = price_multiply*l
    def introduce_self(self):
        print('generator ID: ', self.ID, 'l:', self.l,'price:', self.bid)