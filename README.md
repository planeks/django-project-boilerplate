# Django Project Boilerplate

This repository is a boilerplate Django project for quickly getting started.

## Getting started

Steps:

1. Clone/pull/download this repository
2. Create a virtualenv with `virtualenv env` and install dependencies with `pip install -r requirements.txt`
3. Configure your .env variables
4. Rename your project with `python manage.py rename <yourprojectname> <newprojectname>`

This project includes:

1. Settings modules
2. Django commands for renaming your project and creating a superuser
3. A cli tool for setting environment variables for deployment

## Basics

Before working with a project add a new line to your `/etc/hosts` 
(replace `demo` with your real project name):

    127.0.0.1    demo.local
