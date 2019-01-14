#!/usr/bin/env bash

VERSION=latest
IMAGE_NAME=aheadworks/m2dev-ce

BUILD_ARGS=""
PHP_VERSION=""

while getopts "v:p:dexs" option
do
 case "${option}"
 in
 v)
 VERSION=${OPTARG}
 BUILD_ARGS="${BUILD_ARGS} --build-arg version=${VERSION}"
 ;;
 p)
 PHP_VERSION=${OPTARG}
 ;;
 s) IS_SAMPLEDATA=1

 BUILD_ARGS="${BUILD_ARGS} --build-arg sampledata=1"
 VER_SAMPLEDATA="-sampledata"
 ;;

 d) IS_DEPLOY=1
 ;;

 e) IS_ENTERPRISE=1
 BUILD_ARGS="$BUILD_ARGS --build-arg edition=enterprise"
 IMAGE_NAME=aheadworks/m2dev-ee
 ;;

 x) IS_XDEBUG=1
 VER_XDEBUG="-xdebug"
 BUILD_ARGS="$BUILD_ARGS --build-arg xdebug=1"
 ;;

 esac
done


# Detect what PHP versions to build
# Get first two digits to detect M2 family

a=( ${VERSION//./ } )
family=${a[0]}.${a[1]}

# Build only supported versions

if [[ ${family} == "2.0" ]]; then
    PHP_VERSIONS=("5.6" "7.0")
fi

if [[ ${family} == "2.1" ]]; then
    PHP_VERSIONS=("5.6" "7.0")
fi

if [[ ${family} == "2.2" ]]; then
    PHP_VERSIONS=("7.0" "7.1")
fi

if [[ ${family} == "2.3" ]]; then
    PHP_VERSIONS=("7.1" "7.2")
fi

cp ${COMPOSER_HOME:-~/.composer}/auth.json auth.json.tmp


if [ -n "${PHP_VERSION}" ]; then
    PHP_VERSIONS=("${PHP_VERSION}")
fi

for pv in ${PHP_VERSIONS[@]}; do

    TAG=${VERSION}${VER_SAMPLEDATA}-${pv}${VER_XDEBUG}
    M2DEV_TAG=${pv}${VER_XDEBUG}

    TAG_STR="${IMAGE_NAME}:${TAG}"

    BUILD_ARGS="${BUILD_ARGS} --squash --build-arg auth_json=auth.json.tmp --build-arg tag=${TAG} --build-arg BASE_VERSION=${M2DEV_TAG}"

    echo "Building image ${IMAGE_NAME}:${TAG}"

    docker build -f Dockerfile -t "${TAG_STR}" ${BUILD_ARGS} .
    if [ -n "$IS_DEPLOY" ]; then
        docker push "${TAG_STR}"
    fi;
done

#cleanup
rm auth.json.tmp

