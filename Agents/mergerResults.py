import csv
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

folder = 'Simu7'
returnFile = folder + '/result.csv'
size = 10
metrics = dict()
fieldnames = ['Total number of vehicles','Average departure delay', 'Average vehicular waiting time', 'Average vehicular travel time',
            'Average vehicular travel length','Average vehicular travel speed']
statisticsMacro='/statistics%s.csv'
executions = ['P','NP','ST']
for execution in executions:
    for x in range(1, size):
        with open('simu'+str(x)+statisticsMacro%execution) as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                key = row['Scenario'].split('/')[1]
                if not metrics.has_key(key) :
                    metrics[key] = dict()
                for field in fieldnames:  
                    metrics[key][field] = float(row[field])+metrics[key][field] if metrics[key].has_key(field) else float(row[field])  

def save_csv(metrics):
    with open(returnFile, 'w') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=['Scenario']+fieldnames)
        writer.writeheader()
        for key, val in metrics.items():
            for field in fieldnames:  
                val[field] = str(val[field] / size)  
            val['Scenario']=key
            writer.writerow(val)

def print_graph(metrics, field):
    columns = ['All','Regular','Emergency']
    cValues = ['','regularVeh','priorityVeh']
    distributions = [10,100,1000]
    macroMethod='1per%s.tripinfo%s.xml%s'
    with open(returnFile, 'w') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=['Scenario']+fieldnames)
        writer.writeheader()
        for execution in executions:
            for dist in distributions:
                result = []
                for index in range(0,3):
                    key = macroMethod%(str(dist),execution,cValues[index])
                    result.append(float(metrics[key][field]))
                df2 = pd.DataFrame([result], columns=columns)
                pl = df2.plot.bar()
                fig = pl.get_figure()
                fig.savefig(field+str(dist)+execution+".png")

print_graph(metrics, fieldnames[2])