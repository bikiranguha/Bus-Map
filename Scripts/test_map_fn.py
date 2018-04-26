from manualMapper import MapChange

planningRaw = 'hls18v1dyn_new.raw'
CAPERaw = 'Raw0419_reen.raw'
newRawFile  = 'Raw0419_reen_m.raw'
changeFile = 'testtmp.txt'
MapChange(planningRaw,changeFile,CAPERaw,newRawFile,'planning')