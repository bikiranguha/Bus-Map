import shutil
latestRaw = 'RAW0501.raw'

import tryNumericTFMatching # automation of Load TF matching, as well as incorporating cases identified by Manual Map CS
import loadMap # script which does the maps by looking at newMapFile
import dealWithTFTer # maps all the TF tertiaries to their primaries
import checkMapping # checks for consistency of the manual maps in testMapOld and ManualMapCSPriority1 with that of autoTFMap
import tfMap # do tf maps specified in  matchTFData.txt

destTFData = 'C:/Users/Bikiran/Google Drive/Bus Mapping Project Original/Donut Hole Approach/Donut Hole v2/Raw with only 2 winders\Automate 345 kV mapping/'
shutil.copy(latestRaw,destTFData)