# MSYS

<a class="mk-toclify" id="table-of-contents"></a>

# Table of Contents

- [About](#about)
- [Server Installation](#server-installation)
    - [Environment](#environment)
    - [Get Django](#get-django)
    - [Using PIP](#using-pip)
    - [Get PIP](#get-pip)
    - [Clone the repo](#clone-the-repo)
    - [Run the server in devel mode](#run-the-server-in-devel-mode)
    - [Set up the database](#set-up-the-database)
    - [Import data](#import-data)
- [Client Installation](#client-installation)
    - [Updates](#updates)
    - [System deps](#system-deps)
    - [Python deps](#python-deps)
    - [Get client](#get-client)
    - [Run Client](#run-client)
- [TODO docs](#todo-docs)
- [Roadmap dev](#roadmap-dev)


## About

Msys is a member management and access control system.

## Server Installation

### Environment

Msys is developed on Linux but it could probably run on a number of other systems. Certain packages are required in any case:

	 * Python 3.x
 	 * Django 1.9

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

### Import data

This section is for importing the memberlist used by Helios (google sheet). It expects the sheet with member information to be exported to a CSV file. The script will attempt to open the file "members.csv" and populate the database with both member and membership information.

```
python add_all_members.py
```

## Client Installation

The following was tested on a RaspberryPi 2 running a fresh raspian image

### Updates

```
sudo apt-get update

sudo apt-get upgrade
```

### System deps

```
sudo apt-get install git python3 python3-pip
```

### Python deps

```
mkdir git

cd git

git clone https://github.com/C-o-r-E/SPI-Py.git

sudo pip3 install SPI-Py/

sudo pip3 install RPi.GPIO

```

### Get client

```
git clone https://github.com/C-o-r-E/msys.git
```

### Run Client

```
cd msys/client/
sudo python3 client.py
```

###


# TODO docs

* Set up the webserver
* Set up wsgi



# Roadmap dev

### Server
* Stripe API integration
* Square integration?
* manage rentals (shelves, spaces)
* track training records (or member activities)
* Https

### Client (gatekeeper)
* Test cases
* Red LED for access denied
* investigate new revision of board   

### Client (Desktop)
* Test with 5v FTDI
* Polish the application
