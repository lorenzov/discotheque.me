from django.db import models
from django.contrib.auth.models import User
from random import choice
import string

def get_identifier():
	chars = string.letters + string.digits
	newpasswd = ''
	for i in range(10):
		newpasswd = newpasswd + choice(chars)
	return newpasswd
def create_identifier():
	d_id = ''
	while True:
		d_id = get_identifier()
		print d_id
		dvideos = Video.objects.filter(d_identifier__exact = d_id).count()
		print dvideos
		if dvideos <= 0:
			break
	return d_id.upper()
# Create your models here.




class Video(models.Model):
	identifier = models.CharField(max_length = 15, db_index = True)
	verified = models.BooleanField(default = False)
	validated = models.BooleanField(default = False, db_index = True)
	d_identifier = models.CharField(max_length = 10, blank = True, null = True)
	title = models.TextField(null = True, blank = True)
	thumbnail120 = models.CharField(max_length = 255, blank = True, null = True)
	thumbnail320 = models.CharField(max_length = 255, blank = True, null = True)
	title = models.CharField(max_length = 255, blank = True, null = True)
	def __cmp__(self, other):
		if not type(self) == type(other):
			return False
			
		if other.identifier == self.identifier:
			return True
		return False
	
class MostPlayedVideo(models.Model):
	video = models.ForeignKey(Video, db_index = True)
	user = models.ForeignKey(User, db_index = True, blank = True, null = True)
	stats = models.SmallIntegerField(default = 0, db_index = True)
	count = models.IntegerField(default = 0)	

		   
class Exclusion(models.Model):
	video = models.ForeignKey(Video, db_index = True)
	user = models.ForeignKey(User, db_index = True)
	active = models.BooleanField(default = True)
	date = models.DateTimeField(auto_now_add = True)
	
	
	
class View(models.Model):
	video = models.ForeignKey(Video, db_index = True)
	user = models.ForeignKey(User, db_index = True)
	date = models.DateTimeField(auto_now_add = True)
	youtube = models.BooleanField(default = True)	
	score = models.SmallIntegerField(default = 1)

class Exclusion(models.Model):
	user = models.ForeignKey(User, db_index = True)
	video = models.ForeignKey(Video, db_index = True)
	validated = models.BooleanField(default = True)

class Artist(models.Model):
	name = models.CharField(max_length = 256, db_index = True)
	source = models.CharField(max_length = 24, blank = True, null = True)
	src = models.SmallIntegerField(default = 0, blank = True, null = True)


class VideoArtist(models.Model):
	video = models.ForeignKey(Video, db_index = True)
	artist = models.ForeignKey(Artist, db_index = True)
	
class FacebookUser(models.Model):
	facebook_id = models.CharField(max_length=100, unique=True)
	contrib_user = models.OneToOneField(User)
	contrib_password = models.CharField(max_length=100)

class UserProfile(models.Model):
	user = models.ForeignKey(User, unique = True, db_index = True)
	
	
class FacebookSessionError(Exception):   
	    def __init__(self, error_type, message):
	        self.message = message
	        self.type = error_type
	    def get_message(self): 
	        return self.message
	    def get_type(self):
	        return self.type
	    def __unicode__(self):
	        return u'%s: "%s"' % (self.type, self.message)
class FacebookSession(models.Model):

	    access_token = models.CharField(max_length=103, unique=True)
	    expires = models.IntegerField(null=True)

	    user = models.ForeignKey(User, null=True)
	    uid = models.BigIntegerField(unique=True, null=True)

	    class Meta:
	        unique_together = (('user', 'uid'), ('access_token', 'expires'))

	    def query(self, object_id, connection_type=None, metadata=False):
	        import urllib
	        import simplejson

	        url = 'https://graph.facebook.com/%s' % (object_id)
	        if connection_type:
	            url += '/%s' % (connection_type)

	        params = {'access_token': self.access_token}
	        if metadata:
	            params['metadata'] = 1

	        url += '?' + urllib.urlencode(params)
	        response = simplejson.load(urllib.urlopen(url))
	        if 'error' in response:
	            error = response['error']
	            raise FacebookSessionError(error['type'], error['message'])
	        return response