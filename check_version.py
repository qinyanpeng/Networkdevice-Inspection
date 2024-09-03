###
###网络设备版本检查，基线版本（阈值）在config.py中devices['base_version']配置
###

#基础模块
import os, time, random
import datetime
import re
import requests
import config
import base64 
import pandas as pd
from icontrol.session import iControlRESTSession
from datetime import timedelta
from multiprocessing import Pool
from f5.bigip import ManagementRoot

#以下设备巡检模块
from device.h3cSw5560Netmiko import H3cS5560ei
from device.h3cS7503Netmiko import H3cS7503e
from device.h3cSr6604Netmiko import H3cSr6604
from device.h3cS6800Netmiko import H3cS6800
from device.h3cS12506SNetmiko import h3cS12506S
from device.h3cS12500SNetmiko import h3cS12500S
from device.h3cS10500Netmiko import h3cS10500
from device.h3cMSR56Netmiko import h3cMSR56
from device.h3cF1070Netmiko import h3cF1070
from device.F5 import F5
from device.F5VE import F5VE
from device.huaweiFw9560Netmiko import huaweiFw9560
from device.huaweiAR6300Netmiko import huaweiAR6300
from device.huaweiUSG6300ENetmiko import huaweiUSG6300E
from device.huaweiCE6881Netmiko import huaweiCE6881
from device.huaweiCE16804Netmiko import huaweiCE16804
from device.ciscoN5kNetmiko import ciscoN5k
from device.ciscoN7kNetmiko import ciscoN7k
from device.ciscoASR1000Netmiko import ciscoASR1000
from device.cisco4431Netmiko import cisco4431
from device.ciscoASA5585Netmiko import ciscoASA5585 
from device.hillstoneSG6000Netmiko import hillstoneSG6000
from device.sangforNetmiko import sangfor
from device.ruijieS5750CNetmiko import ruijieS5750C
from device.ruijieS6120Netmiko import ruijieS6120
from device.ruijieS7808CNetmiko import ruijieS7808C
from device.ruijieRSR50X84Netmiko import ruijieRSR50X84
from device.fortigate301Netmiko import fortigate301
from device.ABTNetmiko import ABT
from device.DPADX3000TSGSNetmiko import DPADX3000TSGS
from device.ZCTTNetmiko import ZCTT
from device.radwareNetmiko import radware
from device.riverbedNetmiko import riverbed
from device.ZDNSNetmiko import ZDNS
from sendemail import sendemail


def get_region(name):
    if '-' in name:
        li=name.split('-')
    elif '_' in name:
        li=name.split('_')
    else:
        li=None
    return {'region1':config.region1[li[0]],'region2':config.region2[li[2]]}

def check_baseversion(is_conn,item):
    re="未知"
    try:
        if not is_conn: 
            re = '未取到值'
        elif item['value']=='none':
            re = '未取到值'
        elif item['value']=='-':
            re = '未巡检'
        elif item['state']:
            re = '符合基线'
        else:
            re = '不符合基线'
    except Exception as e:
        print(item,e)
    return re
    
    

def get_inspection_result(device,conn):
    key=device['key']
    ip=device['ip']
    name=device['name']
    check=device['check']
    region=get_region(name)
    region1=region['region1']
    region2=region['region2']
    version={'state':False,'value':'-'}
    is_ok='未知'
    is_connect=False

    if check['version']:
        try:
            version=conn.version()
        except:
            version['state']=False

    if conn.is_alive:
        is_connect=True
            
    else:
        print('【unconnect】',ip)
        is_connect=False
    is_ok=check_baseversion(is_connect,version)
    result={
        "name":name,
        "ip":ip,
        "region1":region1,
        "region2":region2,
        "model":device['key'],
        "baseversion":device['base_version'],
        "version":version['value'],
        "is_version":version['state'],
        "is_connect":is_connect,
        "is_baseversion":is_ok,
        }
    return result

def check(device):
    authtype=device['authtype']
    passwd=config.authtypes[authtype]['password']
    user=config.authtypes[authtype]['username']
    key=device['key']
    ip=device['ip']
    name=device['name']
    inspection_result=list()
    sleeptime=5

    if key=='h3cS5560':
        for i in range(1,4):
            conn=H3cS5560ei(ip,user,passwd)
            if conn.is_alive:
                break
            else:
                print(ip+'第'+str(i)+'次连接失败。',conn)
            time.sleep(sleeptime)
        inspection_result=get_inspection_result(device,conn)
    if key=='h3cS7503':
        for i in range(1,4):
            conn=H3cS7503e(ip,user,passwd)
            if conn.is_alive:
                break
            else:
                print(ip+'第'+str(i)+'次连接失败。',conn)
            time.sleep(sleeptime)
        inspection_result=get_inspection_result(device,conn)

    if key=='F5':
        conn=F5(ip,user,passwd)
        inspection_result=get_inspection_result(device,conn)

    if key=='F5VE':
        conn=F5VE(ip,user,passwd)
        inspection_result=get_inspection_result(device,conn)

    if key=='h3cSR6604':
        for i in range(1,4):
            conn=H3cSr6604(ip,user,passwd)
            if conn.is_alive:
                break
            else:
                print(ip+'第'+str(i)+'次连接失败。',conn)
            time.sleep(sleeptime)
        inspection_result=get_inspection_result(device,conn)

    if key=='h3cS6800':
        for i in range(1,4):
            conn=H3cS6800(ip,user,passwd)
            if conn.is_alive:
                break
            else:
                print(ip+'第'+str(i)+'次连接失败。',conn)
            time.sleep(sleeptime)
        inspection_result=get_inspection_result(device,conn)

    if key=='huaweiFw9560':
        for i in range(1,4):
            conn=huaweiFw9560(ip,user,passwd)
            if conn.is_alive:
                break
            else:
                print(ip+'第'+str(i)+'次连接失败。',conn)
            time.sleep(sleeptime)
        inspection_result=get_inspection_result(device,conn)

    if key=='huaweiAR6300':
        for i in range(1,4):
            conn=huaweiAR6300(ip,user,passwd)
            if conn.is_alive:
                break
            else:
                print(ip+'第'+str(i)+'次连接失败。',conn)
            time.sleep(sleeptime)
        inspection_result=get_inspection_result(device,conn)

    if key=='huaweiUSG6300E':
        for i in range(1,4):
            conn=huaweiUSG6300E(ip,user,passwd)
            if conn.is_alive:
                break
            else:
                print(ip+'第'+str(i)+'次连接失败。',conn)
            time.sleep(sleeptime)
        inspection_result=get_inspection_result(device,conn)


    if key=='huaweiCE6881':
        for i in range(1,4):
            conn=huaweiCE6881(ip,user,passwd)
            if conn.is_alive:
                break
            else:
                print(ip+'第'+str(i)+'次连接失败。',conn)
            time.sleep(sleeptime)
        inspection_result=get_inspection_result(device,conn)

    if key=='huaweiCE16804':
        for i in range(1,4):
            conn=huaweiCE16804(ip,user,passwd)
            if conn.is_alive:
                break
            else:
                print(ip+'第'+str(i)+'次连接失败。',conn)
            time.sleep(sleeptime)
        inspection_result=get_inspection_result(device,conn)

    if key=='ciscoN5k':
        for i in range(1,4):
            conn=ciscoN5k(ip,user,passwd)
            if conn.is_alive:
                break
            else:
                print(ip+'第'+str(i)+'次连接失败。',conn)
        inspection_result=get_inspection_result(device,conn)

    if key=='ciscoN7k':
        for i in range(1,4):
            conn=ciscoN7k(ip,user,passwd)
            if conn.is_alive:
                break
            else:
                print(ip+'第'+str(i)+'次连接失败。',conn)
        inspection_result=get_inspection_result(device,conn)

    if key=='ciscoASR1000':
        for i in range(1,4):
            conn=ciscoASR1000(ip,user,passwd)
            if conn.is_alive:
                break
            else:
                print(ip+'第'+str(i)+'次连接失败。',conn)
        inspection_result=get_inspection_result(device,conn)

    if key=='cisco4431':
        for i in range(1,4):
            conn=cisco4431(ip,user,passwd)
            if conn.is_alive:
                break
            else:
                print(ip+'第'+str(i)+'次连接失败。',conn)
        inspection_result=get_inspection_result(device,conn)

    if key=='ciscoASA5585':
        for i in range(1,4):
            conn=ciscoASA5585(ip,user,passwd)
            if conn.is_alive:
                break
            else:
                print(ip+'第'+str(i)+'次连接失败。',conn)
        inspection_result=get_inspection_result(device,conn)

    if key=='hillstoneSG6000':
        for i in range(1,4):
            conn=hillstoneSG6000(ip,user,passwd)
            if conn.is_alive:
                break
            else:
                print(ip+'第'+str(i)+'次连接失败。',conn)
        inspection_result=get_inspection_result(device,conn)

    if key=='sangfor':
        for i in range(0,2):
            conn=sangfor(ip,user,passwd)
            if conn.is_alive:
                break
            else:
                print(ip+'第'+str(i)+'次连接失败。',conn)
            time.sleep(sleeptime)
        inspection_result=get_inspection_result(device,conn)

    if key=='ruijieS5750C':
        for i in range(1,4):
            conn=ruijieS5750C(ip,user,passwd)
            if conn.is_alive:
                break
            else:
                print(ip+'第'+str(i)+'次连接失败。',conn)
        inspection_result=get_inspection_result(device,conn)

    if key=='ruijieS6120':
        for i in range(1,4):
            conn=ruijieS6120(ip,user,passwd)
            if conn.is_alive:
                break
            else:
                print(ip+'第'+str(i)+'次连接失败。',conn)
        inspection_result=get_inspection_result(device,conn)

    if key=='ruijieS7808C':
        for i in range(1,4):
            conn=ruijieS7808C(ip,user,passwd)
            if conn.is_alive:
                break
            else:
                print(ip+'第'+str(i)+'次连接失败。',conn)
        inspection_result=get_inspection_result(device,conn)

    if key=='fortigate301':
        for i in range(1,4):
            conn=fortigate301(ip,user,passwd)
            if conn.is_alive:
                break
            else:
                print(ip+'第'+str(i)+'次连接失败。',conn)
        inspection_result=get_inspection_result(device,conn)

    if key=='h3cS12506S':
        for i in range(1,4):
            conn=h3cS12506S(ip,user,passwd)
            if conn.is_alive:
                break
            else:
                print(ip+'第'+str(i)+'次连接失败。',conn)
            time.sleep(sleeptime)
        inspection_result=get_inspection_result(device,conn)
    
    if key=='h3cS12500S':
        for i in range(1,4):
            conn=h3cS12500S(ip,user,passwd)
            if conn.is_alive:
                break
            else:
                print(ip+'第'+str(i)+'次连接失败。',conn)
            time.sleep(sleeptime)
        inspection_result=get_inspection_result(device,conn)

    if key=='h3cS10500':
        for i in range(1,4):
            conn=h3cS10500(ip,user,passwd)
            if conn.is_alive:
                break
            else:
                print(ip+'第'+str(i)+'次连接失败。',conn)
            time.sleep(sleeptime)
        inspection_result=get_inspection_result(device,conn)

    if key=='ABT':
        for i in range(1,4):
            conn=ABT(ip,user,passwd)
            if conn.is_alive:
                break
            else:
                print(ip+'第'+str(i)+'次连接失败。',conn)
            time.sleep(sleeptime)
        inspection_result=get_inspection_result(device,conn)

    if key=='DPADX3000TSGS':
        for i in range(1,4):
            conn=DPADX3000TSGS(ip,user,passwd)
            if conn.is_alive:
                break
            else:
                print(ip+'第'+str(i)+'次连接失败。',conn)
            time.sleep(sleeptime)
        inspection_result=get_inspection_result(device,conn)

    if key=='radware':
        for i in range(1,4):
            conn=radware(ip,user,passwd)
            if conn.is_alive:
                break
            else:
                print(ip+'第'+str(i)+'次连接失败。',conn)
            time.sleep(sleeptime)
        inspection_result=get_inspection_result(device,conn)

    if key=='h3cMSR56':
        for i in range(1,4):
            conn=h3cMSR56(ip,user,passwd)
            if conn.is_alive:
                break
            else:
                print(ip+'第'+str(i)+'次连接失败。',conn)
            time.sleep(sleeptime)
        inspection_result=get_inspection_result(device,conn)

    if key=='h3cF1070':
        for i in range(1,4):
            conn=h3cF1070(ip,user,passwd)
            if conn.is_alive:
                break
            else:
                print(ip+'第'+str(i)+'次连接失败。',conn)
            time.sleep(sleeptime)
        inspection_result=get_inspection_result(device,conn)

    if key=='ruijieRSR50X84':
        for i in range(1,4):
            conn=ruijieRSR50X84(ip,user,passwd)
            if conn.is_alive:
                break
            else:
                print(ip+'第'+str(i)+'次连接失败。',conn)
            time.sleep(sleeptime)
        inspection_result=get_inspection_result(device,conn)

    if key=='ZCTT':
        for i in range(1,4):
            passwd=base64.b64decode(passwd)
            conn=ZCTT(ip,user,passwd.decode('utf-8'))
            if conn.is_alive:
                break
            else:
                print(ip+'第'+str(i)+'次连接失败。',conn)
            time.sleep(sleeptime)
        inspection_result=get_inspection_result(device,conn)

    if key=='riverbed':
        for i in range(1,4):
            passwd=base64.b64decode(passwd)
            conn=riverbed(ip,user,passwd.decode('utf-8'))
            if conn.is_alive:
                break
            else:
                print(ip+'第'+str(i)+'次连接失败。',conn)
            time.sleep(sleeptime)
        inspection_result=get_inspection_result(device,conn)

    if key=='ZDNS':
        for i in range(1,4):
            passwd=base64.b64decode(passwd)
            conn=ZDNS(ip,user,passwd.decode('utf-8'))
            if conn.is_alive:
                break
            else:
                print(ip+'第'+str(i)+'次连接失败。',conn)
            time.sleep(sleeptime)
        inspection_result=get_inspection_result(device,conn)

    return inspection_result 

###只能写xlsx的excel，不支持xls后缀。
def writeExcel(excel, sheetname, data):
    writeData=pd.DataFrame(data)
    writeData.to_excel(excel,sheet_name=sheetname,index=False)

if __name__=='__main__':
    emailaddr=['test1@mail.com','test2@mail.com']
    results=list()
    unconnect_count=0
    baseversion_count=0
    not_baseversion_count=0
    name=[]
    ip=[]
    region1=[]
    region2=[]
    model=[]
    baseversion=[]
    version=[]
    is_baseversion=[]

    today=datetime.datetime.now()
    formatted_date=today.strftime("%Y%m%d%H%M")
    formatted_date1=today.strftime("%Y-%m-%d %H:%M")
    ExcelFile='./report/巡检版本基线_'+formatted_date+'.xlsx'
    
    p=Pool(16)
    for device in config.devices:
        results.append(p.apply_async(check,args=(device,)))
    p.close()
    p.join()
    
    for res in results:       
        try:
            name.append(res.get()['name'])
            ip.append(res.get()['ip'])
            region1.append(res.get()['region1'])
            region2.append(res.get()['region2'])
            model.append(res.get()['model'])
            version.append(res.get()['version'])
            baseversion.append(res.get()['baseversion'])
            is_baseversion.append(res.get()['is_baseversion'])
            if not res.get()['is_connect']:
                unconnect_count=unconnect_count+1
            elif res.get()['is_version']:
                baseversion_count=baseversion_count+1
            else:
                not_baseversion_count=not_baseversion_count+1
        except Exception as e:
            print(res.get(),e)
    data=pd.DataFrame({
            "设备名称":name,
            "设备IP":ip,
            "数据中心":region1,
            "所属区域":region2,
            "设备型号":model,
            "基线版本":baseversion,
            "当前版本":version,
            "是否符合基线":is_baseversion,
        })
    Sheetname="网络设备版本巡检表"
    writer=pd.ExcelWriter(ExcelFile)
    if len(name):
        data.to_excel(writer, sheet_name=Sheetname, index=False)
    writer._save()
    writer.close()

    contentText="共巡检{}台设备。其中符合基线版本设备 {} 台，不符合基线版本设备 {} 台。".format(not_baseversion_count+baseversion_count+unconnect_count,baseversion_count,not_baseversion_count)

    sendemail(recv=emailaddr,file=ExcelFile,content=contentText,title="网络设备软件版本巡检")
