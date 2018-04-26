import os
import shutil

dest = 'C:/Users/Bikiran/Documents/Git repositories/Bus Map/Scripts' # destination folder

#shutil.copyfile(AllMapFileNew,os.path.join(dest, name))
for root, dirs, files in os.walk(".", topdown=True):

   for name in files:
   	if name.endswith('.py'):
   		#print name
   		#os.remove(os.path.join(dest, name))
   		abs_path = os.path.join(root, name) # path of file to be copied
   		shutil.copy(abs_path,dest)