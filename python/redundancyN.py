

from Ups import Ups


import numpy as np

class redundancyN:


    def __init__(self, ups_fr, ups_mbc, ups_sp, ups_e, ups_cr, mtime, simHours):
        
        # Initialize the single UPS
        self.ups = Ups(ups_fr, ups_mbc, ups_sp, ups_e, ups_cr, 0)
        self.maintenanceTime = mtime
        self.staticBypassCounter = 0
        self.battery_capacities = np.zeros(simHours)
        self.power_drawn = np.zeros(simHours)
        self.overdraw = 0
        self.overdrawHours = 0

    # each step will be one hour every time
    def stepHour(self, load, utility, hour):
        power = self.ups.step(load, utility)
        
        od = self.ups.get_overdraw()
        if (od != 0):
            self.overdraw += od
            self.overdrawHours += 1


        if self.ups.get_static_bypass():
            self.staticBypassCounter += 1
        
        if (self.staticBypassCounter == self.maintenanceTime):
            self.ups.set_static_bypass()
            self.staticBypassCounter = 0

        if (hour >= self.battery_capacities.size or hour < 0):
            print("Hour doesn't make sense")
        else:
            self.battery_capacities[hour] = self.ups.get_battery_cap()
            self.power_drawn[hour] = power

        if self.ups.get_static_bypass():
            return utility > load
        else:
            return od == 0
    
    def get_battery_capacities(self):
        return self.battery_capacities
    
    def get_power_draw(self):
        return self.power_drawn
    
    def get_total_overdrawn(self):
        return self.overdraw
    
    def get_overdrawn_hours(self):
        return self.overdrawHours
        
