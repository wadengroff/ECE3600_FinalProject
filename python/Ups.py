

import random


class Ups:

    def __init__(self, fr, mbc, sp, e, be, mbd, cr, mtime, id):
        self.failure_rate = fr       # probability to enter bypass
        self.max_battery_cap = mbc   # Battery capacity in watt hours
        self.battery_cap = self.max_battery_cap
        self.static_power = sp       # power consumption when load idle
        self.efficiency = e          # Power out / Power in passing straight through
        self.battery_efficiency = be # Efficiency of battery
        self.max_battery_draw = mbd  # Max power draw for the battery
        self.charge_rate = cr        # Charging rate (percent charge/hour, consider linear)
        self.static_bypass = False
        self.deficit = 0
        self.maintenanceTime = mtime
        self.maintenanceCounter = 0
        self.id = id


    def getHighestLoad(self, utility):
        batteryAvailable = self.battery_cap * self.battery_efficiency
        batteryMax = min(self.max_battery_draw, batteryAvailable)

        return utility * self.efficiency + batteryMax - self.static_power

    def step(self, load, supply): # Steps one hour

        self.deficit = 0
        randNum = random.random()
        if (self.static_bypass or randNum < self.failure_rate):
            self.static_bypass = True

            # Check if we've reached the end of the maintenance window
            self.maintenanceCounter += 1
            if self.maintenanceCounter == self.maintenanceTime:
                self.static_bypass = False
                self.maintenanceCounter = 0
            
            # assume we're still drawing static power
            # Efficiency not relevant because it's a straight connection
            supplyMin = load + self.static_power # Minimum amount needed from supply
            if supply < supplyMin:
                # have a deficit of power
                self.deficit = supplyMin - supply
            return min(self.static_power, supply) # Don't report as using load power
        else:
            # Not in static bypass

            usableSupply = supply * self.efficiency

            neededPower = load + self.static_power
            
            # If usable supply can handle load, also charge battery
            if usableSupply >= neededPower:
                powerLeft = usableSupply - neededPower
                if (self.battery_cap < self.max_battery_cap):
                    # Charge at whatever the charging rate is
                    # If that would overfill, then just take the minimum power
                    # ChargeRate(percent/hour)*MaxCap(watthours)*1hour = watt hours charged
                    wattHourCharge = min(self.charge_rate * self.max_battery_cap, self.max_battery_cap - self.battery_cap)
                    battPower = min(powerLeft, wattHourCharge) # Can only charge with the power left
                    self.battery_cap += battPower # Add the watt hours to the battery capacity
                    
                    # take the battery charging power away used power
                    powerLeft -= battPower

                    # Powerleft is in terms of usable supply power, convert back to consumed
                    supplyUsed = (usableSupply - powerLeft) / self.efficiency
                    return supplyUsed
                else:
                    # Not charging the battery, so we will just return the used supply
                    return neededPower / self.efficiency
            
            else:
                # not enough power from supply alone
                # Need power from battery to continue
                neededBatt = neededPower - usableSupply 
                availableBatt = self.battery_cap * self.battery_efficiency
                if neededBatt > self.max_battery_draw:
                    #print("Need more power from battery than can be drawn")
                    batteryUsed = min(availableBatt, self.max_battery_draw)
                    self.deficit = neededBatt - batteryUsed
                    self.battery_cap -= batteryUsed / self.battery_efficiency
                    return supply # Still using all of supply
                else:
                    # Able to draw needed power if the battery is charged enough
                    if availableBatt > neededBatt:
                        self.battery_cap -= neededBatt / self.battery_efficiency
                    else:
                        #print("Battery not charged enough")
                        self.battery_cap = 0
                        self.deficit = neededBatt - availableBatt
                    return supply # still using all of supply

        
    def get_deficit(self):
        return self.deficit

    def get_static_bypass(self):
        return self.static_bypass
    
    def set_static_bypass(self):
        self.static_bypass = False
        self.battery_cap = 0.5*self.max_battery_cap # assume battery loses charge during maintenance
    
    def get_battery_cap(self):
        return self.battery_cap
    
