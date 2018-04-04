"""
	Update the files in this folder and run this script. They will be automatically updated elsewhere, the dest given here

"""


import shutil

change_map = 'change_map.txt'
FinalRawManual = 'FinalRAW03312018MM2.raw'
#to_do_file = 'still_to_do_txt'
mapped_bus_file = 'mapped_buses_cleaned0313.csv'

# update change_map file in relevant google drive folder
dest_map_change = 'C:/Users/Bikiran/Google Drive/Bus Mapping Project Original/Donut Hole Approach/Donut Hole v2/3 winder substitution/change_map.txt'
shutil.copy(change_map,dest_map_change)

# update final manually changed raw file in relevant google drive folder
dest_raw = 'C:/Users/Bikiran/Google Drive/Bus Mapping Project Original/Donut Hole Approach/Donut Hole v2/Raw with only 2 winders/FinalRAW03312018MM2.raw'
shutil.copy(FinalRawManual,dest_raw)

# update map file
dest_mapfile1 = 'C:/Users/Bikiran/Google Drive/Bus Mapping Project Original/Donut Hole Approach/Donut Hole v2/3 winder substitution/mapped_buses_cleaned0313.csv'
dest_mapfile2 = 'C:/Users/Bikiran/Google Drive/Bus Mapping Project Original/Donut Hole Approach/Donut Hole v2/mapped_buses_cleaned0313.csv'
shutil.copy(mapped_bus_file,dest_mapfile1)
shutil.copy(mapped_bus_file,dest_mapfile2)