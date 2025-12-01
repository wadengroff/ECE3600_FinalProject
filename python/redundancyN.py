

from Ups import Ups


import numpy as np

class redundancyN:


    def __init__(self, ups_fr, ups_mbc, ups_sp, ups_e, ups_be, ups_mbd, ups_cr, mtime, simHours):
        
        # Initialize the single UPS
        self.ups = Ups(ups_fr, ups_mbc, ups_sp, ups_e, ups_be, ups_mbd, ups_cr, mtime, 0)
        self.battery_capacities = np.zeros(simHours)
        self.power_drawn = np.zeros(simHours)
        self.deficit = 0
        self.deficitHours = 0

    # each step will be one hour every time
    def stepHour(self, load, utility, hour):
        power = self.ups.step(load, utility)
        
        deficit = self.ups.get_deficit()
        if (deficit != 0):
            self.deficit += deficit
            self.deficitHours += 1


        if (hour >= self.battery_capacities.size or hour < 0):
            print("Hour doesn't make sense")
        else:
            self.battery_capacities[hour] = self.ups.get_battery_cap()
            self.power_drawn[hour] = power

        return deficit == 0
    
    def get_battery_capacities(self):
        return self.battery_capacities
    
    def get_power_draw(self):
        return self.power_drawn
    
    def get_total_deficit(self):
        return self.deficit
    
    def get_deficit_hours(self):
        return self.deficitHours
        
