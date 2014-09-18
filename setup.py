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
    name='cdsApi',
    version='1.0',
    description='CdsApi',
    author='hardy.Zheng',
    author_email='wei.zheng@yun-idc.com',
    install_requires=[
        'oslo.config>=1.2.1',
        'pecan>=0.4.5',
        'oslo.messaging>=1.3.0',
        'lxml>=2.3',
        'jsonschema>=2.0.0,<3.0.0',
        'jsonpath-rw>=1.2.0,<2.0',
        'anyjson>=0.3.3'
        ],

    packages=find_packages('cds'),
    package_dir={'': 'cds'},
    namespace_packages=['cds'],
    scripts=['cds/cds-agent'],
    data_files=[('etc', ['cds/etc/api_paste.ini'])],
    include_package_data=True
    )
