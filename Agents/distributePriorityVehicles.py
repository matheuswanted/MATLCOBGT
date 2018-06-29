#!/usr/bin/env python
import xml.etree.ElementTree as ET
import os
import optparse

commonTypeLabel = 'regularVeh'
highPriorityLabel = 'priorityVeh'

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

def get_options():
    optParser = optparse.OptionParser()
    optParser.add_option("-f", help="folder")
    options, args = optParser.parse_args()
    return options

if __name__ == "__main__":
    options = get_options()
    folder = options.f
    route = folder + '/poa.rou.xml'
    network = folder + '/poa.net.xml'
    link = folder + '/poa.link.xml'
    dump = folder + '/poa.dump.xml'
    config = folder + '/poa.sumocfg'
    proportions = [10, 100, 1000]

    tripinfoMacro = folder + '/tripinfo%s.xml'
    statisticsMacro = folder + '/statistics%s.csv'
    resultsST = []
    resultsP = []
    resultsNP = []
    for proportion in proportions:
        priorityRoute = distributeVehiclesOnRoutes(route, proportion)
        priorityTripinfo = destinationPath(proportion,tripinfoMacro)
        priorityConfig = configFileSetRoute(config,priorityRoute,proportion)
        os.system("./runner.py -c %s -t %s --nopriority --nogui"%(priorityConfig, priorityTripinfo%'NP'))
        os.system("./runner.py -c %s -t %s --nogui"%(priorityConfig, priorityTripinfo%'P'))
        os.system("sumo -c %s --tripinfo-output %s --ignore-route-errors"%(priorityConfig,  priorityTripinfo%'ST'))
        resultsP.append(priorityTripinfo%'P')
        resultsST.append(priorityTripinfo%'ST')
        resultsNP.append(priorityTripinfo%'NP')
    os.system("python ./statistics.py -t %s -o %s"%(','.join(resultsP),statisticsMacro%'P'))
    os.system("python ./statistics.py -t %s -o %s"%(','.join(resultsNP),statisticsMacro%'NP'))
    os.system("python ./statistics.py -t %s -o %s"%(','.join(resultsST),statisticsMacro%'ST'))

