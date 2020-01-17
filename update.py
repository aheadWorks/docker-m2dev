#!/usr/bin/env python3
"""
Run to generate Dockerfiles for desired PHP versions
"""
from pathlib import Path
from distutils.version import StrictVersion, LooseVersion
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

versions_to_update = ["2.3.4", "2.3.3", "2.3.2-p1", "2.3.2", "2.3.1", "2.3.0", "2.2.9", "2.2.8", "2.2.7", "2.2.6", "2.2.0",  "2.1.17"]


def is_latest_version(version, all_versions):
    if "-" in version:
        return False
    family = StrictVersion(version).version[0:2]
    family_vers = [x for x in sorted([k for k in all_versions if "-" not in k], key=StrictVersion) if StrictVersion(x).version[0:2] == family]

    if family_vers[-1] == StrictVersion(version):
        return True
    return False


with open('Dockerfile.template') as df:
    contents = df.read()

    for original_ver in versions_to_update:
        ver = original_ver
        if "-" in original_ver:
            ver, extra = ver.split("-")

        v = StrictVersion(ver)
        family = ".".join(map(str, v.version[0:2]))

        folder_name = family if is_latest_version(original_ver, versions_to_update) else original_ver

        for php_ver, with_sampledata, with_xdebug in product(php_deps[family], ('', '1'), ('', '1')):
            build_args = {
                'BASE_VERSION': php_ver + ('-xdebug' if with_xdebug else ''),
                'MAGENTO_VERSION': original_ver,
                'WITH_SAMPLEDATA': with_sampledata
            }

            p = Path() / folder_name / build_args['BASE_VERSION'] / ('Dockerfile' + ('.sampledata' if with_sampledata else ''))
            p.parent.mkdir(parents=True, exist_ok=True)

            dockerfile_content = head + reduce(lambda acc, x: acc.replace('%%' + x[0] + '%%', x[1]), build_args.items(), contents)
            p.write_text(dockerfile_content)

            copy_tree('assets', str(p.parent / 'assets'))
            copy_tree('patch', str(p.parent / 'patch'))
            copy_tree('hooks', str(p.parent / 'hooks'))
