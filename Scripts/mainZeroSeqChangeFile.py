# all the steps done to convert the original zero seq data to new zero seq data

import updateZeroSeqFileReady # does bus renumbering
import getZeroSeqFileReady # generate 3 winder tmap
import convert3wto2w0seqv3 # converts all 3 winder tf data to 2 winder data using the tmaps
import changeZeroSeqBoundaryNonComed # renumbers the boundary non-comed buses