#F5虚拟设备
from icontrol.session import iControlRESTSession
from datetime import timedelta
import datetime,time
import re, urllib3
from f5.bigip import ManagementRoot
import requests


class F5VE:
    def __init__(self,ip,username,password):
        self.type='F5VE'
        self.ip=ip
        self.username=username
        self.password=password
        self.timeout=5
        #urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        try:
            self.driver=ManagementRoot( self.ip, self.username, self.password, timeout=self.timeout)
            self.is_alive=True
        except:
            self.is_alive=False

    #CPU巡检。
    #阈值默认值：threshold=50。取cpu1分钟利用率<阈值:返回True，否则为False
    def cpu(self,threshold=70):
        state=True
        output=self.driver.tm.sys.host_info.load().raw
        cpuCount=output['entries']['https://localhost/mgmt/tm/sys/host-info/0']['nestedStats']['entries']['cpuCount']['value']
        cpuInfos=output['entries']['https://localhost/mgmt/tm/sys/host-info/0']['nestedStats']['entries']['https://localhost/mgmt/tm/sys/hostInfo/0/cpuInfo']['nestedStats']['entries']
        #print(cpuInfos)
        shortinfo=list()
        i=0
        for cpuinfo in cpuInfos:
            if i%2==0:
                oneMinAvgUse=100-cpuInfos[cpuinfo]['nestedStats']['entries']['oneMinAvgIdle']['value']
                shortinfo.append(oneMinAvgUse)
                if oneMinAvgUse > threshold:
                    state=False
            i=i+1
        #print(shortinfo)
        return {"state":state,"info":cpuInfos,"value":shortinfo,"type":self.type}

        

    
    #内存巡检。
    #阈值默认值：threshold=80。取内存利用率<阈值:返回True，否则为False
    def memory(self,threshold=80):
        state=True
        value=list()
        output=self.driver.tm.sys.host_info.load().raw
        memoryTotal=output['entries']['https://localhost/mgmt/tm/sys/host-info/0']['nestedStats']['entries']['memoryTotal']['value']
        memoryUsed=output['entries']['https://localhost/mgmt/tm/sys/host-info/0']['nestedStats']['entries']['memoryUsed']['value']
        per=round(memoryUsed/memoryTotal*100)
        value.append(per)
        if per > threshold:
            state=False
        return {"state":state,"value":value,"info":output,"type":self.type}
    

    #风扇巡检
    def fan(self):
        state=True
        return {"state":state,"value":"-","info":"-","type":self.type}

    #电源巡检
    def power(self):
        state=True
        return {"state":state,"value":"-","info":"-","type":self.type}

    #设备启动时间
    #threshold默认为12小时
    def uptime(self,threshold=12):
        state=True
        hours=-1
        output=self.driver.tm.sys.failover.load().raw
        #print(output)
        time=output['apiRawValues']['apiAnonymous']
        #print(time)
        match = re.search(r'\s+(\d+)d\s+(\d+):\d+:\d+',time)
        #print(match)
        try:
            hours = int(match.group(1))*24+int(match.group(2))
            if hours <= threshold:
                state=False
        except:
            state=False
        return {"state":state,"value":hours,"info":time,"type":self.type}


    #温度巡检。
    #阈值默认值：threshold=80。取内存利用率<阈值:返回True，否则为False
    def temperature(self,threshold=80):
        state=True
        value=list()
        output=self.driver.tm.sys.host_info.load().raw
        #memoryTotal=output['entries']['https://localhost/mgmt/tm/sys/host-info/0']['nestedStats']['entries']['memoryTotal']['value']
        #memoryUsed=output['entries']['https://localhost/mgmt/tm/sys/host-info/0']['nestedStats']['entries']['memoryUsed']['value']
        temp=output['entries']['https://localhost/mgmt/tm/sys/hard-ware']
        print(temp)
        #per=round(memoryUsed/memoryTotal*100)
        #value.append(per)
        #if per > threshold:
        #    state=False
        #return {"state":state,"value":value,"info":output,"type":self.type}


    #版本
    #threshold默认为基线版本
    def version(self,threshold="15.1.6.1"):
        state=True
        version="none"
        output=self.driver.tm.sys.version.load().raw
        print(output)
        version=output['entries']['https://localhost/mgmt/tm/sys/version/0']['nestedStats']['entries']['Version']['description']
        print(version)
        try:
            version=output['entries']['https://localhost/mgmt/tm/sys/version/0']['nestedStats']['entries']['Version']['description']
            #version="Version "+version
            if version.replace(" ","") != threshold.replace(" ",""):
                state=False
        except:
            state=False
        return {"state":state,"value":version,"info":output,"type":self.type}




#主程序入口
if __name__ == "__main__":

    ips1=['10.0.0.0']
    user='test'
    passwd='test'
    time1=time.perf_counter()
    for ip in ips1:
        print(ip)
        device=F5VE(ip,user,passwd)
        if device.is_alive:
            cpu=device.cpu()
            print(cpu['value'])
            if not cpu['state']:
                print('cpu',cpu)
            mem=device.memory()
            print(mem['value'])
            if not mem['state']:
                print('mem',mem)
            power=device.power()
            print(power['value'])
            if not power:
                print('power',power)
            uptime=device.uptime()
            print(uptime['value'])
            if not uptime['state']:
                print('uptime',uptime)
            fan=device.fan()
            print(fan['value'])
            if not fan['state']:
                print('fan',fan)
            print(device.version())
        else:
            print('unconnect')
    time2=time.perf_counter()
    print(time2-time1)
