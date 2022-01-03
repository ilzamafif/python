import smartpy as sp

class Calculator(sp.Contract):
    def __init__(self):
        self.init(value = 0)

    @sp.entry_point
    def multiply(self, x, y):
        self.data.value = x * y
    
    @sp.add_test(name = "Calculator")
    def test():
        c1 = Calculator()
        scenario = sp.test_scenario()
        scenario += c1
        scenario += c1.multiply(x = 5, y = 6)