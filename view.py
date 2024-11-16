import pandas as pd
import matplotlib.pyplot as plt
import os

INST_COL = "Inj Gas Meter Volume Instantaneous"
SETPOINT_COL = "Inj Gas Meter Volume Setpoint"
VALVE_COL = "Inj Gas Valve Percent Open"

def readAll():
	data = pd.DataFrame()
	i = 0
	for filename in os.listdir("./data"):
		if i >= 5: break
		i += 1
		df = pd.read_csv("./data/" + filename)
		df = df.ffill().bfill()
		df['Inst/Set/Valve'] = df[INST_COL]/df[SETPOINT_COL]/(df[VALVE_COL])
		
		data = pd.concat([data, df])
	
	return data

def computeMeanSD(data: pd.DataFrame):
	sorted_data = data.sort_values(by="Inst/Set/Valve", ascending=False)
	sorted_top = sorted_data['Inst/Set/Valve'].head(int(.8*len(sorted_data['Inst/Set/Valve'])))
	return (sorted_top.mean(), sorted_top.std())

data = readAll()
(mean, sd) = computeMeanSD(data)

data.plot.scatter(x='Time', y='Inst/Set/Valve')
y = [mean - 2*sd for _ in range(len(data['Time']))]
print(mean)
plt.plot(data['Time'], y, color="red")
plt.show()