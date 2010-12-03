import gdata.youtube
import gdata.youtube.service
from music.discotheque.models import *

yt_service = gdata.youtube.service.YouTubeService()
# The YouTube API does not currently support HTTPS/SSL access.
yt_service.ssl = False

def cerberus():
	videos = Video.objects.filter(verified__exact = False).order_by('-id')
	for video in videos:
		try:
			entry = yt_service.GetYouTubeVideoEntry(video_id= video.identifier) #grabs information about the video
		except:
			
			video.verified = True
			video.save()
			continue
		video.verified = True
		video.save()	
		categories = entry.category
		music = False
		for category in categories:
			if 'music' in category.term.lower():
				music = True
				
		if music == True:
			video.validated = True
			video.verified = True
			d_id = create_identifier()
			video.d_identifier = d_id
		else:
			video.verified = True
			video.validated = False
		
			
		#thumbnails
		th120 = False
		th320 = False
		print entry.media.thumbnail
		for th in entry.media.thumbnail:
			print th.width + ' ' + th.url
			if th.width == '120' and th120 == False:
				print 120
				video.thumbnail120 = th.url
				th120 = True
			if th.width == '320' and th320 == False:
				print 320
				video.thumbnail320 = th.url
				th120 = True
					
		video.title = entry.title.text
			
		
		video.save()



if __name__ == '__main__':
	cerberus()