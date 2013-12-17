import StringIO
from fabric.api import *
from fabric.colors import green, red
from fabric.contrib.files import upload_template, exists, sed
from bh.user import setup_env_for_user


@task
def redis():
    """ compile and install redis
    """
    setup_env_for_user(env.user)
    version = env.REDIS
    run('mkdir -p {admin_home_dir}/~build'.format(**env))
    with cd(env.build):
        tar_pkg = 'redis-{version}.tar.gz'.format(version=version)
        if not exists('{packages_cache}/{tar_pkg}'.format(tar_pkg=tar_pkg, **env)):
            with cd(env.packages_cache):
                run('wget http://download.redis.io/releases/{tar_pkg}'.format(tar_pkg=tar_pkg))
        run('rm -rf redis-{version}'.format(version=version))
        run('tar -xzf {packages_cache}/{tar_pkg}'.format(tar_pkg=tar_pkg, **env))
        with cd('redis-{version}'.format(version=version)):
            run('make PREFIX={base}'.format(**env))
            run('make PREFIX={base} install'.format(**env))
    # check install
    out = run('which redis-server')
    assert out.startswith('{base}/'.format(**env))


@task
def python():
    """ compile and install python
    """
    setup_env_for_user(env.user)
    version = env.PYTHON.replace('Python-', '')
    run('mkdir -p %(admin_home_dir)s/~build' % env)
    with cd(env.build):
        if not exists('%(packages_cache)s/%(PYTHON)s.tgz' % env):
            with cd(env.packages_cache):
                run('wget http://www.python.org/ftp/python/%(PYTHON)s/Python-%(PYTHON)s.tgz' % env)
        run('tar -xzf %(packages_cache)s/Python-%(PYTHON)s.tgz' % env)
        with cd('Python-%(PYTHON)s' % env):
            run('./configure --prefix=%(base)s --enable-shared --with-threads' % env)
            run('make clean')
            run('make')
            run('make install')

    # check local install
    out = run('python -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())"')
    assert out.startswith("%(base)s/" % env), 'Error: `%s` ' % out

    # checl ssl support
    out = run('python -c "import socket;print socket.ssl"')
    assert out.startswith("<function ssl at "), out

    run('wget http://python-distribute.org/distribute_setup.py')
    run('python distribute_setup.py')
    run('easy_install -U pip')
    run('pip install ipython')


@task
def apache():
    """ compile and install apache
    """
    setup_env_for_user(env.user)

    run('mkdir -p %(admin_home_dir)s/~build' % env)
    run('mkdir -p %(admin_home_dir)s/etc/httpd/conf.d' % env)
    with cd(env.build):
        run('tar -xzf %(packages_cache)s/%(APACHE)s.tar.gz' % env)
        with cd(env.APACHE):
            run('./configure '\
                ' --prefix=%(base)s'\
                ' --exec_prefix=%(base)s'\
                ' --bindir=%(base)s/bin'\
                ' --sbindir=%(base)s/bin'\
                ' --libexecdir=%(base)s/lib/apache'\
                ' --mandir=%(base)s/man'\
                ' --sysconfdir=%(base)s/etc/httpd/conf'\
                ' --datadir=%(base)s/var/www'\
                ' --includedir=%(base)s/lib/include/apache'\
                ' --localstatedir=%(base)s/var/run'\
                ' --enable-rewrite'\
                #                ' --enable-rewrite=shared'\
                #                ' --enable-mods-shared=most'\
                ' --with-included-apr'\
                ' --enable-ssl'
            % env)
            run('make clean')
            run('make')
            run('make install')


@task
def sqlite():
    setup_env_for_user(env.user)
    run('mkdir -p %(admin_home_dir)s/~build' % env)
    with cd(env.build):
        run('tar -xzf %(packages_cache)s/%(SQLITE)s.tar.gz' % env)
        with cd(env.SQLITE):
            run('./configure '\
                ' --prefix=%(base)s'\
                ' --exec_prefix=%(base)s'\
                ' --bindir=%(base)s/bin'\
                ' --sbindir=%(base)s/bin' % env )
            run('make')
            run('make install')
            run('sqlite3 -version')

#            run("cp uwsgi %(base)s/bin/uwsgi" % env)

@task
def uwsgi():
    """ compile and install uwsgi
    """
    setup_env_for_user(env.user)
    if not exists('%(packages_cache)s/uwsgi-%(UWSGI)s.tar.gz' % env):
        with cd(env.packages_cache):
            run('wget http://projects.unbit.it/downloads/uwsgi-%(UWSGI)s.tar.gz' % env)

    run('mkdir -p %(admin_home_dir)s/~build' % env)
    with cd(env.build):
        run('tar -xzf %(packages_cache)s/uwsgi-%(UWSGI)s.tar.gz' % env)
        with cd('uwsgi-%(UWSGI)s' % env):
            run('python uwsgiconfig.py --build' % env)
            run("cp uwsgi %(base)s/bin/uwsgi" % env)


@task
def modwsgi():
    """ compile and install modwsgi
    """
    setup_env_for_user(env.user)
    run('mkdir -p %(admin_home_dir)s/~build' % env)
    with cd(env.build):
        run('tar xvfz %(packages_cache)s/%(MOD_WSGI)s.tar.gz' % env)
        with cd(env.MOD_WSGI):
            run('./configure --with-apxs=%(base)s/bin/apxs --with-python=%(base)s/bin/python' % env)
            run('make clean')
            run('make')
            run('make install')


@task
def sqlplus():
    setup_env_for_user(env.user)
    tar = env.deps['sqlplus']
    run('rm -fr ~/~build/sqlplus')
    run('mkdir -p ~/~build/sqlplus')
    with settings(tar=tar):
        put('%(tarballs)s/%(tar)s' % env, '~/~build/sqlplus/')
    with cd('~/~build/sqlplus'):
        run('ls')
        run('unzip %s' % tar)
        run('cp instantclient_11_2/* ~/oracle/instantclient_11_2/')
        run('mv ~/oracle/instantclient_11_2/sqlplus ~/bin/sqlplus')
    run('sqlplus  -V') # simple check


#@task
#def oracle():
#    """ compile and install oracle drivers
#    """
#    setup_env_for_user(env.user)
#    run('mkdir -p %(admin_home_dir)s/~build' % env)
#    #put('%(tarball_dir)s/instantclient-*' % env, env.packages_cache)
#    with cd(env.base):
#        run('rm -fr oracle*')
#        run('mkdir -p oracle')
#        with settings(finder="find %(packages_cache)s -regextype posix-extended -type f -regex '%(packages_cache)s/instantclient-(sdk|basic-linux|sqlplus).*%(ORACLE)s.*'" % env):
#            with cd('oracle'):
#                arch = run('uname -i')
#                if arch == 'x86_64':
#                    run('%(finder)s -exec unzip "{}" \;' % env)
#                elif arch == 'i386':
#                    raise Exception('Not supported')
#
#                env.oracle_home = run('find $PWD -type d -iname "instant*"' % env)
#
#    sed("~/.bash_profile", "export LD_LIBRARY_PATH=.*", "export LD_LIBRARY_PATH=$SITE_ENV/lib:%(oracle_home)s:" % env)
#    sed("~/bin/activate", "export ORACLE_HOME=.*", "export ORACLE_HOME=%(oracle_home)s:" % env)
#
#    run('pip install -I cx_Oracle')
#    run('mkdir -p ~/logs/oracle')
#    run('ln -s ~/logs/oracle %(oracle_home)s/log' % env)
#    # test
#    out = run('python -c "import cx_Oracle;print(222)"')
#    assert out.startswith("222")

@task
def oracle():
    """ compile and install oracle drivers
    """
    setup_env_for_user(env.user)
    run('mkdir -p %(admin_home_dir)s/~build' % env)
    with cd(env.base):
        run('rm -fr oracle*')
        run('mkdir -p oracle')
        with cd('oracle'):
            arch = run('uname -i')
            if arch == 'x86_64':
                run('find %(packages_cache)s -name "instantclient*86-64*" -exec unzip "{}" \;' % env)
            elif arch == 'i386':
                run('find %(packages_cache)s -name "instantclient*" -name "*86-64*" -exec unzip "{}" \;' % env)
            with cd('instantclient_*'):
                run('ln -sf libclntsh.so.11.1 libclntsh.so')

    env.oracle_home = run('find $PWD -type d -iname "instant*"' % env)
    sed("~/.bash_profile", "export LD_LIBRARY_PATH=.*", "export LD_LIBRARY_PATH=$SITE_ENV/lib:%(oracle_home)s:" % env)
    sed("~/bin/activate", "export ORACLE_HOME=.*", "export ORACLE_HOME=%(oracle_home)s:" % env)


    assert exists('%(oracle_home)s/libclntsh.so' % env)
    run('pip install cx_Oracle')
    run('mkdir -p ~/logs/oracle')
    run('ln -s ~/logs/oracle %(base)s/oracle/instantclient_11_2/log' % env)
    # test
    out = run('python -c "import cx_Oracle;print(222)"')
    assert out.startswith("222")


@task
def nginx(version=None):
    """ compile and install nginx
    """
    if version:
        env.NGINX = version
    setup_env_for_user()
    with cd(env.build):
        with cd(env.packages_cache):
            if not exists('%(packages_cache)s/nginx-%(NGINX)s.tar.gz' % env):
                run('wget http://nginx.org/download/nginx-%(NGINX)s.tar.gz' % env)

            if not exists('%(packages_cache)s/pcre-%(PCRE)s.tar.gz' % env):
                run('wget ftp://ftp.csx.cam.ac.uk/pub/software/programming/pcre/pcre-%(PCRE)s.tar.gz' % env)

            if not exists('%(packages_cache)s/uwsgi-%(UWSGI)s.tar.gz' % env):
                run('wget http://projects.unbit.it/downloads/uwsgi-%(UWSGI)s.tar.gz' % env)

        run("tar -xzf %(packages_cache)s/nginx-%(NGINX)s.tar.gz" % env)
        run("tar -xzf %(packages_cache)s/pcre-%(PCRE)s.tar.gz" % env)
        run("tar -xzf %(packages_cache)s/uwsgi-%(UWSGI)s.tar.gz" % env)

        with cd('nginx-%(NGINX)s' % env):
            run("./configure --prefix=%(base)s" \
                " --sbin-path=%(base)s/bin" \
                " --pid-path=%(base)s/run/nginx.pid" \
                " --lock-path=%(base)s/run/nginx.lck" \
                " --user=nginx" \
                " --group=%(group)s" \
                " --with-debug " \
                    #                " --with-google_perftools_module"\
                " --with-select_module" \
                " --with-http_ssl_module" \
                " --with-http_gzip_static_module" \
                " --with-http_stub_status_module" \
                " --with-http_realip_module" \
                " --with-http_ssl_module" \
                " --with-http_sub_module" \
                " --with-http_addition_module" \
                " --with-http_flv_module" \
                " --with-http_addition_module" \
                " --with-file-aio" \
                " --with-sha1-asm" \
                " --http-proxy-temp-path=%(base)s/tmp/proxy/" \
                " --http-client-body-temp-path=%(base)s/tmp/client/" \
                " --http-fastcgi-temp-path=%(base)s/tmp/fcgi/" \
                " --http-uwsgi-temp-path=%(base)s/tmp/uwsgi/" \
                " --http-scgi-temp-path=%(base)s/tmp/scgi/" \
                " --http-log-path=%(base)s/logs/nginx/access.log" \
                " --error-log-path=%(base)s/logs/nginx/error.log" \
                " --with-pcre=../pcre-%(PCRE)s" % env
            )
            run("make")
            run("make install")


@task
def check():
    """ check installation of the servers/appliance
    """
    setup_env_for_user()

    def _test(cmd, where):
        print 'Checking `%s`..' % cmd,
        with settings(warn_only=True):
            out = run(cmd)
            if out.startswith(where):
                print green('Ok')
            else:
                print red("FAIL!!"), out

    puts('Checking installation...')

    with hide('everything'):
        _test('which httpd', '%(base)s/bin/httpd' % env)
        _test('which nginx', '%(base)s/bin/nginx' % env)
        _test('which uwsgi', '%(base)s/bin/uwsgi' % env)
        _test('which python', '%(base)s/bin/python' % env)
        _test('which pip', '%(base)s/bin/pip' % env)

        _test('python -V', 'Python 2.7.2')
        _test('python -c "import cx_Oracle;print(\'cx_Oracle imported\')"', 'cx_Oracle imported')
        _test('python -c "import socket;print socket.ssl"', '<function ssl at')

        print 'Checking $PATH..',
        out = run('echo $PATH')
        assert out.startswith("%(base)s/bin:%(base)s/apache/bin" % env), out
        print green('Ok (%s)' % out)


@task
def copy_cmds():
    """ initalize remote admin home directory
    """
    upload_template("tpls/sbin/all_env_command.sh", "%(PREFIX)s/sbin" % env, env, use_jinja=True)
    run('chmod +x %(PREFIX)s/sbin/*.sh' % env)

@task
def postgresql():
    setup_env_for_user(env.user)
    with cd(env.build):
        run('wget http://ftp.postgresql.org/pub/source/v%(POSTGRES)s/postgresql-%(POSTGRES)s.tar.bz2' % env)
        run('tar -xf postgresql-%(POSTGRES)s.tar.bz2' % env)

        with cd('postgresql-%(POSTGRES)s' % env):
            run('./configure --prefix=%(base)s' % env)
            run('make')
            run('make install')
        run('rm -fr postgresql-%(POSTGRES)s' % env)



def mysql():
    with cd(env.packages_cache):
        if not exists('%(packages_cache)s/mysql-%(MYSQL)s.tar.gz' % env):
                run('wget http://nginx.org/download/mysql-%(MYSQL)s.tar.gz' % env)

    with cd('~/mysql-%(MYSQL)s' % env):
        opts = " ".join([" -DWITH_ARCHIVE_STORAGE_ENGINE=1",
                         " -DWITH_FEDERATED_STORAGE_ENGINE=1",
                         " -DWITH_BLACKHOLE_STORAGE_ENGINE=1",
                         " -DMYSQL_DATADIR={0}/data/",
                         " -DCMAKE_INSTALL_PREFIX={0}/server",
                         #" -DCURSES_LIBRARY=/opt/ncurses/lib/libncurses.a ",
                         #" -DCURSES_INCLUDE_PATH=/opt/ncurses/include/",
                         #" -DHAVE_LIBAIO_H=/opt/libaio/include/ ",
                         " -DINSTALL_LAYOUT=STANDALONE ",
                         " -DENABLED_PROFILING=ON ",
                         " -DMYSQL_MAINTAINER_MODE=OFF",
                         " -DWITH_DEBUG=OFF ",
                         " -DDEFAULT_CHARSET=utf8",
                         " -DENABLED_LOCAL_INFILE=TRUE",
                         " -DWITH_ZLIB=bundled"]).format('~')

        run('cmake %s' % opts)
        run('./configure --with-charset=utf8 --with-collation=utf8_unicode_ci ')
        run('make ')
        run('make mysqlclient libmysql')
        run('make install')
        run('mkdir -p ~/log')
        put(StringIO.StringIO(MYSQL_CONFIG), "~/server/my.cnf")
        run('scripts/mysql_install_db --user=mysql --explicit_defaults_for_timestamp')
        run('./server/bin/mysql  -e "GRANT ALL PRIVILEGES ON *.* TO \'root\'@\'%\' IDENTIFIED BY \'123\' WITH GRANT OPTION;"')
        run('./server/bin/mysql  -e "GRANT ALL PRIVILEGES ON *.* TO \'root\'@\'localhost\' WITH GRANT OPTION;"')

MYSQL_CONFIG = r"""
[mysqld]
datadir={home}/server/data
port=3306
log-error = {home}/log/mysqld.error.log
#character-set-server=utf8
#collation-server=utf8_unicode_ci
#server-id=1382004430

[mysql.server]
user=mysql
basedir={home}/server

""".format(home='/opt/host_services/mysql', host='*', )

MYSQL_START="~/server/bin/mysqld_safe --defaults-file=~/server/my.cnf &"
MYSQL_STOP="~/server/bin/mysqladmin -u root -p shutdown"

@task
@hosts('mysql@pydev.wfp.org')
def config_mysql():
    run('mkdir -p ~/log')

    put(StringIO.StringIO(MYSQL_CONFIG), "~/server/my.cnf")
    put(StringIO.StringIO(MYSQL_START), "~/start.sh")
    put(StringIO.StringIO(MYSQL_STOP), "~/stop.sh")

    run("chmod +x ~/start.sh ~/stop.sh")

@task
def install():
    """ install all required servers/appliance

    this command
    """
    setup_env_for_user(env.user)
    execute(python)
#    execute(apache)
#    execute(modwsgi)

#    execute(oracle)
#    execute(uwsgi)
#    execute(ngnix)
