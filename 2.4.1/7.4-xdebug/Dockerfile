#
# NOTE: THIS DOCKERFILE IS GENERATED VIA "update.py"
#
# PLEASE DO NOT EDIT IT DIRECTLY.
#
ARG BASE_VERSION="7.4-xdebug"

FROM aheadworks/phpdev:${BASE_VERSION}

ARG MAGENTO_VERSION="2.4.1"
ARG MAGENTO_EDITION="community"
ARG WITH_SAMPLEDATA=""
ARG COMPOSER_AUTH

# Install cron
ADD assets/crontab /crontab
RUN crontab /crontab

COPY assets/create-install-dump.sh /tmp/create-install-dump.sh
ADD patch /.patch

COPY assets/inject-ssh-keys.sh /inject-ssh-keys.sh

RUN apk add --no-cache mariadb-client unzip openssh-server openssh-sftp-server php7-zip php7-sockets\
    && VER=""\
    && rm -rf /var/www/html/* \
    && if [ "${MAGENTO_VERSION}" ] ; then\
        _VER="=${MAGENTO_VERSION}"; \
    fi \
    && composer create-project --repository=https://repo.magento.com/ magento/project-${MAGENTO_EDITION}-edition${_VER} /var/www/html \
    && cd /var/www/html \
    && composer config repositories.magento composer https://repo.magento.com/ \
    && chmod u+x bin/magento \
    && COMPOSER_MEMORY_LIMIT=-1  composer install \
    && python3 -c "from pathlib import Path as p; from distutils.dir_util import copy_tree; list(map(lambda x: copy_tree(str(x), '/var/www/html'), [x for x in p('/.patch').glob('*') if str(x.name) == '${MAGENTO_VERSION}']))" \
#    && if [ "$WITH_SAMPLEDATA" ] ; then \
#        mkdir -p /var/www/html/var/composer_home \
#        && php -dmemory_limit=-1 /var/www/html/bin/magento sampledata:deploy; \
#    fi \
    && apk --no-cache add --virtual .mysql mysql \
    && sed -i 's/.*throw new ValidationException(__(implode(PHP_EOL, $validationErrors)));.*//'  setup/src/Magento/Setup/Model/SearchConfig.php
RUN sh /tmp/create-install-dump.sh
RUN rm /tmp/create-install-dump.sh \
    && rm -rf /.patch \
    && mkdir /run/sshd \
    && sed -i s/#PermitRootLogin.*/PermitRootLogin\ yes/ /etc/ssh/sshd_config \
    && sed -i s/AllowTcpForwarding.*/AllowTcpForwarding\ yes/ /etc/ssh/sshd_config \
    && apk del .mysql \
    && composer clearcache \
    && rm -rf /var/lib/mysql

RUN ssh-keygen -A



COPY assets/nginx.conf /etc/nginx/conf.d/default.conf

COPY assets/entrypoint.py /entrypoint.py
RUN if [ ! "$WITH_SAMPLEDATA" ] ; then \
        sed -i 's/.*p2 = subprocess\.Popen(["php", "-d", "memory_limit=4G", "\/var\/www\/html\/bin\/magento", "sampledata:deploy"]).*//'  /entrypoint.py \
        && sed -i 's/.*        sampledata()*//'  /entrypoint.py; \
        fi

ENTRYPOINT ["python3", "/entrypoint.py"]
CMD ["update-and-serve"]