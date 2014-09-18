# -*- coding: utf-8 -*-
#
# Author: John Tran <jhtran@att.com>
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

from novaclient.v1_1 import client as nova_client
from oslo.config import cfg
from openstack.common import log

#cfg.CONF.import_group('service_credentials', 'ceilometer.service')
LOG = log.getLogger(__name__)
conf = cfg.CONF.service_credentials


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
    """A client which gets information via python-novaclient."""

    _search_opts = {'all_tenants': True}
    _instance_name = 'OS-EXT-SRV-ATTR:instance_name'

    def __init__(self):
        """Initialize a nova client object."""
        tenant = conf.os_tenant_id or conf.os_tenant_name
        self.nova_client = nova_client.Client(
            username=conf.os_username,
            api_key=conf.os_password,
            project_id=tenant,
            auth_url=conf.os_auth_url,
            service_type="compute",
            region_name=conf.os_region_name,
            endpoint_type=conf.os_endpoint_type,
            cacert=conf.os_cacert,
            insecure=conf.insecure,
            no_cache=True)

    def get_instances(self):
        compute_nodes = list()
        instances_info = dict()
        #find all nodes of compute from all zone
        for host in novaclient.nova_client.hosts.list(zone='nova'):
                compute_nodes.append(host._info['host_name'])

        #find instances from nodes of compute
        for host in compute_nodes:
            slef._search_opts.update(host=host)
            instances = self.nova_client.servers.list(detailed=True, search_opts=self._search_opts)

            for ins in instances:
                instances_info[ins._info.get('name').lower()] = '%s-%s' %(ins._info.get(self._instance_name), ins.id)
        return instances_info



#if __name__ == '__main__':
    #client = Client()
    ##host = 'compute01'
    ##hosts = client.nova_client.hosts.list(zone="nova")
    ##for host in hosts:
        ##print host._info
    #print get_all_instance(client)
    ##search_opts = {'host': host, 'all_tenants': True}
#    #instances = client.nova_client.servers.list(detailed=True, search_opts=search_opts)
    ##print unicode(instances)

    #for i in instances:
        #resource_id = '%s-%s' %(i._info.get('OS-EXT-SRV-ATTR:instance_name'), i.id)
        #instance_info_map[i._info.get('name')] = resource_id

    #print instance_info_map
    #    #print str(i._info)
    #self.virtual_interfaces
