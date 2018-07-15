"""
function which can automate bus mapping, given the manual mappings in a file
can handle one to many mapping
"""
#import sys
#sys.path.insert(0,'C:/Users/Bikiran/Google Drive/Bus Mapping Project Original/Donut Hole Approach/Donut Hole v2')

changeBusNoLog='changeBusNoLog.txt'
from splitTapVoltAngleFn import splitTapVoltAngles # function which reads tap split data, performs the tap splits and generates the new raw file
def TapLogChange(TapInput):

	with open(changeBusNoLog,'r') as f:
		filecontent = f.read()
		fileLines = filecontent.split('\n')
		CAPEold2NewDict={}
		for line in fileLines:
			if 'CAPE' in line:
				continue
			if '->' in line:
				words=line.split('->')
				CAPEold2NewDict[words[0].strip()]=words[1].strip()

	# open the file which contains the list of manual changes necessary
	with open(TapInput,'r') as f:
		filecontent = f.read()
		fileLines = filecontent.split('\n')
		tapSplitLines=[]
		for line in fileLines:
			if ',' in line:
				capewords = line.split(',')
				capenewwords=[]
				for word in capewords:
					if word.strip() in CAPEold2NewDict.keys():
						capenewwords.append(CAPEold2NewDict[word.strip()])					
					else:
						capenewwords.append(word.strip())
			if capenewwords[2].startswith('400') and len(capenewwords[2]) == 6: # do not include tap inputs where the tap is a tf midpoint
				continue
			tapSplitLines.append(capenewwords[0]+','+capenewwords[1]+','+capenewwords[2])

	#print(tapSplitLines)

	return tapSplitLines



TapInput = 'tap_split_changes_new.txt'
#TapOutput  = 'tap_split_changes_new.txt'
tapSplitLines=TapLogChange(TapInput)
#print(tapSplitLines)
oldRawFile = 'new_Raw0706_3wconv.raw'
newRawFile = 'new_Raw0706_TapDone.raw'
splitTapVoltAngles(oldRawFile,newRawFile,tapSplitLines)

