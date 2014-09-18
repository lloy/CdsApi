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

import functools
import datetime
import os

from ceilometerclient import client as ceilometer_client
from ceilometer.openstack.common import timeutils
from oslo.config import cfg
from openstack.common import log
from ceilometerclient import exc

cfg.CONF.import_group('service_credentials', 'cds.api.service')
conf = cfg.CONF.service_credentials
LOG = log.getLogger(__name__)

FAKE_ENV = {
         'os_username': conf.os_username,
         'os_password':conf.os_password,
         'os_tenant_name':conf.os_tenant_name,
         'os_auth_url':conf.os_auth_url,
         'ceilometer_url':'http://controller:8777/',
         }

def logged(func):

    @functools.wraps(func)
    def with_logging(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            LOG.exception(e)
            raise

    return with_logging


class Client(object):

    _KEY = 'mac'
    _NIC_MAPPING = {
        'rx': 'network.incoming.bytes',
        'tx': 'network.outcoming.bytes',
        }
    _NIC_INCOMING_QURRY = [
        {'field':'resource_id'},
        ]

    """A client which gets information via python-ceilometerclient."""
    def __init__(self):
        """Initialize a ceilometer client object."""
        self.cli = ceilometer_client.get_client(2, **FAKE_ENV)
        self.resources_id = []

    #return value:{'instance-name-uuid':set(['vnic1', 'vnic2']), 'xxx':set(['xxx','xxx'])}
    def get_resources_id(self):
        def _format(res):
            _resources = dict()
            for resource in res:
                _resource = resource.rsplit('-', 2)
                _resources[_resource[0]] = ('%s-%s' %(_resource[1],_resource[2]))
            return _resources

        try:
            tap_resources_id = [rid for rid in self.cli.resources.list()
                    if self._KEY in rid.metadata]
            instance_ids = set([res_id.metadata['instance_id'] for res_id in tap_resources_id])
            return self._filter_repeater_id(instance_ids, tap_resources_id)
        except exc.CommunicationError, e:
            raise exc.CommunicationError(str(e))


    #name is meter name from one resources_id
    def get_onesample(self, name, resource_id):
        print resource_id
        q = self._NIC_INCOMING_QURRY[0].update(value=resource_id)
        kwargs = {'q':q,
                'limit':1}
        resource = self._get_sample(name, **kwargs)

    def _get_sample(self, name, **kwargs):
        resources = self.cli.samples.list(meter_name=self._NIC_MAPPING.get(name), **kwargs)
        if resources:
            print resources
            return '%s%s' %(resources[0].counter_volume, resources[0].counter_unit)
        else:
            return None

    def get_samples(self, name):
        kwargs = {'q':[],
                'limit':1}
        resource = self._get_sample(name, **kwargs)


    def get_statistics(self, name, resource_id, last_time):
        #current_time = datetime.datetime
        last_time = timeutils.parse_isotime('2014-07-01T09:00:15').replace(tzinfo=None)
        current_time = timestamp=timeutils.isotime()

        q = [
                {'field':'resource_id',
                    'op':'eq',
                    'value':resource_id},
                {'field':'timestamp',
                    'op':'gt',
                    'value':"2014-07-01T09:00:15"},
                {'field':'timestamp',
                    'op':'lt',
                    'value':"2014-08-01T09:00:15"},
                ]
        kwargs ={'q':q}
        try:
            statistics_val = self.cli.statistics.list(meter_name=self._NIC_MAPPING.get(name), **kwargs)
            print 'zhengwei list', statistics_val
            return statistics_val
        except Exception, e:
            print str(e)
            return None

    def _filter_repeater_id(self, instance_ids, tap_resources_id):
        using_resource_id = []
        for instance_id in instance_ids:
            same_uuid = []
            for resource_id in tap_resources_id:
                if instance_id == resource_id.metadata['instance_id']:
                    same_uuid.append(resource_id)
            if not same_uuid:
                continue
            using_resource_id.append(self._laster(same_uuid))
        return using_resource_id


    #return laster id that it would have same instance id in those resource ids
    def _laster(self, resource_ids):
        d = {}
        for rid in resource_ids:
            d[rid.first_sample_timestamp] = rid.resource_id

        timestamps = d.keys()
        timestamps.sort()
        return d[timestamps[0]]

#import uuid
#def get_resource_id(client):
    #resources = client.cli.resources.list()
    #return [rid.resource_id for rid in resources
            #if len(rid.resource_id) >len(str(uuid.uuid1()))]

#return value:{'instance-name-uuid':set(['vnic1', 'vnic2']), 'xxx':set(['xxx','xxx'])}
#def get_resource_id(ceilometerclient):
    #def _format(res):
        #_resources = dict()
        #val = set()
        #for resource in res:
            #_resource = resource.rsplit('-', 2)
            #_resources[_resource[0]] = ('%s-%s' %(_resource[1],_resource[2]))
        #return _resources

    #resources = ceilometerclient.cli.resources.list()
    #return _format([rid.resource_id for rid in resources
            #if len(rid.resource_id) >len(str(uuid.uuid1()))])


#if __name__ == '__main__':
    #cfg.CONF.register_cli_opts(CLI_OPTIONS, group="service_credentials")
    #v2 = Client()
    #print get_resource_id(v2)
    ##resource_id = v2.cli.resources.list()

    ##qu = [
            ##{"field": 'resource_id','value':"instance-00000024-facf40be-7947-4932-a1bb-fad6c4499268-tap147d939a-89"},
            ##]
    ###resource_id = v2.cli.statistics.list(meter_name="instance", q)
    ###resource_id = v2.cli.samples.list(meter_name='network.incoming.bytes', q=qu, limit = 1)
    ###resource_id = v2.cli.samples.list(meter_name='network.incoming.bytes', limit = 1)
    ###print '%s%s'%(resource_id[0].counter_volume,resource_id[0].counter_unit)
    ###for rid in resource_id:
        ###print rid.resource_id
        ###break
    ###print cfg.CONF.service_credentials.os_username


