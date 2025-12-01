from Ups import Ups


import numpy as np

class redundancyIsolated:


    def __init__(self, ups_fr, ups_mbc, ups_sp, ups_e, ups_be, ups_mbd, ups_cr, ups_mtime, simHours):
        
        # Initialize the single UPS
        self.primaryUps = Ups(ups_fr, ups_mbc, ups_sp, ups_e, ups_be, ups_mbd, ups_cr, ups_mtime, 0)
        self.secondaryUps = Ups(ups_fr, ups_mbc, ups_sp, ups_e, ups_be, ups_mbd, ups_cr, ups_mtime, 0)
        self.ups_efficiency = ups_e
        self.prim_batt_capacities = np.zeros(simHours)
        self.sec_batt_capacities = np.zeros(simHours)
        self.power_drawn = np.zeros(simHours)
        self.prim_power_drawn = np.zeros(simHours)
        self.sec_power_drawn = np.zeros(simHours)
        self.deficit = 0
        self.deficitHours = 0

    # each step will be one hour every time
    def stepHour(self, load, utility, hour):
        # Check if primary in static bypass
        if self.primaryUps.get_static_bypass():
            # Secondary takes on full load, plus efficiency losses through primary
            sec_load = load / self.ups_efficiency
            power_sec = self.secondaryUps.step(sec_load, utility)
            prim_supply = sec_load - self.secondaryUps.get_deficit()
            power_prim = self.primaryUps.step(load, prim_supply)
        else:
            power_sec = self.secondaryUps.step(0, utility)
            power_prim = self.primaryUps.step(load, utility)

        self.prim_power_drawn[hour] = power_prim
        self.sec_power_drawn[hour] = power_sec
        self.power_drawn[hour] = power_prim + power_sec
        self.prim_batt_capacities[hour] = self.primaryUps.get_battery_cap()
        self.sec_batt_capacities[hour] = self.secondaryUps.get_battery_cap()

        mainDeficit = self.primaryUps.get_deficit()
        if mainDeficit != 0:
            self.deficit += mainDeficit
            self.deficitHours += 1
            return False
        else:
            return True
        
    def get_power_draw(self):
        return self.power_drawn
    
    def get_sec_power(self):
        return self.sec_power_drawn
    
    def get_prim_power(self):
        return self.prim_power_drawn
        
    def get_prim_batt(self):
        return self.prim_batt_capacities
    
    def get_sec_batt(self):
        return self.sec_batt_capacities
    
    def get_total_deficit(self):
        return self.deficit
    
    def get_deficit_hours(self):
        return self.deficitHours

