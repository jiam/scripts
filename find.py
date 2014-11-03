import json
Ifs = ['Ten-GigabitEthernet1/3/0/1','Ten-GigabitEthernet2/3/0/1','Ten-GigabitEthernet1/4/0/1','Ten-GigabitEthernet2/4/0/1','Ten-GigabitEthernet1/4/0/21','Ten-GigabitEthernet2/4/0/21','Ten-GigabitEthernet1/3/0/2','Ten-GigabitEthernet2/3/0/2']
f = open('snmp_port.txt')
content = f.read()
d = json.loads(content)
D = {}
for If in Ifs:
    D[If] = d['10.10.0.1'][If]
print D
f.close()
