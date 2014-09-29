import getpass
import telnetlib
from optparse import OptionParser


__author__ = 'Hardy.zheng'
__email__ = 'wei.zheng@yun-idc.com'


parse = OptionParser()
parse.add_option('-r',
                 '--remote',
                 type='string',
                 dest='host',
                 help="remote host ipaddress")
parse.add_option('-l',
                 '--user',
                 type='string',
                 dest='username',
                 help="remote host username")
parse.add_option('-a',
                 '--address',
                 type='string',
                 dest='ipaddress',
                 help="set remote host ipaddress")

parse.add_option('-t',
                 '--os_type',
                 type='string',
                 dest='os_type',
                 help="remote host system type, support as follow:\
                       [ubuntu,fedora]")

dns = "172.16.0.1"
gateway = '172.16.0.254'


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


os_type = {'ubuntu': {'ifcfg_eth0': ubuntu_eth0,
                      'configure': ubuntu_configure,
                      # 'reboot': '/etc/init.d/networking restart\n'},
                      'reboot': 'reboot\n'},
           'fedora': {'ifcfg_eth0': fedora_eth0,
                      'configure': fedora_configure,
                      'reboot': '/etc/init.d/network restart\n'},
           'centos': {},
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


def get_macaddr():
    pass


def main():
    cmdlist = []
    (options, args) = parse.parse_args()
    if not options.host or \
            not options.username or \
            not options.ipaddress or \
            not options.os_type:
        parse.error('not configure host or username, please cds-telnet --help')

    system = os_type.get(options.os_type, None)
    if not system:
        raise Exception('ERROR: not support %s system' % options.os_type)

    ifcfg_eth0 = system['ifcfg_eth0'] % (options.ipaddress, dns, gateway)

    configure = system['configure'] % ifcfg_eth0
    cmd = system['reboot']
    print configure
    cmdlist.append(configure)
    cmdlist.append(cmd)

    password = getpass.getpass()

    tl = TLogin(options.host, options.username, password, timeout=20)
    tl.flush(cmdlist)
    tl.close()


if __name__ == '__main__':
    main()
