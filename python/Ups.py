

import random


class Ups:

    def __init__(self, fr, mbc, sp, e, cr, id):
        self.failure_rate = fr    # probability to enter bypass
        self.max_battery_cap = mbc     # Battery capacity in watt hours
        self.battery_cap = self.max_battery_cap
        self.static_power = sp    # power consumption when load idle
        self.efficiency = e       # Power out / Power in
        self.charge_rate = cr     # Charging rate (percent charge/hour, consider linear)
        self.static_bypass = False
        self.id = id
    
    def step(self, load, supply): # Step one hour
        randNum = random.random() # [0.0, 1.0)
        print(randNum)
        if (randNum < self.failure_rate):
            self.static_bypass = True # switch to bypass if internal error
            print("Entering Static bypass mode on ups", self.id)
        else:
            print("Not entering bypass on ups", self.id)
            powerLeft = load - supply
            if (powerLeft < 0):
                # use battery power
                self.battery_cap -= load # watt hours - load watts * 1hour step
                self.battery_cap += 
        

    def get_static_bypass(self):
        return self.static_bypass
    
    