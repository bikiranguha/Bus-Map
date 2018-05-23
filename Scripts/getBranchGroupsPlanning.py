import sys
sys.path.insert(0,'C:/Users/Bikiran/Google Drive/Bus Mapping Project Original/Donut Hole Approach/Donut Hole v2')

from generateBranchNeighboursFn import generateNeighbours
from getBusDataFn import getBusData




planningRaw = 'hls18v1dyn_new.raw'
_,BranchDataDictPlanning = generateNeighbours(planningRaw)
BusDataDictPlanning = getBusData(planningRaw)

branchGroupLines=  []
TieDict = {}
for key in BranchDataDictPlanning.keys():
	 #RList  = BranchDataDictPlanning[key].R
	 ZList  = BranchDataDictPlanning[key].Z
	 Bus1 = key
	 Bus2List = BranchDataDictPlanning[key].toBus

	 

	 # Get pairs of buses which have same voltage and angles
	 """
	 Bus1VoltAngle = [float(BusDataDictPlanning[Bus1].voltpu), float(BusDataDictPlanning[Bus1].angle)]
	 for Bus2 in Bus2List:
	 	Bus2VoltAngle = [float(BusDataDictPlanning[Bus2].voltpu), float(BusDataDictPlanning[Bus2].angle)]
	 	if Bus1VoltAngle == Bus2VoltAngle:
	 		print Bus1 + ',' + Bus2
	"""

	 for i in range(len(ZList)):
	 	#Rst = RList[i]
	 	Z = ZList[i]
		if float(Z) <= 1e-4:
			to  = BranchDataDictPlanning[key].toBus[i]
			#Xctance = BranchDataDictPlanning[key].X[i]
			if Bus1 in TieDict.keys():
				TieDict[Bus1].append(to)
			else:
				TieDict[Bus1] = [to]

			#string = key + ',' + to + ',' + str(Rst) + ',' + str(Xctance)
			string = key + ',' + to + ',' + str(Z)
			branchGroupLines.append(string)

if __name__ == "__main__":
	with open('tmpBranchGroupPlanning.txt','w') as f:
		for line in branchGroupLines:
			f.write(line)
			f.write('\n')