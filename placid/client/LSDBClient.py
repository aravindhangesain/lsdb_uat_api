from datetime import datetime
import requests
import json
import os

# This client is for allowing scripts to log in and interract with the live LSDB server
# Built into the client is the capability to interract also with a test server.
#
# To set parameters for LSDBClient, modify config.env
# DEBUG should be set either to 0 for False, or any positive integer for True
#
# Current List of Functions:
#   login(username<string>, password<string>)
#       Logs into the requested server and saves the auth token. Returns none.
#
#   generalGET(url<string>)
#       takes a predefined url as a string and calls GET. Returns the json object of the get.
#
#   generalPOST(url<string>, payload<dict>)
#       takes an url and POSTs the payload at the endpoint. Returns the resulting json object.
#
#   printJSON(jobject<dict>)
#       takes a json object and prints it to the console in a readable format. Returns none.

class LSDBClient:

    __base_headers = {
        'Accept':'application/json',
        'Content Type':'application/json; charset=utf8',
        'User-Agent':'PVEL Test Client'
    }

    users = {}
    auth_header ={}

    def __init__(self, port: str = ''):
        if int(os.environ.get('DEBUG')):
            self.__host: str = os.environ.get('DEBUGHOST')
            self.__port: str = ':' + os.environ.get('DEBUGPORT')
            self.__proto: str = os.environ.get('DEBUGPROTO')
        else:
            self.__port = port
            self.__host: str = os.environ.get('PRODHOST')
            self.__proto: str = os.environ.get('PRODPROTO')

    @property
    def base_url(self) -> str:
        return '{0}://{1}:{2}'.format(self.__proto,self.__host,self.__port)

    def login(self, username:str = '', password:str = '') -> bool:
        SERVER = self.base_url
        if int(os.environ.get('DEBUG')):
            r = requests.post(SERVER + '/api/1.0/signin/', data={'username':os.environ.get('USERNAME'),'password':os.environ.get('PASS')})
        else:
            r = requests.post(SERVER + '/api/1.0/signin/', data={'username':username,'password':password})
        token = json.loads(r.text)['token']
        self.auth_header = {'Authorization':'Token '+token}

    def generalGET(self, url):
        r = requests.get(self.base_url + '/api/1.0/' + url,
            headers = self.auth_header)
        return r.json()

    def rawGET(self, url):
        r = requests.get(self.base_url + '/api/1.0/' + url,
            headers = self.auth_header)
        return r

    def generalPOST(self, url, payload):
        #Payload is a dict premade for post.

        r = requests.post(self.base_url + url,
            data = payload,
            headers = self.auth_header)
        return r.json()

    def printJSON(self, jobject):
        if jobject:
            print(json.dumps(jobject, indent=4, sort_keys=True))

    # def tendemail(self, payload) -> dict:
    #     data = {'username':payload}
    #     r = requests.post(self.base_url + '/api/tendemail/',
    #     data = data,
    #     headers=self.auth_header)
    #     return r.json()
