# compile a set which contains all the gen, load buses and any branches which are important for these buses
# make use of GenBusFile.txt, loadBusFile.txt and list_imp_gen_branches.txt
GenBusFile = 'GenBusFile.txt' # set  of all comed gen buses
loadBusFile = 'loadBusFile.txt' # set of all comed load buses
list_imp_gen_branches = 'list_imp_gen_branches.txt' # set of all buses which are important to gen buses 
raw_file = 'testRAW04052018_fixedload.raw'
imp_file_list = [GenBusFile,loadBusFile,list_imp_gen_branches] # list of file which contains info about gen, load or other imp buses

imp_bus_set = set() # set of all imp LV buses
BusVoltDict = {}

# get comed bus voltages
with open(raw_file, 'r') as f:
	filecontent = f.read()
	fileLines = filecontent.split('\n')
	for line in fileLines:
		if ('PSS' in line) or ('COMED' in line) or ('DYNAMICS' in line):
			continue
		if 'END OF BUS DATA' in line:
			break
		words = line.split(',')
		if len(words) <2:
			continue
		Bus = words[0].strip()
		BusVolt = float(words[2].strip())
		area = words[4].strip()


		if area == '222':
			BusVoltDict[Bus] = BusVolt


# scan all files in imp_file_list and add buses which are LV and which are either gen, load or other imp buses
for file in imp_file_list:
	with open(file,'r') as f:
		filecontent = f.read()
		fileLines = filecontent.split('\n')
		for line in fileLines:
			if line == '':
				continue
			if 'List' in line:
				continue
			Bus = line.strip()
			if BusVoltDict[Bus] < 40.0: # HV bus
				imp_bus_set.add(Bus)
