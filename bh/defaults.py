import os
from fabric.api import *


env.NGINX = 'nginx-1.3.8'
env.UWSGI = 'uwsgi-1.3'
env.PCRE = "8.20"
env.VIRTUALENV = "virtualenv-1.7"
env.REDMINE = "redmine-1.3.0"
env.PYTHON = "2.7.3"
env.APACHE = "httpd-2.2.24"
env.MOD_WSGI = 'mod_wsgi-3.3'
env.SQLITE = 'sqlite-autoconf-3071602'
env.APR = "apr-1.4.6"
env.DISTRIBUTE = "distribute-0.6.24"
env.PIP = "pip-1.0.2"
env.POSTGRES = "9.1.5"
env.OPENLDAP = "2.4.33"
env.PYTHONLDAP = "2.4.10"
env.BERKELEY = "5.3.21"
env.SASL = "2.1.25"
env.LIBTOOL = "2.4.2"
env.unixODBC="2.3.1"
env.PSQLODBC="09.01.0200"

env.tarball_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'tarballs'))
