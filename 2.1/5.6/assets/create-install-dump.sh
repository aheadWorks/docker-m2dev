#!/usr/bin/env sh
#
# Install database, install magento, then dump it's files
#

MAGENTO_URL=http://local.local
MAGENTO_TIMEZONE=Pacific/Auckland
MAGENTO_DEFAULT_CURRENCY=USD
MAGENTO_ADMIN_FIRSTNAME=Admin
MAGENTO_ADMIN_LASTNAME=MyStore
MAGENTO_ADMIN_EMAIL=amdin@example.com
MAGENTO_ADMIN_USERNAME=admin
MAGENTO_ADMIN_PASSWORD=admin123
MAGENTO_ROOT=/var/www/html
MAGENTO_LANGUAGE=en_US
MAGENTO_USE_REWRITES=1
MYSQL_HOST=127.0.0.1
MYSQL_ROOT_PASSWORD=root
MYSQL_USER=root
MYSQL_PASSWORD=root
MYSQL_DATABASE=magento
MYSQL_ALLOW_EMPTY_PASSWORD=yes

rm -R /var/lib/mysql/*
mysql_install_db --user=root --basedir=/usr --datadir=/var/lib/mysql

if [ ! -d "/run/mysqld" ]; then
    mkdir -p /run/mysqld
  fi

  tfile=`mktemp`
  if [ ! -f "$tfile" ]; then
      return 1
  fi

  cat << EOF > $tfile
USE mysql;
FLUSH PRIVILEGES;
GRANT ALL PRIVILEGES ON *.* TO 'root'@'%' IDENTIFIED BY "${MYSQL_ROOT_PASSWORD}" WITH GRANT OPTION;
GRANT ALL PRIVILEGES ON *.* TO 'root'@'localhost' WITH GRANT OPTION;
UPDATE user SET password=PASSWORD("") WHERE user='root' AND host='localhost';
EOF
  if [ "$MYSQL_DATABASE" != "" ]; then
    echo "[i] Creating database: $MYSQL_DATABASE"
    echo "CREATE DATABASE IF NOT EXISTS \`$MYSQL_DATABASE\` CHARACTER SET utf8 COLLATE utf8_general_ci;" >> $tfile
  fi

  /usr/bin/mysqld --user=root --bootstrap --verbose=0 < $tfile
  rm -f $tfile

/usr/bin/mysqld --user=root --console &
sleep 5

echo 'pdo_mysql.default_socket = /run/mysqld/mysqld.sock' >> /usr/local/etc/php/conf.d/docker-php-ext-pdo_mysql.ini

php -f /var/www/html/bin/magento setup:install --base-url=$MAGENTO_URL --use-rewrites=${MAGENTO_USE_REWRITES} --backend-frontname=admin --language=$MAGENTO_LANGUAGE --timezone=$MAGENTO_TIMEZONE --currency=$MAGENTO_DEFAULT_CURRENCY --db-name=$MYSQL_DATABASE --db-user=root --db-host=localhost --use-secure=0 --base-url-secure=0 --use-secure-admin=0 --admin-firstname=$MAGENTO_ADMIN_FIRSTNAME --admin-lastname=$MAGENTO_ADMIN_LASTNAME --admin-email=$MAGENTO_ADMIN_EMAIL --admin-user=$MAGENTO_ADMIN_USERNAME --admin-password=$MAGENTO_ADMIN_PASSWORD

mysqldump -u$MYSQL_USER magento | sed -e 's/DEFINER[ ]*=[ ]*[^*]*\*/\*/' | sed -e 's/DEFINER[ ]*=[ ]*[^*]*PROCEDURE/PROCEDURE/' | sed -e 's/DEFINER[ ]*=[ ]*[^*]*FUNCTION/FUNCTION/'> /var/www/dump.sql
