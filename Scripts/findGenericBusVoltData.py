# find buses which dont have typecode 4 but have a bus voltage magnitude of 1.0000, i.e., their pu voltage
# magnitude is not a solved one

latestRaw = 'tmp_island_branch_fixedv2AngleShifted.raw'

with open(latestRaw,'r') as f:
	filecontent = f.read()
	fileLines = filecontent.split('\n')
	for line in fileLines:
		if ('PSS' in line) or ('COMED' in line) or ('DYNAMICS' in line):
		    continue
		if 'END OF BUS DATA' in line:
		    break
		words = line.split(',')
		if len(words)<2: # continue to next iteration of loop if its a blank line
		    continue

		Bus  = words[0].strip()
		BusType = words[3].strip()
		BusVolt = float(words[7].strip())
		area = words[4].strip()

		if area == '222':
			if BusType != '4' and BusVolt == 1.0:
				print Bus