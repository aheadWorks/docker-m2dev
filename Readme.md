# docker-m2dev

Base image for Magento 2 development. 

**Development purposes only**

This image doing a lot of "wrong" things useful at dev stage, however it is extremely dangerous at production(e.g. runs php-fpm as root)

To simplify things this image contains multiple services inside(nginx, php-fpm, ssh). This allows to run Magento CLI scripts, solves performance issues on Win/Mac with mounted bind volumes.


## What's inside

* installed Magento 2 instance(with optional sampledata)
* PHP-fpm
* nginx
* crontab
* composer
* mhsendmail
* python

Available tags:

* Magento versions 2.1 to 2.3
* With or without bundled sampledata
* PHP versions 5.6, 7.0, 7.1, 7.2 
* With or without XDebug

## Environment variables
This variables can be passed during container run with `-e` flag or docker-compose.yml `environment` node.

* `MAIL_HOST` - mail host server name, all mail is redirected here
* `SSH_PASSWORD` - SSH/SFTP service root password. Default is `root`
* `MYSQL_HOST` - MySQL server hostname. 
* `MYSQL_PORT` - MySQL server port. Default `3306`
* `MYSQL_USER`- MySQL user
* `MYSQL_PASSWORD` - MySQL password
* `MYSQL_DATABASE` - MySQL database to use.
* `MAGENTO_URL` - Magento URL. 
* `MAGENTO_ADMIN_USERNAME` - Magento admin username
* `MAGENTO_ADMIN_PASSWORD` - Magento admin password

## Startup flow
* Waits for MySQL server at `MYSQL_HOST`
* Checks if DB structure is ok in `MYSQL_DATABASE`
* If not, imports pre-saved dump 
* Updates Magento configurable settings
* Runs http frontend and SSH server

## Example docker-compose.yml

```
version: '3.7'
services:
  db:
    environment:
    - MYSQL_ROOT_PASSWORD=myrootpassword
    - MYSQL_USER=magento
    - MYSQL_PASSWORD=magento
    - MYSQL_DATABASE=magento
    image: mysql:5.6.42
    volumes:
    - data-db:/var/lib/mysql
  mail:
    image: mailhog/mailhog
    command:
    - -smtp-bind-addr
    - 0.0.0.0:25
    - -ui-bind-addr
    - 0.0.0.0:80
    - -api-bind-addr
    - 0.0.0.0:80
    ports:
    - 1388:80
    user: root
  web:
    image: aheadworks/m2dev-ce:2.3-7.2-sampledata
    environment:
    - MAIL_HOST=mail
    - MAGENTO_URL=http://local.magento:1380
    - MAGENTO_TIMEZONE=Pacific/Auckland
    - MAGENTO_DEFAULT_CURRENCY=USD
    - MAGENTO_ADMIN_FIRSTNAME=Admin
    - MAGENTO_ADMIN_LASTNAME=MyStore
    - MAGENTO_ADMIN_EMAIL=amdin@example.com
    - MAGENTO_ADMIN_USERNAME=master
    - MAGENTO_ADMIN_PASSWORD=master123
    - MAGENTO_ROOT=/var/www/html
    - MAGENTO_LANGUAGE=en_GB
    - MYSQL_HOST=db
    - MYSQL_ROOT_PASSWORD=myrootpassword
    - MYSQL_USER=magento
    - MYSQL_PASSWORD=magento
    - MYSQL_DATABASE=magento
    - AUTO_SETUP=1
    - COMPOSER_AUTH=
    - SSH_PASSWORD=pushkin
    ports:
    - '1080:80'
    - '1022:22'
    volumes:
    - data-files:/var/www/html
volumes:
  data-db: null
  data-files: null
```