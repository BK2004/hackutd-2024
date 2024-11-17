import pandas as pd
import numpy as np
import os

INST_COL = "Inj Gas Meter Volume Instantaneous"
SETPOINT_COL = "Inj Gas Meter Volume Setpoint"
VALVE_COL = "Inj Gas Valve Percent Open"

well_names = []

def readAll():
	data = pd.DataFrame()
	for filename in os.listdir("./data"):
		df = pd.read_csv("./data/" + filename)
		well_name = filename[:filename.find('_')]
		well_names.append(well_name)

		df['Well'] = [well_name for _ in range(len(df['Time']))]

		df = df.ffill().bfill()
		df['Inst/Set/Valve'] = df[INST_COL] / df[SETPOINT_COL] / df[VALVE_COL]
		
		data = pd.concat([data, df])
	data['Time'] = pd.to_datetime(data['Time'])
	
	return data

def computeMeanSD(data: pd.DataFrame):
	sorted_data = data.sort_values(by="Inst/Set/Valve", ascending=False)
	sorted_top = sorted_data['Inst/Set/Valve'].head(int(0.8 * len(sorted_data['Inst/Set/Valve'])))
	return (sorted_top.mean(), sorted_top.std())

data = readAll()
(mean, sd) = computeMeanSD(data)

def getWellData(well, start_time, end_time):
	ret_data = data.loc[(data['Time'] >= start_time) & (data['Time'] <= end_time) & (data['Well'] == well)]
	return ret_data

# Mark hydrates with anomaly col (red for hydrate, '' otherwise)
def mark_anomalies(data: pd.DataFrame):
	data["anomaly"] = np.where(data['Inst/Set/Valve'] <= mean - 2*sd, True, False)