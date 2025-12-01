
import matplotlib.pyplot as plt
import numpy as np
import random
from Ups import Ups
from redundancyN import redundancyN

simHours = 356*24
times = np.zeros(simHours)
loads = np.zeros(simHours)
supplies = np.zeros(simHours)

# RedundancyN parameters:
#   ups_fr   = failure rate (probability to enter bypass in any given hour)
#   ups_mbc  = max batter capacity (in watt hours)
#   ups_sp   = static power consumption in Watts (consumed with/without load)
#   ups_e    = efficiency of system (Power out/Power in, aka usable energy)
#   ups_cr   = charge rate of the battery (in percent charge per hour)
#   mtime    = time (in hours) to repair problems with a ups
#   simHours = length of the simulation in hours
inst = redundancyN(0.01, 100, 15, 0.8, 0.1, 48, simHours)

staticBypassCounter = 0
failedHours = 0


for i in range(0,simHours):
    times[i] = i

    load = random.randint(0, 200)
    supply = random.randint(150, 300)
    
    if not inst.stepHour(load, supply, i):
        failedHours += 1

    loads[i] = load
    supplies[i] = supply
    # powerDrawn[i] = inst.step(load, supply)
    #batteryCap[i] = ups0.get_battery_cap()


batteryCap = inst.get_battery_capacities()
powerDrawn = inst.get_power_draw()

print("---- FINISHED SIMULATION ----\n\n")

avgPower = powerDrawn.sum() / simHours
print("Average power consumption was", avgPower)
print("")

avgLoadPower = loads.sum() / simHours
print("Average load power requirement was", avgLoadPower)
print("")

print("Failed for", failedHours/24, "days")
print("i.e.", 100*failedHours/(simHours), "Percent failure\n")

print("Overdrew power for", inst.get_overdrawn_hours(), "hours")
print("Total power overdrawn was", inst.get_total_overdrawn(), "Watts")


plt.figure(0)
plt.plot(times, batteryCap)
plt.title("Battery Capacity over time")
plt.xlabel("Time (hours)")
plt.ylabel("Battery Capacity (Watt-Hours)")

plt.figure(1)
plt.plot(times, powerDrawn)
plt.title("Power Drawn by UPS over time")
plt.xlabel("Time (hours)")
plt.ylabel("Power Drawn from Supply (Watts)")

plt.figure(2)
plt.plot(times, supplies, label='Supply')
plt.plot(times, loads, label='load')
plt.title("Supply and load over time")

plt.show()