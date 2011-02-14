# Replace these three settings.
PROJDIR="/home/lviscanti/discotheque.me/src/music"
PIDFILE="$PROJDIR/mysite.pid"
SOCKET="/home/lviscanti/discotheque.sock"
export PYTHONPATH=/var/discotheque/:/home/lviscanti/discotheque.me/src/:/var/django/
export DJANGO_SETTINGS_MODULE=music.settings  
cd $PROJDIR
if [ -f $PIDFILE ]; then
    kill `cat -- $PIDFILE`
    rm -f -- $PIDFILE
fi

exec ./manage.py runfcgi  method=threaded host=127.0.0.1 port=3033 pidfile=$PIDFILE 

