# Crypto trader API

Web API application to trading crypto currency.

## Environment
* Windows 7
* Pycharm Community edition
* Python3.6
* postgres 10
* VirtualBox 6 (CentOS 7)

I worked on Windows 7, but it was ideal environment for production, then I create virtual
**CentOS**. System is in **Python 3.6**, Flask and SQLAlchemy. Docker files created for development/testing
and production environment.

## API description

I design simple and clean structure for **Flask** webservice, prepare for multiple versions of API,
package to design API I use **flask-restx** what is **flask-restplus** fork, but more supported now.
Package to work with database I choose **flask-sqlalchemy** and for serialization
**flask-marshmallow**. For development run **wsgi.py** on development Flask WSGI server. For production I choose **Gunicorn**,
because is simple with good performance and experience with this solution.
I work with Postgres/SQLite database.

I create the **Swagger** documentation is there: http://localhost:5001/api/v1/crypto

## Build and run

For development proposes run wsgi file:

`$ python3.6 wsgi.py`

My System contain two types of Dockerfile and docker-compose files without extension for development/test and
with extension .prod for production environment. After build up image are ready to use
e.g. AWS Fargate and ECS.

Build the images:

`$ docker-compose -f /path_to_dir/docker-compose.yml build`

Once the images is built, run the container:

`$ docker-compose -f /path_to_dir/docker-compose.yml up -d`

Build images an run the container in one step:

`$ docker-compose -f /path_to_dir/docker-compose.yml up -d --build`

For the production images and spin up the containers (use different file: docker-compose.prod.yml):

`$ docker-compose -f /path_to_dir/docker-compose.prod.yml up -d --build`

Bring down the development containers (and the associated volumes with the -v flag):

`$ docker-compose -f /path_to_dir/docker-compose.yml down -v`


## Environment values

My system use system environment:

* FLASK_ENV - dev/test/prod default is dev
* DATABASE_URL - database URL, for dev environment the default is sqlite:///


## Conclusion

I enjoy this task, learn new things. I start working on task on Monday. I not very
familiar with crypto currency problematic, but I believe I understood the assignment well.
When I developed on Windows I changed the server name from 0.0.0.0:5001 to
localhost:5001, because Windows :D.


## Author
* **Peter Hyl**