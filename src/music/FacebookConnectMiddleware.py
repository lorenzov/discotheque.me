# FacebookConnectMiddleware.py
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from music.discotheque.models import UserProfile
from django.conf import settings

import logging
import md5
import urllib
import time
import simplejson
from datetime import datetime

# Rest server used to ask some information on facebook connect
REST_SERVER = 'http://api.facebook.com/restserver.php'

# You can get your User ID here: http://developers.facebook.com/tools.php?api
# MY_FACEBOOK_UID = '535315478'

NOT_FRIEND_ERROR = 'You must be my Facebook friend to log in.'
PROBLEM_ERROR = 'There was a problem. Try again later.'
ACCOUNT_DISABLED_ERROR = 'Your account is not active.'
ACCOUNT_PROBLEM_ERROR = 'There is a problem with your account.'

class FacebookConnectMiddleware(object):
    
    delete_fb_cookies = False
    facebook_user_is_authenticated = False
    
    def process_request(self, request):
        logging.debug(" -- START MIDDLEWARE REQUEST PROCESSING")
        try:
             # Set the facebook message to empty. This message can be used to dispaly info from the middleware on a Web page.
            request.facebook_message = None

            # Don't bother trying FB Connect login if the user is already logged in
            if not request.user.is_authenticated():
                logging.debug(" >> User is NOT authenticated in padiri")
                #logging.debug(request.COOKIES)
                logging.debug(" >> >> Settings: " + settings.API_KEY)
                # FB Connect will set a cookie with a key == FB App API Key if the user has been authenticated
                if settings.API_KEY in request.COOKIES:
                    logging.debug(" >> User is authenticated in FB")
                    
                    signature_hash = self.get_facebook_signature(request.COOKIES, True)
                    logging.debug(" >> got signature")               
                    # The hash of the values in the cookie to make sure they're not forged
                    if(signature_hash == request.COOKIES[settings.API_KEY]):
                        logging.debug(" >> signature hash ok")
                        # If session hasn't expired
                        if(datetime.fromtimestamp(float(request.COOKIES[settings.API_KEY+'_expires'])) > datetime.now()):
                            logging.debug(" >> FB session has not expired (cookies is valid)")
                            
                            try:
                                logging.debug(" >> Search for a user inside the auth_user table")
                                
                                # Try to get Django account corresponding to friend
                                # Authenticate then login (or display disabled error message)
                                django_user = User.objects.get(username=request.COOKIES[settings.API_KEY + '_user'])
                                user = authenticate(username=request.COOKIES[settings.API_KEY + '_user'], 
                                                    password=md5.new(request.COOKIES[settings.API_KEY + '_user'] + settings.SECRET_KEY).hexdigest())
                                if user is not None:
                                    if user.is_active:
                                        logging.debug(" >> Login an existing FB-Altomic User")
                                        request.session['facebook_connection'] = True
                                        
                                        login(request, user)
                                        self.facebook_user_is_authenticated = True
                                    else:
                                        request.facebook_message = ACCOUNT_DISABLED_ERROR
                                        self.delete_fb_cookies = True
                                else:
                                   request.facebook_message = ACCOUNT_PROBLEM_ERROR
                                   self.delete_fb_cookies = True
                            except User.DoesNotExist:
                                logging.debug(" >> Create a new FB-Altomic User")
                                
                                # There is no Django account for this Facebook user.
                                # Create one, then log the user in.
                
                                # Make request to FB API to get user's first and last name
                                user_info_params = {
                                    'method': 'Users.getInfo',
                                    'api_key': settings.API_KEY,
                                    'call_id': time.time(),
                                    'v': '1.0',
                                    'uids': request.COOKIES[settings.API_KEY + '_user'],
									'session_key': request.COOKIES[settings.API_KEY + '_session_key'],
                                    'fields': 'first_name,last_name,email',
                                    'format': 'json',
                                }

                                user_info_hash = self.get_facebook_signature(user_info_params)

                                user_info_params['sig'] = user_info_hash
                
                                user_info_params = urllib.urlencode(user_info_params)

                                user_info_response  = simplejson.load(urllib.urlopen(REST_SERVER, user_info_params))
                
                                # Create user
                                user = User.objects.create_user(request.COOKIES[settings.API_KEY + '_user'], '', 
                                                                md5.new(request.COOKIES[settings.API_KEY + '_user'] + 
                                                                settings.SECRET_KEY).hexdigest())
                                
                                                              
                                user.first_name = user_info_response[0]['first_name']
                                user.last_name = user_info_response[0]['last_name']
                                if user_info_response[0]['email'] is not None:
                                    user.email = user_info_response[0]['email']
                                up.up_name = user_info_response[0]['first_name'] + " " + user_info_response[0]['last_name']
                                up.save()
                                
                                
                                user.save()
                                
                                # Authenticate and log in (or display disabled error message)
                                user = authenticate(username=request.COOKIES[settings.API_KEY + '_user'], 
                                                    password=md5.new(request.COOKIES[settings.API_KEY + '_user'] + settings.SECRET_KEY).hexdigest())
                                if user is not None:
                                    if user.is_active:
                                        logging.debug(" >> Login a new FB-padiri User")
                                        request.session['facebook_connection'] = True
                                        
                                        login(request, user)
                                        self.facebook_user_is_authenticated = True
                                    else:
                                        request.facebook_message = ACCOUNT_DISABLED_ERROR
                                        self.delete_fb_cookies = True
                                else:
                                   request.facebook_message = ACCOUNT_PROBLEM_ERROR
                                   self.delete_fb_cookies = True
                        
                        # Cookie session expired
                        else:
                            # when logout from facebook
                            #logout(request)
                            logging.debug('cookie expired')
                            self.delete_fb_cookies = True
                        
                    # Cookie values don't match hash
                    else:
                        logging.debug('cookie values don''t match hash')
                        #logout(request)
                        self.delete_fb_cookies = True
                
                # User is not authenticated in Facebook
                else:
                    logging.debug(" >> User is not Authenticated in Facebook")
                    
            # Logged in
            else:
                logging.debug(" >> User IS authenticated with Altomic. So do not bother me")
                
                # If FB Connect user
                if settings.API_KEY in request.COOKIES:
                    logging.debug(" >> Still connected to FB")
                    request.session['facebook_connection'] = True
                    
                    # IP hash cookie set
                    if 'fb_ip' in request.COOKIES:
                        
                        try:
                            real_ip = request.META['HTTP_X_FORWARDED_FOR']
                        except KeyError:
                            real_ip = request.META['REMOTE_ADDR']
                        
                        # If IP hash cookie is NOT correct
                        if request.COOKIES['fb_ip'] != md5.new(real_ip + settings.API_SECRET + settings.SECRET_KEY).hexdigest():
                             #logout(request)
                             self.delete_fb_cookies = True
                    # FB Connect user without hash cookie set
                    else:
                        #logout(request)
                        self.delete_fb_cookies = True
                else:
                    # we need this otherwise we will not have the user informations
                    # through the JS call when I log out from facebook
                    # We will not need this when we will make a binding between
                    # the FB user and the Altomic user
                    #if request.session.get('facebook_connection', False):
                    logging.debug(" >> Not connected to FB anymore. Switching to altomic auth system")
                    request.session['facebook_connection'] = False
                    if request.user.is_authenticated():
                        logout(request)
                        
        # Something else happened. Make sure user doesn't have site access until problem is fixed.
        except:
            request.facebook_message = PROBLEM_ERROR
            #logout(request)
            self.delete_fb_cookies = True
        
    def process_response(self, request, response):        
        # Delete FB Connect cookies
        # FB Connect JavaScript may add them back, but this will ensure they're deleted if they should be
        if self.delete_fb_cookies is True:
            response.delete_cookie(settings.API_KEY + '_user')
            response.delete_cookie(settings.API_KEY + '_session_key')
            response.delete_cookie(settings.API_KEY + '_expires')
            response.delete_cookie(settings.API_KEY + '_ss')
            response.delete_cookie(settings.API_KEY)
            response.delete_cookie('fbsetting_' + settings.API_KEY)
    
        self.delete_fb_cookies = False
        
        if self.facebook_user_is_authenticated is True:
            try:
                real_ip = request.META['HTTP_X_FORWARDED_FOR']
            except KeyError:
                real_ip = request.META['REMOTE_ADDR']
            response.set_cookie('fb_ip', md5.new(real_ip + settings.API_SECRET + settings.SECRET_KEY).hexdigest())
        
        # process_response() must always return a HttpResponse
        return response
                                
    # Generates signatures for FB requests/cookies
    def get_facebook_signature(self, values_dict, is_cookie_check=False):
        signature_keys = []
        for key in sorted(values_dict.keys()):
            if (is_cookie_check and key.startswith(settings.API_KEY + '_')):
                signature_keys.append(key)
            elif (is_cookie_check is False):
                signature_keys.append(key)

        if (is_cookie_check):
            signature_string = ''.join(['%s=%s' % (x.replace(settings.API_KEY + '_',''), values_dict[x]) for x in signature_keys])
        else:
            signature_string = ''.join(['%s=%s' % (x, values_dict[x]) for x in signature_keys])
        signature_string = signature_string + settings.API_SECRET

        return md5.new(signature_string).hexdigest()
        
