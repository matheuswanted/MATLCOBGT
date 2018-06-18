#!/usr/bin/env python
import xml.etree.ElementTree as ET
import os

commonTypeLabel = 'regularVeh'
highPriorityLabel = 'priorityVeh'
folder = 'Poa2'
route = folder + '/poa.rou.xml'
network = folder + '/poa.net.xml'
link = folder + '/poa.link.xml'
dump = folder + '/poa.dump.xml'
tripinfo = folder + '/tripinfo.xml'
additional = folder + '/poa.additional.xml'
statistics = folder + '/statistics.csv'
config = folder + '/poa.sumocfg'
proportions = [10, 100, 1000]

def distributeVehiclesOnRoutes (path, proportion):
    dest = destinationPath(proportion, path)
    cont = 0
    et = ET.parse(path)
    for child in et.getroot():
        if child.tag == 'vehicle':
            child.attrib['type'] = commonTypeLabel if cont % proportion else highPriorityLabel 
            cont+=1
    et.write(dest)
    return dest

def getFile (path):
    destSplit = path.split('/')
    return destSplit[len(destSplit)-1]

def configFileSetRoute(configPath,routePath, proportion):
    dest = destinationPath(proportion, configPath)
    et = ET.parse(configPath)
    et.getroot().find('input').find('route-files').attrib['value']=getFile(routePath)
    et.write(dest)
    return dest

def destinationPath(proportion, path):
    destSplit = path.split('/')
    destSplit[len(destSplit)-1] = '1per' + str(proportion) + '.' + destSplit[len(destSplit)-1]
    return '/'.join(destSplit)

if __name__ == "__main__":
    results = []
    for proportion in proportions:
        priorityRoute = distributeVehiclesOnRoutes(route, proportion)
        priorityTripinfo = destinationPath(proportion,tripinfo)
        priorityDump = destinationPath(proportion,dump)
        priorityLink = destinationPath(proportion,link)
        priorityConfig = configFileSetRoute(config,priorityRoute,proportion)
        #os.system("./runner.py -c %s -t %s --nogui"%(priorityConfig, priorityTripinfo))
        results.append(priorityTripinfo)
    os.system("python ./statistics.py -t %s -o %s"%(','.join(results),statistics))