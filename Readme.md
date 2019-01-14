# docker-m2dev

Base image for Magento 2 development. 

**Development purposes only**

This image doing a lot of "wrong" things useful at dev stage, however it is extremely dangerous at production(e.g. runs php-fpm as root)

## What's inside

* installed Magento 2 instance(with optional sampledata)
* PHP-fpm
* nginx
* crontab
* composer
* mhsendmail
* python

