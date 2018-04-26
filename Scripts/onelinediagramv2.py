"""
Print all data of any bus within a depth of 1 for prespecified raw file
"""

AllBuses = set()
#depthOne = []
#rawfile = 'NewCAPERawClean.raw'
#rawfile = 'FinalRAW03312018.raw'
#rawfile = 'testRAW04052018_fixedload.raw'
#rawfile = 'tmp_island_branch_fixedv2.raw'
rawfile = 'hls18v1dyn_new.raw'
#rawfile = 'RAW0406018.raw'
#rawfile = 'tmp_island_branch_fixed.raw'
#rawfile = 'tmp_island_branch_fixedv2AngleShifted.raw'
#rawfile = 'Raw0414tmp.raw'
#rawfile = 'Raw0419_reen.raw'
changeLog = 'changeBusNoLog.txt'
NewBusSet = set()
OldBusSet = set()
MapDict = {} # Maps new bus numbers to old bus numbers
print 'Raw File: ', rawfile



def changeIfOldBus(Bus,line,wordIndex):
    # put old bus number in parenthesis (if any)
    if Bus in MapDict.keys():
        actualBusName = MapDict[Bus]
        line = busLineWithActualName(line,actualBusName,wordIndex)
        return line
    else:
        return line

def busLineWithActualName(line,Bus,wordIndex):
    # change line (to print) if the bus number has been changed
    words = line.split(',')
    words[wordIndex] += '[' + Bus + ']'
    newLine = ''
    for word in words:
        newLine += word
        newLine += ','
    newLine = newLine[:-1]
    return newLine

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
        NewBusSet.add(NewBus)
        MapDict[NewBus] = OldBus


def printOneLineDiagram(searchBus):
    # prints all the info in a depth of one for searchBus

    headerList = ['PSS','COMED','DYNAMICS']
    with open(rawfile,'r') as f:
        filecontent = f.read()
        fileLines = filecontent.split('\n')
        for line in fileLines:
            header_flag = 0

            for header in headerList:
                if header in line:
                    header_flag = 1
                    break
            if header_flag == 1:
                continue


            if 'END OF BUS DATA' in line:
                break


            words = line.split(',')
            if len(words) <2:
                continue

            #area = words[4].strip()
            Bus = words[0].strip()
            if searchBus == Bus:
                print "Bus Data:"
                line = changeIfOldBus(Bus,line,0)
                #print '\n'
                print line
                #depthOne.append(Bus)
            AllBuses.add(Bus)







    # print branch data
    for line in fileLines:
        if 'END OF GENERATOR DATA' in line:
            branchStartIndex = fileLines.index(line) + 1
        if 'END OF BRANCH DATA' in line:
            branchEndIndex = fileLines.index(line)
            
    #branchStartIndex = fileLines.index('0 / END OF GENERATOR DATA, BEGIN BRANCH DATA') + 1
    #branchEndIndex = fileLines.index('0 / END OF BRANCH DATA, BEGIN TRANSFORMER DATA')

    print '\n'
    print 'Branch Data:'


    for i in range(branchStartIndex, branchEndIndex):
        line = fileLines[i]
        words = line.split(',')
        Bus1 = words[0].strip()
        Bus2 = words[1].strip()
        if searchBus == Bus1:
            depthOne.append(Bus2)
            line = changeIfOldBus(Bus1,line,0)
            line = changeIfOldBus(Bus2,line,1)
            print line
        elif searchBus == Bus2:
            depthOne.append(Bus1)
            line = changeIfOldBus(Bus1,line,0)
            line = changeIfOldBus(Bus2,line,1)
            print line


    # print transformer data
    for line in fileLines:
        if 'END OF BRANCH DATA' in line:
            tfStartIndex = fileLines.index(line) + 1
        if 'END OF TRANSFORMER DATA' in line:
            tfEndIndex = fileLines.index(line)
    #tfStartIndex = fileLines.index('0 / END OF BRANCH DATA, BEGIN TRANSFORMER DATA') + 1
    #tfEndIndex = fileLines.index('0 / END OF TRANSFORMER DATA, BEGIN AREA DATA')

    i = tfStartIndex
    print '\n'
    print 'Transformer Data:'
    while i<tfEndIndex:
        line = fileLines[i]
        words = line.split(',')
        Bus1 = words[0].strip()
        Bus2 = words[1].strip()
        Bus3 = words[2].strip()

        if Bus3 == '0':
            if searchBus ==  Bus1:
                depthOne.append(Bus2)
                line = changeIfOldBus(Bus1,line,0)
                line = changeIfOldBus(Bus2,line,1)
                print line
            if searchBus ==  Bus2:
                depthOne.append(Bus1)
                line = changeIfOldBus(Bus1,line,0)
                line = changeIfOldBus(Bus2,line,1)
                print line
            i+=4
            
        else:
            if searchBus ==  Bus1:
                line = changeIfOldBus(Bus1,line,0)
                line = changeIfOldBus(Bus2,line,1)
                line = changeIfOldBus(Bus3,line,2)
                depthOne.append(Bus2)
                depthOne.append(Bus3)
                print line
            if searchBus ==  Bus2:
                line = changeIfOldBus(Bus1,line,0)
                line = changeIfOldBus(Bus2,line,1)
                line = changeIfOldBus(Bus3,line,2)
                depthOne.append(Bus1)
                depthOne.append(Bus3)
                print line
            if searchBus ==  Bus3:
                line = changeIfOldBus(Bus1,line,0)
                line = changeIfOldBus(Bus2,line,1)
                line = changeIfOldBus(Bus3,line,2)
                depthOne.append(Bus1)
                depthOne.append(Bus2)
                print line
            i+=5



    # any generator data within a depth of 1
    for line in fileLines:
        if 'END OF FIXED SHUNT DATA' in line:
            genStartIndex = fileLines.index(line) + 1
        if 'END OF GENERATOR DATA' in line:
            genEndIndex = fileLines.index(line) 
    #genStartIndex = fileLines.index('0 / END OF FIXED SHUNT DATA, BEGIN GENERATOR DATA')+1
    #genEndIndex = fileLines.index('0 / END OF GENERATOR DATA, BEGIN BRANCH DATA')

    print '\n'
    print 'Generator Data in a Depth of One:'
    for i in range(genStartIndex, genEndIndex):
        line = fileLines[i]
        words = line.split(',')
        Bus = words[0].strip()

        if Bus in depthOne:
            line = changeIfOldBus(Bus,line,0)
            print line
        if Bus == searchBus:
            line = changeIfOldBus(Bus,line,0)
            print line
    # any load within a depth of 1
    for line in fileLines:
        if 'END OF BUS DATA' in line:
            loadStartIndex = fileLines.index(line) + 1
        if 'END OF LOAD DATA' in line:
            loadEndIndex = fileLines.index(line) 
    #loadStartIndex = fileLines.index('0 / END OF BUS DATA, BEGIN LOAD DATA') + 1
    #loadEndIndex = fileLines.index('0 / END OF LOAD DATA, BEGIN FIXED SHUNT DATA')

    print '\n'
    print 'Load Data in a Depth of One:'

    for i in range(loadStartIndex,loadEndIndex):
        line = fileLines[i]
        words = line.split(',')
        Bus = words[0].strip()
        if Bus == searchBus:
            line = changeIfOldBus(Bus,line,0)
            print line
        if Bus in depthOne:
            line = changeIfOldBus(Bus,line,0)
            print line


    # print connected bus data
    print '\n'
    print "Connected Bus Data:"
    for line in fileLines:
        header_flag = 0

        for header in headerList:
            if header in line:
                header_flag = 1
                break
        if header_flag == 1:
            continue


        if 'END OF BUS DATA' in line:
            break


        words = line.split(',')
        if len(words) <2:
            continue

        #area = words[4].strip()
        Bus = words[0].strip()
        if Bus in depthOne:
            line = changeIfOldBus(Bus,line,0)
            print line

    print '\n'


            


while 1:
    depthOne = []
    searchBus = raw_input('Please enter bus number: ').strip()
    printOneLineDiagram(searchBus)
