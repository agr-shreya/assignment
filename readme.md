## Packages to install
1. Packages related to linting
   > flake8==5.0.4
   > pyflakes==2.5.0
   > autopep8==1.7.0 

2. Package for enums
    > django-enum-choices==2.1.4

3. Celery
   > celery==5.2.7
   > django-celery-beat==2.3.0
   > python-crontab==2.6.0

4. Django
   > Django==4.0.7

5. Postgres
   > psycopg2-binary==2.9.3

6. Mailjet
   > mailjet-rest==1.3.4

7. Extract vars from .env
   > python-dotenv==0.21.0

8. Date time util for scheduling services (acc. to limit & frequency)
   > python-dateutil==2.8.2


## Setting up database
### Prerequisites
1. Database: Postgres
2. db-name: ob__mailing_system
3. RabbitMQ & celery installed


### Steps:
1. Create a db ob__mailing_system
2. To start the django server

Run in main dir
```
> python3 manage.py makemigrations
> python3 manage.py migrate
> python3 manage.py runserver
```

* I believe makemigration won't be required since all the migrations are already stored in the codebase itself

3. To start the message broker service (rabbitMQ)
```
> rabbitmq-server
```

This, will start running the rabbitMQ server locally. Since, I am using my local server, I have used the following to connect to my celery server.

```py
CELERY_BROKER_URL = 'amqp://localhost'
```

4. To schedule my tasks on celery on a regular interval (run at every 2 min, expires in 1 min), I have used celery-beat

```
> celery -A mailing_system.celery beat
```

5. Run the celery server to view logs of the scheduled tasks

```
> python3 -m celery -A mailing_system worker
```