"""
Generate the new switched shunt data, including any bus renumbering
"""


#newdir = 'Important Data'

#from mapRemainingBus import  TrueGenBusSet
#from generateNeighboursPlanning import NeighbourDict
from generateNeighboursFn import getNeighbours
#from changetfDatav4 import BusVoltageDict
from getBusDataFn import getBusData

PSSErawFile = 'hls18v1dyn_1219.raw'
AllMapFile = 'AllMappedLog.txt'
manualMapFile = 'mapped_buses_cleaned_for_load_shunt.csv'
newShuntData =  'newShuntData.txt' # output of this file
ssBusNoChangeLog =  'ssBusNoChangeLog.txt' # log of changes made in this file
changeLog = 'changeBusNoLog.txt'
BusData = 'PSSE_bus_data.txt'
outsideComedFile = 'outsideComedBusesv4.txt'
isolatedCAPEBusList = 'isolatedCAPEBusList_All.txt' # list of buses which are isolated in cape
GenBusChangeLog = 'GenBusChange.log' # log file of CAPE buses which have been renumbered to PSSE gen bus numbers
NeighbourDict = getNeighbours(PSSErawFile) # dict of neighbours in planning
#PSSEGenFile = 'PSSEGenFile.txt'
BusDataDict = getBusData(PSSErawFile)
genLines = []
ComedBusSet = set()
MapDict = {}
ManualMapDict = {}
ssBusNoChangeDict ={}
changeBusNoLogList = []
OldBusSet  =set()
changeNameDict = {}
#BusVoltageDict = {}
noNeedtoMapSet = set()
TrueGenBusSet = set() # set of all gen buses, numbered according to planning
"""
with open(BusData,'r') as f:
    filecontent = f.read()
    fileLines = filecontent.split('\n')
    for line in fileLines:
        words = line.split(',')
        if len(words) <2:
            continue
        Bus = words[0].strip()
        Volt = words[2].strip()
        BusVoltageDict[Bus] = Volt
"""
# get the set of true gen buses (numbered according to planning)
with open(GenBusChangeLog,'r') as f:
    filecontent = f.read()
    fileLines = filecontent.split('\n')
    for line in fileLines:
        if 'CAPE' in line:
            continue
        if '->' not in line:
            continue
        words = line.split('->')
        TrueGenBusSet.add(words[0].strip())




# get a set of buses which dont need to be included in the branch data
with open(outsideComedFile,'r') as f:
    filecontent = f.read()
    fileLines = filecontent.split('\n')
    for line in fileLines:
        if 'Manually' in line:
            continue
        if line.strip() != '':
            noNeedtoMapSet.add(line.strip())
            #CAPEMappedSet.add(line.strip())

# get the set of isolated buses and add them to no need to Map Set
with open(isolatedCAPEBusList,'r') as f:
    filecontent = f.read()
    fileLines = filecontent.split('\n')
    for line in fileLines:
        if 'isolated' in line:
            continue
        noNeedtoMapSet.add(line.strip())

#########



def changeRegulatingBus(line):
    words = line.split(',')
    regulateBus = words[6].strip()
    newBus = ''
    if int(regulateBus) == 0:
        return line

    if regulateBus in TrueGenBusSet: # original gen bus (no need to change)
        return line
        #newShuntLines.append(line)

    if regulateBus in MapDict.keys(): # map the Comed PSSE bus to CAPE bus
        newBus = MapDict[regulateBus]
    elif regulateBus in ManualMapDict.keys():
        newBus = ManualMapDict[regulateBus]
    else: # if no mapping done (for tf midpoint)
        #print "Unmapped shunt regulating bus: ", regulateBus

        # See if any neighbours of same voltage is mapped
        # If mapped, then make that the regulating bus
        neighbourList = list(NeighbourDict[regulateBus])
        regulateBusVolt = BusDataDict[regulateBus].NominalVolt
        found = 0
        for neighbour in neighbourList:
            if BusDataDict[neighbour].NominalVolt == regulateBusVolt:
                if neighbour in MapDict.keys():
                    newBus = MapDict[neighbour]
                    found = 1
                    break
                elif neighbour in ManualMapDict.keys():
                    newBus = ManualMapDict[neighbour]
                    found = 1
                    break
        if found == 0:
            print "Unmapped shunt regulating bus: ", regulateBus
                    

        ##newShuntLines.append(line)
    if newBus in OldBusSet:
        newBus = changeNameDict[newBus]

    words[6] = ' '*(6-len(newBus)) + newBus

    newLine = ''
    for word in words:
        newLine += word
        newLine += ','

    return newLine

    #newShuntLines.append(newLine[:-1])






with open(AllMapFile,'r') as f:
    filecontent = f.read()
    fileLines = filecontent.split('\n')
    for line in fileLines:
        if 'CAPE' in line:
            continue

        words = line.split('->')
        if len(words) < 2:
            continue
        PSSEBus = words[0].strip()
        CAPEBus = words[1].strip()
        if CAPEBus not in noNeedtoMapSet:
            MapDict[PSSEBus] = CAPEBus  

# open the simple map and generate a dictionary of PSSE->CAPE maps, also generate sets of PSSE and CAPE buses to be mapped
with open(manualMapFile,'r') as f:
    filecontent = f.read()
    fileLines = filecontent.split('\n')
    for line in fileLines:
        words = line.split(',')
        if len(words) <2:
            continue
        PSSEBus = words[0].strip()
        CAPEBus = words[5].strip()
        PSSEBusCode = words[2].strip()
        if 'M' in PSSEBusCode:
            continue
        if PSSEBus in ['NA','']:
            continue
        if CAPEBus in ['NA','']:
            continue
        if CAPEBus not in noNeedtoMapSet:
            ManualMapDict[PSSEBus] = CAPEBus

# look at log files which contains all the changed bus number
with open(changeLog,'r') as f:
    filecontent = f.read()
    fileLines = filecontent.split('\n')
    for line in fileLines:
        if 'CAPE' in line:
            continue
        words = line.split('->')
        if len(words) < 2:
            continue
        OldBus = words[0].strip()
        NewBus = words[1].strip()
        OldBusSet.add(OldBus)
        #NewBusSet.add(NewBus)
        changeNameDict[OldBus] = NewBus



newShuntLines = []
with open(PSSErawFile,'r') as f:
    filecontent = f.read()
    fileLines = filecontent.split("\n")
    for line in fileLines:
        if ('PSS' in line) or ('COMED' in line) or ('DYNAMICS' in line):
            continue
        if 'END OF BUS DATA' in line:
            break
        words = line.split(',')
        if len(words)<2: # continue to next iteration of loop if its a blank line
            continue
        BusCode = words[3].strip()
        area = words[4].strip()
        if area == '222':
            genLines.append(line)
            ComedBusSet.add(words[0].strip())    


    switchedShuntStartIndex = fileLines.index('0 / END OF FACTS DEVICE DATA, BEGIN SWITCHED SHUNT DATA') + 1
    switchedShuntEndIndex = fileLines.index('0 / END OF SWITCHED SHUNT DATA, BEGIN GNE DATA')
    for i in range(switchedShuntStartIndex,switchedShuntEndIndex):
        line = fileLines[i]

        words = line.split(',')
        if len(words)<2: # continue to next iteration of loop if its a blank line
            continue
        Bus = words[0].strip()
        if Bus in ComedBusSet:
            currentLine = ''
            try:
                CAPEBus = MapDict[Bus]
                ssBusNoChangeDict[Bus] = CAPEBus
            except:
                try:
                    CAPEBus = ManualMapDict[Bus]
                    ssBusNoChangeDict[Bus] = CAPEBus
                except:
                    print 'Unmapped shunt buses: ', Bus
            if CAPEBus in OldBusSet:
                CAPEBus = changeNameDict[CAPEBus]
                ssBusNoChangeDict[Bus] = CAPEBus
            words[0] = ' '*(6-len(CAPEBus)) + CAPEBus
            ind = 1
            for word in words:
                currentLine +=word
                if ind != len(words):
                    currentLine += ','
                ind +=1

            currentLine =  changeRegulatingBus(currentLine) # change the regulating bus
            newShuntLines.append(currentLine)

with open(newShuntData,'w') as f:
    for line in newShuntLines:
        f.write(line)
        f.write('\n')

# log file of load bus number change
with open(ssBusNoChangeLog,'w') as f:
    f.write('PSSEBus->CAPEBus\n')
    for key in ssBusNoChangeDict:
        mapStr = key + '->' + ssBusNoChangeDict[key]
        f.write(mapStr)
        f.write('\n')

duplicateDict = {}
with open(ssBusNoChangeLog,'r') as f:
    filecontent = f.read()
    fileLines = filecontent.split('\n')
    for line in fileLines:
        if 'CAPE' in line:
            continue

        words = line.split('->')
        if len(words)<2:
            continue
        PSSEBus = words[0].strip()
        CAPEBus = words[1].strip()
        if CAPEBus not in duplicateDict.keys():
            duplicateDict[CAPEBus] = []
        duplicateDict[CAPEBus].append(PSSEBus)
#print duplicateDict


for key in duplicateDict.keys():
    if len(duplicateDict[key])>1:
        print 'Duplicate Shunt Mapping -> ' + key + ' : ' + str(duplicateDict[key]) 
