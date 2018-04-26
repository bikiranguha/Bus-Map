PSSErawFile = 'hls18v1dyn_1219.raw'
PSSEGenFile = 'PSSEGenFile.txt'

genLines = []
GenBusSet = set()
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
        if BusCode == '2' and area == '222':
            genLines.append(line)
            GenBusSet.add(words[0].strip())

with open(PSSEGenFile,'w') as f:
    f.write('List of gen buses in the planning data in the ComEd case:\n\n\n')
    for line in genLines:
        f.write(line)
        f.write('\n')

# verify all generator buses have been mapped properly, otherwise print those which are not
with open('GenBusChange.log', 'r') as f:
        filecontent = f.read()
        fileLines = filecontent.split('\n')
        for line in fileLines:
            if 'CAPE' in line:
                continue
            words = line.split('->')
            if len(words) < 2:
                continue
            PSSEBus = words[1].strip()
            if PSSEBus not in GenBusSet:
                print PSSEBus