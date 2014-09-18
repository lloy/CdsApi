#
# Copyright 2012 New Dream Network, LLC (DreamHost)
#
# Author: hardy.Zheng <wei.zheng@cds.com>
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from oslo.config import cfg
from pecan import hooks
from cds.openstackclient import ceilometer_client
from cds.openstackclient import nova_client
#from ceilometer.storage import impl_mongodb

#from ceilometer import pipeline


URL = 'mongodb://ceilometer:q1w2e3r4t5@controller:27017/ceilometer'
class CeilometerAPIHook(hooks.PecanHook):

    def __init__(self):
        self.ceilometer = ceilometer_client.Client()

    def before(self, state):
        state.request.ceilometer = self.ceilometer

class NovaAPIHook(hooks.PecanHook):

    def __init__(self):
        self.nova = nova_client.Client()

    def before(self, state):
        state.request.nova = self.nova

#class DBHook(hooks.PecanHook):

    #def __init__(self):
        #self.storage_connection = impl_mongodb.Connection(URL)

    #def before(self, state):
        #state.request.storage_conn = self.storage_connection



