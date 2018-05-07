""" generates a dyr file full of diverse GENROU parameter sets
	generators in a substation have the same set of parameters, except the Zsource
	Files needed in the same directory:
	 	'pf_example_gen_data.txt' : this contains the generator data from which 
	 	 bus numbers are extracted as well as the gen zSource
	 	 'sampleGenDyr.txt': these files contain different parameter sets for GENROU
	 	 'pf_substation_report.txt': needed to get substation name of the bus


"""


import os
import random

###### INPUT FILES####################
genDataFile = 'pf_ornl_gen_data.txt'
substationFile = 'pf_ornl_substation_report.txt'
######################################

###### OUTPUT FILES####################
output_file = 'pf_mult_all.dyr'
######################################

genBusList = [] # BusList contains a list of all the bus numbers in string format
zSourceList = [] # contains all the Zsource values of the generators
IDList = [] # contains the machine ID of all the generators


with open(genDataFile,'r') as f:
    filecontent = f.read()
    fileLines = filecontent.split("\n")
    for line in fileLines:

        words = line.split(',')
        genBusList.append(words[0].strip())
        zSourceList.append(words[10].strip())
        IDstr = words[1]
        IDList.append(IDstr[1:3].strip())


subDict= {} # dictionary which tells which bus belongs to which substation
sampleGenDict = {} # dictionary which tells which GENROU sample has been assigned to the substation
sampleExcDict = {} # dictionary which tells which EXC sample has been assigned to the substation
sampleGovDict = {} # dictionary which tells which GOV sample has been assigned to the substation


items = os.listdir(".")  # get a list of all files in current directory

sampleGenList = [] # a list of sampleGenDyr.txt files in the current directory
sampleExcList = [] # a list of sampleExcDyr.txt files in the current directory
sampleGovList = [] # a list of sampleGovDyr.txt files in the current directory


for names in items:
    if names.endswith(".txt") and names.startswith("sampleGen"):
        sampleGenList.append(names)
    if names.endswith(".txt") and names.startswith("sampleExc"):
        sampleExcList.append(names)
    if names.endswith(".txt") and names.startswith("sampleGov"):
        sampleGovList.append(names)


sampleGenDyrDict = {} # a dictionary which will store all the GENROU sample parameter data
sampleExcDyrDict  = {} # a dictionary which will store all the EXC sample parameter data 
sampleGovDyrDict  = {} # a dictionary which will store all the GOV sample parameter data

def makeSampleDyrDict(sampleList, sampleDict):
    """ function to generate a parameter set dictionary
        where each element of the dictionary is a sample parameter set 
    """
    for i in range(len(sampleList)):
        with open(sampleList[i],'r') as f:
            filecontent = f.read()
            sampleDict[i] = filecontent.split(' ')

# generating sample dictionaries for generators, exciters and governors
makeSampleDyrDict(sampleGenList,sampleGenDyrDict)
makeSampleDyrDict(sampleExcList,sampleExcDyrDict)
makeSampleDyrDict(sampleGovList,sampleGovDyrDict)





""" these dictionaries are needed to substitute values of bus data, machine id and zsource """
genBusIndex = {}
excBusIndex = {}
govBusIndex = {}
XdIndex = {}
genIDindex = {}
excIDindex = {}
govIDindex = {}

# please check the values to search for, they will change based on the samples used """
genBusIndex[0] = sampleGenDyrDict[0].index('101')
genBusIndex[1] = sampleGenDyrDict[1].index('206')
genBusIndex[2] = sampleGenDyrDict[2].index('211')
genBusIndex[3] = sampleGenDyrDict[3].index('3011')

excBusIndex[0] = sampleExcDyrDict[0].index('101')
excBusIndex[1] = sampleExcDyrDict[1].index('206')
excBusIndex[2] = sampleExcDyrDict[2].index('211')
excBusIndex[3] = sampleExcDyrDict[3].index('3011')

govBusIndex[0] = sampleGovDyrDict[0].index('101')
govBusIndex[1] = sampleGovDyrDict[1].index('206')

XdIndex[0] = sampleGenDyrDict[0].index('0.30000')
XdIndex[1] = sampleGenDyrDict[1].index('0.25000')
XdIndex[2] = sampleGenDyrDict[2].index('0.2600')
XdIndex[3] = sampleGenDyrDict[3].index('0.35000')

genIDindex[0] = sampleGenDyrDict[0].index('1')
genIDindex[1] = sampleGenDyrDict[1].index('1')
genIDindex[2] = sampleGenDyrDict[2].index('1')
genIDindex[3] = sampleGenDyrDict[3].index('1')

excIDindex[0] = sampleExcDyrDict[0].index('1')
excIDindex[1] = sampleExcDyrDict[1].index('1')
excIDindex[2] = sampleExcDyrDict[2].index('1')
excIDindex[3] = sampleExcDyrDict[3].index('1')

govIDindex[0] = sampleGovDyrDict[0].index('1')
govIDindex[1] = sampleGovDyrDict[1].index('1')



# get substation data for the buses
with open(substationFile,'r') as f:
	    filecontent = f.read()
	    fileLines = filecontent.split("\n")
	    for line in fileLines:
    		ifHeader = line.find('Substation')
    		if ifHeader != -1:
    			continue
    		words = line.split(" ")
    		lessWords = []
    		for word in words:
    			if word !='' and word != 'CO':
    				lessWords.append(word)
    		if len(lessWords) == 8:
    			subName = lessWords[0]
    			bus = lessWords[1]
    			subDict[bus] = subName
    			if subName not in sampleGenDict:
    				sampleGenNo = random.choice(range(len(sampleGenDyrDict)))
    				sampleExcNo = random.choice(range(len(sampleExcDyrDict)))
    				sampleGovNo = random.choice(range(len(sampleGovDyrDict)))
    				sampleGenDict[subName] = sampleGenNo
    				sampleExcDict[subName] = sampleExcNo
    				sampleGovDict[subName] = sampleGovNo
    		else:
    			subName1 = lessWords[0]
    			subName2 = lessWords[1]
    			subName = subName1 + ' ' + subName2
    			bus = lessWords[2]
    			subDict[bus] = subName
    			if subName not in sampleGenDict:
    				sampleGenNo = random.choice(range(len(sampleGenDyrDict)))
    				sampleExcNo = random.choice(range(len(sampleExcDyrDict)))
    				sampleGovNo = random.choice(range(len(sampleGovDyrDict)))
    				sampleGenDict[subName] = sampleGenNo
    				sampleExcDict[subName] = sampleExcNo
    				sampleGovDict[subName] = sampleGovNo



with open(output_file,'w') as f:
	for i in range(len(genBusList)):
		subStation = subDict[genBusList[i]] # get substation name of the bus
		sampleGenNo = sampleGenDict[subStation]	# get sampleGenNo to use from the dyr list 
		sampleExcNo = sampleExcDict[subStation]
		sampleGovNo = sampleGovDict[subStation]
		sampleGenDyr = sampleGenDyrDict[sampleGenNo]
		sampleExcDyr = sampleExcDyrDict[sampleExcNo]
		sampleGovDyr = sampleGovDyrDict[sampleGovNo]
		sampleGenDyr[genBusIndex[sampleGenNo]] = genBusList[i] # replace bus no in sample
		sampleGenDyr[XdIndex[sampleGenNo]] = zSourceList[i] # replace Zsource in sample
		sampleGenDyr[genIDindex[sampleGenNo]] = IDList[i]	  # replace ID in sample
		sampleExcDyr[excBusIndex[sampleExcNo]] = genBusList[i]
		sampleExcDyr[excIDindex[sampleExcNo]] = IDList[i]
		sampleGovDyr[govBusIndex[sampleGovNo]] = genBusList[i]
		sampleGovDyr[govIDindex[sampleGovNo]] = IDList[i]
		for word in sampleGenDyr:

			if word=='':
				f.write(' ')
			elif word=="'GENROU'":
				f.write(' ')
				f.write(word)
			else:
				f.write(word)
		f.write('\n')

		for word in sampleExcDyr:
			if word=='':
				f.write(' ')
			elif word in ["'IEEET1'","'SCRX'","'SEXS'"]:
				f.write(' ')
				f.write(word)
			else:
				f.write(word)
		f.write('\n')

		for word in sampleGovDyr:
			if word=='':
				f.write(' ')
			elif word == "'TGOV1'":
				f.write(' ')
				f.write(word)
			else:
				f.write(word)
		f.write('\n')


			


