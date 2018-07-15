# script by hemanth to distill the tf 3w changelogs

f1='tf3winderChangeLogIter3.txt'


changeLog = 'changeBusNoLog.txt'
changeDictOldToNew = {} # keeps track of old to new changes
changeDictNewToOld = {}


with open(changeLog,'r') as f:
    filecontent = f.read()
    fileLines = filecontent.split('\n')
    for line in fileLines:
        if 'CAPE' in line:
            continue
        words = line.split('->')
        if len(words) < 2:
            continue
        OldBus = words[0].strip()
        NewBus = words[1].strip()
        changeDictOldToNew[OldBus] = NewBus
        changeDictNewToOld[NewBus] = OldBus

with open(f1,'r') as f:
	filecontent = f.read()
	fileLines = filecontent.split('\n')

	for line in fileLines:
		if '->' in line:
			words=line.split('->')
			if len(words[1])==1:
				capewords=words[0].split(',')
				capeoldwords=[]
				for i in range(len(capewords)-1):
					if capewords[i] in changeDictNewToOld.keys():
						capeoldwords.append(changeDictNewToOld[capewords[i]])
					else:
						capeoldwords.append(capewords[i])

				print capeoldwords[0].rjust(6)+','+capeoldwords[1].rjust(6)+','+capeoldwords[2].rjust(6)+','+capewords[3]+'->'+words[1]
	print 'set maps'
	for line in fileLines:
		if '->' in line:
			words=line.split('->')
			if 'set' in words[1]:
				words2=words[1][5:len(words[1])-2]
				words2=words2.split(',')

				capewords=words[0].split(',')
				capeoldwords=[]
				for i in range(len(capewords)-1):
					if capewords[i] in changeDictNewToOld.keys():
						capeoldwords.append(changeDictNewToOld[capewords[i]])
					else:
						capeoldwords.append(capewords[i])

				if ' ' in words2[2][2:8]:
					print capeoldwords[0].rjust(6)+','+capeoldwords[1].rjust(6)+','+capeoldwords[2].rjust(6)+','+capewords[3]+'->'+words2[0].strip("'").strip()+','+words2[1][2:8] +','+words2[2][2:9]
				
				else:
					print capeoldwords[0].rjust(6)+','+capeoldwords[1].rjust(6)+','+capeoldwords[2].rjust(6)+','+capewords[3]+'->'+words2[0].strip("'").strip()+','+words2[1][2:8] +','+words2[2][2:8]

	print 'list maps'
	for line in fileLines:
		if '->' in line:
			words=line.split('->')
			if 'set' not in words[1] and '[' in words[1]:
				words2=words[1][1:len(words[1])-1]
				words2=words2.split(',')

				capewords=words[0].split(',')
				capeoldwords=[]
				for i in range(len(capewords)-1):
					if capewords[i] in changeDictNewToOld.keys():
						capeoldwords.append(changeDictNewToOld[capewords[i]])
					else:
						capeoldwords.append(capewords[i])
				
				if ' ' in words2[2][2:8]:
					print capeoldwords[0].rjust(6)+','+capeoldwords[1].rjust(6)+','+capeoldwords[2].rjust(6)+','+capewords[3]+'->'+words2[0].strip("'").strip()+','+words2[1][2:8] +','+words2[2][2:9]

				else:
					print capeoldwords[0].rjust(6)+','+capeoldwords[1].rjust(6)+','+capeoldwords[2].rjust(6)+','+capewords[3]+'->'+words2[0].strip("'").strip()+','+words2[1][2:8] +','+words2[2][2:8]


	
	print 'two winder maps'
	for line in fileLines:
		if '->' in line:
			words=line.split('->')

			if 'set' not in words[1] and '[' not in words[1]:
				words2=words[1].split(',')
				if len(words2)==4 and words2[2].strip()=='0':
					capewords=words[0].split(',')
					capeoldwords=[]
					for i in range(len(capewords)-1):
						if capewords[i] in changeDictNewToOld.keys():
							capeoldwords.append(changeDictNewToOld[capewords[i]])
						else:
							capeoldwords.append(capewords[i])
					print capeoldwords[0].rjust(6)+','+capeoldwords[1].rjust(6)+','+capeoldwords[2].rjust(6)+','+capewords[3]+'->'+words[1]

	print 'three winder maps'
	for line in fileLines:
		if '->' in line:
			words=line.split('->')

			if 'set' not in words[1] and '[' not in words[1]:
				words2=words[1].split(',')
				if len(words2)==4 and words2[2].strip()!='0':
					capewords=words[0].split(',')
					capeoldwords=[]
					for i in range(len(capewords)-1):
						if capewords[i] in changeDictNewToOld.keys():
							capeoldwords.append(changeDictNewToOld[capewords[i]])
						else:
							capeoldwords.append(capewords[i])
					print capeoldwords[0].rjust(6)+','+capeoldwords[1].rjust(6)+','+capeoldwords[2].rjust(6)+','+capewords[3]+'->'+words[1]


	print 'special cases'
	for line in fileLines:
		if '->' in line:
			words=line.split('->')

			if 'Special' in line:
				
				for i in range(len(capewords)-1):
					if capewords[i] in changeDictNewToOld.keys():
						capeoldwords.append(changeDictNewToOld[capewords[i]])
					else:
						capeoldwords.append(capewords[i])
				print capeoldwords[0].rjust(6)+','+capeoldwords[1].rjust(6)+','+capeoldwords[2].rjust(6)+','+capewords[3]+'->'+words[1]


	print '750048,1022,5342,1 ->270899', '272587', ' 275321'+' changed manually in list maps'

