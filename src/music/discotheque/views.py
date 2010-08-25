# Create your views here.
from django.contrib.auth import authenticate, login
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden, HttpResponseServerError, HttpResponsePermanentRedirect
from django.shortcuts import render_to_response
from django.template import Context, loader, RequestContext
from django.contrib.auth.decorators import login_required
from django.views.decorators.vary import vary_on_headers
from django.contrib.auth.models import *
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.core import serializers
from django.shortcuts import get_object_or_404
from django.core.cache import cache
from music.discotheque.models import *
from django.template.defaultfilters import slugify
from music import settings
import datetime
import hashlib
import logging
import urlparse
import simplejson
import urllib
import cgi
import random


def welcome(request):
	if request.user.is_authenticated():
		return HttpResponseRedirect('/home/')
		template_context = {'settings': settings,  'lastvideos': Video.objects.filter(validated__exact = True).order_by('-id')[:20]}
		return render_to_response('login.html', template_context, context_instance=RequestContext(request))
		
	else:
		mpvvideos = []	    
		mpv = MostPlayedVideo.objects.filter(stats__exact = 2).order_by('-count')[:6]
		for vid in mpv:
			mpvvideos.append(vid.video)
				

		template_context = {'settings': settings,  'lastvideos': mpvvideos} #Video.objects.filter(validated__exact = True).order_by('-id')[:8]
		return render_to_response('login.html', template_context, context_instance=RequestContext(request))
def new(request):
	template_context = {'settings': settings,  'lastvideos': Video.objects.filter(validated__exact = True).order_by('-id')[:8]}
	return render_to_response('new.html', template_context, context_instance=RequestContext(request))



	


def stats(request):
	views = View.objects.all().order_by('-id')[:10]
	template_context = {'views': views}
	return render_to_response('stats.html', template_context,context_instance=RequestContext(request) )	


def data_lastplayed(request):
	if not request.user.is_authenticated():
		return HttpResponse('[]', mimetype="text/plain")
	views = View.objects.filter(user__exact = request.user).order_by('-id')[:50]
	videos = ''
	for view in views:
		identifier = view.video.identifier
		if not identifier in videos:
			videos += '|' + identifier
		pass
	#first character ignored
	return HttpResponse(videos[1:], mimetype="text/plain")


def play(request, id):
	user = User.objects.get(pk = id)	
	mpv = MostPlayedVideo.objects.filter(user__exact = user, stats__exact = 0).order_by('-count')	
	views = View.objects.filter(user__exact = user, youtube__exact = True).order_by('-date')[:30]
	videos = []
	for view in views:
		video = view.video
		if not video.validated == True:
			continue
		if not video in videos:
			videos.append(video)
			if len(videos) == 40:
				break
		pass
	pass
	mpvs = []
	for mpvideo in mpv:
		mpvs.append(mpvideo.video)
	c = RequestContext(request, {'lastvideosth': videos, 'lastvideos': videos , 'mostplayedvideos': mpvs, 'mostplayedvideosth': mpvs, 'user': user})
	t = loader.get_template('play.html')
	return HttpResponse(t.render(c))

def robots(request):
	output = 'User-agent: *\nDisallow: /services\nDisallow: /data'
	return HttpResponse(output, mimetype = 'text/plain')
				
def home(request):
	if not request.user.is_authenticated():
		return HttpResponseRedirect('/')
	
	
	mpv = MostPlayedVideo.objects.filter(user__exact = request.user, stats__exact = 0).order_by('-count')	
	views = View.objects.filter(user__exact = request.user, youtube__exact = True).order_by('-date')[:30]
	videos = []
	for view in views:
		video = view.video
		if not video.validated == True:
			continue
		if not video in videos:
			videos.append(video)
			if len(videos) == 40:
				break
		pass
	pass
	mpvs = []
	for mpvideo in mpv:
		mpvs.append(mpvideo.video)
	c = RequestContext(request, {'lastvideosth': videos, 'lastvideos': videos , 'mostplayedvideos': mpvs, 'mostplayedvideosth': mpvs})
	t = loader.get_template('home.html')
	return HttpResponse(t.render(c))


def drag(request):
		if not request.user.is_authenticated():
			return HttpResponseRedirect('/')


		mpv = MostPlayedVideo.objects.filter(user__exact = request.user, stats__exact = 0).order_by('-count')	
		views = View.objects.filter(user__exact = request.user, youtube__exact = True).order_by('-date')[:5]
		videos = []
		for view in views:
			video = view.video
			if not video.validated == True:
				continue
			if not video in videos:
				videos.append(video)
				if len(videos) == 10:
					break
			pass
		pass
		mpvs = []
		for mpvideo in mpv:
			mpvs.append(mpvideo.video)
		c = RequestContext(request, {'videos': mpvs,})
		t = loader.get_template('drag.html')
		return HttpResponse(t.render(c))

def video_view(request, id, slug):
	video = Video.objects.get(pk = id)
	c = RequestContext(request, {'lastvideos': Video.objects.filter(validated__exact = True).order_by('-id')[:4], 'video_id' : id, 'video': video })
	t = loader.get_template('video.html')
	return HttpResponse(t.render(c))

def video(request, id):
	video = Video.objects.get(pk = id)
	c = RequestContext(request, {'lastvideos': Video.objects.filter(validated__exact = True).order_by('-id')[:4], 'video_id' : id, 'video': video })
	t = loader.get_template('video.html')
	return HttpResponsePermanentRedirect('/v/' + str(video.id) + '/' + slugify(video.title) + '/')		




def visit_youtube(request):
	#print request.GET
	#if request.user.is_authenticated():
	#query_st = urlparse.parse_qsl(request.GET)
	if not request.user.is_authenticated():
		return HttpResponse('not logged')
	if 'url' in request.GET:
		url = request.REQUEST['url']
		video_id = None
		try:

			video_id = cgi.parse_qs(urlparse.urlparse(url).query)['v'][0]
		except Exception, e:
			logging.error('urlparse failed: ' + url + ' ' )
			return HttpResponse(ko)
		logging.debug('video_id' + video_id)
		video = Video.objects.get_or_create(identifier= video_id)[0]
		view = View(video = video, user = request.user)
		view.save()
		return HttpResponse('ok')


		#print query_st
	return HttpResponse('ok')
		#else:
		#	return HttpResponse('ko')




def visit_discotheque(request):
	#print request.GET
	#if request.user.is_authenticated():
	#query_st = urlparse.parse_qsl(request.GET)
	if not request.user.is_authenticated():
		return HttpResponse('not logged')
	if 'url' in request.GET:
		url = request.REQUEST['url']
		video_id = url
		
		logging.debug('video_id' + video_id)
		video = Video.objects.get_or_create(identifier= url)[0]
		view = View(video = video, user = request.user)
		view.youtube = False
		view.save()
		return HttpResponse('ok')
		
	
	#print query_st
	return HttpResponse('ok')
	#else:
	#	return HttpResponse('ko')
	
def service_exclude(request):	
	if not request.user.is_authenticated():
		return HttpResponse('not logged')
	if 'url' in request.GET:
		url = request.REQUEST['url']	
	video = Video.objects.get(identifier__exact = url)
	exclusion = Exclusion.objects.get_or_create(user = request.user, video = video)
	exclusion[0].save()
	#deleted this video from mostplayedvideo
	mpvs = MostPlayedVideo.objects.filter(video__exact = video, user__exact = request.user)
	for mpv in mpvs:
		mpv.delete()
	return HttpResponse('ok', mimetype = 'text/plain')
	
	
	
	
def like_discotheque(request):
	#print request.GET
	#if request.user.is_authenticated():
	#query_st = urlparse.parse_qsl(request.GET)
	if not request.user.is_authenticated():
		return HttpResponse('not logged')
	if 'url' in request.GET:
		url = request.REQUEST['url']
		video_id = url

		video = Video.objects.get_or_create(identifier= url)[0]
		view = View(video = video, user = request.user)
		view.youtube = False
		#this is a like!
		view.score = 3
		view.save()
		return HttpResponse('ok')


		#print query_st
		return HttpResponse('ok')
		#else:
		#	return HttpResponse('ko')
		
def login(request):
	    error = None

	    if request.user.is_authenticated():
	        return HttpResponseRedirect('/home/')

	    if request.GET:
	        if 'code' in request.GET:
	            args = {
	                'client_id': '120761471302389',
	                'redirect_uri': 'http://www.discotheque.me/login/',
	                'client_secret': '25e65e879035f7a013e2337b6d9c149d',
	                'code': request.GET['code'],
	            }

	            url = 'https://graph.facebook.com/oauth/access_token?' + urllib.urlencode(args)
	            response = cgi.parse_qs(urllib.urlopen(url).read())
	            access_token = ''
	            try: 
	                access_token = response['access_token'][0]
	            except:
	                return HttpResponse(url)
                

	            facebook_session = FacebookSession.objects.get_or_create(
	                access_token=access_token,
	            )[0]
	            expires = response['expires'][0]
	            facebook_session.expires = expires
	            facebook_session.save()

	            user = auth.authenticate(token=access_token, request = request)
	            if user:
	                if user.is_active:
	                    auth.login(request, user)
	                    return HttpResponseRedirect('/home/')
	                else:
	                    error = 'AUTH_DISABLED'
	            else:
	                error = 'AUTH_FAILED'
	        elif 'error_reason' in request.GET:
	            error = 'AUTH_DENIED'
	    mpvvideos = []	    
	    mpv = MotPlayedVideo.objects.filter(stats__exact = 1)
	    for vid in mpv:
	    	mpvvideos.append(vid.video)
	    	if len(mpvvideos) > 6:
	    		break
	    	break	
	
	    template_context = {'settings': settings, 'error': error, 'lastvideos': mpvvideos} #Video.objects.filter(validated__exact = True).order_by('-id')[:4]
	    return render_to_response('login.html', template_context, context_instance=RequestContext(request))


def data_mostplayed(request, type = 0):
	if not request.user.is_authenticated():
		return HttpResponse('you must be logged in in order to execute this request')
	videos = MostPlayedVideo.objects.filter(user__exact = request.user, stats__exact = type).order_by('-count')
	output = ''
	
	for video in videos:
		try:
			output +=  + '|' + video.video.identifier
		except:
			pass
	return HttpResponse(output[1:], mimetype="text/plain")
		

def go_next(request, id):
	video = Video.objects.get(pk = id)
	views = View.objects.filter(video__exact = video).order_by('-id')[:10]
	next_video = None
	for view in views:
		prec_view = View.objects.filter(user__exact = view.user, id__lte = view.id).exclude(video__exact = video).order_by('-id')[:1]
		if prec_view.count() >0:
			next_video = prec_view[0].video
			break
	if next_video == None:
		next_videos = Video.objects.all().order_by('-id')[:100]
		random.seed()
		next_video = next_videos[random.sample(range(100), 1)[0]]
	return HttpResponsePermanentRedirect('/v/' + str(next_video.id) + '/' + slugify(video.title) + '/')	
	

def xd_receiver(request):
	return render_to_response('xd_receiver.html')
