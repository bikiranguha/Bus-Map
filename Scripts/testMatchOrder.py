"""
just a little script to test the sorting idea in analysis345v2.py
"""

from difflib import SequenceMatcher
from string import punctuation

special_symbols = set(punctuation)


def getCompactString(s):
	compSList = [x for x in s if not (x == ' ' or x in special_symbols)]
	compS = ''
	for ele in compSList:
		compS += ele
	return compS



planningBusName = 'ESS W407K;9T'
CAPEsubNameList = ['ESS W-407-4 FERMILAB', 'ESS W-601 ROUT59', 'ESS W-407-6 FERMILAB - KAUTZ ROAD']
planningBusNameCompact = getCompactString(planningBusName)
print planningBusName
for CAPEsubName in CAPEsubNameList:
	CAPEsubNameCompact = getCompactString(CAPEsubName)
	similarity =  SequenceMatcher(None,planningBusNameCompact, CAPEsubNameCompact).ratio()

	print CAPEsubName +': ' + str(similarity)