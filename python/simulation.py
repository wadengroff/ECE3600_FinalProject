
import matplotlib.pyplot as plt
import numpy as np
import random
from Ups import Ups
from redundancyN import redundancyN
from redundancyIsolated import redundancyIsolated
from redundancyNp1 import redundancyNp1

simHours = 28*24
times = np.zeros(simHours)
loads = np.zeros(simHours)
supplies = np.zeros(simHours)

ups_fr = 0.01    # Failure rate (probability to enter bypass in any given hour)
ups_mbc = 5000   # Max Battery Capacity (watt hours)
ups_sp = 15      # Static power consumption in Watts (consumed with/without load)
ups_e = 0.95     # Efficiency passing input power to load/battery
ups_be = 0.8     # Battery Efficiency (when converting to power out)
ups_mbd = 500    # Max battery power draw
ups_cr = 0.1     # Charge rate for battery (in percent of max capacity)
ups_mtime = 48   # Maintenance time for ups (time to fix static bypass problems)


instN = redundancyN(ups_fr, ups_mbc, ups_sp, ups_e, ups_be, ups_mbd, ups_cr, ups_mtime, simHours)
instIso = redundancyIsolated(ups_fr, ups_mbc, ups_sp, ups_e, ups_be, ups_mbd, ups_cr, ups_mtime, simHours)
instNp1 = redundancyNp1(ups_fr, ups_mbc, ups_sp, ups_e, ups_be, ups_mbd, ups_cr, ups_mtime, simHours)


for i in range(0,simHours):
    times[i] = i

    load = random.randint(500, 2000)
    supply = random.randint(1500, 3000)
    
    instN.stepHour(load, supply, i)
    instIso.stepHour(load, supply, i)
    instNp1.stepHour(load, supply, i)

    loads[i] = load
    supplies[i] = supply
    


batteryCap = instN.get_battery_capacities()
powerDrawn = instN.get_power_draw()

print("---- FINISHED SIMULATION ----\n\n")

avgPower = powerDrawn.sum() / simHours
print("N Average power consumption was", avgPower)
print("")

avgLoadPower = loads.sum() / simHours
print("Average load power requirement was", avgLoadPower)
print("")

failedHours = instN.get_deficit_hours()
print("N Failed for", failedHours/24, "days")
print("i.e.", 100*failedHours/(simHours), "Percent failure\n")

print("N Overdrew power for", instN.get_deficit_hours(), "hours")
print("Total power overdrawn was", instN.get_total_deficit(), "Watts")
print("\n\n")


print("Isolated Redundancy Model:")
isoPower = instIso.get_power_draw()
print("Isolated drew average of", isoPower.sum()/simHours)
print("Total power of", isoPower.sum())
print("")

isoFailedHours = instIso.get_deficit_hours()
print("Iso failed for", isoFailedHours/24, "days")
print("i.e.", 100*isoFailedHours/(simHours), "Percent failure\n")

isoMultiplier = isoPower.sum()/powerDrawn.sum()
print("Isolated redundancy drew", isoMultiplier, "Times the power of N")
print("Failed for", failedHours/isoFailedHours, "times fewer hours")


print("\n\n")
print("N+1 Redundancy Model:")
np1Power = instNp1.get_power_draw()
print("N+1 drew average of", np1Power.sum()/simHours)
np1FailedHours = instNp1.get_deficit_hours()
print("N+1 failed for", np1FailedHours/24, "days")
print("i.e.", 100*np1FailedHours/simHours, "Percent failure\n")

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

np1Batt0 = instNp1.get_batt0()
np1Batt1 = instNp1.get_batt1()
plt.figure(3)
plt.plot(times, np1Batt0, label='Battery 0')
plt.plot(times, np1Batt1, label='Battery 1')
plt.title("Battery Charges over Time for N+1")

plt.show()