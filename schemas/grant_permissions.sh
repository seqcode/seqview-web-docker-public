mysql -u root -p$MYSQL_ROOT_PASSWORD << GRANTS
create user '$DJANGO_USER'@'$DJANGO_HOST' identified by '$DJANGO_PWORD';
grant select on core.* to '$DJANGO_USER'@'$DJANGO_HOST';
grant select on seqdata.* to '$DJANGO_USER'@'$DJANGO_HOST';
grant all privileges on browserwebsite.* to '$DJANGO_USER'@'$DJANGO_HOST';
GRANTS
