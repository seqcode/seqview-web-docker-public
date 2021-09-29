# seqview-web-docker-public

## Installation

* Requirements
  * Docker >= 20.10.1
  * docker-compose >= 1.26.2
  * git >= 2.20.1

Clone this repo, then clone the repo igv-webapp-embeddable into the src/ directory. This step will be integrated into the Dockerfile in future versions.
````
git clone https://github.com/seqcode/seqview-web-docker.git
cd seqview-web-docker/src
git clone https://github.com/seqcode/igv-webapp-embeddable.git
````

Look at the docker-compose.yml file for configuration options.  If you have an existing mysql database with all the tables needed for seqview, set the fields in the docker-compose.yml as follows:
- Under the 'db' container definition, in the volume directive, map the location of your mysql data directory, mysql config, and optionally the mysql logs to the locations within the mysql container. For example, with a mysql instance on CentOS, this would look like:
```
volumes:
  - ./schemas:/docker-entrypoint-initdb.d/:ro
  - /etc/my.cnf/:/etc/mysql/conf.d:ro
  - /var/lib/mysql:/var/lib/mysql
  - /var/log:/var/log/
```
- You will also need to adjust the user directive under the db container defininition. Map the user id of your mysql user to id 27 in the container. 

 If you don't have an existing mysql database, the relevant databases will be created at startup in the mount location you specify in the docker-compose.yml. 

Create a file .env with the following fields with the values set to your preferences:

````
DEBUG='TRUE'
HOST=
SECRET_KEY=
DJANGO_USER=
DJANGO_SUPERUSER_USERNAME=
DJANGO_SUPERUSER_PASSWORD=
DJANGO_HOST=
MYSQL_ROOT_PASSWORD=
HOSTNAME=
````

Run the following to build the docker image:

````
docker-compose build
````

## Running the Container:

### Production

Once the container is built, you do not need to re-build it everytime the website is started again. Start the container by running:

```
docker-compose up
```


### Development

Modify your docker-compose.dev.yml file to add your configuration information.

Run:

```
docker-compose --f docker-compose.yml --f docker-compose.dev.yml up
```

With this, when you edit source in the genome-browser-client directory your changes will automatically be updated in the browser with [react hot module reloading](https://github.com/gaearon/react-hot-loader). Also, changes made to the source code in genome-browser will be auto-loaded for your next api call.

## Adding Data

If you are running seqview-web for the first time, you will want to create a superuser for the website. With the docker container started (see the [development](#development) and [production](#production) sections for starting the container), run the following command:

```
docker exec -it seqview-web-docker_seqview_1 python manage.py createsuperuser
```

This will prompt you for a username, email and password for the user. Input these and record them somewhere.

Now open the website in your browser:

```
<HOST_NAME>/admin/login/
```

Input your superuser credentials. From here, you can create users to access the website by going to the "Users" tab.
