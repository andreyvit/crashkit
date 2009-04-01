SET	app_name	crashkit

REPOS	crashkit	-	YourSway CrashKit
	GIT	andreyvit	-	git@github.com:andreyvit/yoursway-feedback.git
	GIT	fourdman	-	git@github.com:fourdman/yoursway-feedback.git

VERSION	crashkit.cur	crashkit	heads/master

NEWDIR	java.dir	temp	%-java	-
NEWDIR	python.dir	temp	%-python	-
NEWDIR	php.dir	temp	%-php	-

NEWFILE	crashkit-java.zip	featured	crashkit-java-[ver].zip	CrashKit Java [ver]
NEWFILE	crashkit-python.zip	featured	crashkit-python-[ver].zip	CrashKit Python [ver]
NEWFILE	crashkit-js.zip	featured	crashkit-javascript-[ver].zip	CrashKit JavaScript [ver]
NEWFILE	crashkit-php.zip	featured	crashkit-php-[ver].zip	CrashKit PHP [ver]


COPYTO	[java.dir]
	INTO	/	[crashkit.cur]/java-client
	
SUBSTVARS	[java.dir<alter>]/com.yoursway.crashkit/src/com/yoursway/crashkit/internal/Constants.java	{{}}

ZIP	[crashkit-java.zip]
	INTO	crashkit-java-[ver]	[java.dir]


COPYTO	[python.dir]
	INTO	/	[crashkit.cur]/python-client
	
SUBSTVARS	[python.dir<alter>]/crashkit.py	{{}}

ZIP	[crashkit-python.zip]
	INTO	crashkit-python-[ver]	[python.dir]


COPYTO	[php.dir]
	INTO	/	[crashkit.cur]/php-client
	
SUBSTVARS	[php.dir<alter>]/crashkit.inc.php	{{}}

ZIP	[crashkit-php.zip]
	INTO	crashkit-php-[ver]	[php.dir]


ZIP	[crashkit-js.zip]
	INTO	crashkit-javascript-[ver]	[crashkit.cur]/javascript-client


PUT	s3-builds	crashkit-java.zip
PUT	s3-builds	crashkit-python.zip
PUT	s3-builds	crashkit-js.zip
PUT	s3-builds	crashkit-php.zip
PUT	s3-builds	build.log

