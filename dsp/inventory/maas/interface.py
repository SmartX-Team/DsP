import oauth.oauth as oauth
import httplib2
import uuid
import logging
import json
import time
from dsp.inventory import inven_exceptions


class MaasInterface:
    # For singleton design
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(MaasInterface, cls).__new__(cls)
        return cls._instance

    def __init__(self, maas_ip, apikey):
        self._maas_url = None
        self._resource_token = None
        self._consumer_token = None
        self._logger = None

        self.initialize(maas_ip, apikey)

    def initialize(self, maas_ip, apikey):
        self._logger = logging.getLogger(self.__class__.__name__)
        self._maas_url = "http://{}/MAAS/api/2.0/".format(maas_ip)
        self._set_maas_token(apikey)

    def _set_maas_token(self, _apikey):
        if not _apikey:
            raise inven_exceptions.NotExistRequiredParameterException("MAAS", "apikey",
                                                                      "API Key for MAAS is missing in setting.yaml")
        keys = _apikey.split(':')
        resource_tok_string = "oauth_token_secret=%s&oauth_token=%s" % (keys[2], keys[1])
        self._resource_token = oauth.OAuthToken.from_string(resource_tok_string)
        self._consumer_token = oauth.OAuthConsumer(keys[0], "")

    def deploy_machine_by(self, _hostname, _distro='xenial'):
        target_machine = self.get_machine_by(_hostname)
        if not target_machine:
            return None
        post_body = dict()

        trial = 0
        while True:
            if target_machine[u'status'] is 6:
                # Release the machine
                self._logger.info("Start to release")
                uri = "machines/" + target_machine['system_id'] + "/?op=release"
                self._http_post(uri)

            elif target_machine[u'status'] is 4 and target_machine[u'power_state'] == 'on':
                # Turn off the machine
                uri = "machines/" + target_machine['system_id'] + "/?op=power_off"
                post_body['stop_mode'] = 'soft'
                self._http_post(uri, json.dump(post_body))

            elif target_machine[u'status'] is 4 and target_machine[u'power_state'] == u'off':
                # Allocate Machine
                self._logger.info("Allocate the machine " + _hostname)
                uri = "machines/" + "/?op=allocate"
                post_body['system_id'] = target_machine['system_id']
                self._http_post(uri, json.dumps(post_body))
                post_body.clear()

                # Deploy Machine
                self._logger.info("Start to deploy the machine " + _hostname)
                uri = "machines/" + target_machine['system_id'] + "/?op=deploy"
                post_body['distro_series'] = _distro
                self._http_post(uri, json.dumps(post_body))
                break

            if ++trial > 10:
                self._logger.error('Cannot Deploy Machine within 50 Seconds')
                return False
            time.sleep(5)
        return True

    def get_machine_by(self, _hostname):
        _response, content = self._http_get("machines/")
        if _response["status"] != "200":
            self._logger.error("HTTP Error: " + _response["reason"] + "Code: "
                               + _response["status"])
            return None

        machines = json.loads(content)
        for machine in machines:
            if machine["hostname"] == _hostname:
                return machine
        self._logger.error("Machine " + _hostname + " can't be found in MAAS")
        return None

    def _http_get(self, _uri):
        oauth_request = oauth.OAuthRequest.from_consumer_and_token \
            (self._consumer_token,
             token=self._resource_token,
             http_url=self._maas_url,
             parameters={'oauth_nonce': uuid.uuid4().hex})
        oauth_request.sign_request(oauth.OAuthSignatureMethod_PLAINTEXT(),
                                   self._consumer_token,
                                   self._resource_token)

        headers = oauth_request.to_header()
        url = "%s%s" % (self._maas_url, _uri)
        http = httplib2.Http()
        return http.request(url, "GET", headers=headers, body=None)

    def _http_post(self, _uri, _body=None):
        oauth_request = oauth.OAuthRequest.from_consumer_and_token\
            (self._consumer_token,
             token=self._resource_token,
             http_url=self._maas_url,
             parameters={'oauth_nonce': uuid.uuid4().hex})
        oauth_request.sign_request(oauth.OAuthSignatureMethod_PLAINTEXT(),
                                   self._consumer_token,
                                   self._resource_token)

        headers = oauth_request.to_header()
        url = "%s%s" % (self._maas_url, _uri)
        http = httplib2.Http()

        if _body:
            body = json.dumps(_body)
        else:
            body = None
        response = http.request(url, "POST", headers=headers, body=body)
        self._logger.debug(response)
        return response

if __name__ == "__main__":
    mif = MaasInterface("setting.yaml")
#    response = mif.get_machine('K1-GJ1-DataHub1')
#    print response
    response = mif.deploy_machine_by('K1-GJ1-DataHub1')
    print response
