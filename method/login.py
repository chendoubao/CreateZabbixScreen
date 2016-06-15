#!/usr/bin/env python
#coding:utf-8

import requests
import json
import sys
reload(sys)
sys.setdefaultencoding('UTF-8')

#class zabbixtools(zabbix_url,zabbix_user,zabbix_pass):
class zabbixtools:
    def __init__(self,zabbix_url,zabbix_user,zabbix_pass):
        self.url = zabbix_url
        self.user = zabbix_user
        self.passwd = zabbix_pass
        self.header = {"Content-Type": "application/json"}
        self.authID = self.user_login()
    def user_login(self):
        data = json.dumps(
                {
                    "jsonrpc": "2.0",
                    "method": "user.login",
                    "params": {
                        "user": self.user,
                        "password": self.passwd
                        },
                    "id": 0
                })
        try:
            response = requests.post(self.url,headers=self.header,data=data)
        except requests.exceptions.InvalidSchema:
            print "URL ERRO,请确定URL路径的正确性-初始化"
        else:
            try:
                authID = response.json()['result']
            except KeyError:
                print "check the username or password!"
            else:
                return authID
    def get_data(self,data):
#        global authID
#        authID = self.authID
        try:
            response = requests.post(self.url,headers=self.header,data=data)
        except requests.exceptions.InvalidSchema:
            print "URL ERRO,请确定URL路径的正确性-getdata"
        else:
            return response

