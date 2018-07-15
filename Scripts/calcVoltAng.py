#start: LV side of tf
# end: other side of HV line
import math
startV = 0.95441
startAng = -61.8389
endV = 1.00148
endAng = -61.8382
Rend = 9.66667E-05
Rstart = 1.7597E-03/167.0*100
Xend = 3.90000E-04
Xstart = 1.07650E-01/167.0*100

voltDiff = endV - startV
angDiff = endAng - startAng

Zstart = math.sqrt(Rstart**2 + Xstart**2)
Zend = math.sqrt(Rend**2 + Xend**2)
Ztot = Zstart + Zend
RatioStart = Zstart/Ztot
RatioEnd = Zend/Ztot

tapV = startV + RatioStart*voltDiff
tapAng = startAng + RatioStart*angDiff

print tapV
print tapAng


