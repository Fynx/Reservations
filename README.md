Reservations
============

Django application for rooms reservation.

### Requirements

* Django 1.6.2
* Python 3.3.3 (temporarily)
* South 0.8.4

### Installation

* Initialise database
_python manage.py syncdb --migrate_

* Migrate data
_python manage.py migrate_

* In order to remigrate data for room attributes
_python manage.py migrate res 0001 --fake_
_python manage.py migrate_
