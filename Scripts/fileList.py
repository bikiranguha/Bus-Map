import os

lst = os.listdir('.')
for file in lst:
	if not file.endswith('.pyc'):
		print file