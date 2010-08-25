from music.discotheque.models import *
from django.contrib.auth.models import User
from operator import itemgetter
import datetime
import fileinput
import time


def go_maecenas():
	count = 0
	artists = Artist.objects.all()
	for artist in artists:
		videos = Video.objects.filter(validated__exact = True)
		for video in videos:
			if artist.name.lower() in video.title.lower():
				print 'found ' + artist.name + ' ' + video.title
				videoartist = VideoArtist.objects.filter(video__exact = video, artist__exact = artist)
				if videoartist.count() == 0:
					videoartist = VideoArtist()
					videoartist.video = video
					videoartist.artist = artist
					print 'creating videoartist'
					videoartist.save()
			pass
		count += 1
		
		time.sleep(0.01)
	

if __name__ == '__main__':
	go_maecenas()