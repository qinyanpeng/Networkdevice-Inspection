#飞塔
from netmiko import ConnectHandler
from datetime import timedelta
import re, time

class fortigate301:
    def __init__(self,ip,username,password):
        self.type='fortigate301'
        self.info={'device_type':'linux',
                   'ip':ip,
                   'username':username,
                   'password':password}
        try:
            self.driver=ConnectHandler(**self.info)
            self.is_alive=True
        except:
            self.is_alive=False

    #CPU巡检。
    #阈值默认值：threshold=70。取cpu1分钟利用率<阈值:返回True，否则为False
    def cpu(self,threshold=70):
        state=True
        match=''
        value=''
        values=[]
        output=''
        command="get system performance status"
        for i in range(0,3):
            try:
                output=self.driver.send_command(command,read_timeout=10)
                #print(output)
                state=True
                break
            except:
                #print(output)
                state=False
        match = re.findall(r'nice\s+(\d+)%\s+idle',output)
        #print(match)
        if len(match)==0:
            state=False
        else:
            for v in match:
                value=100-float(v)
                values.append(value)
                if value > threshold:
                    state=False
        return {"state":state,"value":values,"info":output,"type":self.type,"threshold":threshold}

    
    #内存巡检。
    #阈值默认值：threshold=60。取内存利用率<阈值:返回True，否则为False
    def memory(self,threshold=60):
        state=True
        match=''
        output=''
        value=list()
        command="get system performance status"
        for i in range(0,3):
            try:
                output=self.driver.send_command(command,read_timeout=10,use_textfsm=True)
                state=True
                break
            except:
                #print(output)
                state=False
        #print(output)
        match = re.findall(r'used\s+[(](\d+)%[)],',output)
        #print(match)
        if len(match)==0:
            state=False
        else:
            for v in match:
                value.append(float(v))
                if float(v) > threshold:
                    state=False
        return {"state":state,"value":value,"info":output,"type":self.type,"threshold":threshold}

    #电源巡检
    def power(self):
        state=True
        return {"state":state,"value":"-","info":"-","type":self.type,"threshold":"-"}


    #风扇巡检
    def fan(self):
        state=True
        return {"state":state,"value":"-","info":"-","type":self.type,"threshold":"-"}

    #设备启动时间
    def uptime(self,threshold=12):
        uptime_hours=-1
        match='None'
        output='None'
        state=True
        command="get system performance status"
        for i in range(0,3):
            try:
                output=self.driver.send_command(command)
                if output:
                    state=True
                    uptime_hours=0
                    break
            except:
                #print(output)
                state=False
        years=re.search(r'(\d+)\s+years?',output)
        weeks=re.search(r'(\d+)\s+weeks?',output)
        days=re.search(r'(\d+)\s+days?',output)
        hours=re.search(r'(\d+)\s+hours?',output)
        if years:
            uptime_hours = 0+int(years.group(1))*365*24
        if weeks:
            uptime_hours = uptime_hours + int(weeks.group(1))*7*24
        if days:
            uptime_hours = uptime_hours + int(days.group(1))*24
        if hours:
            uptime_hours = uptime_hours + int(hours.group(1))
        if uptime_hours<=12:
            state=False
        return {"state":state,"value":uptime_hours,"info":output,"type":self.type,"threshold":threshold}

    def version(self,threshold="FortiOS 5.6.14 9 build1727 (GA)"):
        state=True
        version="none"
        command="get system status"
        output=''
        for i in range(0,2):
            output=self.driver.send_command(command)
            match=re.search(r'Version:\s+(.*)\n',output)
            if match:
                state=True
                version=match.group(1)
                break
            else:
                print(self.info['ip'],"command:",command,'第'+str(i)+'次正则匹配失败，匹配内容(output,match)：',output,match)
                state=False
                time.sleep(3)

        if match:
            if version.replace(" ","")==threshold.replace(" ",""):
                state=True
            else:
                state=False
        return {"state":state,"value":version,"info":output,"type":self.type}


    def close(self):
        self.driver.disconnect() 

if __name__ == "__main__":

    ips=['10.10.10.10']
    user='user'
    passwd='test'
    time1=time.perf_counter()
    for ip in ips:
        print(ip)
        device=fortigate301(ip,user,passwd)
        if device.is_alive:
            cpu=device.cpu()
            print(cpu)
            if not cpu['state']:
                print('cpu',cpu)
            mem=device.memory()
            print(mem)
            #if not mem['state']:
            #    print('mem',mem)
            #power=device.power()
            #if not power:
            #    print('power',power)
            #uptime=device.uptime()
            #print(uptime)
            #if not uptime['state']:
            #    print('uptime',uptime)
            #fan=device.fan()
            #if not fan['state']:
            #    print('fan',fan)
            print(device.version())
            device.close()
        else:
            print('unconnect')
    time2=time.perf_counter()
    print(time2-time1)
