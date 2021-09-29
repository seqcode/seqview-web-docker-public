cd /usr/src/seqview
cp -r /tmp/static/* /usr/src/seqview/static/

gunicorn seqview.wsgi:application --reload --bind 0.0.0.0:8000

#echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('$DJANGO_SUPERUSER_USERNAME', '$DJANGO_SUPERUSER_EMAIL', '$DJANGO_SUPERUSER_PASSWORD')" | python manage.py shell
