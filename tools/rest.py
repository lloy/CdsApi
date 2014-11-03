__author__ = 'Hardy.zheng'
__email__ = "wei.zheng@yun-idc.com"

import httplib
import json

# default host ip
REST_SERVER = "api"
REST_SERVER_PORT = 80


class RestException(Exception):
    pass


class RestRequest(object):
    def __init__(self, host=None, port=None):
        self.host = host
        self.port = port

        if not host:
            f = None
            try:
                f = open("rest_server.conf")
                host_ip = f.readline()
            except Exception, e:
                print e
                raise RestException("Error to get rest host ip from configure file")
            finally:
                f.close()

            if host_ip:
                self.host = host_ip
            else:
                self.host = REST_SERVER
        if not port:
            self.port = REST_SERVER_PORT

    def _build_header(self):
        headers = {"Content-Type": "application/json",
                   "Accept-Encoding": "gzip;q=1.0, identity; q=0.5",
                   "Accept": "application/json"}
        return headers

    def _send_request(self, uri, method, body, token):
        if not uri:
            raise RestException("uri is required!")

        conn = None
        try:
            print self.host, self.port
            conn = httplib.HTTPConnection(self.host, self.port)
            headers = self._build_header()
            if token:
                headers["Cookie"] = token
            conn.request(method, uri, body, headers)
            response = conn.getresponse()
            status = response.status
            result = response.read()
        except Exception, e:
            print "Exception: %s" % e
            raise e
        finally:
            if conn:
                conn.close()
        return (status, result)

    def login(self, username=None, password=None):
        uri = "/authenticate/"
        d = {"user": "/root/root",
             "password": "opzooncloud"}
        if username:
            d["user"] = username
        if password:
            d["password"] = password
        print "login: %s" % d
        body = json.dumps(d)
        conn = None
        try:
            print self.host, self.port
            conn = httplib.HTTPConnection(self.host, self.port)
            conn.request("POST", uri, body, self._build_header())
            response = conn.getresponse()
            token = response.getheader("Set-Cookie")
            print "token: %s" % token
        except Exception, e:
            print "Exception: %s" % e
            raise e
        finally:
            if conn:
                conn.close()
        return token

    def get(self, uri, body=None, token=None):
        return self._send_request(uri, "GET", body, token)

    def post(self, uri, body, token):
        return self._send_request(uri, "POST", body, token)

    def put(self, uri, body, token):
        return self._send_request(uri, "PUT", body, token)

    def delete(self, uri, body, token):
        return self._send_request(uri, "DELETE", body, token)


if __name__ == "__main__":
    rest = RestRequest("101.251.194.66", 5022)
    status, result = rest.get("/instances/", None)
    # print (status, result)
    for i in json.loads(result):
        print i
    # for i in result:
        # print str(i)
    # print json.loads(result)
