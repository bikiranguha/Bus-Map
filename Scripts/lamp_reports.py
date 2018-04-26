# System imports
import os,sys


from os import listdir
from os.path import isfile, join
from checkLoadSplit import multTFLoad
sys.path.append(r"C:\Program Files (x86)\PTI\PSSE33\PSSBIN")
os.environ['PATH'] = (r"C:\Program Files (x86)\PTI\PSSE33\PSSBIN;"
                       + os.environ['PATH'])

# Select working path ##########################################################
#os.chdir(r"C:\Users\bikiran_remote\Desktop\NewCAPECleanOld")
################################################################################
# Local imports
import redirect
import psspy
import dyntools
import csv


planningRaw = 'hls18v1dyn_1219.raw'
psse_log = 'log_planning_multTFLoad.txt'
redirect.psse2py()
psspy.psseinit(buses=80000)
# Silence all psse outputs
psspy.report_output(2,psse_log,[0,0])
psspy.progress_output(6,psse_log,[0,0]) #ignored
psspy.alert_output(6,psse_log,[0,0]) #ignored
psspy.prompt_output(6,psse_log,[0,0]) #ignored
##############################

ierr = psspy.read(0, planningRaw)


# File:"C:\Users\bikiran_remote\Desktop\report_bus_data.py", generated on MON, MAR 05 2018  19:33, release 33.03.00
for bus in multTFLoad:
	ierr = psspy.bsys(1,0,[0.0,0.0],0,[],1,[int(bus)],0,[],0,[]) # PAGE 1373 of API book
	ierr = psspy.lamp(1,0) # page 258 of API book


"""
with open(psse_log,'r') as f:
    filecontent = f.read()
    fileLines = filecontent.split('\n')

print fileLines[-1]
"""
