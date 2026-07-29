class contract:
    def __init__(self, l, alfa, beita):
        self.l = l
        self.f = self.l/2
        self.alfa = alfa
        self.beita = beita
        #print('The contract conditions : ', self.l, self.f, self.alfa, self.beita)

    def introduce_self(self):
        print("The grid ask to reduce", self.l, "kWh", "in this contract", )
        print("The penalty of this contract is: ", self.f, "$")
        print('With the variables: ', 'alfa=', self.alfa, 'beita=', self.beita)