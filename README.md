
Running Tests
-------------

You need nose and nose-gae:

    sudo easy_install nose
    sudo easy_install nosegae
    sudo easy_install webtest
    sudo easy_install BeautifulSoup
    sudo easy_install gaetestbed
    sudo easy_install 'fixture[decorators]'

To run tests continuously during development, download nosyd.

Download Growl SDK from http://growl.info/downloads_developers.php; click the file to mount it. Then:

    $ cp -r '/Volumes/Growl 1.2 SDK/Bindings/python/' /tmp/py-Growl
    $ cd /tmp/py-Growl/
    $ sudo python setup.py install

