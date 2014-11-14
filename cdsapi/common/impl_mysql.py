# yes

__author__ = 'Hardy.zheng'
__email__ = 'wei.zheng@yun-idc.com'


import MySQLdb
import logging
from MySQLdb import Error as MySqlError

from cdsapi import cfg
from cdsapi import exc


CONF = cfg.CONF
LOG = logging.getLogger(__name__)


class _MysqlBase(object):
    def __init__(self):
        try:
            self.conn = self._conn()
            self.cur = None
            self.set()
        except MySQLdb.Error, e:
            LOG.error(str(e))

    def _conn(self):
        try:
            return MySQLdb.Connection(
                host=CONF.db.host,
                user=CONF.db.user,
                passwd=CONF.db.passwd,
                db=CONF.db.name,
                port=int(CONF.db.port))
        except MySQLdb.Error, e:
            LOG.error(str(e))
            return None

    def set(self):
        try:
            if self.conn:
                self.cur = self.conn.cursor()
        except MySQLdb.Error, e:
            self.conn = None
            self.cur = None
            LOG.error(str(e))

    def reconn(self):
        self.conn = self._conn()
        self.set()

    def refresh(self):
        self.clear()
        self.reconn()
        self.set()

    def clear(self):
        if self.cur:
            self.cur.close()
            self.cur = None
        if self.conn:
            self.conn.close()
            self.conn = None

    def runCommand(self, cmd):
        try:
            if not self.conn or not self.cur:
                raise MySqlError('Not Connect DB')
            self.cur.execute(cmd)
            return self.cur.fetchall()
        except Exception, e:
            LOG.debug(str(e))
            raise MySqlError(str(e))

    def _isfound(self, id):
        raise NotImplementedError('_MysqlBase _isfound Not Implemented')


class TasksTable(_MysqlBase):

    table = CONF.db.tasks

    def get(self, task_id):
        cmd = "select * from %s where task_id=\"%s\"" % (self.table, task_id)
        LOG.debug('tasks GET command: %s ' % cmd)
        self.refresh()
        tasks = self.runCommand(cmd)
        if tasks:
            return tasks
        else:
            LOG.debug("Empty set")
            return None

    def add(self, **kwargv):
        """
        kwargv parms:
            task_id: task uniquely identifies
            create_time: task create time
            template_type: instance template type
            model_type: instance type
            status: task status
            instances_num: create instance number
        """
        if self._isfound(kwargv['task_id']):
            return False
        cmd = "insert into %s (task_id, create_time, template_type, model_type,\
               status, is_run, instances_num) values(\"%s\",\"%s\",\"%s\",\"%s\",\"%s\",%d, %d)" \
               % (self.table,
                  kwargv['task_id'],
                  kwargv['create_time'],
                  kwargv['template_type'],
                  kwargv['model_type'],
                  kwargv['status'],
                  0,
                  kwargv['instances_num'])
        LOG.debug('TasksTable add cmd : %s' % cmd)
        self.runCommand(cmd)
        self.conn.commit()

    def _isfound(self, task_id):
        if self.get(task_id):
            return True
        else:
            return False


class InstancesTable(_MysqlBase):

    table = CONF.db.instances

    def list(self, customers, **kw):
        cmd = "select * from %s where customers='%s'" % (self.table, customers)
        if kw:
            search_string = ''
            for k, v in kw.items():
                search_string += "and %s=\"%s\"" % (k, v)
            cmd += search_string
        LOG.debug('instances GET_ALL cmd: %s' % cmd)
        self.refresh()
        instances = self.runCommand(cmd)
        if not instances:
            raise exc.NotFound('Not a instance in Cds', '00202')
        return instances

    def get(self, instance_uuid):
        cmd = "select * from %s where instance_uuid=\"%s\"" % (self.table, instance_uuid)
        self.refresh()
        instance = self.runCommand(cmd)
        LOG.debug("storage in mysql instance: %s" % str(instance))
        if not instance:
            LOG.error('NotFound instance %s' % instance_uuid)
            raise exc.NotFound('NotFound instance %s' % instance_uuid, '00301')
        return instance

    def getInstancesfromtask_id(self, task_id):
        cmd = "select * from %s where task_id=\"%s\" and status=\"running\""\
              % (self.table, task_id)
        LOG.debug('getInstancesfromtask_id cmd %s' % cmd)
        self.refresh()
        instances = self.runCommand(cmd)
        LOG.debug('instances: %s' % str(instances))
        if not instances:
            return None
        return instances

    def add(self, **kwargv):
        """
        kwargv parms:
            instance_uuid: instance uniquely identifies
            name: instance name
            ip: instance ipaddress
            status: instance status, [running, stop, error, deleting, lanuching]
            os_type: instance system type
            username: instance user name
            passwd: instance user password
            template_type: instance template_type: TemplateType
            instance_type: instance type: InstancesType
            iaas_type: iaas type eg: openstack, vsphere
            customers: 1haodian
            create_time: instance create time
            online_time: instance login time
            off_time: instance show down time
        """
        raise NotImplementedError('instance add interface Not Implemented')

    def update(self, **kwargv):
        """
        parms the same as add interface
        """

        raise NotImplementedError('instance add interface Not Implemented')

    def delete(self, instance_uuid):
        cmd = "update %s set status=\"deleting\" where instance_uuid=\"%s\""\
              % (self.table, instance_uuid)
        LOG.debug("instance delete cmd %s" % cmd)
        if self._isfound(instance_uuid):
            self.runCommand(cmd)
            self.conn.commit()

    def _isfound(self, instance_uuid):
        if self.get(instance_uuid):
            return True
        else:
            return False


class IpTable(_MysqlBase):

    table = CONF.db.iptable

    def get_all(self, flag):
        if flag == 'ALL':
            cmd = "select ipaddress from %s " % self.table
        if flag == 'ALLOC':
            cmd = "select ipaddress from %s where is_alloc= %d" % (self.table, 1)
        if flag == 'UN_ALLOC':
            cmd = "select ipaddress from %s where is_alloc= %d" % (self.table, 0)
        self.refresh()
        ipaddress = self.runCommand(cmd)
        if not ipaddress:
            raise exc.NotFound('Not a ipaddress', '03001')

    def get(self):
        raise NotImplementedError('IpTable get interface Not Implemented')

    def add(self, **kwargv):
        raise NotImplementedError('IpTable add interface Not Implemented')

    def update(self, **kwargv):
        raise NotImplementedError('IpTable update interface Not Implemented')

    def delete(self, ipaddress):
        raise NotImplementedError('IpTable delete interface Not Implemented')


class TemplateTable(_MysqlBase):
    table = CONF.db.template

    def get_all(self):
        raise NotImplementedError('Template get interface Not Implemented')

    def get(self, name):
        cmd = "select * from %s where name=\"%s\"" % (self.table, name)
        LOG.debug('TemplateTable cmd %s' % cmd)
        self.refresh()
        template = self.runCommand(cmd)
        if template:
            return template
        else:
            return None

    def add(self, **kwargv):
        pass

    def delete(self, name):
        raise NotImplementedError('TemplateTable delete interface Not Implemented')


class DriversTable(_MysqlBase):

    table = CONF.db.driver

    def get_all(self):
        raise NotImplementedError('Drivers get interface Not Implemented')

    def update_drivers(self, status):
        raise NotImplementedError('Drivers update interface Not Implemented')
