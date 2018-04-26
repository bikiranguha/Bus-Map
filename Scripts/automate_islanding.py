# try to automate the process of detecting islands  and disconnecting them
# Please select the working directory

# System imports
import os,sys


from os import listdir
from os.path import isfile, join
sys.path.append(r"C:\Program Files (x86)\PTI\PSSE33\PSSBIN")
os.environ['PATH'] = (r"C:\Program Files (x86)\PTI\PSSE33\PSSBIN;"
                       + os.environ['PATH'])

# Select working path ##########################################################
os.chdir(r"C:\Users\bikiran_remote\Desktop\Old raw")
################################################################################
# Local imports
import redirect
import psspy
import dyntools
import csv

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
bus_count = 0 # keep count of number of buses in island getting disconnected
# the tree command is responsible for detecting and disconnecting islands (see API book page 651)
ierr, buses = psspy.tree(1,1)  
bus_count +=buses
while buses >0:
	ierr, buses = psspy.tree(2,1)
	bus_count += buses

ierr = psspy.rawd_2(0,1,[1,1,1,0,0,0,0],0,raw_new)
print 'Number of buses disconnected: ', bus_count

