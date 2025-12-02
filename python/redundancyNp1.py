from Ups import Ups


import numpy as np



# Models the Isolated Redundancy Configuration
# 
# Diagram:
#
#         Utility
#            |
#           / \
#        UPS1  UPS2
#          \   /
#           \ /
#            |
#          load
#
# This model uses two separate UPS modules that can be of different makes, specs, etc.
# Primary UPS handles the entire load normally, unless it experiences an internal fault.
# When the primary has a fault, it switches to static bypass, which takes its input from 
# the output of the secondary UPS. Thus, the entire load is instantly transferred to
# the Secondary UPS
class redundancyNp1:

    def __init__(self, ups_fr, ups_mbc, ups_sp, ups_e, ups_be, ups_mbd, ups_cr, ups_mtime, simHours):
        self.ups0 = Ups(ups_fr, ups_mbc, ups_sp, ups_e, ups_be, ups_mbd, ups_cr, ups_mtime, 0)
        self.ups1 = Ups(ups_fr, ups_mbc, ups_sp, ups_e, ups_be, ups_mbd, ups_cr, ups_mtime, 0)
        self.ups_static_power = ups_sp
        self.batt_capacities0 = np.zeros(simHours)
        self.batt_capacities1 = np.zeros(simHours)
        self.power_drawn = np.zeros(simHours)
        self.power_drawn0 = np.zeros(simHours)
        self.power_drawn1 = np.zeros(simHours)
        self.totalDeficit = 0
        self.deficitHours = 0
        self.unprotectedHours = 0

    def stepHour(self, load, utility, hour):
        idealLoad = load / 2 # Ideally evenly distribute load
        distrUtility = utility/2
        # Neither in static bypass
        if not (self.ups0.get_static_bypass() or self.ups1.get_static_bypass()):
            max0 = self.ups0.getHighestLoad(distrUtility)
            max1 = self.ups1.getHighestLoad(distrUtility)
            deficit = 0 # Will be 0 except in one if clause
            if (max0+max1 < load):
                # Unable to support the entire load
                # Just give each the max load they can do and record deficit
                power0 = self.ups0.step(max0, distrUtility)
                power1 = self.ups1.step(max1, distrUtility)
                if (self.ups0.get_deficit() != 0):
                    print("Deficit should have been exactly 0 for ups0")
                if (self.ups1.get_deficit() != 0):
                    print("Deficit should have been exactly 0 for ups1")
                deficit = load - max0 - max1
                print("Deficit is", deficit, "With supply", utility, " and load", load)
            elif max0 >= idealLoad and max1 >= idealLoad:
                power0 = self.ups0.step(idealLoad, distrUtility)
                power1 = self.ups1.step(idealLoad, distrUtility)
            elif max0 < max1:
                power0 = self.ups0.step(load, distrUtility)
                leftover = self.ups0.get_deficit() # Get whatever is leftover for ups1
                power1 = self.ups1.step(leftover, distrUtility)
            else: # max1 < max0
                power1 = self.ups1.step(load, distrUtility)
                leftover = self.ups1.get_deficit()
                power0 = self.ups0.step(leftover, distrUtility)
            totalPower = power0 + power1

        # Both in static bypass
        elif self.ups0.get_static_bypass() and self.ups1.get_static_bypass():
            power0 = self.ups0.step(idealLoad, distrUtility)
            power1 = self.ups1.step(idealLoad, distrUtility)

            # In static bypass, load power is not included in return, so add back
            power0 += idealLoad - self.ups0.get_deficit()
            power1 += idealLoad - self.ups1.get_deficit()

            totalPower = power0 + power1

            # These deficits should both be equals
            deficit = self.ups0.get_deficit() + self.ups1.get_deficit()

            # This part seems okay
            # if deficit > 0:
            #     print("Deficit 0 in static bypass with", utility, "supply")
            #     print("Load is", load)

        # ONLY ups0 is in static bypass
        elif self.ups0.get_static_bypass():
            power1 = self.ups1.step(load, distrUtility) # Take as much from here as possible
            leftover = self.ups1.get_deficit()
            #print("Leftover:", leftover, " and utility for other=", distrUtility)
            power0 = self.ups0.step(leftover, distrUtility)

            # UPS 0 in static bypass, so load power was not included
            # Add back in here
            power0 += leftover - self.ups0.get_deficit()

            totalPower = power0 + power1
            # Total deficit will come from ups0 since it should handle deficit from 1
            deficit = self.ups0.get_deficit()

        else: # self.ups1.get_static_bypass()
            power0 = self.ups0.step(load, distrUtility)
            leftover = self.ups0.get_deficit()
            power1 = self.ups1.step(leftover, distrUtility)

            # UPS1 in static bypass, so load power was not included
            # add back here
            power1 += leftover - self.ups1.get_deficit()

            totalPower = power0 + power1
            # Total deficit will come from ups1 since it should handle deficit from 0
            deficit = self.ups1.get_deficit()

        self.batt_capacities0[hour] = self.ups0.get_battery_cap()
        self.batt_capacities1[hour] = self.ups1.get_battery_cap()

        self.power_drawn[hour] = totalPower
        self.power_drawn0[hour] = power0
        self.power_drawn1[hour] = power1

        if self.ups0.get_static_bypass() and self.ups1.get_static_bypass():
            self.unprotectedHours += 1

        if deficit != 0:
            self.totalDeficit += deficit
            self.deficitHours += 1
            return False
        else:
            return True


    def get_power_draw(self):
        return self.power_drawn

    def get_power0(self):
        return self.power_drawn0
    
    def get_power1(self):
        return self.power_drawn1
    
    def get_batt0(self):
        return self.batt_capacities0
    
    def get_batt1(self):
        return self.batt_capacities1
    
    def get_total_deficit(self):
        return self.totalDeficit
    
    def get_deficit_hours(self):
        return self.deficitHours

    def get_unprotected_hours(self):
        return self.unprotectedHours

