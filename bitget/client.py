import requests
import json
from . import consts as c, utils, exceptions


class Client(object):

    def __init__(self, api_key, api_secret_key, passphrase, use_server_time=False, first=False,is_demo=False):

        self.API_KEY = api_key
        self.API_SECRET_KEY = api_secret_key
        self.PASSPHRASE = passphrase
        self.use_server_time = use_server_time
        self.first = first
        self.is_demo=is_demo

    def _request(self, method, request_path, params, cursor=False):
        if method == c.GET:
            request_path = request_path + utils.parse_params_to_str(params)
        # url
        url = c.API_URL + request_path

        # 获取本地时间
        timestamp = utils.get_timestamp()

        # sign & header
        if self.use_server_time:
            # 获取服务器时间接口
            timestamp = self._get_timestamp()

        body = json.dumps(params) if method == c.POST else ""
        sign = utils.sign(utils.pre_hash(timestamp, method, request_path, str(body)), self.API_SECRET_KEY)
        if c.SIGN_TYPE == c.RSA:
            sign = utils.signByRSA(utils.pre_hash(timestamp, method, request_path, str(body)), self.API_SECRET_KEY)
        header = utils.get_header(self.API_KEY, sign, timestamp, self.PASSPHRASE)
        
        if self.is_demo:
            header["paptrading"] = "1"
        
        if self.first:
            print("url:", url)
            print("method:", method)
            print("body:", body)
            print("headers:", header)
            # print("sign:", sign)
            self.first = False




        # send request
        response = None
        if method == c.GET:
            response = requests.get(url, headers=header)
            print("response : ",response.text)
        elif method == c.POST:
            response = requests.post(url, data=body, headers=header)
            print("response : ",response.text)
            #response = requests.post(url, json=body, headers=header)
        elif method == c.DELETE:
            response = requests.delete(url, headers=header)

        print("status:", response.status_code)
        # exception handle
        if not str(response.status_code).startswith('2'):
            raise exceptions.BitgetAPIException(response)
        try:
            res_header = response.headers
            if cursor:
                r = dict()
                try:
                    r['before'] = res_header['OK-BEFORE']
                    r['after'] = res_header['OK-AFTER']
                except:
                    pass
                return response.json(), r
            else:
                return response.json()

        except ValueError:
            raise exceptions.BitgetRequestException('Invalid Response: %s' % response.text)

    def _request_without_params(self, method, request_path):
        return self._request(method, request_path, {})

    def _request_with_params(self, method, request_path, params, cursor=False):
        return self._request(method, request_path, params, cursor)

    def _get_timestamp(self):
        url = c.API_URL + c.SERVER_TIMESTAMP_URL
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()['timestamp']
        else:
            return ""
