#F5设备
from icontrol.session import iControlRESTSession
from datetime import timedelta
import datetime
import re, urllib3
from f5.bigip import ManagementRoot
from netmiko import ConnectHandler
import requests, time

class F5:
    def __init__(self,ip,username,password):
        self.type="F5"
        self.device_type='f5_tmsh'
        self.ip=ip
        self.username=username
        self.password=password
        self.timeout=5
        #urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        try:
            self.driver=ManagementRoot( self.ip, self.username, self.password, timeout=self.timeout)
            self.is_alive=True
        except Exception as e:
            print("api connect error:",e)
            self.is_alive=False
    

    #ssh执行命令，返回回显
    def command(self,command):
        re=''
        info={'device_type':'f5_tmsh',
              'ip':self.ip,
              'username':self.username,
              'password':self.password,
              'read_timeout_override':10}
        try:
            driverSsh=ConnectHandler(**info)
            self.is_alive=True
            for i in range(1,3):
                try:
                    re=driverSsh.send_command(command,read_timeout=20)
                except Exception as e:
                    print(self.info['ip'],command,'command failed:',i, e)
                time.sleep(5)
        except Exception as e:
            print("ssh connect error:",e)
            self.is_alive=False

        return re


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
    def memory(self,threshold=60):
        state=True
        value=list()
        output=self.driver.tm.sys.host_info.load().raw
        memoryTotal=output['entries']['https://localhost/mgmt/tm/sys/host-info/0']['nestedStats']['entries']['memoryTotal']['value']
        memoryUsed=output['entries']['https://localhost/mgmt/tm/sys/host-info/0']['nestedStats']['entries']['memoryUsed']['value']
        per=round(memoryUsed/memoryTotal*100)
        value.append(int(per))
        if per > threshold:
            state=False
        return {"state":state,"value":value,"info":output,"type":self.type}
    

    #风扇巡检
    def fan(self):
        state=True
        value=list()
        fans=''
        output=self.driver.tm.sys.hardware.load().raw
        try:
            fans=output['entries']['https://localhost/mgmt/tm/sys/hardware/chassis-fan-status-index']['nestedStats']['entries']
            for key in fans:
                fanStatus=fans[key]['nestedStats']['entries']['status']['description']
                value.append(fanStatus)
                if fanStatus != 'up':
                    state=False
        except:
            state=False
        return {"state":state,"value":value,"info":fans,"type":self.type}

    #电源巡检
    def power(self):
        state=True
        value=list()
        powers=''
        output=self.driver.tm.sys.hardware.load().raw
        try:
            powers=output['entries']['https://localhost/mgmt/tm/sys/hardware/chassis-power-supply-status-index']['nestedStats']['entries']
            for key in powers:
                powerStatus=powers[key]['nestedStats']['entries']['status']['description']
                value.append(powerStatus)
                if powerStatus != 'up':
                    state=False
        except:
            state=False
        return {"state":state,"value":value,"info":powers,"type":self.type}

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
        output=self.driver.tm.sys.hardware.load().raw
        try:
            temps=output['entries']['https://localhost/mgmt/tm/sys/hardware/chassis-temperature-status-index']['nestedStats']['entries']
            i=0 
            for key in temps:
                i=i+1
                indexUrl="https://localhost/mgmt/tm/sys/hardware/chassis-temperature-status-index/{}".format(i)
                temp=temps[key]['nestedStats']['entries']['temperature']['value']
                hiLimit=temps[key]['nestedStats']['entries']['hiLimit']['value']
                loLimit=temps[key]['nestedStats']['entries']['loLimit']['value']
                if int(temp)<int(loLimit) or int(temp)>int(hiLimit):
                    state=False
        except:
            state=False
        return {"state":state,"value":value,"info":temps,"type":self.type}

    #版本
    #threshold默认为基线版本
    def version(self,threshold="15.1.6.1"):
        state=True
        version="none"
        output=self.driver.tm.sys.version.load().raw
        #version=output['entries']['https://localhost/mgmt/tm/sys/version/0']['nestedStats']['entries']['Version']['description']
        print(version)
        try:
            version=output['entries']['https://localhost/mgmt/tm/sys/version/0']['nestedStats']['entries']['Version']['description']
            if version.replace(" ","") != threshold.replace(" ",""):
                state=False
        except:
            state=False
        return {"state":state,"value":version,"info":output,"type":self.type}

    #base_servers,base_timezone默认为基线版本
    def check_ntp_acl(self,threshold=['10.10.0.1','10.10.0.1', '10.11.0.1', '10.11.0.2']):
        base_timezone = 'Asia/Shanghai'
        base_servers=[ '10.10.0.1','10.10.0.1', '10.11.0.1', '10.11.0.2']
        state=True
        servers="none"
        output=self.driver.tm.sys.ntp.load().raw
        try:
            servers=output['servers']
            timezone=output['timezone']
        #    print(servers)
            servers.sort()
            base_servers.sort()
            if servers == base_servers and timezone==base_timezone:
                state=True
            else:
                state=False
        except:
            state=False
        return {"state":state,"value":servers,"threshold":base_servers,"info":output}

    #base_server默认为基线版本
    def check_syslog_remoteservers_acl(self):
        base_servers=['10.10.0.1','10.10.0.1', '10.11.0.1', '10.11.0.2']
        state=True
        servers=[]
        output=self.driver.tm.sys.syslog.load().raw
        try:
            for o in output['remoteServers']:
                servers.append(o['host'])
            servers.sort()
            base_servers.sort()
            if servers == base_servers:
                state=True
            else:
                state=False
        except Exception as e:
            print("check_syslog_remoteservers_acl error:",e)
            state=False
        return {"state":state,"value":servers,"threshold":base_servers,"info":output,}

    #base_server默认为基线版本
    def check_snmp_allowedaddresses_acl(self):
        base_servers=['10.10.0.1/255.255.255.248', '10.10.0.1']
        state=True
        servers=[]
        output=self.driver.tm.sys.snmp.load().raw
        try:
            servers=output['allowedAddresses']
            servers.sort()
            base_servers.sort()
            if servers == base_servers:
                state=True
            else:
                state=False
        except:
            state=False
        return {"state":state,"value":servers,"threshold":base_servers,"info":output,}

    #base_server默认为基线版本
    def check_icontrolsoap_acl(self):
        base_servers=['10.10.2.0/24',  '10.12.2.0/24']
        state=True
        servers=[]
        command="list sys icontrol-soap"
        for i in range(0,3):
            output=self.command(command)
            match = re.search(r'[{](.*)[}]',output)
            if match:
                break
            print(self.info['ip'],'命令：',command,'第'+str(i)+'次正则匹配失败，匹配内容(output,match)：',output,match)
        if match:
            tmp=match.group(1)  
            servers=tmp.split()
            servers.sort()
            base_servers.sort()
            if servers == base_servers:
                state=True
            else:
                state=False
        else:
            state=False
        return {"state":state,"value":servers,"threshold":base_servers,"info":output,}

    #base_server默认为基线版本
    def check_sshd_acl(self):
        base_servers=['10.10.2.0/24', '10.12.6.0/24', '10.10.8.0/24', ]
        state=True
        servers=[]
        output=self.driver.tm.sys.sshd.load().raw
        try:
            servers=output['allow']
            servers.sort()
            base_servers.sort()
            if servers == base_servers:
                state=True
            else:
                state=False
        except:
            state=False
        return {"state":state,"value":servers,"threshold":base_servers,"info":output,}

    #base_server默认为基线版本
    def check_httpd_acl(self):
        base_servers=['10.12.2.0/24', '10.12.6.0/24', '10.10.8.0/24']
        state=True
        servers=[]
        output=self.driver.tm.sys.httpd.load().raw
        try:
            servers=output['allow']
            servers.sort()
            base_servers.sort()
            if servers == base_servers:
                state=True
            else:
                state=False
        except:
            state=False
        return {"state":state,"value":servers,"threshold":base_servers,"info":output,}


if __name__ == "__main__":

    ips=['10.10.10.10']
    user='test'
    passwd='test'
    today=datetime.datetime.now()
    formatted_date=today.strftime("%Y%m%d%H")
    formatted_date1=today.strftime("%Y-%m-%d %H:%M")
    
    for ip in ips:
        print(ip)
        device=F5(ip,user,passwd)
        print(device.is_alive)
        if device.is_alive:
            print(device.temperature())
            print(device.check_icontrolsoap_acl())
