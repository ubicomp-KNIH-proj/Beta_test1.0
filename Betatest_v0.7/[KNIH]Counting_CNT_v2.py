import requests
import json

IoT_1 = "http://114.71.220.59:7579"

def countCIN(serverName, aeName, today):
    cra = '&cra=' + today + 'T000000'
    crb = '&crb=' + today + 'T235959'
    
    url1 = IoT_1 + "/Mobius/" + aeName + "/mobile?fu=1&ty=4&rcn=4" + cra + crb
    url2 = IoT_1 + "/Mobius/" + aeName + "/watch?fu=1&ty=4&rcn=4"  + cra + crb
    payload={}
    headers = {
      'Accept': 'application/json',
      'X-M2M-RI': '12345',
      'X-M2M-Origin': 'ubicomp_super'
    }
    try:
        response1 = requests.request("GET", url1, headers=headers, data=payload)
        response2 = requests.request("GET", url2, headers=headers, data=payload)
        data1 = json.loads(response1.text)
        data2 = json.loads(response2.text)
        total = len(data1['m2m:uril'])
        total = total + len(data2['m2m:uril'])
        return total

    except:
        # print("mobile: ", response1)
        # print("watch: ", response2)
        return None

def getCountDict(today):
    dict_CIN = {}

    for i in range(600, 1000):
        aeName = 'S' + str(i)
        cnt = countCIN('IoT_1', aeName, today)
        if cnt == None:
            continue
        else:
            dict_CIN[aeName] = cnt
    
    return dict_CIN


dic = getCountDict('20220707')
print(dic)