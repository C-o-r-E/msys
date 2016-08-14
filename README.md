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

```
wget https://bootstrap.pypa.io/get-pip.py
```

```
python get-pip.py --user
```

### get django

```
pip install django --user
```

### clone the repo

```
git clone https://github.com/C-o-r-E/msys.git
```

```
cd msys/msys
```

```
echo "somerandomdata" > key.txt
```

You should replace that string with real random data... (read the Django docs for more info)

### Run the server in devel mode

```
python manage.py runserver
```

At this point the server should start. It might complain about unapplied migrations which we will resolve later.

Now open a browser and navigate to http://127.0.0.1:8000/members (the server should indicate the listening address in the terminal where it was started). If all went well you should see a prompt to log in to the member system.

### Set up the database

Use Ctrl-C in the terminal to halt the devel server. We now need to create a super user.

```
python manage.py createsuperuser
```

Once the superuser is created, we need to create the database tables required for msys to function correctly. To create the proper structure do the following:

```
python manage.py makemigrations members
```




### TODO - Docs

* Set up the database
* Set up the webserver
* Set up wsgi
* import members data
* client docs


### TODO - Dev

* jquery datepicker for certain forms
* Client
    * Test cases for latency
    * Design access cache
    * Protocol for transmitting access info
* Get import script to populate stripe data
* Update instance on Morgianna
* Stripe API integration
    
