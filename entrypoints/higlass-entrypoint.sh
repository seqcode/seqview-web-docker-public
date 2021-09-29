cd /usr/src/higlassWrapper/
python manage.py runserver 0.0.0.0:9000 >> /data/log/hgWrapper 2>&1&
cd /home/higlass/projects/
supervisord -n

