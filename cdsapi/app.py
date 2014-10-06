#

import logging
import os
import pecan
from paste import deploy
from wsgiref import simple_server


from cdsapi import hooks
from cdsapi import cfg
from cdsapi import config as api_config
from cdsapi import middleware


__author__ = 'hardy.Zheng'


CONF = cfg.CONF
LOG = logging.getLogger(__name__)


# Set up the pecan configuration
def get_pecan_config():
    filename = api_config.__file__.replace('.pyc', '.py')
    return pecan.configuration.conf_from_file(filename)


def setup_app(pecan_config=None):
    if not pecan_config:
        pecan_config = get_pecan_config()

    # pecan.configuration.set_config(dict(pecan_config), overwrite=True)
    # print pecan_config
    # print pecan_config.app.template_path
    # Replace DBHook with a hooks.TransactionHook
    app_hooks = [
        hooks.TasksHook(),
        hooks.IpTableHook(),
        hooks.TemplateHook(),
        hooks.InstancesHook()]

    app = pecan.make_app(
        pecan_config.app.root,
        static_root=pecan_config.app.static_root,
        template_path=pecan_config.app.template_path,
        hooks=app_hooks,
        wrap_app=middleware.ParsableErrorMiddleware,
        guess_content_type_from_ext=False
    )

    return app


class Application(object):
    def __init__(self):
        pc = get_pecan_config()
        # pc.app.debug = CONF.api.debug
        self.app = setup_app(pecan_config=pc)

    def __call__(self, environ, start_response):
        return self.app(environ, start_response)


def get_server_cls():
    """Return an appropriate WSGI server class base on provided host
    """
    return simple_server.WSGIServer


def get_handler_cls():

    cls = simple_server.WSGIRequestHandler

    class ApiCloudHandler(cls, object):
        def address_string(self):
            if int(CONF.api.enable_dns_lookup):
                return super(ApiCloudHandler, self).address_string()
            else:
                # disable reverse dns lookup, directly return ip adress
                return self.client_address[0]

    return ApiCloudHandler


# Build the WSGI app
def load_app():
    cfg_file = CONF.api.paste_config
    LOG.debug("WSGI config requested: %s" % cfg_file)
    if not os.path.exists(cfg_file):
        root = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                            '..', '..', 'etc', 'cdsapi'
                                            ))
        cfg_file = os.path.join(root, cfg_file)
    if not os.path.exists(cfg_file):
        raise Exception('paste_config.ini Not Found')

    LOG.debug("Full WSGI config used: %s" % cfg_file)
    return deploy.loadapp("config:" + cfg_file)


# Create the WSGI server and start it
def build_server():
    app = load_app()
    host, port = CONF.api.host, int(CONF.api.port)
    print host, port
    if not host or not port:
        raise Exception('Not Configure Host or Port')
    server_cls = get_server_cls()
    srv = simple_server.make_server(host, port, app,
                                    server_cls, get_handler_cls())

    LOG.info('Starting server in PID %s' % os.getpid())
    LOG.info("Configuration:")

    if host == '0.0.0.0':
        LOG.info(
            'serving on 0.0.0.0:%s, view at http://127.0.0.1:%s'
            % (port, port))
    else:
        LOG.info("serving on http://%s:%s"
                 % (host, port))
    return srv


def app_factory(global_config, **local_conf):
    return Application()
