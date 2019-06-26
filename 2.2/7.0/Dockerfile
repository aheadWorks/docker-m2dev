#
# NOTE: THIS DOCKERFILE IS GENERATED VIA "update.py"
#
# PLEASE DO NOT EDIT IT DIRECTLY.
#
ARG BASE_VERSION="7.0"

FROM aheadworks/phpdev:${BASE_VERSION}

ARG MAGENTO_VERSION="2.2.9"
ARG MAGENTO_EDITION="community"
ARG WITH_SAMPLEDATA=""
ARG COMPOSER_AUTH

# Install cron
ADD assets/crontab /crontab
RUN crontab /crontab

COPY assets/create-install-dump.sh /tmp/create-install-dump.sh
ADD patch /.patch

RUN apk add --no-cache mariadb-client unzip openssh-server openssh-sftp-server \
    && VER=""\
    && rm -rf /var/www/html/* \
    && if [ "${MAGENTO_VERSION}" ] ; then\
        _VER="=${MAGENTO_VERSION}"; \
    fi \
    && composer create-project --repository=https://repo.magento.com/ magento/project-${MAGENTO_EDITION}-edition${_VER} /var/www/html \
    && cd /var/www/html \
    && composer config repositories.magento composer https://repo.magento.com/ \
    && chmod u+x bin/magento \
    && composer install \
    && python3 -c "from pathlib import Path as p; from distutils.dir_util import copy_tree; from distutils.version import StrictVersion; list(map(lambda x: copy_tree(str(x), '/var/www/html'), [x for x in p('/.patch').glob('*') if StrictVersion(str(x.name)) == '${MAGENTO_VERSION}']))" \
    && if [ "$WITH_SAMPLEDATA" ] ; then \
        mkdir -p /var/www/html/var/composer_home \
        && /var/www/html/bin/magento sampledata:deploy; \
    fi \
    && apk --no-cache add --virtual .mysql mysql \
    && sh /tmp/create-install-dump.sh \
    && rm /tmp/create-install-dump.sh \
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

ENTRYPOINT ["/usr/bin/python3", "/entrypoint.py"]
CMD ["update_and_serve"]