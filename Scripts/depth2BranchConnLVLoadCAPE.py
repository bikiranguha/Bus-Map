"""
get depth 2 branch data (even disconnected ones) for ComedLVLoadBusSet in CAPE
"""

from loadSplitCAPE import ComedLVLoadSet
from generateBranchDictCAPE import BranchConnDict # includes any branch data, even disconnected ones
Depth2Dict = {}


# get the required set
for bus in ComedLVLoadSet:
	if bus in BranchConnDict.keys(): 
		Depth2Dict[bus] = set()
		neighbourdepth1 = BranchConnDict[bus]  # get branches
		#add depth 1 neighbours
		for neighbour in neighbourdepth1:
			if  neighbour != bus:
				Depth2Dict[bus].add(neighbour)
				# add depth 2 neighbours
				if neighbour in BranchConnDict.keys():
					neighbourdepth2 = BranchConnDict[neighbour] # depth 2
					for n2 in neighbourdepth2:
						if n2 != bus:
							Depth2Dict[bus].add(n2)



