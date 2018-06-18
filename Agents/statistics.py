#!/usr/bin/env python
"""
@file    networkStatistics.py
@author  Yun-Pang Floetteroed
@author  Michael Behrisch
@date    2007-02-27
@version $Id: networkStatistics.py 22608 2017-01-17 06:28:54Z behrisch $

This script is to calculate the global performance indices according to the SUMO-based simulation results.
Besides, this script is also to execute the significance test for evaluating the results from different assignment methods.
The t test and the Kruskal-Wallis test are available in this script. 
If not specified, the Kruskal-Wallis test will be applied with the assumption that data are not normally distributed.

The analyzed parameters include:
- travel length
- travel time
- travel speed
- stop time

SUMO, Simulation of Urban MObility; see http://sumo.dlr.de/
Copyright (C) 2007-2017 DLR (http://www.dlr.de/) and contributors

This file is part of SUMO.
SUMO is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 3 of the License, or
(at your option) any later version.
"""
from __future__ import absolute_import
from __future__ import print_function

import os
import sys
import datetime
import math
import operator

from xml.sax import saxutils, make_parser, handler
from optparse import OptionParser
from statisticsElements import Assign, T_Value, H_Value, VehInformationReader, getStatisticsOutput, getSignificanceTestOutput
# in /opt/sumo/tools/assign/tables.py
from tables import chiSquareTable, tTable
import xml.etree.ElementTree  as ET
def dict_to_xml(tag, d):
    '''
    Turn a simple dict of key/value pairs into XML
    '''
    elem = ET.Element(tag)
    for key, val in d.items():
        child = ET.Element('simulation')
        child.attrib['value']=key
        metricTag = ET.Element('metric')
        metricTag.attrib['id']='totalNumberOfVehicles'
        metricTag.attrib['value']=str(val.totalVeh)
        child.append(metricTag)
        metricTag = ET.Element('metric')
        metricTag.attrib['id']='total departure delay'
        metricTag.attrib['value']=str(val.totalDepartDelay)
        child.append(metricTag)
        metricTag = ET.Element('metric')
        metricTag.attrib['id']='average departure delay'
        metricTag.attrib['value']=str(val.avgDepartDelay)
        child.append(metricTag)
        metricTag = ET.Element('metric')
        metricTag.attrib['id']='total waiting time'
        metricTag.attrib['value']=str(val.totalWaitTime)
        child.append(metricTag)
        metricTag = ET.Element('metric')
        metricTag.attrib['id']='average vehicular waiting time'
        metricTag.attrib['value']=str(val.avgWaitTime)
        child.append(metricTag)
        metricTag = ET.Element('metric')
        metricTag.attrib['id']='average vehicular travel time'
        metricTag.attrib['value']=str(val.avgTravelTime)
        child.append(metricTag)
        child.attrib['value']=key
        metricTag = ET.Element('metric')
        metricTag.attrib['id']='total travel time'
        metricTag.attrib['value']=str(val.totalTravelTime)
        child.append(metricTag)
        child.attrib['value']=key
        metricTag = ET.Element('metric')
        metricTag.attrib['id']='total travel length'
        metricTag.attrib['value']=str(val.totalTravelLength)
        child.append(metricTag)

        metricTag = ET.Element('metric')
        metricTag.attrib['id']='average vehicular travel length'
        metricTag.attrib['value']=str(val.avgTravelLength)
        child.append(metricTag)
        metricTag = ET.Element('metric')
        metricTag.attrib['id']='average vehicular travel speed'
        metricTag.attrib['value']=str(val.avgTravelSpeed)
        child.append(metricTag)
        elem.append(child)
    return elem

import csv

def print_csv(d, file):
    with open(file, 'w') as csvfile:
        fieldnames = ['Scenario','Total number of vehicles','Average departure delay', 'Average vehicular waiting time', 'Average vehicular travel time',
                    'Average vehicular travel length','Average vehicular travel speed']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for key, val in d.items():
            writer.writerow({'Scenario':key,'Total number of vehicles': str(val.totalVeh), 'Average departure delay': str(val.avgDepartDelay), 
                            'Average vehicular waiting time': str(val.avgWaitTime), 'Average vehicular travel time':str(val.avgTravelTime),
                            'Average vehicular travel length':str(val.avgTravelLength),'Average vehicular travel speed':str(val.avgTravelSpeed)})
    



def getBasicStats(verbose, method, vehicles, assignments):
    totalVeh = 0.
    totalTravelTime = 0.
    totalTravelLength = 0.
    totalTravelSpeed = 0.
    totalWaitTime = 0.
    totalDiffSpeed = 0.
    totalDiffLength = 0.
    totalDiffWaitTime = 0.
    totalDiffTravelTime = 0.
    totalDepartDelay = 0.


    priorityTotalVeh = dict()
    priorityTotalTravelTime = dict()
    priorityTotalTravelLength = dict()
    priorityTotalTravelSpeed = dict()
    priorityTotalWaitTime = dict()
    priorityTotalDiffTime = dict()
    priorityTotalDiffSpeed = dict()
    priorityTotalDiffLength = dict()
    priorityTotalDiffWaitTime = dict()
    priorityTotalDiffTravelTime = dict()
    priorityTotalDepartDelay = dict()

    priorityAvgTravelTime = dict()
    priorityAvgTravelLength = dict()
    priorityAvgTravelSpeed = dict()
    priorityAvgWaitTime = dict()
    priorityAvgDepartDelay = dict()
    for veh in vehicles:
        t = veh.vType
        totalVeh += 1
        veh.method = method
        # unit: speed - m/s; traveltime - s; travel length - m
        veh.speed = veh.travellength / veh.traveltime
        totalTravelTime += veh.traveltime
        totalTravelLength += veh.travellength
        totalWaitTime += veh.waittime
        totalTravelSpeed += veh.speed
        totalDepartDelay += veh.departdelay
        if(not priorityTotalVeh.has_key(t)):
            priorityTotalVeh[t] = 0
            priorityTotalTravelTime[t] = 0
            priorityTotalTravelLength[t] = 0
            priorityTotalWaitTime[t] = 0
            priorityTotalTravelSpeed[t] = 0
            priorityTotalDepartDelay[t] = 0
        
        priorityTotalVeh[t] += 1
        priorityTotalTravelTime[t] += veh.traveltime
        priorityTotalTravelLength[t] += veh.travellength
        priorityTotalWaitTime[t] += veh.waittime
        priorityTotalTravelSpeed[t] += veh.speed
        priorityTotalDepartDelay[t] += veh.departdelay
        
    if verbose:
        print('totalVeh:', totalVeh)
    for key in priorityTotalVeh:
        totalVehDivisor = max(1, priorityTotalVeh[key])  # avoid division by 0
        priorityAvgTravelTime[key] = priorityTotalTravelTime[key] / totalVehDivisor
        priorityAvgTravelLength[key] = priorityTotalTravelLength[key] / totalVehDivisor
        priorityAvgTravelSpeed[key] = priorityTotalTravelSpeed[key] / totalVehDivisor
        priorityAvgWaitTime[key] = priorityTotalWaitTime[key] / totalVehDivisor
        priorityAvgDepartDelay[key] = priorityTotalDepartDelay[key] / totalVehDivisor

    totalVehDivisor = max(1, totalVeh)  # avoid division by 0
    avgTravelTime = totalTravelTime / totalVehDivisor
    avgTravelLength = totalTravelLength / totalVehDivisor
    avgTravelSpeed = totalTravelSpeed / totalVehDivisor
    avgWaitTime = totalWaitTime / totalVehDivisor
    avgDepartDelay = totalDepartDelay / totalVehDivisor
    for veh in vehicles:
        t = veh.vType
        if  not priorityTotalDiffTravelTime.has_key(t): 
            priorityTotalDiffSpeed[t] = 0
            priorityTotalDiffLength[t] = 0
            priorityTotalDiffWaitTime[t] = 0
            priorityTotalDiffTravelTime[t] = 0
        priorityTotalDiffTravelTime[t] += (veh.traveltime - priorityAvgTravelTime[t])**2
        priorityTotalDiffSpeed[t] += (veh.speed - priorityAvgTravelSpeed[t])**2
        priorityTotalDiffLength[t] += (veh.travellength - priorityAvgTravelLength[t])**2
        priorityTotalDiffWaitTime[t] += (veh.waittime - priorityAvgWaitTime[t])**2
                
        totalDiffTravelTime += (veh.traveltime - avgTravelTime)**2
        totalDiffSpeed += (veh.speed - avgTravelSpeed)**2
        totalDiffLength += (veh.travellength - avgTravelLength)**2
        totalDiffWaitTime += (veh.waittime - avgWaitTime)**2

    # SD: standard deviation
    SDTravelTime = (totalDiffTravelTime / totalVehDivisor)**(0.5)
    SDLength = (totalDiffLength / totalVehDivisor)**(0.5)
    SDSpeed = (totalDiffSpeed / totalVehDivisor)**(0.5)
    SDWaitTime = (totalDiffWaitTime / totalVehDivisor)**(0.5)

    for key in priorityTotalVeh:
        prioritySDTravelTime = (priorityTotalDiffTravelTime[key] / totalVehDivisor)**(0.5)
        prioritySDLength = (priorityTotalDiffLength[key] / totalVehDivisor)**(0.5)
        prioritySDSpeed = (priorityTotalDiffSpeed[key] / totalVehDivisor)**(0.5)
        prioritySDWaitTime = (priorityTotalDiffWaitTime[key] / totalVehDivisor)**(0.5)
        assignments[method+key] = Assign(method+key, priorityTotalVeh[key], priorityTotalTravelTime[key], priorityTotalTravelLength[key],
                                        priorityTotalDepartDelay[key], priorityTotalWaitTime[key],priorityAvgTravelTime[key],
                                        priorityAvgTravelLength[key],priorityAvgTravelSpeed[key],priorityAvgDepartDelay[key],
                                        priorityAvgWaitTime[key], prioritySDTravelTime, prioritySDLength, prioritySDSpeed, prioritySDWaitTime)

    assignments[method] = Assign(method, totalVeh, totalTravelTime, totalTravelLength,
                                 totalDepartDelay, totalWaitTime, avgTravelTime,
                                 avgTravelLength, avgTravelSpeed, avgDepartDelay,
                                 avgWaitTime, SDTravelTime, SDLength, SDSpeed, SDWaitTime)


# The observations should be drawn from a normally distributed population.
# For two independent samples, the t test has the additional requirement
# that the population standard deviations should be equal.
def doTTestForAvg(verbose, tValueAvg, assignments):
    if verbose:
        print('begin the t test!')
    for num, A in enumerate(assignments):
        for B in assignments[num + 1:]:
            sdABTravelTime = 0.
            sdABSpeed = 0.
            sdABLength = 0.
            sdABWaitTime = 0.
            if str(A.label) != str(B.label):
                sdABTravelTime = (float(A.totalVeh - 1) * ((A.SDTravelTime)**2) + float(
                    B.totalVeh - 1) * ((B.SDTravelTime)**2)) / float(A.totalVeh + B.totalVeh - 2)
                sdABTravelTime = sdABTravelTime**(0.5)

                sdABSpeed = (float(A.totalVeh - 1) * ((A.SDSpeed)**2) + float(
                    B.totalVeh - 1) * ((B.SDSpeed)**2)) / float(A.totalVeh + B.totalVeh - 2)
                sdABSpeed = sdABSpeed**(0.5)

                sdABLength = (float(A.totalVeh - 1) * ((A.SDLength)**2) + float(
                    B.totalVeh - 1) * ((B.SDLength)**2)) / float(A.totalVeh + B.totalVeh - 2)
                sdABLength = sdABLength**(0.5)

                sdABWaitTime = (float(A.totalVeh - 1) * ((A.SDWaitTime)**2) + float(
                    B.totalVeh - 1) * ((B.SDWaitTime)**2)) / float(A.totalVeh + B.totalVeh - 2)
                sdABWaitTime = sdABWaitTime**(0.5)

                tempvalue = (
                    float(A.totalVeh * B.totalVeh) / float(A.totalVeh + B.totalVeh))**0.5

                avgtraveltime = abs(
                    A.avgTravelTime - B.avgTravelTime) / sdABTravelTime * tempvalue

                avgtravelspeed = abs(
                    A.avgTravelSpeed - B.avgTravelSpeed) / sdABSpeed * tempvalue

                avgtravellength = abs(
                    A.avgTravelLength - B.avgTravelLength) / sdABLength * tempvalue

                if sdABWaitTime != 0.:
                    avgwaittime = abs(
                        A.avgWaitTime - B.avgWaitTime) / sdABWaitTime * tempvalue
                else:
                    avgwaittime = 0.
                    print(
                        'check if the information about veh.waittime exists!')
                freedomdegree = A.totalVeh + B.totalVeh - 2
                if freedomdegree > 30 and freedomdegree <= 40:
                    freedomdegree = 31
                if freedomdegree > 40 and freedomdegree <= 50:
                    freedomdegree = 32
                if freedomdegree > 50 and freedomdegree <= 60:
                    freedomdegree = 33
                if freedomdegree > 60 and freedomdegree <= 80:
                    freedomdegree = 34
                if freedomdegree > 80 and freedomdegree <= 100:
                    freedomdegree = 35
                if freedomdegree > 100:
                    freedomdegree = 36
                lowvalue = tTable[freedomdegree][6]
                highvalue = tTable[freedomdegree][9]

                tValueAvg[A][B] = T_Value(
                    avgtraveltime, avgtravelspeed, avgtravellength, avgwaittime, lowvalue, highvalue)


def doKruskalWallisTest(verbose, groups, combivehlist, assignments, label, hValues):
    if verbose:
        print('\nbegin the Kruskal-Wallis test!')
        print('methods:', label)
        print('number of samples:', len(combivehlist))
    adjlabel = label + '_' + "adjusted"
    if groups >= 100.:
        groups = 100.
    lowvalue = chiSquareTable[int(groups) - 1][2]
    highvalue = chiSquareTable[int(groups) - 1][4]

    H = H_Value(label, lowvalue, highvalue)
    adjH = H_Value(adjlabel, lowvalue, highvalue)
    hValues.append(H)
    hValues.append(adjH)

    for index in [("traveltime"), ("speed"), ("travellength"), ("waittime")]:
        for veh in combivehlist:
            veh.rank = 0.
        for method in assignments.itervalues():
            method.sumrank = 0.

        samecountlist = []
        current = 0
        lastrank = 0
        subtotal = 0.
        adjusted = 0.

        combivehlist.sort(key=operator.attrgetter(index))
        totalsamples = len(combivehlist)

        for i in range(0, len(combivehlist)):
            samecount = 0
            if i <= current:
                if index == "traveltime":
                    value = combivehlist[current].traveltime
                elif index == "speed":
                    value = combivehlist[current].speed
                elif index == "travellength":
                    value = combivehlist[current].travellength
                elif index == "waittime":
                    value = combivehlist[current].waittime
            else:
                print('error!')

            for j in range(current, len(combivehlist)):
                if index == "traveltime":
                    if combivehlist[j].traveltime == value:
                        samecount += 1
                    else:
                        break
                elif index == "speed":
                    if combivehlist[j].speed == value:
                        samecount += 1
                    else:
                        break
                elif index == "travellength":
                    if combivehlist[j].travellength == value:
                        samecount += 1
                    else:
                        break
                elif index == "waittime":
                    if combivehlist[j].waittime == value:
                        samecount += 1
                    else:
                        break

            if samecount == 1.:
                lastrank += 1.
                combivehlist[current].rank = lastrank
            else:
                sumrank = 0.
                for j in range(0, samecount):
                    lastrank += 1.
                    sumrank += lastrank
                rank = sumrank / samecount
                for j in range(0, samecount):
                    combivehlist[current + j].rank = rank

                elem = (value, samecount)
                samecountlist.append(elem)

            current = current + samecount

            if current > (len(combivehlist) - 1):
                break
                print('current:', current)

        for veh in combivehlist:
            for method in assignments.itervalues():
                if veh.method == method.label:
                    method.sumrank += veh.rank

        for method in assignments.itervalues():
            subtotal += (method.sumrank**2.) / method.totalVeh

        for elem in samecountlist:
            adjusted += (float(elem[1]**3) - float(elem[1]))

        c = 1. - (adjusted / float(totalsamples**3 - totalsamples))

        if index == "traveltime":
            H.traveltime = 12. / \
                (totalsamples * (totalsamples + 1)) * \
                subtotal - 3. * (totalsamples + 1)
            if c > 0.:
                adjH.traveltime = H.traveltime / c
        elif index == "speed":
            H.travelspeed = 12. / \
                (totalsamples * (totalsamples + 1)) * \
                subtotal - 3. * (totalsamples + 1)
            if c > 0.:
                adjH.travelspeed = H.travelspeed / c
        elif index == "travellength":
            H.travellength = 12. / \
                (totalsamples * (totalsamples + 1)) * \
                subtotal - 3. * (totalsamples + 1)
            if c > 0.:
                adjH.travellength = H.travellength / c
        elif index == "waittime":
            H.waittime = 12. / \
                (totalsamples * (totalsamples + 1)) * \
                subtotal - 3. * (totalsamples + 1)
            if c > 0.:
                adjH.waittime = H.waittime / c

optParser = OptionParser()
optParser.add_option("-t", "--tripinform-file", dest="vehfile",
                     help="read vehicle information generated by the DUA assignment from FILE (mandatory)", metavar="FILE")
optParser.add_option("-o", "--output-file", dest="outputfile", default="Global_MOE.txt",
                     help="write output to FILE", metavar="FILE")
optParser.add_option("-g", "--SGToutput-file", dest="sgtoutputfile", default="significanceTest.txt",
                     help="write output to FILE", metavar="FILE")
optParser.add_option("-v", "--verbose", action="store_true", dest="verbose",
                     default=False, help="tell me what you are doing")
optParser.add_option("-e", "--tTest", action="store_true", dest="ttest",
                     default=False, help="perform the t-Test")
optParser.add_option("-k", "--kruskalWallisTest", action="store_true", dest="kwtest",
                     default=False, help="perform the Kruskal-Wallis-Test")


(options, args) = optParser.parse_args()

if not options.vehfile:
    optParser.print_help()
    sys.exit()
parser = make_parser()

allvehicles = {}
for filename in options.vehfile.split(","):
    allvehicles[filename] = []
    parser.setContentHandler(VehInformationReader(allvehicles[filename]))
    parser.parse(filename)

# Vehicles from dua, incremental, clogit and oneshot are in included in
# the allvehlist.

# The results of the t test are stored in the tValueAvg.
tValueAvg = {}
# The resultes of the Kruskal-Wallis test are stored in the hValues.
hValues = []

# intitalization
combilabel = ''

assignments = {}
# calculate/read the basic statistics
for method, vehicles in allvehicles.items():
    getBasicStats(options.verbose, method, vehicles, assignments)

def print_xml(result, outputfile):
    ele = dict_to_xml('statistcs',(result))
    xml = ET.ElementTree() 
    xml._setroot(ele) 
    xml.write(outputfile)
    #getStatisticsOutput(assignments, options.outputfile)


#print_xml(assignments, options.outputfile)
print_csv(assignments, options.outputfile)

print('The calculation of network statistics is done!')

# begin the significance test for the observations with a normal distribution
if options.ttest:
    print('begin the t test!')
    for A in assignments.itervalues():
        tValueAvg[A] = {}
    doTTestForAvg(options.verbose, tValueAvg, list(assignments.itervalues()))
    print('The t test is done!')
if options.kwtest:
    # The Kruskal-Wallis test is applied for the data, not drawn from a
    # normally distributed population.
    groups = 2
    values = list(allvehicles.iteritems())
    for num, A in enumerate(values):
        for B in values[num + 1:]:
            combilabel = ''
            combivehlist = []
            combilabel = A[0] + '_' + B[0]
            print('Test for:', combilabel)
            for veh in A[1]:
                combivehlist.append(veh)
            for veh in B[1]:
                combivehlist.append(veh)
            doKruskalWallisTest(
                options.verbose, groups, combivehlist, assignments, combilabel, hValues)

getSignificanceTestOutput(
    assignments, options.ttest, tValueAvg, hValues, options.sgtoutputfile)
print('The Significance test is done!')
