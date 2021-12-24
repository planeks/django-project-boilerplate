# Django Project Boilerplate

This repository is a boilerplate Django project for quickly getting started.

## Getting started

Steps:

1. Clone/pull/download this repository
2. Create a virtualenv with `python3 -m venv env_py37` and install dependencies with `pip install -r requirements.txt`
3. Create directories `email`, `media`, `staticfiles`
4. Configure your `.env` variables

This project includes:

1. Settings modules
2. Django commands for renaming your project and creating a superuser
3. Basic templates with Bootstrap4 support
4. A rich set of useful template tags

## How to rename project

1. Rename `demo` directory which contains `wsgi.py` file
2. Add proper line to your `.env` file, like `PROJECT_NAME=<project_name>`


## Basics

Before working with a project add a new line to your `/etc/hosts` 
(replace `demo` with your real project name):

    127.0.0.1    demo.local


### How to run local development server

    DJANGO_SETTINGS_MODULE=demo.settings.development ./manage.py runserver

If you need to load some alternate configuration you can use the next command:

```bash
$ sh -ac ". <name_of_dotenv_file>; python manage.py runserver"
```

Alternatively, if you are working with same configuration you can add the next line
to your `env_py37/bin/activate`:

```bash
export $(.env | xargs)
```

### How to create new superuser

    DJANGO_SETTINGS_MODULE=demo.settings.development ./manage.py createsuperuser

### How to run Celery worker

    DJANGO_SETTINGS_MODULE=demo.settings.development celery -A demo worker -B --loglevel=info

### How to run unit tests

    DJANGO_SETTINGS_MODULE=demo.settings.testing ./manage.py test

### How to create the new app

    mkdir djapps/newapp
    DJANGO_SETTINGS_MODULE=demo.settings.development ./manage.py startapp newapp djapps/newapp
