cp -r /tmp/static/* /usr/src/seqview/static/
cd /usr/src/seqview

gunicorn seqview.wsgi:application --reload --bind 0.0.0.0:8000 --daemon 

#echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('$DJANGO_SUPERUSER_USERNAME', '$DJANGO_SUPERUSER_EMAIL', '$DJANGO_SUPERUSER_PASSWORD')" | python manage.py shell

cd /usr/src/seqview/frontend/src/
npm install
npm run start:dev

