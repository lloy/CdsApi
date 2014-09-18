
import ConfigParser
import os

from cdsapi import exc

__author__ = 'Hardy.zheng'


_configure_file = '/etc/cds/cdsapi.cfg'

_DEFAULT_CONFIG = {
    'api': {
        'host': '0.0.0.0',
        'port': 5022,
        'debug': True,
        'paste_config': '/etc/cdsapi/api_paste.ini'},
    'log': {
        'handler': 'console, rotating',
        'path': '/var/log/cds/cdsapi.log',
        'max_bytes': '1*1024*1024',
        'back_count': 5,
        'level': '1'},
    }


class Section(object):

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

    def update(self, k, v):
        setattr(self, k, v)


class ApiSection(Section):

    name = 'api'

    def __init__(self):
        kw = _DEFAULT_CONFIG.get(self.name)
        super(ApiSection, self).__init__(**kw)


class LogSection(Section):

    name = 'log'

    def __init__(self):
        kw = _DEFAULT_CONFIG.get(self.name)
        super(LogSection, self).__init__(**kw)


class Factory():
    def get_section(self, name):
        sections = {
            'api': lambda: ApiSection(),
            'log': lambda: LogSection()}
        return sections[name]()


class Config():

    f = Factory()

    def __init__(self):
        keys = _DEFAULT_CONFIG.keys()
        for k in keys:
            setattr(self, k, Config.f.get_section(k))

    def _is_exists(self, config_file):
        if not os.path.exists(config_file):
            return False
        else:
            return True

    def __call__(self, config_file):
        try:
            if not self._is_exists(config_file):
                raise exc.NotFoundConfigureFile('Not Found config file')
            conf = ConfigParser.ConfigParser()
            conf.read(config_file)
            for k in conf.sections():
                p = getattr(self, k, None)
                if not p:
                    setattr(self, k, Config.f.get_section(k))
                options = conf.options(k)
                for option in options:
                    p.update(option, conf.get(k, option))
        except Exception, e:
            raise e


def reload_config():
    Config(_configure_file)

CONF = Config()
