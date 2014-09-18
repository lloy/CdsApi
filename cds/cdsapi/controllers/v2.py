#
# Copyright 2014 china, LLC (CDS)
# Copyright Ericsson AB 2013. All rights reserved
#
# Authors: Hardy.zheng <wei.zheng@yun-idc.com>
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
"""Version 2 of the API.
"""
import ast
import json
import uuid
import base64
import copy
import traceback
import croniter
import datetime
import functools
import inspect
import json
import jsonschema
import pytz
import simplejson
import uuid

#from oslo.config import cfg
import pecan
from pecan import rest
from pecan import abort
from pecan import expose
import wsmeext.pecan as wsme_pecan
import six
import wsme
from openstack.common.gettextutils import _
from wsme import types as wtypes
from cds.openstackclient.ceilometer_client import Client as V2Ceilometer
from cds.openstackclient.nova_client import Client as V2Nova

from openstack.common import strutils
from openstack.common import timeutils


operation_kind = wtypes.Enum(str, 'lt', 'le', 'eq', 'ne', 'ge', 'gt')

def recursive_keypairs(d, separator=':'):
    """Generator that produces sequence of keypairs for nested dictionaries."""
    for name, value in sorted(d.iteritems()):
        if isinstance(value, dict):
            for subname, subvalue in recursive_keypairs(value, separator):
                yield ('%s%s%s' % (name, separator, subname), subvalue)
        elif isinstance(value, (tuple, list)):
            # When doing a pair of JSON encode/decode operations to the tuple,
            # the tuple would become list. So we have to generate the value as
            # list here.

            # in the special case of the list item itself being a dict,
            # create an equivalent dict with a predictable insertion order
            # to avoid inconsistencies in the message signature computation
            # for equivalent payloads modulo ordering
            first = lambda i: i[0]
            m = map(lambda x: six.text_type(dict(sorted(x.items(), key=first))
                                            if isinstance(x, dict)
                                            else x).encode('utf-8'),
                    value)
            yield name, list(m)
        else:
            yield name, value


def _flatten_metadata(metadata):
    """Return flattened resource metadata.

    Metadata is returned with flattened nested structures (except nested sets)
    and with all values converted to unicode strings.
    """
    if metadata:
        # After changing recursive_keypairs` output we need to keep
        # flattening output unchanged.
        # Example: recursive_keypairs({'a': {'b':{'c':'d'}}}, '.')
        # output before: a.b:c=d
        # output now: a.b.c=d
        # So to keep the first variant just replace all dots except the first
        return dict((k.replace('.', ':').replace(':', '.', 1),
                     six.text_type(v))
                    for k, v in recursive_keypairs(metadata,
                                                         separator='.')
                    if type(v) is not set)
    return {}



class _Base(wtypes.Base):

    @classmethod
    def from_db_model(cls, m):
        return cls(**(m.as_dict()))

    @classmethod
    def from_db_and_links(cls, m, links):
        return cls(links=links, **(m.as_dict()))

    def as_dict(self, db_model):
        valid_keys = inspect.getargspec(db_model.__init__)[0]
        if 'self' in valid_keys:
            valid_keys.remove('self')
        return self.as_dict_from_keys(valid_keys)

    def as_dict_from_keys(self, keys):
        return dict((k, getattr(self, k))
                    for k in keys
                    if hasattr(self, k) and
                    getattr(self, k) != wsme.Unset)


class Link(_Base):
    """A link representation."""

    href = wtypes.text
    "The url of a link"

    rel = wtypes.text
    "The name of a link"

    @classmethod
    def sample(cls):
        return cls(href=('http://localhost:8777/v2/meters/volume?'
                         'q.field=resource_id&'
                         'q.value=bd9431c1-8d69-4ad3-803a-8d4a6b89fd36'),
                   rel='volume'
                   )


class Query(_Base):
    """Query filter."""

    # The data types supported by the query.
    _supported_types = ['integer', 'float', 'string', 'boolean']

    # Functions to convert the data field to the correct type.
    _type_converters = {'integer': int,
                        'float': float,
                        'boolean': functools.partial(
                            strutils.bool_from_string, strict=True),
                        'string': six.text_type,
                        'datetime': timeutils.parse_isotime}

    _op = None  # provide a default

    def get_op(self):
        return self._op or 'eq'

    def set_op(self, value):
        self._op = value

    field = wtypes.text
    "The name of the field to test"

    # op = wsme.wsattr(operation_kind, default='eq')
    # this ^ doesn't seem to work.
    op = wsme.wsproperty(operation_kind, get_op, set_op)
    "The comparison operator. Defaults to 'eq'."

    value = wtypes.text
    "The value to compare against the stored data"

    type = wtypes.text
    "The data type of value to compare against the stored data"

    def __repr__(self):
        # for logging calls
        return '<Query %r %s %r %s>' % (self.field,
                                        self.op,
                                        self.value,
                                        self.type)

    @classmethod
    def sample(cls):
        return cls(field='resource_id',
                   op='eq',
                   value='bd9431c1-8d69-4ad3-803a-8d4a6b89fd36',
                   type='string'
                   )

    def as_dict(self):
        return self.as_dict_from_keys(['field', 'op', 'type', 'value'])

    def _get_value_as_type(self, forced_type=None):
        """Convert metadata value to the specified data type.

        This method is called during metadata query to help convert the
        querying metadata to the data type specified by user. If there is no
        data type given, the metadata will be parsed by ast.literal_eval to
        try to do a smart converting.

        NOTE (flwang) Using "_" as prefix to avoid an InvocationError raised
        from wsmeext/sphinxext.py. It's OK to call it outside the Query class.
        Because the "public" side of that class is actually the outside of the
        API, and the "private" side is the API implementation. The method is
        only used in the API implementation, so it's OK.

        :returns: metadata value converted with the specified data type.
        """
        type = forced_type or self.type
        try:
            converted_value = self.value
            if not type:
                try:
                    converted_value = ast.literal_eval(self.value)
                except (ValueError, SyntaxError):
                    # Unable to convert the metadata value automatically
                    # let it default to self.value
                    pass
            else:
                if type not in self._supported_types:
                    # Types must be explicitly declared so the
                    # correct type converter may be used. Subclasses
                    # of Query may define _supported_types and
                    # _type_converters to define their own types.
                    raise TypeError()
                converted_value = self._type_converters[type](self.value)
        except ValueError:
            msg = (_('Unable to convert the value %(value)s'
                     ' to the expected data type %(type)s.') %
                   {'value': self.value, 'type': type})
            raise ClientSideError(msg)
        except TypeError:
            msg = (_('The data type %(type)s is not supported. The supported'
                     ' data type list is: %(supported)s') %
                   {'type': type, 'supported': self._supported_types})
            raise ClientSideError(msg)
        except Exception:
            msg = (_('Unexpected exception converting %(value)s to'
                     ' the expected data type %(type)s.') %
                   {'value': self.value, 'type': type})
            raise ClientSideError(msg)
        return converted_value

class Resource(_Base):
    """An externally defined object for which samples have been received."""

    resource_id = wtypes.text
    "The unique identifier for the resource"

    project_id = wtypes.text
    "The ID of the owning project or tenant"

    user_id = wtypes.text
    "The ID of the user who created the resource or updated it last"

    first_sample_timestamp = datetime.datetime
    "UTC date & time not later than the first sample known for this resource"

    last_sample_timestamp = datetime.datetime
    "UTC date & time not earlier than the last sample known for this resource"

    metadata = {wtypes.text: wtypes.text}
    "Arbitrary metadata associated with the resource"

    links = [Link]
    "A list containing a self link and associated meter links"

    source = wtypes.text
    "The source where the resource come from"

    def __init__(self, metadata=None, **kwds):
        metadata = metadata or {}
        metadata = _flatten_metadata(metadata)
        super(Resource, self).__init__(metadata=metadata, **kwds)

    @classmethod
    def from_api_model(cls, m):
        return cls(resource_id=m.resource_id,
                   project_id=m.project_id,
                   #user_id='efd87807-12d2-4b38-9c70-5f5c2ac427ff',
                   timestamp=datetime.datetime.utcnow(),
                   source="openstack",
                   #metadata={'name1': 'value1',
                             #'name2': 'value2'},
                    metadata = m.metadata
                   )

    @classmethod
    def sample(cls):
        return cls(resource_id='bd9431c1-8d69-4ad3-803a-8d4a6b89fd36',
                   project_id='35b17138-b364-4e6a-a131-8f3099c5be68',
                   user_id='efd87807-12d2-4b38-9c70-5f5c2ac427ff',
                   timestamp=datetime.datetime.utcnow(),
                   source="openstack",
                   metadata={'name1': 'value1',
                             'name2': 'value2'},
                   links=[Link(href=('http://localhost:8777/v2/resources/'
                                     'bd9431c1-8d69-4ad3-803a-8d4a6b89fd36'),
                               rel='self'),
                          Link(href=('http://localhost:8777/v2/meters/volume?'
                                     'q.field=resource_id&'
                                     'q.value=bd9431c1-8d69-4ad3-803a-'
                                     '8d4a6b89fd36'),
                               rel='volume')],
                   )


class ClientSideError(wsme.exc.ClientSideError):
    def __init__(self, error, status_code=400):
        pecan.response.translatable_error = error
        super(ClientSideError, self).__init__(error, status_code)


class EntityNotFound(ClientSideError):
    def __init__(self, id):
        error = '%s Not Found' %id
        super(EntityNotFound, self).__init__(error,status_code=404)






def get_all_instance(novaclient):

    compute_nodes = list()
    instances_info = dict()
    #find all nodes of compute from all zone
    for host in novaclient.nova_client.hosts.list(zone='nova'):
            compute_nodes.append(host._info['host_name'])

    #find instances from nodes of compute
    for host in compute_nodes:
        search_opts.update(host=host)
        instances = novaclient.nova_client.servers.list(detailed=True, search_opts=search_opts)

        for ins in instances:
            instances_info[ins._info.get('name').lower()] = '%s-%s' %(ins._info.get(instance_name), ins.id)
    return instances_info


class VnicController(rest.RestController):
    print 'VnicController'
    #@expose
    @expose('json')
    #@wsme_pecan.wsexpose([Resource], [Query], int)
    #def get_all(self, lasttime):
    def get_all(self):

        try:
            resources_id = pecan.request.ceilometer.get_resources_id()
            #print resources_id
            if resources_id:
                #return simplejson.dumps(resources_id)
                for rid in resources_id:
                    print rid
                    val = pecan.request.ceilometer.get_statistics('rx', rid, '2013-12-01T18:00')
                print val
            else:
                print resources_id , 'not found'
                abort(404)
        except Exception, e:
            print str(e)
            traceback.print_exc()
            abort(410)


class V2Controller(object):
    """Version 2 API controller root in CDS."""
    print 'zhengwei'
    vnic = VnicController()
