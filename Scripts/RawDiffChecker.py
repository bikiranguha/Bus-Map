f1='cape_old_load.txt'
f2='cape_new_load.txt'

f1out='f1out.txt'
f2out='f2out.txt'

f1lines=[]
f2lines=[]
with open(f1,'r') as f:
	filecontent = f.read()
	fileLines = filecontent.split('\n')
	f1lines =fileLines

with open(f2,'r') as f:
	filecontent = f.read()
	fileLines = filecontent.split('\n')
	f2lines=fileLines


with open(f1out,'w') as f:
	for line in f1lines:
		if line not in f2lines:
			f.write(line)
			f.write('\n')

with open(f2out,'w') as f:
	for line in f2lines:
		if line not in f1lines:
			f.write(line)
			f.write('\n')

	
