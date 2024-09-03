#python3

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

# #生成PDF所依赖的模块
# from createPDF import Graphs
# from reportlab.pdfbase import pdfmetrics   # 注册字体
# from reportlab.pdfbase.ttfonts import TTFont  # 字体类
# from reportlab.platypus import Table, SimpleDocTemplate, Paragraph, Image, PageBreak  # 报告内容相关类
# from reportlab.lib.pagesizes import letter, A4, landscape  # 页面的标志尺寸(8.5*inch, 11*inch)
# from reportlab.lib.styles import getSampleStyleSheet  # 文本样式
# from reportlab.lib import colors  # 颜色模块
# from reportlab.graphics.charts.barcharts import VerticalBarChart  # 图表类
# from reportlab.graphics.charts.legends import Legend  # 图例类
# from reportlab.graphics.shapes import Drawing  # 绘图工具
# from reportlab.lib.units import cm  # 单位：cm
# #注册字体(提前准备好字体文件, 如果同一个文件需要多种字体可以注册多个)
# pdfmetrics.registerFont(TTFont('SimSun', 'SimSun.ttf'))

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


#设备划分区域
def get_region(name):
    if '-' in name:
        li=name.split('-')
    elif '_' in name:
        li=name.split('_')
    else:
        li=None
    return {'region1':config.region1[li[0]],'region2':config.region2[li[2]]}

#结果中判断显示"正常"或者"异常"
def abnormal_info(item):
    if item['state']:
        if item['value']=='-':
            return '-'
        else:
            return '正常'
    else:
        return '异常'
    

#巡检指标项
def get_inspection_result(device,conn):
    normal=list()
    abnormal=list()
    memoryvalue=''
    cpuvalue=''
    uptimevalue=''
    ip=device['ip']
    model=device['key']
    name=device['name']
    check=device['check']
    region=get_region(name)
    region1=region['region1']
    region2=region['region2']
    cpu={'state':True,'value':'-'}
    memory={'state':True,'value':'-'}
    power={'state':True,'value':'-'}
    fan={'state':True,'value':'-'}
    uptime={'state':True,'value':'-'}
    temperature={'state':True,'value':'-'}
    board={'state':True,'value':'-'}
    mlag={'state':True,'value':'-'}
    ospf={'state':True,'value':'-'}
    bgp={'state':True,'value':'-'}
    irf={'state':True,'value':'-'}

    if check['cpu']:
        try:
            cpu=conn.cpu()
            cpuvalue='('+str(max(cpu['value']))+')'
        except  Exception as e:
            cpu['state']=False
            print('【error conn cpu】',ip,e)
    else:
        cpu['state']=True
        cpuvalue='-'

    if check['mem']:
        try:
            memory=conn.memory()
            #memoryvalue='('+(' '.join(memory['value']))+')'
            memoryvalue='('+str(max(memory['value']))+')'
        except  Exception as e:
            memory['state']=False
            print('【error conn memory】',ip,e)
    else:
        memory['state']=True
        memoryvalue='-'

    if check['power']:
        try:
            for i in range(1,4):
                power=conn.power()
                if power['state']:
                    break
        except Exception as e:
            power['state']=False
            print('【error conn power】',ip,e)
    else:
        power['state']=True
        powervalue='-'

    if check['fan']:
        try:
            fan=conn.fan()
        except Exception as e:
            fan['state']=False
            print('【error conn fan】',ip,e)
    else:
        fan['state']=True
        fanvalue='-'

    if check['uptime']:
        try:
            uptime=conn.uptime()
            uptimevalue='('+str(uptime['value'])+')'
        except Exception as e:
            uptime['state']=False
            print('【error conn uptime】',ip,e)
    else:
        uptime['state']=True
        uptimevalue='-'

    if check['temperature']:
        try:
            temperature=conn.temperature()
            #tempraturevalue='('+str(temprature['value'])+')'
        except Exception as e:
            temperature['state']=False
            print('【error conn】temperature',ip,e)
    else:
        temperature['state']=True
        temperature['value']='-'
        #tempraturevalue='-'

    if check['board']:
        try:
            board=conn.board()
            boardvalue='('+str(board['value'])+')'
        except Exception as e:
            board['state']=False
            print('【error conn board】',ip,e)
    else:
        board['state']=True
   
    if check['mlag']:
        try:
            mlag=conn.mlag()
        except Exception as e:
            mlag['state']=False
            print('【error conn mlag】',ip,e)
    else:
        mlag['state']=True
    
    if check['ospf']:
        try:
            ospf=conn.ospf()
        except Exception as e:
            ospf['state']=False
            print('【error conn ospf】',ip,e)
    else:
         ospf['state']=True

    if check['bgp']:
        try:
            bgp=conn.bgp()
        except Exception as e:
            bgp['state']=False
            print('【error conn bgp】',ip,e)
    else:
        bgp['state']=True

    if check['irf']:
        try:
            irf=conn.irf()
        except Exception as e:
            irf['state']=False
            print('【error conn irf】',ip,e)
    else:
        irf['state']=True
        irfvalue='-'
    
    if conn.is_alive:
        if cpu['state'] and fan['state'] and power['state'] and uptime['state'] and memory['state'] and ospf['state'] and bgp['state'] and mlag['state'] and irf['state'] and temperature['state'] and board['state']:
            print('【normal】,{},cpu:{}, memory:{}, power:{}, fan:{}, uptime:{}, ospf:{}, bgp:{}, mlag:{}, irf:{},temperature:{},board:{}'.format(ip,cpu,memory,power,fan,uptime,ospf,bgp,mlag,irf,temperature,board))
            normal={
                "name":name,
                "ip":ip,
                "model":model,
                "region1":region1,
                "region2":region2,
                "cpu":abnormal_info(cpu)+cpuvalue,
                "memory":abnormal_info(memory)+memoryvalue,
                "power":abnormal_info(power),
                "fan":abnormal_info(fan),
                "uptime":abnormal_info(uptime)+uptimevalue,
                "temperature":abnormal_info(temperature),
                "board":abnormal_info(board),
                "ospf":abnormal_info(ospf),
                "bgp":abnormal_info(bgp),
                "mlag":abnormal_info(mlag),
                "irf":abnormal_info(irf),
                "board":abnormal_info(board),
                }
        else:
            try:
                print('【abnormal】,{},cpu:{}, memory:{}, power:{}, fan:{}, uptime:{}, ospf:{}, bgp:{}, mlag:{}, irf:{},temperature:{},board:{}'.format(ip,cpu,memory,power,fan,uptime,ospf,bgp,mlag,irf,temperature,board))
            except:
                print('【abnormal】日志异常',ip)
            abnormal={
                "name":name,
                "ip":ip,
                "model":model,
                "region1":region1,
                "region2":region2,
                "cpu":abnormal_info(cpu)+cpuvalue,
                "memory":abnormal_info(memory)+memoryvalue,
                "power":abnormal_info(power),
                "fan":abnormal_info(fan),
                "uptime":abnormal_info(uptime)+uptimevalue,
                "temperature":abnormal_info(temperature),
                "board":abnormal_info(board),
                "ospf":abnormal_info(ospf),
                "bgp":abnormal_info(bgp),
                "mlag":abnormal_info(mlag),
                "irf":abnormal_info(irf),
                "board":abnormal_info(board),
                }
    else:
        try:
            print('【unconnect】,{}, {},{},cpu:{}, memory:{}, power:{}, fan:{}, uptime:{}, ospf:{}, bgp:{}, mlag:{}, irf:{},temperature:{},board:{}'.format(ip,device,conn,cpu,memory,power,fan,uptime,ospf,bgp,mlag,irf,temperature,board))
        except:
            print('【unconnect】日志异常',ip)
        abnormal={
                "name":name,
                "ip":ip,
                "model":model,
                "region1":region1,
                "region2":region2,
                "cpu":"设备未连接",
                "memory":"设备未连接",
                "power":"设备未连接",
                "fan":"设备未连接",
                "uptime":"设备未连接",
                "temperature":"设备未连接",
                "board":"设备未连接",
                "ospf":"设备未连接",
                "bgp":"设备未连接",
                "mlag":"设备未连接",
                "irf":"设备未连接",
                "board":"设备未连接",
                }
    return {"normal":normal,"abnormal":abnormal}


#判断设备类型进行巡检
def check(device):
    # 对应config.py中authtypes
    # authtype对应authtypes的key
    # device['authtype']对应config.py
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
    recv_emailaddr=['test@mail.com']
    contentPDF=list()
    results=list()

    abnormal=list()
    normal=list()
    
    abnormal_data=1
    abnormal_name=[]
    abnormal_ip=[]
    abnormal_model=[]
    abnormal_region1=[]
    abnormal_region2=[]
    abnormal_cpu=[]
    abnormal_memory=[]
    abnormal_power=[]
    abnormal_fan=[]
    abnormal_uptime=[]
    abnormal_temperature=[]
    abnormal_board=[]
    abnormal_ospf=[]
    abnormal_bgp=[]
    abnormal_mlag=[]
    abnormal_irf=[]

    normal_data=0
    normal_name=[]
    normal_ip=[]
    normal_model=[]
    normal_region1=[]
    normal_region2=[]
    normal_cpu=[]
    normal_memory=[]
    normal_power=[]
    normal_fan=[]
    normal_uptime=[]
    normal_temperature=[]
    normal_board=[]
    normal_ospf=[]
    normal_bgp=[]
    normal_mlag=[]
    normal_irf=[]
    


    abnormal_little_title="异常设备列表"
    normal_little_title="正常设备列表"
    today=datetime.datetime.now()
    formatted_date=today.strftime("%Y%m%d%H%M")
    formatted_date1=today.strftime("%Y-%m-%d %H:%M")
    ExcelFile='./report/巡检报告_'+formatted_date+'.xlsx'
  
    #多线程
    p=Pool(16)
    for device in config.devices:
        results.append(p.apply_async(check,args=(device,)))
    p.close()
    p.join()
    
    for res in results:       
        try:
            if res.get()['abnormal']:
                print("res-get-abnormal",res.get()['abnormal'])
                #abnormal.append(tuple(res.get()['abnormal']))
                abnormal_name.append(res.get()['abnormal']['name'])
                abnormal_ip.append(res.get()['abnormal']['ip'])
                abnormal_model.append(res.get()['abnormal']['model'])
                abnormal_region1.append(res.get()['abnormal']['region1'])
                abnormal_region2.append(res.get()['abnormal']['region2'])
                abnormal_cpu.append(res.get()['abnormal']['cpu'])
                abnormal_memory.append(res.get()['abnormal']['memory'])
                abnormal_power.append(res.get()['abnormal']['power'])
                abnormal_fan.append(res.get()['abnormal']['fan'])
                abnormal_uptime.append(res.get()['abnormal']['uptime'])
                abnormal_temperature.append(res.get()['abnormal']['temperature'])
                abnormal_board.append(res.get()['abnormal']['board'])
                abnormal_ospf.append(res.get()['abnormal']['ospf'])
                abnormal_bgp.append(res.get()['abnormal']['bgp'])
                abnormal_mlag.append(res.get()['abnormal']['mlag'])
                abnormal_irf.append(res.get()['abnormal']['irf'])
        except:
            print(res.get())

        try:
            if res.get()['normal']:
                print("res-get-normal",res.get()['normal'])
                #生产excel所需格式的数据
                normal_name.append(res.get()['normal']['name'])
                normal_ip.append(res.get()['normal']['ip'])
                normal_model.append(res.get()['normal']['model'])
                normal_region1.append(res.get()['normal']['region1'])
                normal_region2.append(res.get()['normal']['region2'])
                normal_cpu.append(res.get()['normal']['cpu'])
                normal_memory.append(res.get()['normal']['memory'])
                normal_power.append(res.get()['normal']['power'])
                normal_fan.append(res.get()['normal']['fan'])
                normal_uptime.append(res.get()['normal']['uptime'])
                normal_temperature.append(res.get()['normal']['temperature'])
                normal_board.append(res.get()['normal']['board'])
                normal_ospf.append(res.get()['normal']['ospf'])
                normal_bgp.append(res.get()['normal']['bgp'])
                normal_mlag.append(res.get()['normal']['mlag'])
                normal_irf.append(res.get()['normal']['irf'])
        except:
            print(res.get())

    writer=pd.ExcelWriter(ExcelFile)

    #所有正常设备
    if normal_name:
        normal_data=pd.DataFrame({
            "设备名称":normal_name,
            "设备IP":normal_ip,
            "设备型号":normal_model,
            "数据中心":normal_region1,
            "所属区域":normal_region2,
            "CPU":normal_cpu,
            "内存":normal_memory,
            "电源":normal_power,
            "风扇":normal_fan,
            "运行时间":normal_uptime,
            "温度":normal_temperature,
            "板卡状态":normal_board,
            "OSPF状态":normal_ospf,
            "BGP状态":normal_bgp,
            "M-LAG状态":normal_mlag,
            "IRF状态":normal_irf,
        })
     #所有异常设备
    if abnormal_name:
        abnormal_data=pd.DataFrame({
            "设备名称":abnormal_name,
            "设备IP":abnormal_ip,
            "设备型号":abnormal_model,
            "数据中心":abnormal_region1,
            "所属区域":abnormal_region2,
            "CPU":abnormal_cpu,
            "内存":abnormal_memory,
            "电源":abnormal_power,
            "风扇":abnormal_fan,
            "运行时间":abnormal_uptime,
            "温度":abnormal_temperature,
            "板卡状态":abnormal_board,
            "OSPF状态":abnormal_ospf,
            "BGP状态":abnormal_bgp,
            "M-LAG状态":abnormal_mlag,
            "IRF状态":abnormal_irf,
        })


    normalSheetname="正常设备列表"
    abnormalSheetname="异常设备列表"
    
    abnormallen=len(abnormal_name)
    normallen=len(normal_name)
    print("normallen,abnormallen:",abnormallen,normallen)
    #生成所有网络设备巡检报告
    writer=pd.ExcelWriter(ExcelFile)
    if abnormallen:
        abnormal_data.to_excel(writer, sheet_name=abnormalSheetname, index=False)
    if normallen:
        normal_data.to_excel(writer, sheet_name=normalSheetname, index=False)
    writer._save()
    writer.close()
   
    
    #发送邮件
    contentText="共巡检{}台设备，其中正常设备 {} 台，异常设备 {} 台。".format(abnormallen+normallen,normallen,abnormallen)
    sendemail(recv=recv_emailaddr,file=ExcelFile,content=contentText,title="网络设备巡检（CPU|MEMORY|FAN|POWER|UPTIME|OSPF|板卡|BGP|温度|MLAG|IRF）")
    