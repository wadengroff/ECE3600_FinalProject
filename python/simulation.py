
import matplotlib.pyplot as plt
import numpy as np
import random
import pandas as pd
import math

from Ups import Ups
from redundancyN import redundancyN
from redundancyIsolated import redundancyIsolated
from redundancyNp1 import redundancyNp1
from redundantCatcher import redundantCatcher
from actual_number import convert_ratio_to_watts

capacity = 36*1000 # in watts
convert_ratio_to_watts(capacity)

input_file = 'cella_pdu6_hourly_watts.csv'
df = pd.read_csv(input_file)
load_power_data = df['actual_power_watts']

simHours = 365*24
times = np.zeros(simHours)
loads = np.zeros(simHours)
supplies = np.zeros(simHours)


def genGaussian(mean, dev):
    result = 0
    for i in range(8):
        result += random.random() # from 0.0 to 1.0
    # Generates mean of 4
    result -= 4
    # Variance of each component is 1/12
    # they sum because independent => total variance = 2/3  => std dev = sqrt(2/3)
    result *= math.sqrt(3/2) # Make 1 variance
    result *= dev
    result += mean
    return result
    



ups_fr = 0.000364    # Failure rate (probability to enter bypass in any given hour)
ups_mbc = capacity*3   # Max Battery Capacity (watt hours)
ups_sp = 15      # Static power consumption in Watts (consumed with/without load)
ups_e = 0.98     # Efficiency passing input power to load/battery
ups_be = 0.8     # Battery Efficiency (when converting to power out)
ups_mbd = capacity    # Max battery power draw
ups_cr = 0.1     # Charge rate for battery (in percent of max capacity)
ups_mtime = 48   # Maintenance time for ups (time to fix static bypass problems)


instN = redundancyN(ups_fr, ups_mbc, ups_sp, ups_e, ups_be, ups_mbd, ups_cr, ups_mtime, simHours)
instIso = redundancyIsolated(ups_fr, ups_mbc, ups_sp, ups_e, ups_be, ups_mbd, ups_cr, ups_mtime, simHours)
instNp1 = redundancyNp1(ups_fr, ups_mbc, ups_sp, ups_e, ups_be, ups_mbd, ups_cr, ups_mtime, simHours)
instCatcher = redundantCatcher(ups_fr, ups_mbc, ups_sp, ups_e, ups_be, ups_mbd, ups_cr, ups_mtime, simHours)


for i in range(0,simHours):
    times[i] = i

    seriesInd = i % len(load_power_data)
    load = load_power_data[seriesInd]
    load_offset = random.randint(round(-capacity*0.05), round(capacity*0.05))
    load += load_offset

    #supply = random.randint(round(capacity*0.69), round(capacity*0.76))
    supply = genGaussian(capacity*0.74, capacity*0.02)

    instN.stepHour(load, supply, i)
    instIso.stepHour(load, supply, i)
    instNp1.stepHour(load, supply, i)
    instCatcher.stepHour(load, supply, i)

    loads[i] = load
    supplies[i] = supply
    

# Grab all main statistics
N_power_drawn = instN.get_power_draw()
N_avg_power = N_power_drawn.sum() / simHours
N_deficit = instN.get_total_deficit()
N_hoursDeficit = instN.get_deficit_hours()
N_percentDown = 100 * N_hoursDeficit / simHours
N_unprotectedHours = instN.get_unprotected_hours()

Np1_power_drawn = instNp1.get_power_draw()
Np1_avg_power = Np1_power_drawn.sum() / simHours
Np1_deficit = instNp1.get_total_deficit()
Np1_hoursDeficit = instNp1.get_deficit_hours()
Np1_percentDown = 100 * Np1_hoursDeficit / simHours
Np1_unprotectedHours = instNp1.get_unprotected_hours()

iso_power_drawn = instIso.get_power_draw()
iso_avg_power = iso_power_drawn.sum() / simHours
iso_deficit = instIso.get_total_deficit()
iso_hoursDeficit = instIso.get_deficit_hours()
iso_percentDown = 100 * iso_hoursDeficit / simHours
iso_unprotectedHours = instIso.get_unprotected_hours()

catcher_power_drawn = instCatcher.get_power_draw()
catcher_avg_power = catcher_power_drawn.sum() / simHours
catcher_deficit = instCatcher.get_total_deficit()
catcher_hoursDeficit = instCatcher.get_deficit_hours()
catcher_percentDown = 100 * catcher_hoursDeficit / simHours
catcher_unprotectedHours = instCatcher.get_unprotected_hours()

# Plot main statistics as a grouped bar graph
models = ("N", "Iso", "N+1", "Catcher")
stats = {
    'Average Power': (N_avg_power/1000, iso_avg_power/1000, Np1_avg_power/1000, catcher_avg_power/1000),
    'Percent Downtime': (N_percentDown, iso_percentDown, Np1_percentDown, catcher_percentDown)
}

x = np.arange(len(models))  # the label locations
width = 0.25  # the width of the bars
multiplier = 0

fig, ax0 = plt.subplots(layout='constrained')
ax1 = ax0.twinx() 
axes = [ax0, ax1]

colors = ['tab:blue', 'tab:green']

i = 0
for attribute, measurement in stats.items():
    offset = width * multiplier

    rects = axes[i].bar(x + offset, measurement, width, label=attribute, color=colors[i])
    axes[i].bar_label(rects, padding=3)
    multiplier += 1
    i += 1


# Add some text for labels, title and custom x-axis tick labels, etc.
ax0.set_ylabel('Power (kW)')
ax0.set_xticks(x + width, models)
ax0.legend(loc='upper left', ncols=2)
ax0.set_ylim(capacity*0.7/1000, capacity*0.76/1000)

ax1.set_ylabel('Percent Downtime')
ax1.legend(loc='upper right', ncols=2)
ax1.set_ylim(0, 100)

plt.title("Power Draw and Portion Downtime for UPS Models")


# Plot supply and load over time
plt.figure(2)
plt.plot(times, supplies, label='Supply')
plt.plot(times, loads, label='load')
plt.title("Supply and load over time")
plt.legend() 

# Plot battery charges for N+1 over time
np1Batt0 = instNp1.get_batt0()
np1Batt1 = instNp1.get_batt1()
plt.figure(3)
plt.plot(times, np1Batt0, label='Battery 0')
plt.plot(times, np1Batt1, label='Battery 1')
plt.title("Battery Charges over Time for N+1")
plt.legend() 


# Plot catcher model charges over time
catchBatt0 = instCatcher.get_batt0()
catchBatt1 = instCatcher.get_batt1()
catchBatt2 = instCatcher.get_batt2()
plt.figure(4)
plt.plot(times, catchBatt0, label='Battery 0')
plt.plot(times, catchBatt1, label='Battery 1')
plt.plot(times, catchBatt2, label='Battery 2')
plt.title("Battery Charges over Time for Catcher")
plt.legend() 


plt.show()