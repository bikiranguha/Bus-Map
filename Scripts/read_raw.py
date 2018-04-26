# just read the file and solve power flow
# Please select the working directory

# System imports
import os,sys


from os import listdir
from os.path import isfile, join
sys.path.append(r"C:\Program Files (x86)\PTI\PSSE33\PSSBIN")
os.environ['PATH'] = (r"C:\Program Files (x86)\PTI\PSSE33\PSSBIN;"
                       + os.environ['PATH'])

# Select working path ##########################################################
os.chdir(r"C:\Users\bikiran_remote\Desktop")
################################################################################
# Local imports
import redirect
import psspy
import dyntools
import csv



pf_options = [
    0,  #disable taps
    0,  #disable area exchange
    0,  #disable phase-shift
    0,  #disable dc-tap
    0,  #disable switched shunts
    0,  #do not flat start
    0,  #apply var limits immediately
    0,  #disable non-div solution
]



# Inputs and outputs
filename = 'tmpv2.raw' # old raw file
raw_new = 'tmpv2_island.raw' # new raw file created after disconnecting all the islands
psse_log = 'psse_log.txt'
######
redirect.psse2py()
psspy.psseinit(buses=80000)
# Redirect any psse outputs to psse_log
psspy.report_output(2,psse_log,[0,0])
psspy.progress_output(6,psse_log,[0,0]) #ignored
psspy.alert_output(6,psse_log,[0,0]) #ignored
psspy.prompt_output(6,psse_log,[0,0]) #ignored
##############################


ierr = psspy.read(0, filename)
ierr = psspy.fnsl(pf_options) # solve power flow

