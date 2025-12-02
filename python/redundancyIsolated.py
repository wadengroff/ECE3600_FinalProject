from Ups import Ups


import numpy as np



# Models the Isolated Redundancy Configuration
# 
# Diagram:
#
#         Utility
#            |
#           / \
#          /  UPS2
#         |    /
#         |   /
#         UPS1
#           |
#          load
#
# This model uses two separate UPS modules that can be of different makes, specs, etc.
# Primary UPS handles the entire load normally, unless it experiences an internal fault.
# When the primary has a fault, it switches to static bypass, which takes its input from 
# the output of the secondary UPS. Thus, the entire load is instantly transferred to
# the Secondary UPS
class redundancyIsolated:


    def __init__(self, ups_fr, ups_mbc, ups_sp, ups_e, ups_be, ups_mbd, ups_cr, ups_mtime, simHours):
        
        # Initialize the single UPS
        self.primaryUps = Ups(ups_fr, ups_mbc, ups_sp, ups_e, ups_be, ups_mbd, ups_cr, ups_mtime, 0)
        self.secondaryUps = Ups(ups_fr, ups_mbc, ups_sp, ups_e, ups_be, ups_mbd, ups_cr, ups_mtime, 0)
        self.ups_static_power = ups_sp
        self.prim_batt_capacities = np.zeros(simHours)
        self.sec_batt_capacities = np.zeros(simHours)
        self.power_drawn = np.zeros(simHours)
        self.prim_power_drawn = np.zeros(simHours)
        self.sec_power_drawn = np.zeros(simHours)
        self.deficit = 0
        self.deficitHours = 0
        self.unprotectedHours = 0

    # each step will be one hour every time
    def stepHour(self, load, utility, hour):
        # Check if primary in static bypass
        if self.primaryUps.get_static_bypass():
            # Secondary takes on full load, plus efficiency losses through primary
            sec_load = load + self.ups_static_power
            power_sec = self.secondaryUps.step(sec_load, utility)
            prim_supply = sec_load - self.secondaryUps.get_deficit()
            power_prim = self.primaryUps.step(load, prim_supply)
            
            # If secondary is also in static bypass, both ups report static usage
            # Add back in the load, take minimum with utility
            if self.secondaryUps.get_static_bypass():
                self.power_drawn[hour] = min(utility, load+power_prim+power_sec)
                self.sec_power_drawn[hour] = power_sec # Secondary is only static here
                # assign the load used to primary
                self.prim_power_drawn[hour] = self.power_drawn[hour] - self.sec_power_drawn[hour]
            else:
                # If not in static bypass, secondary includes load power
                self.power_drawn[hour] = power_prim + power_sec
                self.prim_power_drawn[hour] = power_prim
                self.sec_power_drawn[hour] = power_sec
            
        
        # Otherwise, not in static bypass
        else:
            # Secondary has no load, this should be only static
            power_sec = self.secondaryUps.step(0, utility)
            # Primary includes load
            power_prim = self.primaryUps.step(load, utility)
            self.power_drawn[hour] = power_prim + power_sec
            self.prim_power_drawn[hour] = power_prim
            self.sec_power_drawn[hour] = power_sec

        
        self.prim_batt_capacities[hour] = self.primaryUps.get_battery_cap()
        self.sec_batt_capacities[hour] = self.secondaryUps.get_battery_cap()

        if self.primaryUps.get_static_bypass() and self.secondaryUps.get_static_bypass():
            self.unprotectedHours += 1

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

    def get_unprotected_hours(self):
        return self.unprotectedHours
