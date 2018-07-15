"""
Gets all the relevant tf data from the raw file
Case 984,1717,1718,4113:
   984,400116,     0,'1 ' + 100000,400116,     0,'1 '  = 272352,275152,     0,'1 '
100000,400239,     0,'1 ' + 1717,400239,     0,'1 ' =  275152,273089,     0,'1 '
100000,  1718,     0,'1 ' = 275152,273090,     0,'1 '
Case 989,1717,1718,7380:
   989,400117,     0,'1 ' + 100006,400117,     0,'1 ' =  272353,275153,     0,'1 '
100006,400242,     0,'1 ' +   1717,400242,     0,'1 ' = 275153,273089,     0,'1 '
100006,  1718,     0,'1 ' = 275153,273090,     0,'1 '
Case 993,1717,1718,4233:
   993,400118,     0,'2 ' + 100008,400118,     0,'2 ' = 272353,275159,     0,'1 '
100008,400243,     0,'2 '  +   1717,400243,     0,'2 ' = 275159,273089,     0,'1 '
100008,  1718,     0,'1 ' =  275159,273090,     0,'1 '
Case  1205,1213, 1221,1222:
  1205,400129,     0,'1 ' + 100002,400129,     0,'1 ' + 100002,400240,     0,'1 ' +   1213,400240,     0,'1 ' = 271310,272990,     0,'1 '
Case 1201,1209, 1220,1223:
  1201,400128,     0,'1 ' + 100004,400128,     0,'1 ' + 100004,400241,     0,'1 ' +   1209,400241,     0,'1 ' = 271311,272991,     0,'1 '

Other special cases detailed in Final_Sol_3w:
Case 750391,1727,2517,'1 ':
750391,400084,     0,'1 ' = 272432,275236,     0,'1 '
  1727,400084,     0,'1 ' = 273108,275236,     0,'1 '
Case 750392,1728,2518,'1 '
750392,400085,     0,'1 ' = 272433,275235,     0,'1 ' 
  1728,400085,     0,'1 ' = 273109,275235,     0,'1 '
Case 750156,750165,750166,'1 ':
750156,400031,     0,'1 ' = 270716,   338,     0,'86'
750165,400031,     0,'1 ' = 275650,   338,     0,'86'
750166,400031,     0,'1 ' = 275950,   338,     0,'86'
Case 750206[352]:
  3782,750206,     0,'1 ' = 274769,   374,     0,'1 '
  3783,750206,     0,'1 ' = 274769,   375,     0,'1 '
  3784,750206,     0,'1 ' = 274769,   376,     0,'1 '
  3785,750206,     0,'1 ' = 274769,   377,     0,'1 '
"""
ImpTFList = [984,1717,1718,4113,100000,400116,400239,989,1717,1718,7380,400117,100006,400242,993,1717,1718,4233,100008,400118,400243,1205,400129,100002,1213,400240,1201,400128,100004,400241,1209,750391,1727,400084,750392,1728,400085,50156,750165,750166,400031,750206]
ImpTFListStr = []
manualTFDataToAdd = []
for tf in ImpTFList:
  ImpTFListStr.append(str(tf))

RAWFile = 'RAW0620.raw'
with open(RAWFile,'r') as f:
  filecontent = f.read()
  fileLines = filecontent.split('\n')


# build a dictionary of comed transformer (relevant) data to be substituted into CAPE data
tfStartIndex = fileLines.index('0 / END OF BRANCH DATA, BEGIN TRANSFORMER DATA') + 1
tfEndIndex = fileLines.index('0 / END OF TRANSFORMER DATA, BEGIN AREA DATA')



# generate a dictionary from the planning data, values are relevant tf info
i = tfStartIndex
while i < tfEndIndex:
  line = fileLines[i]
  words = line.split(',')
  Bus1 = words[0].strip()
  Bus2 = words[1].strip()
  Bus3 = words[2].strip()

  if Bus1 in ImpTFListStr and Bus2 in ImpTFListStr:
    manualTFDataToAdd.append(line)
    for j in range(3):
      i+=1
      line = fileLines[i]
      manualTFDataToAdd.append(line)

    i+=1
  else:
    i+=4




for line in manualTFDataToAdd:
  print line
	