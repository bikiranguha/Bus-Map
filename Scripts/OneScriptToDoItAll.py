# get the raw file from CAPE and apply all the manual changes (mostly for some 3 winders and 4 winders)
import fixExportedCAPERaw

# generate the first iteration of the donut hole raw file
import mapAndcopyGen # map and copy gen data
import map345 # map 345 kv buses
import mapRemainingBus # map all buses
# NOTE: Please add all the isolated buses (can be found from isolatedBusList.txt) to no need to map set and use it as reference on what to add and what not to add
import changebranchDatav3 # generate new branch data
import changetfDatav4 # generate new transformer data
import mapLoad # generate new load data
#import loadConflictResolution # ran within mapLoad
import findShuntv2 # generate new switched shunt data
import cutoutComed
import compileAll0322
# Verified till here


# Now do the following things:
#  For the bus maps, the highest priority is the file which hemanth gave me. Carry out the mappings in that file, with phase shifts applied. After that, we 
# look at the 345 mappings, then the manual maps. Then any remaining maps will be carried out via neighbour BFS algorithm.
# Then we change all the branch data. Here we apply the branch impedance changes (given by hemanth and also mine if any)
# Then we look at transformer changes applied (by hemanth and by myself in the 3 winder substitution data. Only 3w->3w and 2w->2w subs can be applied here.
# After this, i give the file over to prof, who applies the perl script.
# Then i apply the tricky tf mappings (2w->3w or vice versa)
# Then i add all the manual data (bus, branch, tf) and skip corresponding data  


#In compileAll0322, TFIter3 is being used to get the tf data for comed. In place of this, we need our own tf data (which will have all tf data properly changed) 
# Think about whether to apply the final bus mapping before or after the first iteration of the raw file
# Or maybe we dont need to map the midpoints at all, they will be mapped properly
# If we decide to do the proper bus maps at the very beginning, then we should use old bus numbers for mapping.
# Also, we should do the tmaps separately. For the tmaps, the CAPE side should provide tmaps instead of the fict midpoints
# While applying the bus maps, we need to consider the phase shifts as well. We can use the logAngleChange for this
# 