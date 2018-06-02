#!/usr/bin/env python
import os
import sys
import optparse
import subprocess
import random
import shutil

def get_options():
    optParser = optparse.OptionParser()
    optParser.add_option('-t', help="path to *.trips.xml")
    optParser.add_option('-n', help='path to *.net.xml')
    optParser.add_option('-o', help='output file')
    optParser.add_option('-i', help="number of iterations of duarouter")
    return optParser.parse_args()

def getTmpFolder(paths):
    folderPath = '.'
    for i in range(0,len(paths)-1):
        folderPath += '/' + paths[i]
    folderPath += '/tmp'
    return folderPath

def getTmpFile(path):
    paths = path.split('/')
    return '../' + paths[len(paths)-1]

def mkdir(dirPath):
    if not os.path.exists(dirPath):
        os.makedirs(dirPath)

if __name__ == "__main__":
    opts, args = get_options()
    currDir = os.getcwd()
    if not opts.t or not opts.n or not opts.i or not opts.o:
        raise Exception('Arguments -t -n -i required')
    splitted_trips = opts.t.split('/')
    tripFileSplitted = splitted_trips[len(splitted_trips)-1].split('.')
    tmp = getTmpFolder(splitted_trips)
    tmpTrip, tmpNet = getTmpFile(opts.t), getTmpFile(opts.n)
    mkdir(tmp) 
    os.chdir(tmp)

    os.system("$SUMO_HOME/tools/assign/duaIterate.py -n %s -t %s -l %s"%(tmpNet,tmpTrip,opts.i))

    os.chdir('../')
    s = ''
    s += str(int(opts.i)-1)
    if(len(s) == 1):
        s = '00'+s
    elif(len(s) == 2):
        s = '0'+s

    os.chdir(currDir)

    shutil.copyfile(tmp+'/'+tripFileSplitted[0]+'_%s.rou.xml'%(s) ,opts.o)

    shutil.rmtree(tmp)
    

