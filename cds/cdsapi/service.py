#!/usr/bin/env python
#
# Author: hardy.Zheng <wei.zheng@yun-idc.com>
#

from cdsapi import cfg
from cdsapi import exc
from cdsapi.log import Logger


def set_log(name):
    log_handlers = [h.strip() for h in cfg.CONF.log.handler.split(',')]
    logger = Logger(name,
                    cfg.CONF.log.level,
                    cfg.CONF.log.path,
                    log_handlers,
                    cfg.CONF.log.max_bytes,
                    cfg.CONF.log.back_count)
    return logger.setup()


def set_configure(filename):
    try:
        cfg._configure_file = filename
        cfg.CONF(filename)
    except exc.ConfigureException, e:
        raise exc.ConfigureException(e.msg)


def prepare_service(filename):
    set_configure(filename)
    set_log('cdsapi')
