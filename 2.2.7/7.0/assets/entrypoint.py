import click
import subprocess
import shlex
import time
import pathlib
import re
import os

@click.group()
@click.pass_context
def cli(ctx):
    ctx.obj = {
        'MAGENTO_ROOT': '/var/www/html',
        'WWW_USER': 'root'
    }
    subprocess.check_call("sh /update-host-machine.sh", shell=True)
    pass

def install_modules():
    os.chdir('/var/www/html')
    modules = os.environ.get('MODULE_LIST')
    print(modules)
    if not modules == '':
        secret_key = "LS0tLS1CRUdJTiBPUEVOU1NIIFBSSVZBVEUgS0VZLS0tLS0KYjNCbGJuTnphQzFyWlhrdGRqRUFBQUFBQkc1dmJtVUFBQUFFYm05dVpRQUFBQUFBQUFBQkFBQUJsd0FBQUFkemMyZ3RjbgpOaEFBQUFBd0VBQVFBQUFZRUFwdnZOYVUyVzdSZUlQSHI5WVFGYjdLTDNxdXYzdzU5ZzI0Q3RXWkNicDFGQzhwWGJqVUkwCnR5VkhYbjBVbkZoSTlCUnVsbzdRMkF5WE9kdHBsNW0xMEV6MXJsaW9DZlZSMllvbXZueVhDNUdEc1U2R2dRVlpDaVNFWW0KR25vcWhZMXB6eEY4WlRUbCtqYmo2a3dibFhqSDRxZlBMc3pGWlF5MEV4WmNPT0YwcHRGTXAvNGdTUmlJTzlLcGI4WFM3agpvRE8zNDFhZ2VHYk1qUC9BUXBLMEptdm1nOEtkWGMyMzVmTTJITVN5REJtT2ZvUkZCWE9IWktSTlRZV0pSRHFFZzlYUDMxCnhSN1RiZGowWkVjMjBzS3ZRVkJLZDV5TEFMZVRtNzVZWE1CN1JCK1lxSks5L2tYdFUrOXFyV2x6UnEvUFlkTUhpbWxsdDQKUDdabk9Bd2hwWHphenE2SUdTMis5dlJFU2ZLWlgxUllnTGdXZElCWlJabHFsZlhhKzBZNDBuOUFzamFaK2gzUDRWdVhWNApsR0dJaDVwYWdoNnR2aFZjQjFLVVZDdjU2RmhocHdLaWhmTC90Wm5uVysxUzF3Y2VUNG96ems3K1Y1YjJrTkpib2ZESUtSCjhwekVIU200bW9FZ0QrT2F2L2kveitYQU8rL0xCTU84c1lYR1BtdTdBQUFGaUE5OXp6OFBmYzgvQUFBQUIzTnphQzF5YzIKRUFBQUdCQUtiN3pXbE5sdTBYaUR4Ni9XRUJXK3lpOTZycjk4T2ZZTnVBclZtUW02ZFJRdktWMjQxQ05MY2xSMTU5Rkp4WQpTUFFVYnBhTzBOZ01sem5iYVplWnRkQk05YTVZcUFuMVVkbUtKcjU4bHd1Umc3Rk9ob0VGV1Fva2hHSmhwNktvV05hYzhSCmZHVTA1Zm8yNCtwTUc1VjR4K0tuenk3TXhXVU10Qk1XWERqaGRLYlJUS2YrSUVrWWlEdlNxVy9GMHU0NkF6dCtOV29IaG0Kekl6L3dFS1N0Q1pyNW9QQ25WM050K1h6Tmh6RXNnd1pqbjZFUlFWemgyU2tUVTJGaVVRNmhJUFZ6OTljVWUwMjNZOUdSSApOdExDcjBGUVNuZWNpd0MzazV1K1dGekFlMFFmbUtpU3ZmNUY3VlB2YXExcGMwYXZ6MkhUQjRwcFpiZUQrMlp6Z01JYVY4CjJzNnVpQmt0dnZiMFJFbnltVjlVV0lDNEZuU0FXVVdaYXBYMTJ2dEdPTkovUUxJMm1mb2R6K0ZibDFlSlJoaUllYVdvSWUKcmI0VlhBZFNsRlFyK2VoWVlhY0Nvb1h5LzdXWjUxdnRVdGNISGsrS004NU8vbGVXOXBEU1c2SHd5Q2tmS2N4QjBwdUpxQgpJQS9qbXIvNHY4L2x3RHZ2eXdURHZMR0Z4ajVydXdBQUFBTUJBQUVBQUFHQVV1dDNkWE15SDBvd1BOaFdPbldTVUZBYzdLCk9BeFlPL2RVRFExRWtiQWxzNEEzNm5KOTVZanhuVDl2Zmw1RDF5L01Hb3FOc0Nta2FtVWZUQzJxVlp3N1p6eWIvOHNmVkEKVCtacWx1MEhsSmNON2w0d0xLR2JOWTRzcnk0UE1KYW9odW9vVHNZTldEM2x5amtSVjZIUjk5SXZCeDBhdWQyakFVdStXKwpwZ0JQRFFlaUtVbm9mbVBRUXVTNWZ1ZWRkdThYNjlNZ2N5YUplanUrREVlRXFoYXZMcDVVUWZJUldtM0dtSjFYOVhhdXJGCjk4MTIrTjRGdmRSWkRzWGhCQ0NLSUJYYm1LbjVyWjJUcDVZV0xya3RVOXh4SlVRNDdCWVpkS3l6SFZvTHBqVmVIRlJZenEKeWNpTTZ6eCtwZGc4MFNGTFd5Z3VmVWplS2lDdEExTExUeXVxb2VYODBBdlhBcDZrV1pJSlJ5TlNBeDRJclF1Z0xSVVNQbApFZndiendCekR0dnVsd3RJOC90TlJOcm1USXVsaURRSUNrdEVjMU1XUXJUUlErOTVsK2FuVXJEL1lnS2R2NzNIQUZ0NU5pClp5VHE5dlR4RWc3VlZjN0hVMDlVNStrV3JLTDRSalFyM3pXMTM3S3dGcmJZdGxjMlRERU0zWE5pZS9wd0V0R2lVQkFBQUEKd1FDWU5WYnZlSTNkNHJYZ0MvbmdUQXlCeEhPT1NhNC9uTDJ6VEdsYnpQc0FXM0Ztd284R2l6N1VVSTQ0bHQyenBpVUljdAo0RXhrN0FyWklNYU82ZjMwWnZ2eEFxNkhRUUZTblZNNXVzMkxlTU1TZG1kbVp3RSswQ1JyVHVQN1RjQTRGOGRacnBuQ3BxCmZTb01YUGRZWnpDdG9CNFR2KzBaOUZpS2s5N3VtWWJKVmcrVHl3Z0UyOHlGWE9xUE9yOHA4OUxabnBEVVptZnByTnhuTTYKdS9RTGgzeTd1dGxUMnBvOEpobzBqMnpsVktuUWJMcmdzVzhYT1RWYnBSR0RtcUFNZ0FBQURCQU03UkxLZFpMeENFa0c4Tgpzd09pOWdUV1pXdm9YbWFZdERHTEhhRHF0ZU9WbUE3QzdaRVhNazg4OVVUN1d6Kzd0ZFpXYkpXMW9XNmIydEdwM3M3MG1lClVWZTBIdEFnUllGTm5NWGJiaStua25Dd3psWHYwaGMxOGdpaVVlcVNYUng5Q3ZrYzY3bUdIWkRlRHdnU2p6U2ZCVEQ1elYKN2xBUHg0NHVYbDR2YkUvdHFhTHRMbGhXaVRJT3JmQTZIN1BnVVZrSkJPaDFidlk0NDVCT2pJdVU2czBuNDFVM3FTYnhKTwo1cmt2eG1zbjlZa1VqZkhNZ2xIUlRpZDJJU0dNeFdYUUFBQU1FQXpyR2FpOHFiUURIcDZFTW9ibWtVRUdRZzI0bEF3dUt3CkRYeDI2NlVWb3JveGRKUFd2RGhmRTRpMVFLMXM0ZFdzRXk0YlpHOURxYlNxYWVDN3lTdHJzQkVXZVFoQXhxc1EzQmNDTngKT0FIU2kzYTh0SDZvRkxjRCtQdDlFTGZCK1lhQ1RJNnhTT1QvM0RRazRORDd3YXRmcGlQb21YQzZKOXl3SHltajdqTjAydgo0MzBwZ1VEWXZnWEtKMHFHRWpOaElpaStIL2VxV0dYRmJyR0dEcW8xUVV0Y21VQzF0c2NnOEtybFhBS2xiY0dDM1FpNk1ICk1FZjE1MHhQKzZVZmozQUFBQURXNXVkWE5sY2tCdWJuVnpaWElCQWdNRUJRPT0KLS0tLS1FTkQgT1BFTlNTSCBQUklWQVRFIEtFWS0tLS0tCg=="
        os.environ['SECRET_KEY'] = secret_key
        os.system('umask  077 ; echo ${SECRET_KEY} | base64 -d > ~/.ssh/id_rsa')
        os.system('apk add openssh-client')
        os.system('apk add git')
        os.system('composer config repositories.dev_aheadworks composer https://composer.do.staging-box.net/')
        if ',' in modules:
            modules_list = modules.split(',')
        else:
            modules_list = [modules]
            print(modules_list)
        for m in modules_list:
            if '/' in m:
                m = m.strip()
                print(m)

                p = subprocess.Popen(['composer', 'require', m])
                p.wait()
                os.system('cat composer.json')
            else:
                raise ValueError('incorrect module name')

def execute(path, user, cmd):
    cmd = 'su {user} -c "php {path}/bin/magento %s"' % cmd
    return subprocess.check_output(cmd.format(user=user, path=path), shell=True)


def set_ssh(user):
    os.system('su ' + str(user) + ' -c "sh /inject-ssh-keys.sh"')


def set_password(user, password):
    return subprocess.check_output("echo \"{user}:{password}\" | chpasswd".format(user=user, password=password),
                                   shell=True)


def set_config_values(path, user, mode='config', opts={}):
    params = " ".join(["--{k}={v}".format(k=shlex.quote(k), v=shlex.quote(v)) for k, v in opts.items()])
    cmd = 'setup:{mode}:set -n {params}'.format(user=user, path=path, params=params,
                                                mode=mode)
    return execute(path, user, cmd)


def serve():
    """ Run PHP-fpm, cron, nginx """
    click.echo("Starting crond...")
    subprocess.check_call("crond")
    click.echo("Starting nginx & fpm...")
    # Generate new host keys if they not exist
    if not pathlib.Path('/etc/ssh/ssh_host_rsa_key').exists():
        subprocess.check_call("ssh-keygen -A", shell=True)
    subprocess.check_call("/usr/sbin/sshd -D -e & nginx -g \"daemon off;\" & docker-php-entrypoint php-fpm -R",
                          shell=True)


@cli.command()
@click.pass_context
@click.option('--ssh-password', envvar="SSH_PASSWORD", default='root', required=True)
@click.option('--mysql-host', envvar="MYSQL_HOST", required=True)
@click.option('--mysql-port', envvar="MYSQL_PORT", default=3306, required=True)
@click.option('--mysql-user', envvar="MYSQL_USER", required=True)
@click.option('--mysql-password', envvar="MYSQL_PASSWORD", required=True)
@click.option('--mysql-database', envvar="MYSQL_DATABASE", required=True)
@click.option('--mysql-prefix', envvar="MYSQL_PREFIX", required=True, default="")
@click.option('--magento-url', envvar='MAGENTO_URL')
@click.option('--magento-language', envvar='MAGENTO_LANGUAGE')
@click.option('--magento-default-currency', envvar='MAGENTO_DEFAULT_CURRENCY')
@click.option('--magento-timezone', envvar='MAGENTO_TIMEZONE')
@click.option('--magento-admin-firstname', envvar='MAGENTO_ADMIN_FIRSTNAME')
@click.option('--magento-admin-lastname', envvar='MAGENTO_ADMIN_LASTNAME')
@click.option('--magento-admin-email', envvar='MAGENTO_ADMIN_EMAIL')
@click.option('--magento-admin-username', envvar='MAGENTO_ADMIN_USERNAME')
@click.option('--magento-admin-password', envvar='MAGENTO_ADMIN_PASSWORD')
@click.option('--dump-file', envvar="DUMP_FILE", default='/var/www/dump.sql', required=True)
def update_and_serve(ctx, ssh_password, mysql_host, mysql_port, mysql_user, mysql_password, mysql_database,
                     mysql_prefix, magento_url,
                     magento_language, magento_default_currency, magento_timezone,
                     magento_admin_firstname, magento_admin_lastname, magento_admin_email, magento_admin_username,
                     magento_admin_password,
                     dump_file):
    # Set root & primary user password
    click.echo("Setting passwords for user %s" % ctx.obj['WWW_USER'])
    set_password(ctx.obj['WWW_USER'], ssh_password)
    set_ssh(ctx.obj['WWW_USER'])

    click.echo("Waiting for db at %s:%s" % (mysql_host, mysql_port))

    n = 240
    while True:
        try:
            subprocess.check_call(
                (
                    'mysql '
                    " -u{mysql_user}"
                    " -p{mysql_password}"
                    " -h{mysql_host}"
                    ' -e"quit"'
                ).format(
                    mysql_user=mysql_user,
                    mysql_password=mysql_password,
                    mysql_host=mysql_host,
                    mysql_database=mysql_database
                ), shell=True
            )
            break
        except subprocess.CalledProcessError as e:
            if not n:
                raise
            n -= 1
        time.sleep(1)

    click.echo("Setting DB credentials")
    opts = {
        'db-host': mysql_host,
        'db-name': mysql_database,
        'db-user': mysql_user,
        'db-password': mysql_password
    }
    if mysql_prefix:
        opts['db-prefix'] = mysql_prefix

    set_config_values(ctx.obj['MAGENTO_ROOT'], ctx.obj['WWW_USER'], opts=opts)

    try:
        tables = subprocess.check_output((
            "mysql -B"
            " -u{mysql_user}"
            " -p{mysql_password}"
            " -h{mysql_host}"
            " --disable-column-names"
            " {mysql_database} -e \"show tables\""
        ).format(
            mysql_user=mysql_user,
            mysql_password=mysql_password,
            mysql_host=mysql_host,
            mysql_database=mysql_database
        ), stderr=subprocess.STDOUT, shell=True)
    except subprocess.CalledProcessError as e:
        tables = ''

    if (mysql_prefix + 'admin_user') not in str(tables):
        click.echo("DB is empty(or DB %s doesn't exist). Will import dump" % mysql_database)

        subprocess.check_output(
            "mysql -h{mysql_host} -u{mysql_user} -p{mysql_password} {mysql_database} < {dump_file}".format(
                mysql_user=mysql_user,
                mysql_host=mysql_host,
                mysql_password=mysql_password,
                mysql_database=mysql_database,
                dump_file=dump_file
            ),
            shell=True
        )
        if (mysql_prefix):

            def query(q, fn=subprocess.check_call, pipe=""):
                """
                Perform a query and return result as a string
                :param q:
                :param fn:
                :return str|int:
                """
                params = dict(
                     mysql_user=mysql_user,
                     mysql_host=mysql_host,
                     mysql_password=mysql_password,
                     mysql_database=mysql_database,
                     mysql_prefix=mysql_prefix
                )

                _query = q. format(**params)
                _query = _query.replace("`", "\`")
                _cmd = "mysql -h{mysql_host} -u{mysql_user} -p{mysql_password} -ANrs" \
                                          " -e\"{query}\"".format(query=_query, **params)
                if pipe:
                    _cmd = '%s | %s' % (_cmd, pipe)

                out = fn(_cmd, shell=True)
                if isinstance(out, bytes):
                    return out.decode()
                return out


            # Apply prefix to databases imported from dump
            click.echo("Adding prefix %s to tables" % mysql_prefix)
            q = "select concat('rename table ', db, '.', tb, ' to ', db, '.', prfx, tb, ';')" \
                " from (select table_schema db, table_name tb from information_schema.tables where" \
                " table_schema in ('{mysql_database}') and table_type='BASE TABLE') A, (SELECT '{mysql_prefix}' prfx) B" \
                .format(mysql_database=mysql_database, mysql_prefix=mysql_prefix)

            subprocess.check_output(
                "mysql -h{mysql_host} -u{mysql_user} -p{mysql_password} -AN -e\"{query}\""
                " | mysql -h{mysql_host} -u{mysql_user} -p{mysql_password}".format(
                    mysql_user=mysql_user,
                    mysql_host=mysql_host,
                    mysql_password=mysql_password,
                    mysql_database=mysql_database,
                    query=q
                ),
                shell=True
            )
            click.echo("Patching sales_sequence_meta table to fit DB prefix")
            query("UPDATE `{mysql_database}`.`{mysql_prefix}sales_sequence_meta` SET sequence_table=CONCAT('{mysql_prefix}', sequence_table)")

            click.echo("Patching views to fit DB prefix")
            views = query("SELECT TABLE_NAME FROM INFORMATION_SCHEMA.VIEWS WHERE"
                                          " TABLE_SCHEMA = '{mysql_database}'", fn=subprocess.check_output).split("\n")
            views = list(filter(None, views))

            for v in views:
                crv = query("SHOW CREATE VIEW {mysql_database}.%s" % v, fn=subprocess.check_output, pipe="cut -f2")
                crv = re.sub("`" + mysql_database + "`\.`([^`]+)`", "`" + mysql_database + "`.`" + mysql_prefix + "\\1`", crv)
                click.echo("Re-creating view: %s%s" % (mysql_prefix, v))
                query(crv)
                query("DROP VIEW IF EXISTS {mysql_database}.%s" % v)

    click.echo("Re-creating admin account")
    subprocess.check_output(
        'mysql -h{host} -u{user} -p{password} -e "USE {database}; DELETE FROM {mysql_prefix}admin_user"'.format(
            host=mysql_host,
            user=mysql_user,
            password=mysql_password,
            database=mysql_database,
            mysql_prefix=mysql_prefix
        ),
        shell=True
    )

    execute(
        ctx.obj['MAGENTO_ROOT'],
        ctx.obj['WWW_USER'],
        (
            "admin:user:create"
            " --admin-firstname={magento_admin_firstname}"
            " --admin-lastname={magento_admin_lastname}"
            " --admin-email={magento_admin_email}"
            " --admin-user={magento_admin_username}"
            " --admin-password={magento_admin_password}"
        ).format(
            magento_admin_firstname=magento_admin_firstname,
            magento_admin_lastname=magento_admin_lastname,
            magento_admin_email=magento_admin_email,
            magento_admin_username=magento_admin_username,
            magento_admin_password=magento_admin_password
        )
    )

    opts = {}
    if magento_url:
        opts['base-url'] = magento_url
    if magento_language:
        opts['language'] = magento_language
    if magento_default_currency:
        opts['currency'] = magento_default_currency
    if magento_timezone:
        opts['timezone'] = magento_timezone
    if len(opts.keys()):
        click.echo("Updating other params: %s" % ", ".join(opts.keys()))
        set_config_values(ctx.obj['MAGENTO_ROOT'], ctx.obj['WWW_USER'], mode='store-config', opts=opts)

    click.echo("Cleaning up cache")
    execute(ctx.obj['MAGENTO_ROOT'],
            ctx.obj['WWW_USER'], 'cache:clean')

    install_modules()

    serve()


if __name__ == '__main__':
    cli()
