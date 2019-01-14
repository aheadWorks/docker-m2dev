#!/usr/bin/env python3
"""
Run to generate Dockerfiles for desired PHP versions
"""
from pathlib import Path
from distutils.version import StrictVersion
from distutils.dir_util import copy_tree
from functools import reduce
from itertools import product

head = """#
# NOTE: THIS DOCKERFILE IS GENERATED VIA "update.py"
#
# PLEASE DO NOT EDIT IT DIRECTLY.
#
"""

paths_to_copy = ("assets", "patch")


php_deps = {
    '2.3': ["7.2", "7.1"],
    '2.2': ["7.1", "7.0"],
    "2.1": ["7.0", "5.6"]
}

versions_to_update = ["2.3.0", "2.2.7", "2.1.16"]

with open('Dockerfile.template') as df:
    contents = df.read()

    for ver in versions_to_update:

        v = StrictVersion(ver)
        folder_name = ".".join(map(str, v.version[0:2]))

        for php_ver, with_sampledata, with_xdebug in product(php_deps[folder_name], ('', '1'), ('', '1')):
            build_args = {
                'BASE_VERSION': php_ver + ('-xdebug' if with_xdebug else ''),
                'MAGENTO_VERSION': ver,
                'WITH_SAMPLEDATA': with_sampledata
            }

            p = Path() / folder_name / build_args['BASE_VERSION'] / ('Dockerfile' + ('.sampledata' if with_sampledata else ''))
            p.parent.mkdir(parents=True, exist_ok=True)

            dockerfile_content = head + reduce(lambda acc, x: acc.replace('%%' + x[0] + '%%', x[1]), build_args.items(), contents)
            p.write_text(dockerfile_content)

            copy_tree('assets', str(p.parent / 'assets'))
            copy_tree('patch', str(p.parent / 'patch'))
            copy_tree('hooks', str(p.parent / 'hooks'))
