#!/usr/bin/env python
"""
(Notes from the original gist start here)
Pip requirements:
-----------------
ecdsa==0.10
netaddr==0.7.10
pycrypto==2.6.1
pyvmomi==5.5.0
wsgiref==0.1.2
"""


from pyVim.connect import SmartConnect, Disconnect
from pyVmomi import vim
# from pyVim import vmodl
import MySQLdb
import datetime
from MySQLdb import Error as MySqlError
import uuid
import copy
import time
import atexit
import getpass
import telnetlib
# import os
import sys
# from netaddr import IPNetwork, IPAddress
import argparse
# from copy import deepcopy

# DEFIND VMWARE VCENTER SERVER
vserver = "10.128.11.2"
port = 443
username = "api.Adm1n@cdscloud.local"
password = "cloud-P@$$w0rd@2014"
vcenter = {
    "vserver": vserver,
    "port": port,
    "username": username,
    "password": password,
    }


clusters = {
    "POD10-CLU01": {'template_name': 'Moban-YiHaoDian-10-55-0-253-CentOS6.4-64bit-20141020-cluster01', 'number': 300},
    "POD10-CLU02": {'template_name': 'Moban-YiHaoDian-10-55-0-253-CentOS6.4-64bit-20141101-cluster02', 'number': 300},
    "POD10-CLU03": {'template_name': 'Moban-YiHaoDian-10-55-0-253-CentOS6.4-64bit-20141020-cluster03', 'number': 0}
}

# DEFIND VMWARE VCENTER DATABASE
datacenter_name = "POD10(SH_JQ)"
cluster_name = "POD10-CLU01"
compute_resource = ""
datastore_name = "POD10-CLU01-VOL"
network_name = "vlan1000(POD10-YiHaoDian)"
default_datacenter = {
    "datacenter_name": datacenter_name,
    "cluster_name": cluster_name,
    "compute_resource": compute_resource,
    "datastore_name": datastore_name,
    "network_name": network_name,
    }

instances_alloc_table = {}

# DEFIND TEMPLATE HOST
TEMPLATE_HOST = "10.55.0.253"
custom_dns = "8.8.8.8"
custom_username = "root"
custom_password = "cds-zhengwei"


# DEFIND DATABASE CONFIGURE
db_host = "10.128.23.150"
db_username = "admin"
db_password = "q1w2e3"
db_name = "apicloud"
db_port = 3306

################################################
# defind ubuntu eth0 configure
################################################
ubuntu_eth0 = """
auto lo
iface lo inet loopback

auto eth0
iface eth0 inet static
address %s
netmask 255.255.255.0
network 172.16.0.0
broadcast 172.16.0.255
dns-nameservers %s
gateway %s
"""
ubuntu_configure = "echo \"%s\" > /etc/network/interfaces\n"

################################################
# defind fedora eth0 configure
################################################
fedora_eth0 = """
NAME=eth0
ONBOOT=yes
TYPE=Ethernet
BOOTPROTO=static
DEFROUTE=yes
PREFIX0=24
IPADDR0=%s
DNS1=%s
GATEWAY0=%s
"""
fedora_configure = "echo \"%s\" > /etc/sysconfig/network-scripts/ifcfg-eth0\n"

################################################
# defind centos eth0 configure
################################################
centos_eth0 = """
DEVICE=eth0
TYPE=Ethernet
ONBOOT=yes
NM_CONTROLLED=yes
BOOTPROTO=static
IPADDR=%s
NETMASK=255.255.255.0
GATEWAY=%s
DNS=%s
"""
centos_configure = "echo \"%s\" > /etc/sysconfig/network-scripts/ifcfg-eth0\n"


centos_hostname_cfg = """
NETWORKING=yes
HOSTNAME=%s
"""

ubuntu_hostname = "hostname %s"
fedora_hostname = "hostname %s"
centos_hostname = "echo \"%s\" > /etc/sysconfig/network\n"

###########################
# YHD configure         ###
###########################
deploy_key="""
ssh-rsa AAAAB3NzaC1yc2EAAAABIwAAAQEAzpuECoOcRhxWS7uoKOmtGIijntHwVO+NCzXRA8zZpwGjA/hf4VSFuuVyJE4E4gSPtG4Wh19cAhPLD85F9F9jba+dS1I27WvG8bNVQemVgcRmHcKDFNb234K9sMaApWARxYMmgXycnpZg/6wacwgZLuX9YoX4gmrhdIgBb6Y5V7cqA860Wr90otvaIPeAYorN6Gbb0sv/o5pp+ch1Sn7x3RLI37gLLg3wPvWLQApd+64tWEzRk+a+7bF6alcZ3OpdLBBApU54Fb5jQFovzuKD/CFioOJoQaQjbiKrRp/PGYhmlD26cg8sssUjvE2j7FG269IiY1b/4i5RhqELeePw1Q== deploy@xen0328-vm05
ssh-rsa AAAAB3NzaC1yc2EAAAABIwAAAQEAx4NJmzuzX4qckbcj1dXvDltQHFemJRaqVu3WJMEF4VSgttGLfmfVVKBpwN1OdEIWgtWxPvxrcO8O767n1MpCyZ86p5aqC8aEPzgZq/ew0+D5jKBC9Jmudvn/iUASIpMDWMSwlW9ApC4TWURwUjfNmuqb8n1J8hJZUjQdKjBtd9bxO9gFBJS15pXI7dOExyEuJ9qR3SBwsAlR2r7RPB/9e2J3mnt9Bo1psAtUUzfP5WEpEK6c7LTjgrtokHCnufW0E58ABdSuUmI2/PQr/R6Dcy7f2u+PDNRfOUcq7YjwYiSsxugKkTRAGSjwb1i/K2WKPGA6Dtap2d1fgdSgkUm1qQ== deploy@xen21-vm04
ssh-rsa AAAAB3NzaC1yc2EAAAABIwAAAQEAuhHxbWxdQqKtvJ8tZQ3eswaR1nw9DE5anjcMBo58djrOig+zacdpzIR0HiH2bK4GpdU3vBoQU5bwGyCorALn7d1Lpqf/pSjzHHpow4C6JKXvLRXCzKAT0AAhzsSBT/OjzsRmb0wRCfwzsHQsaxTtLWq4PVQthdz20IO1vDZC0nCv6YQPKlOlGqyOINkmISzII7lN8z4bFZPZwhx4vX0GZd82U7od49Z1Yqu07eIRLh/0gnGQqFpZyvb0ub/8Mv8dFRBtzH3YfuiAYBGilsMRsU83sJNUqdw2w/qltw5xvA9447pBW3HOJs7z1vd7PNKUr+npy4zkcpe7qDyR6N6snQ== deploy@xen21-vm04
"""

root_key = """
ssh-dss AAAAB3NzaC1kc3MAAACBAKXGqtplWSVzTPrZVNq9WiDVY7RqbX6oD5J64WZ6DC+KNHEPRUPDmmWZJnkHkspphOi1p5y3pxCkCcvq7dzqzjlY016jcd980jQ5xnZ1AAs9nj1j9C2Q6amalNRfalu6bdkO5t4giCRvOSTt9aHLP1sQVsgTpDo+axn6pgFl78pRAAAAFQCTbZKBj+rTpJCxxguGY+2y7/FBTQAAAIABTfLKx/CqzKrmp5NWpExWTqdf9A2Z31HNRg8hd/8FTAuli7fxjd8HcQRXeBNAowwoTrD575O3T+7wuvSSoLL8rXHx3BB6yM0AMRTyrRjfA+dtxOjTGtCCOTLX58sUrd/d3rXfANukZQ2ELlDpNmKU430AY+5f5FPnENunbDzThwAAAIBQLF0HJvCGAWXnWH5KO5bNRl2WGYtBp213gI42aDagiJe6JjpQiVvslYJqm2gK87TLeB9jmBBNx2OapvZUNVA6FRog2qA181T6R35caysbXjiSfrnF8ancMy9q1Vw2Uh/qLYKD+YR+2+4cTbvDBB3pY9llU3gyVMSWY4quKiAG4A== root@xen21-vm04
ssh-rsa AAAAB3NzaC1yc2EAAAABIwAAAQEAzLq8vroVNHCfjBpTqA3IALq/bbGQb0Wi6o5fLKIyYOtUEofs13xJ01puTKGOlULfj0PPwWspy896tZruqT1B28Q+SE7AkYUo/0EN6WS50Zo91Sl1AtXGSMehShfJ0Kbg4JR691ahE1XOQE3pl1c9Gk23JJyYC6hE/0UHdEXa3s1tI1fhMrXDBK00novr2EiEwt0gLpbOGN8tS2g0ojjILdFZJzFSMG2XA+cMtQg8TNCvG2D/g4OLRxSLXRfJ1i6m+qwSYV28fLSD3pEaNYMidBByIFAs7C/4Zlied2ZNaNU7UDfwbWyQN2uPaWwbcW9LzLGrs0LZrvmscdPMdHnRVQ== root@xen21-vm04
"""

YHD_CFG = """
useradd -m deploy\n
mkdir /home/deploy/.ssh\n
echo \"%s\" > /home/deploy/.ssh/authorized_keys\n
mkdir /root/.ssh\n
echo \"%s\" > /root/.ssh/authorized_keys\n
sed -i \"s/^\(deploy:\)[^:]*:/\\1*:/\" /etc/shadow\n
sed -i \"s/^\(root:\)[^:]*:/\\1*:/\" /etc/shadow\n
""" % (deploy_key, root_key)


os_type = {'ubuntu': {'ifcfg_eth0': ubuntu_eth0,
                      'configure': ubuntu_configure,
                      'reboot': 'reboot\n',
                      'poweroff': 'poweroff\n',
                      'hostname': ubuntu_hostname,
                      'yhd_configure': YHD_CFG,
                      'close_23': 'chkconfig xinetd off\n'},
           'fedora': {'ifcfg_eth0': fedora_eth0,
                      'configure': fedora_configure,
                      'reboot': '/etc/init.d/network restart\n',
                      'poweroff': 'poweroff\n',
                      'hostname': fedora_hostname,
                      'yhd_configure': YHD_CFG,
                      'close_23': 'chkconfig xinetd off\n'},
           'centos': {'ifcfg_eth0': centos_eth0,
                      'configure': centos_configure,
                      'reboot': '/etc/init.d/network restart\n',
                      'hostname': centos_hostname,
                      'yhd_configure': YHD_CFG,
                      'poweroff': 'poweroff\n',
                      'close_23': 'chkconfig xinetd off\n'},
           'win7': {},
           'winxp': {}}


class TLogin(object):
    def __init__(self, host, username, password, port=23, timeout=5):
        self.tn = telnetlib.Telnet(host, port, timeout)
        self.username = username
        if not password:
            raise Exception('not input password')
        self.password = password
        self.login(username, password)

    def login(self, username, password):
        self.tn.read_until("login: ")
        self.tn.write(username + "\n")
        self.tn.read_until("Password: ")
        self.tn.write(password + "\n")

    def close(self):
        self.tn.close()

    def flush(self, cmdlist):
        for cmd in cmdlist:
            print cmd
            self.tn.write(cmd)
        self.tn.write("exit\n")
        self.tn.read_all()


class _MysqlBase(object):
    def __init__(self):
        try:
            self.conn = self._conn()
            self.cur = None
            self.set()
        except MySQLdb.Error, e:
            print str(e)

    def _conn(self):
        try:
            return MySQLdb.Connection(
                host=db_host,
                user=db_username,
                passwd=db_password,
                db=db_name,
                port=db_port)
        except MySQLdb.Error, e:
            print "XXXXXXXXX "
            print str(e)
            return None

    def set(self):
        try:
            if self.conn:
                self.cur = self.conn.cursor()
        except MySQLdb.Error, e:
            self.conn = None
            self.cur = None
            print str(e)

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
            print str(e)
            raise MySqlError(str(e))

    def _isfound(self, id):
        raise NotImplementedError('_MysqlBase _isfound Not Implemented')


class Instance(object):

    instances = "instances"
    iptable = "iptable"
    CREATE_CMD = "insert into instances (\
    instance_uuid,\
    name,\
    ip,\
    status,\
    os_type,\
    username,\
    passwd,\
    template_type,\
    instance_type,\
    iaas_type,\
    is_alloc,\
    create_time,\
    online_time,\
    off_time,\
    flag) values(\"%s\",\"%s\",\"%s\",\"%s\",\"%s\",\"%s\",\
    \"%s\",\"%s\",\"%s\",\"%s\",\"%d\",\"%s\",\"%s\",\"%s\",\"%s\")"
    TITLE = "instance-%s"
    DEFAULT_IAAS_TYPE = "vsphere"
    DEFAULT_CUSTOMERS = "1hao"
    DEFAULT_USERNAME = "test"
    DEFAULT_PASSWD = "123456"

    def __init__(self):
        self.conn = _MysqlBase()

    def found(self):
        pass

    def _get_cmd(self, instance_name, ip, ipflag, model_type="8-8-200", template_type="centos6.4"):
        instance_uuid = str(uuid.uuid1())
        name = instance_name
        ts = time.time()
        timestamp = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
        ip = ip
        status = "stop"
        username = custom_username
        passwd = custom_password
        os_type = template_type
        instance_type = model_type
        iaas_type = "vsphere"
        is_alloc = 0
        create_time = online_time = off_time = timestamp
        return self.CREATE_CMD % (instance_uuid, name,
                                  ip,
                                  status,
                                  os_type,
                                  username,
                                  passwd,
                                  template_type,
                                  instance_type,
                                  iaas_type,
                                  is_alloc,
                                  create_time,
                                  online_time,
                                  off_time,
                                  ipflag), ip

    def alloc_ip(self, ip):
        print 'alloc ip : %s' % ip
        cmd = "update %s set is_alloc=1 where ipaddress=\"%s\"" % (self.iptable, ip.strip())
        self._commit(cmd)

    def _commit(self, cmd):
        self.conn.runCommand(cmd)
        self.conn.conn.commit()

    def get_idle_ip(self, flag):
        cmd = "select ipaddress,gateway from %s where is_alloc=0 and flag=\"%s\"" % (self.iptable, flag)
        ips = self.conn.runCommand(cmd)
        if ips:
            print "ipaddress: %s" % str(ips[0][0])
            print "gateway: %s" % str(ips[0][1])
            return ips[0][0], ips[0][1]
        return None


# reconfigure host
def reconfigure(instance, name, ip, gateway, flag, ipflag):
    try:
        # set system type
        yhd_os_type = "centos"
        cmdlist = []
        system = os_type.get(yhd_os_type, None)
        if not system:
            raise Exception('ERROR: not support %s system' % yhd_os_type)

        # set reconfigure ip and poweroff command
        ifcfg_eth0 = system['ifcfg_eth0'] % (ip, gateway, custom_dns)
        configure = system['configure'] % ifcfg_eth0

        # set host name
        hostname = 'instance-%s' % ip.replace('.', '-')
        cfg = centos_hostname_cfg % hostname
        hostname_configure = system['hostname'] % cfg

        # set close Telnet command
        close_telnet = system['close_23']

        # set poweroff command
        poweroff = system['poweroff']
        print poweroff
        yhd_command = system['yhd_configure']

        cmdlist.append(configure)
        cmdlist.append(hostname_configure)
        if flag:
            cmdlist.append(yhd_command)
        cmdlist.append(close_telnet)
        cmdlist.append(poweroff)

        # login host pass Telnet
        tl = TLogin(TEMPLATE_HOST, custom_username, custom_password, timeout=20)
        instance.alloc_ip(ip)
        cmd, ip = instance._get_cmd(name, ip, ipflag)
        print cmd
        instance._commit(cmd)
        tl.flush(cmdlist)
        tl.close()
    except Exception, e:
        print str(e)


def WaitTask(task, actionName='job', hideResult=False):
    print 'Waiting for %s to complete.' % actionName

    while task.info.state == vim.TaskInfo.State.running:
        time.sleep(2)

    if task.info.state == vim.TaskInfo.State.success:
        if task.info.result is not None and not hideResult:
            out = '%s completed successfully, result: %s' % (actionName, task.info.result)
        else:
            out = '%s completed successfully.' % actionName
    else:
        out = '%s did not complete successfully: %s' % (actionName, unicode(task.info.error))
        print out
        # should be a Fault... check XXX
        raise task.info.error

    # may not always be applicable, but can't hurt.
    return task.info.result


# Get the vsphere object associated with a given text name
def get_obj(content, vimtype, name):
    obj = None
    container = content.viewManager.CreateContainerView(content.rootFolder, vimtype, True)
    for c in container.view:
        if c.name == name:
            obj = c
            break
    return obj


# Connect to vCenter server and deploy a VM from template
def clone(instance, instance_name, template_name, ip, gateway, flag, ipflag):

    try:
        si = SmartConnect(
            host=vcenter['vserver'],
            user=vcenter["username"],
            pwd=vcenter["password"],
            port=vcenter["port"])
    except IOError, e:
        sys.exit("Unable to connect to vsphere server. Error message: %s" % e)

    # add a clean up routine
    atexit.register(Disconnect, si)
    content = si.RetrieveContent()

    # get the vSphere objects associated with the human-friendly labels we supply
    datacenter = get_obj(content,
                         [vim.Datacenter],
                         default_datacenter["datacenter_name"])
    print datacenter
    # get the folder where VMs are kept for this datacenter
    destfolder = datacenter.vmFolder
    print destfolder

    # get cluster
    cluster = get_obj(
        content,
        [vim.ClusterComputeResource],
        default_datacenter['cluster_name'])
    print cluster

    # compute = get_obj(content, [vim.ComputeResource], default_datacenter["compute_resource"])
    # print type(compute)

    # use same root resource pool that my desired cluster uses
    # print compute.resourcePool
    resource_pool = cluster.resourcePool
    # resource_pool = compute.resourcePool
    datastore = get_obj(content, [vim.Datastore], default_datacenter["datastore_name"])
    template_vm = get_obj(content, [vim.VirtualMachine], template_name)

    # Relocation spec
    relospec = vim.vm.RelocateSpec()
    relospec.datastore = datastore
    relospec.pool = resource_pool

    # VM config spec
    vmconf = vim.vm.ConfigSpec()

    # Hostname settings
    ident = vim.vm.customization.LinuxPrep()
    print type(ident)
    ident.hostName = vim.vm.customization.FixedName()
    ident.hostName.name = instance_name
    print type(ident.hostName)

    # Clone spec
    clonespec = vim.vm.CloneSpec()
    clonespec.location = relospec
    clonespec.config = vmconf
    clonespec.powerOn = True
    clonespec.template = False

    # fire the clone task
    task = template_vm.Clone(
        folder=destfolder,
        name=instance_name.title(),
        spec=clonespec)
    WaitTask(task, 'VM clone task')
    time.sleep(60)

    # reconfigure host
    reconfigure(instance, instance_name, ip, gateway, flag, ipflag)


# set depoly instance policy
def set_alloc_policy(number):
    instance_pool = 0
    for num in clusters.values():
        instance_pool += num['number']

    if not instance_pool:
        return

    count = 0
    prefix_number = 0
    cluster_number = len(clusters)
    for k, v in clusters.items():
        if count < (cluster_number - 1):
            alloc_instance_number = int(round(number*(float(v['number'])/instance_pool)))
            prefix_number += alloc_instance_number
            instances_alloc_table[k] = alloc_instance_number
        else:
            instances_alloc_table[k] = (number - prefix_number)
        count += 1
    print "INSTANCES ALLOC TABLE: %s\t" % instances_alloc_table


# elect instance from datacenter
def elect(ring):
    print instances_alloc_table
    cluster = instances_alloc_table.keys()
    name = cluster[ring]
    number = instances_alloc_table.get(name)
    if number > 1:
        instances_alloc_table[name] = (number-1)
        return name
    elif number == 1:
        instances_alloc_table[name] = 0
        return name


def filter_noalloc_cluster():
    alloc_talbe = copy.copy(instances_alloc_table)
    for k, v in alloc_talbe.items():
        if v == 0:
            instances_alloc_table.pop(k)


"""
Sub Main program
"""


def main(**kwargs):
    # what VM template to use
    # set_alloc_policy(kwargs['number'])
    template_name = kwargs['template']
    yhd_flag = kwargs['yhd']
    ipflag = kwargs['flag']
    print yhd_flag
    print template_name

    # # get idle ip from db
    instance_db_handle = Instance()

    # # clone template to a new VM
    # ring_point = 0
    for i in range(0, kwargs['number']):
        # filter_noalloc_cluster()
        # if ring_point >= len(instances_alloc_table):
            # ring_point = 0

        print "START create [%d] instance..." % (i+1)
        ip, gateway = instance_db_handle.get_idle_ip(ipflag)
        if not ip:
            raise Exception("not alloc ip")
        ipname = ip.replace('.', '-')
        name = "instance-%s-%s" % (str(uuid.uuid1()), ipname)
        print 'instance-name: %s' % name
        # cluster_name = elect(ring_point)
        # print "cluster_name", cluster_name
        # if cluster_name:
            # template_name = clusters.get(cluster_name, None)['template_name']
        # print "template_name", template_name
        clone(instance_db_handle, name, template_name, ip, gateway, yhd_flag, ipflag)
        # ring_point += 1
        # time.sleep(3)

"""
 Main program
"""
if __name__ == "__main__":
    if getpass.getuser() != 'root':
        sys.exit("You must be root to run this.  Quitting.")

    # Define command line arguments
    parser = argparse.ArgumentParser(
        description='Deploy a new VM in vSphere')

    parser.add_argument(
        '--number',
        type=int,
        help='Number of CPUs',
        default=2)
    parser.add_argument(
        '--template',
        type=str,
        help='Number of CPUs',
        default='centos6.4')
    parser.add_argument(
        '--flag',
        type=str,
        help='used for promote',
        default='unfixable')

    parser.add_argument('--yhd-flag', dest='yhd', action='store_true')
    parser.add_argument('--no-yhd-flag', dest='yhd', action='store_false')
    parser.set_defaults(yhd=True)

    # Parse arguments and hand off to main()
    args = parser.parse_args()
    main(**vars(args))
