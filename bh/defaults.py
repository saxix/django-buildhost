import os
from fabric.api import *


env.NGINX = '1.4.1'
env.UWSGI = '1.9.18.2'
env.PCRE = "8.21"
env.MYSQL = "5.6.14"
#env.VIRTUALENV = "virtualenv-1.7"
env.REDMINE = "redmine-1.3.0"
env.PYTHON = "2.7.5"
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
env.ORACLE='12.1.0.1.0'
env_ORACLE_BASE='12_1'

env.tarball_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'tarballs'))
