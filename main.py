#!/usr/bin/env python
#coding:utf-8

import requests
import json
import sys
reload(sys)
sys.setdefaultencoding('UTF-8')

import method.login as login


# import config info
import method.info as info
zabbix_url  = info.zabbix_url
zabbix_user = info.zabbix_user
zabbix_pass = info.zabbix_pass
graph_names = info.graph_names
group_names = info.group_names
graph_width = info.graph_width
graph_height= info.graph_height
graph_hsize = info.graph_hsize
graph_vsie  = info.graph_vsie


print '\033[1;31;40m'
print "=" * 50
print 'ZABBIX_HOST:\t',zabbix_url
print 'ZABBIX_USER:\t',zabbix_user
print 'Group_name:\t',group_names
print 'Graph_name:\t',graph_names
print 'graph_width:\t',graph_width
print 'graph_height:\t',graph_height
print 'graph_hsize:\t',graph_hsize
print 'graph_vsie:\t',graph_vsie
print "=" * 50
print '\033[0m'
print

# method import
# login and getdata method
method = login.zabbixtools(zabbix_url,zabbix_user,zabbix_pass)
authID = method.user_login()

# get  group's id.
def groupid_get(group_name):
    data = json.dumps(
            {
                "jsonrpc": "2.0",
                "method": "hostgroup.get",
                "params": {
                    "output": "groupid",
                    "filter": { "name": group_name,}
                },
                "auth": authID,"id": 1})
    try:
        res = method.get_data(data).json()['result']
    except:
        res = []
    groupids = []
    if res:
        for i in res:
            groupids.append(i['groupid'])
    return groupids


# get group's hostids.
def group_get(groupids):
    data = json.dumps(
            {
                "jsonrpc": "2.0",
                "method": "host.get",
                "params": {
                    "output":["hostid"],
                    "groupids": groupids,
                    },
                "auth": authID,
                "id": 1
            })
    res = method.get_data(data).json()['result']
    hostids = []
    for i in res:
        hostids.append(i['hostid'])
    return hostids

def graph_get(hostids,graph_name):
    data = json.dumps({
                "jsonrpc": "2.0",
                "method": "graph.get",
                "params": {
                    "output":["graphid"],
                    "hostids": hostids ,
                    "filter":{
                    "name":graph_name,
                    },},
                "auth": authID,
                "id": 1
            })
    res = method.get_data(data).json()['result']
    graphid = []
    if res:
        for i in res:
            graphid.append(i['graphid'])
    return graphid

def screenid_get(screenname):
    data = json.dumps({
            "jsonrpc": "2.0",
            "method": "screen.get",
            "params": {
                "output": "screenids",
                "filter":{
                "name": screenname
                },},
                "auth": authID,
                "id": 1
    })
    res = method.get_data(data).json()['result']
    if  res:
        return res[0]['screenid']
    else:
        return res

def screenid_del(screenid):
    data = json.dumps({
            "jsonrpc": "2.0",
            "method": "screen.delete",
            "params": [
                screenid,
                ],
                "auth": authID,
                "id": 1
    })
    res = method.get_data(data).json()['result']
    print "\033[32;40m[INFO]\033[0m Delete old screen..."
    if res:
        print "\033[32;40m[INFO]\033[0m Delete ok, waite to create new screen..."


def compute_graphid(graphid):
    compute_x  = len(graphid)/24
    compute_xy = len(graphid)%24
    if compute_xy != 0:
        compute_x += 1
    compute_list = []
    for i in range(compute_x):
        list_y = i + 1
        compute_list.append(graphid[i*24:list_y*24])
    return compute_list

def graph_listCreate(graphid):
    x = 0
    y = 0
    graph_list = []
    for graphresouce in graphid:
        graph_list.append({
            "resourcetype": "0",
            "resourceid": graphresouce,
            "width": graph_width,
            "height": graph_height,
            "x": x,
            "y": y,
            "colspan": "1",
            "rowspan": "1",
            "elements": "0",
            "valign": "0",
            "halign": "0",
            "style": "0",
            "url": "",
            "dynamic": "1"
            })
        x += 1
        if x == graph_hsize:
            x = 0
            y += 1

    return graph_list


def screenCreate(graph_list,screen_name):
    #hsize 列
    #vsie 行
    data = json.dumps(
            {
                "jsonrpc": "2.0",
                "method": "screen.create",
                "params": {
                    "name": screen_name,
                    "hsize":graph_hsize,
                    "vsize":graph_vsie,
                    "screenitems":graph_list,
                },
                "auth": authID,"id": 1})
    res = method.get_data(data).json()
    return res

if __name__ == "__main__":
    for group_name in group_names:
        for graph_name in graph_names:
            print "\033[32;40m[INFO]\033[0m Now \033[32;40m'%s'\033[0m  's \033[33;40m'%s'\033[0m start create.." %(group_name,graph_name)
            print "*" * 50
            groupids = groupid_get(group_name)
            if not groupids:
                print "\033[31;40m[ERRO]\033[0m Can not find group_id for:",group_name,". Skip..."
                print "\033[31;40m[ERRO]\033[0m Please check group_name: \033[32;40m'%s'\033[0m ..." %group_name
                print ""
                break
            hostids = group_get(groupids)
            graphid = graph_get(hostids,graph_name)
            if not graphid:
                print "\033[33;40m[WARN]\033[0m The graph_name may be wrong or this group don't have this graph_name. Skip..."
                print "\033[33;40m[WARN]\033[0m %s 's '%s' ..." %(group_name,graph_name)
                print "\033[33;40m[WARN]\033[0m Please check graph_name: \033[32;40m'%s'\033[0m  ..." %graph_name
                print ""
                break
            graphid_list = compute_graphid(graphid)
            for graph_num in range(len(graphid_list)):
                num = 1
                num += graph_num
                screenname=group_name+"_"+graph_name+"_"+str(num)
                screenid=screenid_get(screenname)
                if screenid:
                    screenid_del(screenid)
                graph_list = graph_listCreate(graphid_list[graph_num])
                x = screenCreate(graph_list,screenname)
                print "\033[32;40m[INFO]\033[0m Create new screen..."
                print "\033[32;40m[INFO]\033[0m Screen name: \033[32;40m%s\033[0m" %(group_name+"_"+graph_name+"_"+str(num))
                print "\033[32;40m[INFO]\033[0m Status Code:",x 
                print ""
