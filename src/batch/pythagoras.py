from music.discotheque.models import *
from django.contrib.auth.models import User
from operator import itemgetter
import datetime

import time

def calculate(user, stats = 0, days = 90):
	views = View.objects.filter(user__exact = user, date__gte = datetime.datetime.now() - datetime.timedelta(days))
	videos = {}
	for view in views:
		video = view.video.identifier
		if video in videos.keys():
			val = videos[video]
			if view.youtube:
				videos[video] = val + 1.5
			else:
				videos[video] = val + 1
		else:
			if view.youtube:
				videos[video] = 1.5
			else:
				videos[video] = view.score
		pass
	pass
	sorted_videos = sorted(videos.iteritems(), key=itemgetter(1), reverse = True)
	index = 0
	#print sorted_videos
	for s_video in sorted_videos:
		
		exclusion = Exclusion.objects.filter(video__identifier__exact = s_video[0], user__exact = user )
		if exclusion.count() > 0:
			#this video can't be included
			continue
		
		mpv = MostPlayedVideo(user = user)
		mpv.video = Video.objects.get(identifier__exact = s_video[0])
		mpv.count = s_video[1]
		mpv.stats = stats
		mpv.save()
		
		index += 1
		if index > 400:
			break
		pass
	pass
	
def calculateTop(stats = 1, days = 90):
	views = View.objects.filter( date__gte = datetime.datetime.now() - datetime.timedelta(days))
	if views.count() == 0:
		calculateTop(stats, days * 2)
		return
	videos = {}
	for view in views:
		video = view.video.identifier
		if video in videos.keys():
			val = videos[video]
			if view.youtube:
				videos[video] = val + 1.5
			else:
				videos[video] = val + 1
			
		else:
			if view.youtube:
				videos[video] = 1.5
			else:
				videos[video] = view.score
		pass
	pass
	sorted_videos = sorted(videos.iteritems(), key=itemgetter(1), reverse = True)
	index = 0
	#print sorted_videos
	time.sleep(0.1)
	for s_video in sorted_videos:
		mpv = MostPlayedVideo()
		mpv.video = Video.objects.get(identifier__exact = s_video[0])
		mpv.count = int(s_video[1])
			
		mpv.stats = stats
		mpv.save()

		index += 1
		if index > 700:
			break
		pass
		pass


def deleteTop(stats = 1):
	MostPlayedVideo.objects.filter(stats__exact = stats).delete()

def delete(user, stats = 0):
	MostPlayedVideo.objects.filter(user__exact = user, stats__exact = stats).delete()
	
	
if __name__ == '__main__':
	deleteTop()
	calculateTop()
	deleteTop(2)
	calculateTop(2,0.3)
	users = User.objects.all()
	for user in users:
		delete(user, 0)
		calculate(user, 0, 90)
		time.sleep(0.01)
	
		