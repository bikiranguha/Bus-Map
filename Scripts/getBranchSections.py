# Script to output which buses are grouped together in CAPE

CAPErawFile = 'CAPE_RAW0225v33.raw'



BranchGroupList = []

# make a list in which each element is a bus group
with open(CAPErawFile,'r') as f:
	filecontent = f.read()
	fileLines = filecontent.split('\n')
	branchStartIndex = fileLines.index('0 / END OF GENERATOR DATA, BEGIN BRANCH DATA')+1
	branchEndIndex = fileLines.index('0 / END OF BRANCH DATA, BEGIN TRANSFORMER DATA')
	for i in range(branchStartIndex,branchEndIndex): # search through branch data
		words = fileLines[i].split(',')
		BranchCode = words[2].strip()
		BranchStatus = words[13].strip()
		if BranchCode == "'99'" and BranchStatus == '1':
#			count +=1
			Bus1 = words[0].strip()
			Bus2 = words[1].strip()
			if len(BranchGroupList) !=0:
				found = 0
				for lst in BranchGroupList: # search through each group
					if Bus1 in lst:
						if Bus2 not in lst: # Bus 1 present, so add Bus2
							ind = BranchGroupList.index(lst)
							lst.append(Bus2)
							BranchGroupList[ind] = lst
							found = 1
							break
						else: # Both bus 1 and bus 2 are present
							found = 1
							break
						
					elif Bus2 in lst: # Bus 2 present but Bus 1 not present
						ind = BranchGroupList.index(lst)
						lst.append(Bus1)
						BranchGroupList[ind] = lst
						found = 1
						break

				if found == 0: # None of the buses present
					lst = []
					lst.append(Bus1) 
					lst.append(Bus2)
					BranchGroupList.append(lst)

			else: # BranchGroupList is empty
				lst = []
				lst.append(Bus1)
				lst.append(Bus2)
				BranchGroupList.append(lst)

						
with open('branchGroupv3.txt','w') as f:
	for lst in BranchGroupList:
		strng = ''
		for Bus in lst:
			strng+=Bus
			if Bus != lst[-1]:
				strng += ','
		f.write(strng)
		f.write('\n')


#print count