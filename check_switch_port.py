#!/usr/bin/python
from pysnmp.entity.rfc3413.oneliner import cmdgen
import multiprocessing
import hosts
import os
import json

ifNameOid = (1,3,6,1,2,1,31,1,1,1, 1)
ifStatusOid = (1,3,6,1,2,1, 2,2,1,8)
ifAliasOid = (1,3,6,1,2,1,31,1,1,1,18)
Community = hosts.hosts()
num = 1

def snmp_get(snmpTarget, snmpCommunity):

    cmdGen = cmdgen.CommandGenerator()
    errorIndication, errorStatus, errorIndex, varBinds = cmdGen.getCmd(
        cmdgen.CommunityData(snmpCommunity),
        cmdgen.UdpTransportTarget((snmpTarget, 161)),
        cmdgen.MibVariable('SNMPv2-MIB', 'sysName', 0),
        timeout = 40,
   )

    if errorIndication:
        print(errorIndication)
    else:
        if errorStatus:
            print('%s at %s' % (
                errorStatus.prettyPrint(),
                errorIndex and varBinds[int(errorIndex)-1] or '?'
                )
            )
        else:
            for name, val in varBinds:
                hostname = val.prettyPrint()
    return hostname


def snmp_walk(snmpTarget, snmpCommunity, plainOID):
    L = []
    errorIndication, errorStatus, \
        errorIndex, varBindTable = cmdgen.CommandGenerator().nextCmd(
        cmdgen.CommunityData('test-agent', snmpCommunity),
        cmdgen.UdpTransportTarget((snmpTarget, 161)),
        plainOID,
        timeout = 40,
        )

    if errorIndication:
        print errorIndication
    else:
        if errorStatus:
            print '%s at %s\n' % (
            errorStatus.prettyPrint(),
            errorIndex and varBindTable[-1][int(errorIndex)-1] or '?'
            )
        else:
            for varBindTableRow in varBindTable:
                for name, val in varBindTableRow:
                    name = name.prettyPrint()
                    val = val.prettyPrint()
                #print '%s = %s' % (name.prettyPrint(), val.prettyPrint())
                    L.append(val)
    return L 
            
#snmp_walk('127.0.0.1','public_kingsoft',ifStatusOid)            

def fetch(snmpTarget,snmpCommunity):
        ifName = snmp_walk(snmpTarget,snmpCommunity,ifNameOid)
        ifStatus = snmp_walk(snmpTarget,snmpCommunity,ifStatusOid)
        ifAlias = snmp_walk(snmpTarget,snmpCommunity,ifAliasOid)
        if len(ifName) == len(ifStatus):
            D_status = dict(zip(ifName,ifStatus))
            S_status = json.dumps(D_status)
            if S_status:
                f_status = open('./port_status/'+snmpTarget,'w')
                f_status.write(S_status)
                f_status.close()

        if len(ifName) == len(ifAlias):
            D_alias = dict(zip(ifName,ifAlias))
            S_alias = json.dumps(D_alias)
            if S_alias:
                f_alias = open('./port_alias/'+snmpTarget,'w')
                f_alias.write(S_alias)
                f_alias.close()

            
def store(Community,num):
    while len(Community) != 0:
        jobs = []
        for i in xrange(num):
            if len(Community) != 0:
                snmpTarget,snmpCommunity = Community.popitem()
                print snmpTarget
                t = multiprocessing.Process(target=fetch,args=(snmpTarget,snmpCommunity))
                jobs.append(t)
        for t in jobs:
            t.start()

#store(Community,num)

def load():
    ip_status_dict = {}
    ip_alias_dict = {}
    for file_status in os.listdir('./port_status'):
        f_status = open('./port_status/'+file_status,'r')
        content_status = f_status.read()
        try:
            status_dict = json.loads(content_status)
        except Exception:
            print file_status
        snmpTarget = file_status
	ip_status_dict[file_status] = status_dict
    for file_alias in os.listdir('./port_alias'):
        f_alias = open('./port_alias/'+file_alias,'r')
        content_alias = f_alias.read()
        try:
            alias_dict = json.loads(content_alias)
        except Exception:
            print file_alias
        snmpTarget = file_alias
        ip_alias_dict[file_alias] = alias_dict
    
    return (ip_status_dict,ip_alias_dict)
def send_alert(snmpTarget,snmpCommunity):
    hostname = snmp_get(snmpTarget,snmpCommunity)
    ip_status_dict,ip_alias_dict = load()
    status_dict = ip_status_dict[snmpTarget]
    alias_dict = ip_alias_dict[snmpTarget]
    ifName = snmp_walk(snmpTarget,snmpCommunity,ifNameOid)
    ifStatus = snmp_walk(snmpTarget,snmpCommunity,ifStatusOid)
    if len(ifName) == len(ifStatus):
        D = dict(zip(ifName,ifStatus))
        for key in  D.keys():
            if status_dict[key] != D[key] and D[key] == 2:
                if 'CORE' in hostname: 
                    evt="%s %s is down" % (snmpTarget,key)
                    send_event.send_event(ip[0],"check_port_status",evt,3,"/Net/Status")
                    print evt
                if 'uplink' in alias_dict[key]:
                    evt="%s %s is down" % (snmpTarget,key)
                    send_event.send_event(ip[0],"check_port_status",evt,3,"/Net/Status")
                    print evt
    else:
        print '%s snmp collect failed' % (snmpTarget)
        

    
        
        
def check(Community,num):
    while len(Community) != 0:
        jobs = []
        for i in xrange(num):
            if len(Community) != 0:
                snmpTarget,snmpCommunity = Community.popitem()
                t = multiprocessing.Process(target=send_alert,args=(snmpTarget,snmpCommunity))
                jobs.append(t)
        for t in jobs:
            t.start()
check(Community,num)   
#store(Community,num)   

