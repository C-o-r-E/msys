

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