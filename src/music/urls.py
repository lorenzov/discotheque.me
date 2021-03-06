from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    # (r'^music/', include('music.foo.urls')),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # (r'^admin/', include(admin.site.urls)),
	(r'^services/visit/youtube/$', 'music.discotheque.views.visit_youtube'),
	
	(r'^services/go/next/(?P<id>\d+)/$', 'music.discotheque.views.go_next'),
	(r'^services/video/exclude/$', 'music.discotheque.views.service_exclude'),
	(r'^services/video/view/$', 'music.discotheque.views.visit_discotheque'),
	(r'^services/video/like/$', 'music.discotheque.views.like_discotheque'),
	#(r'^play/(?P<base62_id>\w+)$', 'music.discotheque.views.play'),
	(r'^$', 'music.discotheque.views.welcome'),
	(r'new/$', 'music.discotheque.views.new'),
	(r'^home/$', 'music.discotheque.views.home'),
	(r'^play/(?P<id>\d+).*/$', 'music.discotheque.views.play'),
	(r'^xd_receiver\.html$', direct_to_template, {'template': 'xd_receiver.htm'}),
	(r'^video/(?P<id>\d+)/$', 'music.discotheque.views.video'),
	(r'^v/(?P<id>\d+)/(?P<slug>).*/$', 'music.discotheque.views.video_view'),
	(r'^data/mostplayed/(?P<type>\d+)/$', 'music.discotheque.views.data_mostplayed'),
	(r'^data/lastplayed/$', 'music.discotheque.views.data_lastplayed'),
	(r'^send/$', 'music.discotheque.views.send'),
	(r'^stats/$', 'music.discotheque.views.stats'),
	(r'^drag/$', 'music.discotheque.views.drag'),
	(r'^robots\.txt$', 'music.discotheque.views.robots'),
    url(r'^login/$', 'music.discotheque.views.login'), 


)
