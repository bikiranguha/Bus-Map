PSSErawFile = 'hls18v1dyn_new.raw'

ComedMidpointSet = set()
MidpointDict = {} # key: Comed midpoint bus, value: Set of all the real buses it is connected to
MidpointNeighbour = {} # key: Neighbour of a midpoint, value: corresponding midpoint
# get a set of comed buses
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
            #ComedBusSet.add(words[0].strip())
            BusName = words[1].strip()
            suffix = BusName.split(';')
            try:
                if 'M' in suffix[1]:
                    #print line
                    ComedMidpointSet.add(words[0].strip())
            except:
                continue

for Bus in ComedMidpointSet:
    MidpointDict[Bus] = set()



tfStartIndex = fileLines.index('0 / END OF BRANCH DATA, BEGIN TRANSFORMER DATA') + 1
tfEndIndex = fileLines.index('0 / END OF TRANSFORMER DATA, BEGIN AREA DATA')

k = tfStartIndex
while k < tfEndIndex:
    line = fileLines[k]
    words = line.split(',')
    Bus1 = words[0].strip()
    Bus2 = words[1].strip()
    Bus3 = words[2].strip()

    if Bus3 == '0':
        if Bus1 in ComedMidpointSet:
            MidpointDict[Bus1].add(Bus2)
            MidpointNeighbour[Bus2] = Bus1
            k+=4
        elif Bus2 in ComedMidpointSet:
            MidpointDict[Bus2].add(Bus1)
            MidpointNeighbour[Bus1] = Bus2
            k+=4

        else:
            k+=4


    else:
        if Bus1 in ComedMidpointSet or Bus2 in ComedMidpointSet or Bus3 in ComedMidpointSet:
            print line
        k+=5

