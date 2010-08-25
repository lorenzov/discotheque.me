from music.discotheque.models import *
from django.contrib.auth.models import User
from operator import itemgetter
import datetime
import fileinput

def go_import():
	
	for line in fileinput.input(['artists.txt']):
		if '(' in line:
			line = line[:line.find('(')]
		if len(line) < 2:
			#skip short lines
			continue
		print 'name ' + line
		
		artists = Artist.objects.filter(name__exact = line)
		try:
			if artists.count() > 0:
				#skip, already existing
				continue
			
			artist = Artist()
			artist.name = line
			print 'creating ' + line
			print ' ----'
			artist.save()
		except:
			print 'error while saving ' + line
			print '......'

if __name__ == '__main__':
	go_import()