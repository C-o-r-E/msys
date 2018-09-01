

## Client Installation

The following was tested on a RaspberryPi 2 running a fresh raspian image

### Updates

```
sudo apt-get update

sudo apt-get upgrade
```

### System Dependencies

```
sudo apt-get install git python3 python3-pip
```

### Python Dependencies

```
mkdir git

cd git

git clone https://github.com/C-o-r-E/SPI-Py.git

sudo pip3 install SPI-Py/

sudo pip3 install RPi.GPIO

```

### Get Client

```
git clone https://github.com/C-o-r-E/msys.git
```

### Run Client

```
cd msys/client/
chmod 755 client.py
./client.py
```

## Kiosk Installation

After installing the client, there are some additional dependencies for the Kiosk

### System Dependencies

```
sudo apt-get install qt5-default pyqt5-dev pyqt5-dev-tools python3-pyqt5.qtwebkit
```

### Python Dependencies

None at the moment