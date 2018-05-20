#planning345BusFile = 'C:/Users/Hemanth/OneDrive/NameMatchingFiles/' + 'BusLines345Planning.txt'
planning345BusFile = 'BusLines345Planning.txt'
#NameMatchFinal = 'C:/Users/Hemanth/OneDrive/NameMatchingFiles/' + 'NameMatchFinal.txt'
NameMatchFinal = 'NameMatchFinal.txt'
Bus2SubDict={} # planning bus name to CAPE substation name
BusNum2NameDict={} # planning bus number to bus name
BusNum2SubNameDict={} # Planning Bus number to CAPE substation name
with open(NameMatchFinal,'r') as f:
    filecontent = f.read()
    fileLines = filecontent.split('\n')
    for line in fileLines:
        words = line.split('->')
        if len(words) < 2:
            continue
        BusName = words[0].strip("'").strip()
        SubName = words[1].strip()
        Bus2SubDict[BusName] = SubName

with open(planning345BusFile,'r') as f:
    filecontent = f.read()
    fileLines = filecontent.split('\n')
    for line in fileLines:
        if ',' in line:
            words = line.split(',')
            BusNumber = words[0].strip()
            BusName2 = words[1].strip("'").strip()
            BusNum2NameDict[BusNumber]= BusName2
            BusNum2SubNameDict[BusNumber]= Bus2SubDict[BusName2]

"""
print BusNum2NameDict['270607']
print BusNum2NameDict['270662']
print BusNum2NameDict['270666']
print BusNum2NameDict['270674']
print BusNum2NameDict['270691']            

print BusNum2SubNameDict['270607']
print BusNum2SubNameDict['270662']
print BusNum2SubNameDict['270666']
print BusNum2SubNameDict['270674']
print BusNum2SubNameDict['270691']
"""