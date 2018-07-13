import csv
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

folder = 'Poa2'
returnFile = folder + '/result.csv'
size = 10
metrics = dict()
fieldnames = ['Total number of vehicles','Average departure delay', 'Average vehicular waiting time', 'Average vehicular travel time',
            'Average vehicular travel length','Average vehicular travel speed']
statisticsMacro='/statistics%s.csv'
executions = ['P','NP','ST']


def avg_csvs_statis(files):
    metrics =  dict()
    cont = dict()
    for file in files:
        with open(file) as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                key = row['Scenario'].split('/')[1]
                if not metrics.has_key(key) :
                    metrics[key] = dict()
                    cont[key] = dict()
                for field in fieldnames:  
                    metrics[key][field] = float(row[field])+metrics[key][field] if metrics[key].has_key(field) else float(row[field])
                    cont[key][field] = cont[key][field]+1 if cont[key].has_key(field) else 1
    for key in metrics:
        for field in fieldnames:
            metrics[key][field] = metrics[key][field]/cont[key][field]
    return metrics

def get_simulationfiles(range):
    files = []
    for x in range:
        files =files + get_exections_from_simu('simu'+str(x))
    return files

def get_exections_from_simu(prefix):
    files = []
    for execution in executions:
        files.append(prefix+statisticsMacro%execution)
    return files

def save_csv(metrics):
    with open(returnFile, 'w') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=['Scenario']+fieldnames)
        writer.writeheader()
        for key, val in metrics.items():
            for field in fieldnames:  
                val[field] = str(val[field])  
            val['Scenario']=key
            writer.writerow(val)

def print_graph(metrics, field, prefix):
    columns = ['All','Regular','Emergency']
    cValues = ['','regularVeh','priorityVeh']
    distributions = [10,100,1000]
    macroMethod='1per%s.tripinfo%s.xml%s'
    with open(returnFile, 'w') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=['Scenario']+fieldnames)
        writer.writeheader()
        for execution in executions:
            dicti = dict()
            dicti['Distribution'] = distributions
            for dist in distributions:
                dicti[str(dist)] = []
                for index in range(0,3):
                    key = macroMethod%(str(dist),execution,cValues[index])
                    dicti[str(dist)].append(float(metrics[key][field]))
            df2 = pd.DataFrame(dicti, columns=['Distribution']+columns)
            print(df2)
            pl = df2.plot.bar(label=df2['Distribution'][0])
            print(pl)
            fig = pl.get_figure()
            fig.savefig(prefix+field+execution+".png")
            return


def print_all_graphs(range):
    for x in range:
        m = avg_csvs_statis(get_exections_from_simu('simu'+str(x))) 
        print_graph(m,fieldnames[2],str(x))

print_all_graphs(range(1,2))

#print_graph(avg_csvs_statis(get_simulationfiles(range(4,10))), fieldnames[2], '')
#print_graph(avg_csvs_statis(get_exections_from_simu('simu1')), fieldnames[2])