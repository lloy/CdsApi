#!/usr/bin/env python
# Copyright (c) 2013 Hewlett-Packard Development Company, L.P.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# THIS FILE IS MANAGED BY THE GLOBAL REQUIREMENTS REPO - DO NOT EDIT


from setuptools import setup, find_packages

# In python < 2.7.4, a lazy loading of package `pbr` will break
# setuptools if some other modules registered functions in `atexit`.
# solution from: http://bugs.python.org/issue15881#msg170215

setup(
    name='cdsapi',
    version='1.0',
    description='cdsapi',
    author='hardy.Zheng',
    author_email='wei.zheng@yun-idc.com',
    install_requires=[
        'lxml>=2.3',
        'pecan>=0.4.5',
        'WSME>=0.6',
        'six>=1.7.0',
        'PasteDeploy>=1.5.0',
        'paste>=1.7',
        'babel>=0.8',
        'simplejson>=3.0',
        'WebOb>=1.2.3',
        'six>=1.7.0',
        'jsonschema>=2.0.0,<3.0.0',
        'jsonpath-rw>=1.2.0,<2.0',
        'anyjson>=0.3.3'],

    packages=find_packages(),
    # package_dir={'': 'api'},
    namespace_packages=['cdsapi'],
    scripts=['cds-api'],
    # data_files=[('etc', ['etc/api_paste.ini'])],
    include_package_data=True
    )
