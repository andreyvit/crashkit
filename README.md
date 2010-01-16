CrashKit
========

Running Tests
-------------

You need pexpect (http://www.noah.org/wiki/Pexpect, http://pexpect.sourceforge.net/pexpect.html):

    wget http://pexpect.sourceforge.net/pexpect-2.3.tar.gz
    tar xzf pexpect-2.3.tar.gz
    cd pexpect-2.3
    sudo python ./setup.py install

Run CrashKit development server on port 5005:

    dev_appserver.py -p 5005 crashkit/server
    
Create a “test” account and add the following products if they don't already exists:
* py
* django
* php
* java
* js

Run the tests:

    cd crashkit/tests
    ./runtests.py
