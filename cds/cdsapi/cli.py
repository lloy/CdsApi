#!/usr/bin/env python
# -*- coding: utf-8 -*-
#

"""Command line tool for creating meter for cds.
"""
from cdsapi import app
from cdsapi import service


def api():
    service.prepare_service()
    srv = app.build_server()
    srv.serve_forever()
