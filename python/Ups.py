

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
        self.overdraw = 0
        self.id = id
    
    # Returns the power drawn
    def step(self, load, supply): # Step one hour

        # Can only use this portion of the energy in
        usableSupply = supply * self.efficiency

        # Check if it will randomly fail
        randNum = random.random() # [0.0, 1.0)
        if (self.static_bypass or randNum < self.failure_rate):
            self.static_bypass = True # switch to bypass if internal error
            
            #print("Entering Static bypass mode on ups", self.id)
            return min(load, usableSupply)
        else:
            # Non-failure

            # Usually all power will come from the supply to load
            # If not enough, takes from battery
            powerLeft = load - usableSupply

            self.overdraw = 0

            # If negative, take from battery
            if (powerLeft > 0):
                # use battery power to fill extra space
                self.battery_cap -= powerLeft # watt hours - load watts * 1hour step
                if self.battery_cap < 0:
                    self.overdraw = -self.battery_cap
                    self.battery_cap = 0
                return supply # Using all of supply
            else:
                # If we aren't using battery, charge it with leftover power
                if (self.battery_cap < self.max_battery_cap):
                    # Joules it would charge in an hour
                    joules = min(self.max_battery_cap-self.battery_cap, self.charge_rate * self.max_battery_cap)
                    power = joules / 60 / 60 # joules per second
                    chargePower = min(power, -powerLeft)
                    self.battery_cap += chargePower * 60 * 60
                    return load / self.efficiency + chargePower
                else:
                    return min(load / self.efficiency + self.static_power, supply)
                    

        
    def get_overdraw(self):
        return self.overdraw

    def get_static_bypass(self):
        return self.static_bypass
    
    def set_static_bypass(self):
        self.static_bypass = False
    
    def get_battery_cap(self):
        return self.battery_cap
    
