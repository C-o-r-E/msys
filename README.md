# MSYS

## About

Msys is a member management and access control system.

## Installation (Server)

### Environment

Msys is developed on Linux but it could probably run on a number of other systems. Certain packages are required in any case:

	 * Python 2.x
 	 * Django 1.7

A webserver and database will also be required. In this guide we will focus on the following ones:

     * Nginx
 	 * Sqlite


### Using PIP

You can install the dependancies using whatever method (virtualenv, package manager) but we will use pip for the sake of being universal

### get pip

> $ wget https://bootstrap.pypa.io/get-pip.py

> $ python get-pip.py --user

### get django

> $ pip install django --user


### clone the repo

> $ git clone https://github.com/C-o-r-E/msys.git

> $ cd msys/msys

> $ echo "somerandomdata" > key.txt

You should replace that string with real random data... (read the Django docs for more info)

### Run the server in devel mode

> $ python manage.py runserver


### TODO

* Set up the database
* Set up the webserver
* Set up wsgi
* import members data
* client docs