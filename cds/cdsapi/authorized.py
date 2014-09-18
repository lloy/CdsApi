import uuid

class auth_token(object):
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        return self.app(environ, start_response)

    @classmethod
    def factory(cls, global_conf, **kwargs):
        print 'cds-vnic:', global_conf, kwargs
        return auth_token


class Resource(object):

    def __init__(self):
        self.value = 'test '
        self.resource_id = uuid.uuid1()

    def get_resource(self):
        return '%s%s' %(self.resource_id ,'zhengwei test')

def get_conn():
    return Resource()
