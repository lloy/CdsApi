#!/usr/bin/env python
# -*- coding: utf-8 -*-
#

"""Command line tool for creating meter for cds.
"""
from cdsapi import app
from cdsapi import service


def api(config_file):
    service.prepare_service(config_file)
    srv = app.build_server()
    srv.serve_forever()
