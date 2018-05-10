"""
Provides a function which organizes the branch impedance and tf impedance data into a class
"""

import math


def generateNeighbours(Raw):

	class BranchData(object):
		def __init__(self):
			self.toBus = []
			self.R = []
			self.X = []
			self.cktID = []
			self.Z = []


	BranchNeighbourDict = {}
	BranchDataDict = {}
	ComedBusSet = set()

	def BusAppend(Bus,NeighbourBus,NeighbourDict):
		if Bus not in NeighbourDict.keys():
			NeighbourDict[Bus] = []
		NeighbourDict[Bus].append(NeighbourBus)

	def generateBranchData(BranchDataDict,Bus1,Bus2,cktID,R,X):
		if Bus1 not in BranchDataDict.keys():
			BranchDataDict[Bus1] = BranchData()

		BranchDataDict[Bus1].toBus.append(Bus2)
		BranchDataDict[Bus1].R.append(R)
		BranchDataDict[Bus1].X.append(X)
		BranchDataDict[Bus1].Z.append(Z)
		BranchDataDict[Bus1].cktID.append(cktID)
		return BranchDataDict




	with open(Raw, 'r') as f:
		filecontent = f.read()
		fileLines = filecontent.split('\n')
		for line in fileLines:
			if ('PSS' in line) or ('COMED' in line):
				continue
			if 'END OF BUS DATA' in line:
				break
			words = line.split(',')
			if len(words) <2:
				continue
			Bus = words[0].strip()
			area = words[4].strip()
			if area == '222':
				ComedBusSet.add(Bus)
			#AreaDict[Bus] = area


		branchStartIndex = fileLines.index('0 / END OF GENERATOR DATA, BEGIN BRANCH DATA') + 1
		branchEndIndex = fileLines.index('0 / END OF BRANCH DATA, BEGIN TRANSFORMER DATA')

		for i in range(branchStartIndex, branchEndIndex):
			line = fileLines[i]
			words = line.split(',')
			Bus1 = words[0].strip()
			Bus2 = words[1].strip()
			status = words[-5].strip()

			if Bus1 in ComedBusSet or Bus2 in ComedBusSet:
				if status == '1':
					cktID = words[2].strip("'")
					R = float(words[3].strip())
					X = float(words[4].strip())
					Z = math.sqrt(R**2 + X**2)

					BusAppend(Bus1,Bus2,BranchNeighbourDict)
					BusAppend(Bus2,Bus1,BranchNeighbourDict)
					BranchDataDict = generateBranchData(BranchDataDict,Bus1,Bus2,cktID,R,X)
					BranchDataDict = generateBranchData(BranchDataDict,Bus2,Bus1,cktID,R,X)


	return BranchNeighbourDict, BranchDataDict

	



