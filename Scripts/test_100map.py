Map345Get100 = 'Map345Full_check.txt'
toCheckCAPE100 = set()

with open(Map345Get100,'r') as f:
	filecontent = f.read()
	fileLines = filecontent.split('\n')
	for line in fileLines:
		if line == '':
			continue
		arrow_count = line.count('->')
		if arrow_count > 1:
			#print line
			words = line.split('->')
			if words[2].strip() == '':
				continue
			
			CAPEBus = words[0].strip()
			toCheckCAPE100.add(CAPEBus)

			"""
			planningBus = words[2].strip()
			newStr = CAPEBus  + '->' + planningBus
			print newStr
			"""
			
with open('CAPECheck100.txt','w') as f:
	for Bus in list(toCheckCAPE100):
		f.write(Bus)
		f.write('\n')
