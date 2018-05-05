from manualMapper import MapChange


planningRaw = 'hls18v1dyn_1219.raw'
CAPERaw = 'RAW0501.raw'
newRawFile = 'RAW0501.raw'
originalCase = 'CAPE'
changeFile = 'changeExp.txt'
MapChange(planningRaw,changeFile,CAPERaw,newRawFile,originalCase)