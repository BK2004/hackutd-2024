import pandas as pd
import numpy as np
import os

INST_COL = "Inj Gas Meter Volume Instantaneous"
SETPOINT_COL = "Inj Gas Meter Volume Setpoint"
VALVE_COL = "Inj Gas Valve Percent Open"
MIN_TIMESTAMP = 0

well_names = []

def convert_data(well_name: str, df: pd.DataFrame) -> pd.DataFrame:
	df['Well'] = [well_name] * len(df['Time'])
	df = df.ffill().bfill()
	df['Inst/Set/Valve'] = df[INST_COL] / df[SETPOINT_COL] / (df[VALVE_COL] / 100)
	return df

def read_all() -> pd.DataFrame:
	data = pd.DataFrame()
	for filename in os.listdir("./data"):
		df = pd.read_csv("./data/" + filename)
		well_name = filename.split("_")[0]
		well_names.append(well_name)

		df = convert_data(well_name, df)
		
		data = pd.concat([data, df])
	data['Time'] = pd.to_datetime(data['Time'])
	
	return data

def compute_mean_sd(data: pd.DataFrame) -> tuple[float, float]:
	sorted_data = data.sort_values(by="Inst/Set/Valve", ascending=False)
	sorted_top = sorted_data['Inst/Set/Valve'].head(int(0.8 * len(sorted_data['Inst/Set/Valve'])))
	return sorted_top.mean(), sorted_top.std()

data = read_all()
MIN_TIMESTAMP = data['Time'].min()
mean, sd = compute_mean_sd(data)

def get_well_data(well, start_time, end_time) -> pd.DataFrame:
	ret_data = data.loc[(data['Time'] >= start_time) & (data['Time'] <= end_time) & (data['Well'] == well)]
	return ret_data

# Mark hydrates with anomaly col (red for hydrate, '' otherwise)
def mark_anomalies(data: pd.DataFrame):
	data["anomaly"] = np.where(data['Inst/Set/Valve'] <= mean - 2 * sd, True, False)
