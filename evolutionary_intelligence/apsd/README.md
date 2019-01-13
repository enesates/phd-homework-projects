# Area Priority Sensor Deployment

Development of Techniques for Area Priority Estimation on Satellite Images and Sensor Deployment Optimization

## Coordinates
1. Izmir Gulf:  (38.418897, 27.128677)
2. Istanbul Straight: (41.005294, 28.977127)
3. Kumamoto: (32.835318, 130.683403)
4. Karabuk: (41.211722,32.602959)

## Installation steps
### For DEB based systems
* `sudo apt-get install python-numpy`
* `sudo apt-get install python-scipy`
* `sudo apt-get install python-matplotlib`
* `sudo pip install pycluster` (in pycluster directory: `python setup.py install`)
* `sudo pip install pybrain`
* optional steps:
    * `sudo apt-get install python-pip`
    * `sudo pip install bitarray`
    * `sudo apt-get install python-tk`
    * `sudo pip install neurolab`
    * for include <time.h> error: `sudo apt-get install python2.7-dev`
### For RPM based systems
* `sudo yum install numpy`
* `sudo yum install scipy`
* `sudo yum install python-matplotlib`
* `sudo yum install python-pip`
* `sudo python-pip install pycluster` (in pycluster directory: `python setup.py install`)
  * if it fails (Python.h) install `python-devel` maybe it comes with `scipy`
### For Mac OS X
* `sudo port -v install py27-pygtk`
* `sudo ln -sf /opt/local/bin/python2.7 /usr/bin/python`
* `sudo easy_install pip`
* `sudo pip install virtualenvwrapper`
* `brew install cairo`
* `sudo pip install cairocffi` (pycairo replace)
* `brew install pygtk
* `python setup.py install` (in pycluster directory)