import click
import subprocess
import shlex
import time
import pathlib
import re

@click.group()
@click.pass_context
def cli(ctx):
    ctx.obj = {
        'MAGENTO_ROOT': '/var/www/html',
        'WWW_USER': 'root'
    }
    subprocess.check_call("sh /update-host-machine.sh", shell=True)
    pass


def execute(path, user, cmd):
    cmd = 'su {user} -c "php {path}/bin/magento %s"' % cmd
    return subprocess.check_output(cmd.format(user=user, path=path), shell=True)


def set_ssh(user):
    return subprocess.check_output('su {user} -c "sh /inject-ssh-keys.sh"'.format(user=user), shell=True)


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

    serve()


if __name__ == '__main__':
    cli()
