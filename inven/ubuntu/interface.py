import oauth.oauth as oauth
import httplib2
import uuid
import logging
import json
import time


class MaasInterface:
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(MaasInterface, cls).__new__(cls)
        return cls._instance

    def __init__(self, __url, __apikey):
        self.maas_url = None
        self.resource_token = None
        self.consumer_token = None

        if __url:
            self.maas_url = __url
        if __apikey:
            self.set_token(__apikey)

        self._logger = logging.getLogger(__name__)
        self._logger.setLevel(logging.DEBUG)

        return

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
        mch = self.get_machine(__hostname)
        if not mch:
            return None
        tdict = dict()

        trial = 0
        while True:
            if mch[u'status'] is 6:
                # Release the machine
                print "Start to release"
                uri = "machines/" + mch['system_id'] + "/?op=release"
                self.post(uri)
            elif mch[u'status'] is 4 and mch[u'power_state'] == 'on':
                # Turn off the machine
                uri = "machines/" + mch['system_id'] + "/?op=power_off"
                tdict['stop_mode'] = 'soft'
                self.post(uri, json.dump(tdict))
            elif mch[u'status'] is 4 and mch[u'power_state'] == u'off':
                # Deploy Machine

                self._logger.info("Start to Deploy")
                uri = "machines/" + "/?op=allocate"
                tdict['system_id'] = mch['system_id']
                self.post(uri, json.dumps(tdict))
                tdict.clear()

                print "Start to Deploy"
                uri = "machines/" + mch['system_id'] + "/?op=deploy"
                tdict['distro_series'] = __distro
                self.post(uri, json.dumps(tdict))
                tdict.clear()
                break
            if ++trial > 5:
                self._logger.error('Cannot Deploy Machine within 25 Seconds')
                return False
            time.sleep(5)
        return True

    def _distro_mapping(self, __dist):
        if "14.04" in __dist:
            return 'trusty'
        elif "14.10" in __dist:
            return 'unicorn'
        elif "15.04" in __dist:
            return 'vervet'
        elif "15.10" in __dist:
            return 'werewolf'
        elif "16.04" in __dist:
            return 'xenial'
        elif "16.10" in __dist:
            return 'yak'
        elif "17.04" in __dist:
            return 'zapus'
        else:
            return __dist

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
        print response
        return response

if __name__ == "__main__":
    apikey = "FWU2ydTZ8Hwz45wq8C:QXsxQPJSTkjraPzJYS:" \
             "rMKfWzRyg36awkBZpKqHUkuyPM33E92Q"
    maas_url = "http://116.89.190.141/MAAS/api/2.0/"
    mif = MaasInterface(maas_url, apikey)

#    response = mif.get_machine('K1-GJ1-DataHub1')
#    print response
    response = mif.deploy_machine('K1-GJ1-DataHub1')
    print response
