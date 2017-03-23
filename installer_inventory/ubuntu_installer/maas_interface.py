import sys
import oauth.oauth as oauth
import httplib2
import uuid
import logging
import json
import time


class MaasInterface:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(MaasInterface, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        self.maas_url = None
        self.resource_token = None
        self.consumer_token = None

        self._logger = logging.getLogger("MaasInterface")
        self._logger.setLevel(logging.DEBUG)
        fm = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        ch.setFormatter(fm)
        self._logger.addHandler(ch)

    def initizilize(self, __url, __apikey):
        self.maas_url = __url
        self.set_token(__apikey)

    def set_token(self, __apikey):
        if not __apikey:
            self._logger.error("API Key for MAAS is missing in setting.yaml")
            return -1
        keys = __apikey.split(':')
        resource_tok_string = "oauth_token_secret=%s&oauth_token=%s" % \
                              (keys[2], keys[1])
        self.resource_token = oauth.OAuthToken.from_string(resource_tok_string)
        self.consumer_token = oauth.OAuthConsumer(keys[0], "")
        return

    def get(self, __uri):
        oauth_request = oauth.OAuthRequest.from_consumer_and_token \
            (self.consumer_token,
             token=self.resource_token,
             http_url=self.maas_url,
             parameters={'oauth_nonce': uuid.uuid4().hex})
        oauth_request.sign_request(oauth.OAuthSignatureMethod_PLAINTEXT(),
                                   self.consumer_token,
                                   self.resource_token)

        headers = oauth_request.to_header()
        url = "%s%s" % (self.maas_url, __uri)
        http = httplib2.Http()
        return http.request(url, "GET", headers=headers, body=None)

    def get_machine(self, __hostname):
        _response, content = self.get_machines()
        if _response["status"] != "200":
            self._logger.error("HTTP Error: " + _response["reason"] + "Code: "
                               + _response["status"])
            return None

        t = json.loads(content)
        for m in t:
            if m["hostname"] == __hostname:
                return m

        self._logger.error("Machine " + __hostname + " can't be found in MAAS")
        return None

    def deploy_machine(self, __hostname, __distro='xenial'):
        tdict = dict()
        trial = 0
        while True:
            mch = self.get_machine(__hostname)
            if not mch:
                return None

            if mch[u'status'] is 6:
                # Deployed State
                self._logger.info("Release the machine "+__hostname)
                uri = "machines/" + mch['system_id'] + "/?op=release"
                self.post(uri)
            elif mch[u'status'] is 4 and mch[u'power_state'] == 'on':
                # Ready State / Power On
                self._logger.info("Turn off the machine " + __hostname)
                uri = "machines/" + mch['system_id'] + "/?op=power_off"
                tdict[u'stop\_mode'] = u'soft'
                self.post(uri, json.dump(tdict))
            elif mch[u'status'] is 4 and mch[u'power_state'] == u'off':
                # Ready State / Power Off
                self._logger.info("Allocate the machine "+__hostname)
                uri = "machines/" + "/?op=allocate"
                tdict[u'system_id'] = mch['system_id']
                self.post(uri, json.dumps(tdict))
                tdict.clear()
	    elif mch[u'status'] is 10 and mch[u'power_state'] == u'off':
                # Allocated State / Power Off
                self._logger.info("Deploy the machine "+__hostname)
                uri = "machines/" + mch['system_id'] + "/?op=deploy"
                tdict[u'distro_series'] = __distro
                self.post(uri, json.dumps(tdict))
                tdict.clear()
            elif mch[u'status'] is 9:
                # Deploying State
                self._logger.info("Deploying the machine " + __hostname)
                break
            if ++trial > 10:
                self._logger.error('Cannot Deploy Machine within 50 Seconds')
                return False
            time.sleep(5)
        return True

    def get_machines(self):
        return self.get("machines/")

    def get_nic(self, __hostname):
        pass

    def set_ipaddr(self):
        pass

    def post(self, __uri, __msg=None):
        oauth_request = oauth.OAuthRequest.from_consumer_and_token\
            (self.consumer_token,
             token=self.resource_token,
             http_url=self.maas_url,
             parameters={'oauth_nonce': uuid.uuid4().hex})
        oauth_request.sign_request(oauth.OAuthSignatureMethod_PLAINTEXT(),
                                   self.consumer_token,
                                   self.resource_token)

        headers = oauth_request.to_header()
        url = "%s%s" % (self.maas_url, __uri)
        http = httplib2.Http()

        if __msg:
            body = json.dumps(__msg)
        else:
            body = None
        response = http.request(url, "POST", headers=headers, body=body)
        #print response
        return response

def main():
    target_machine = None

    if len(sys.argv) is 4:
        target_machine = sys.argv[1]
        maas_url = sys.argv[2]
        apikey = sys.argv[3]
    elif len(sys.argv) is 2:
        target_machine = sys.argv[1]
        apikey = "FWU2ydTZ8Hwz45wq8C:QXsxQPJSTkjraPzJYS:rMKfWzRyg36awkBZpKqHUkuyPM33E92Q"
        maas_url = "http://210.125.84.235/MAAS/api/2.0/"
    else:
        print "Usage: ./maas_interface.py <Hostname> <MAAS_URL> <MAAS_APIKEY>"
        exit(-1)

    mif = MaasInterface()
    mif.initizilize(maas_url, apikey)
    print "(maas_interface.py): Start to install Ubuntu on "+target_machine
    #response = mif.get_machines()
    #print response
    response = mif.deploy_machine(target_machine)
    #print response

if __name__ == "__main__":
    main()
