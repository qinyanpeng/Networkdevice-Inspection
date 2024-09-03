from netmiko import ConnectHandler
from datetime import timedelta
import re, time

class radware:
    def __init__(self,ip,username,password):
        self.type='radeware'
        self.info={'device_type':'generic',
                   'ip':ip,
                   'username':username,
                   'password':password}
        for i in range(1,4):
            try:
                self.driver=ConnectHandler(**self.info)
                self.is_alive=True
                break
            except Exception as e:
                self.is_alive=False
                print(self.info['ip'],'connect failed:', e)
            time.sleep(10)

    #执行命令，返回回显
    def command(self,command):
        output=''
        for i in range(1,4):
            try:
                output=self.driver.send_command(command,read_timeout=20)
                break
            except Exception as e:
                print(self.info['ip'],command,'command failed:',i, e)
            time.sleep(10)
        return output

    #CPU。
    #阈值默认值：threshold=70。取cpu1分钟利用率<阈值:返回True，否则为False
    def cpu(self,threshold=70):
        state=True
        match=''
        output=''
        value=[]
        command="/stats/sp/allcpu"
        for i in range(1,4):
            output=self.command(command)
            match = re.findall(r'(\d+)%',output)
            if len(match)!=0:
                break
            else:
                print(self.info('ip'),i,'次失败，命令：',command)
        #print(match)
        if len(match)==0:
            state=False
        else:
            for v in match:
                value.append(int(v))
                if int(v) > threshold:
                    state=False
        return {"state":state,"value":value,"info":output,"type":self.type}

    #内存。
    #阈值默认值：threshold=60。取内存利用率<阈值:返回True，否则为False
    def memory(self,threshold=60):
        state=True
        match=''
        output=''
        value=list()
        command="/stats/sp/allmem"
        for i in range(0,3):
            output=self.command(command)
            match = re.findall(r'(\d+)%',output)
            if len(match)!=0:
                break
        if len(match)==0:
            state=False
        else:
            for v in match:
                value.append(int(v))
                if int(v) > threshold:
                    state=False
        return {"state":state,"value":value,"info":output,"type":self.type}

    #电源巡检
    def power(self):
        state=True
        match=''
        output=''
        command="/info/sys/ps"
        for i in range(0,3):
            output=self.command(command)
            match = re.findall(r'Status:\s+(\w+)',output)
            if len(match)!=0:
                break
        if len(match)==0:
            state=False
        else:
            for v in match:
                if v != "OK":
                    state=False
                    break
        return {"state":state,"value":match,"info":output,"type":self.type}

    #设备启动时间
    def uptime(self,threshold=12):
        uptime_hours=-1
        match=''
        output=''
        state=True
        command="/info/sys/general"
        for i in range(1,4):
            output=self.command(command) 
            years=re.search(r'(\d+)\s+years?',output)
            weeks=re.search(r'(\d+)\s+weeks?',output)
            days=re.search(r'(\d+)\s+days?',output)
            hours=re.search(r'(\d+)\s+hours?',output)
            if years or weeks or days or hours:
                uptime_hours=0
                break
        if years:
            uptime_hours = 0+int(years.group(1))*365*24
        if weeks:
            uptime_hours = uptime_hours + int(weeks.group(1))*7*24
        if days:
            uptime_hours = uptime_hours + int(days.group(1))*24
        if hours:
            uptime_hours = uptime_hours + int(hours.group(1))
        if int(uptime_hours)<=12:
            state=False
        return {"state":state,"value":uptime_hours,"info":output,"type":self.type}

    #风扇巡检
    def fan(self,threshold=90):
        state=True
        match='None'
        output='None'
        command="/info/sys/fan"
        for i in range(0,3):
            output=self.command(command)
            match = re.findall(r'(\d+)%',output)
            if len(match)!=0:
                break
        if len(match)==0:
            state=False
        else:
            for v in match:
                if int(v)>threshold :
                    state=False
                    break
        return {"state":state,"value":match,"info":output,"type":self.type}

    #温度巡检
    def temperature(self,threshold=90):
        state=True
        match='None'
        output='None'
        command="/info/sys/temp"
        for i in range(0,3):
            output=self.command(command)
            match = re.findall(r'Current device temperature is (\w+)\n',output)
            if len(match)!=0:
                break
        if len(match)>0:
            for v in match:
                if v=="OK":
                    state=True
                else:
                    state=False
                    break
        else:
            state=False
        return {"state":state,"value":match,"info":output,"type":self.type}

    def version(self,threshold="Version 32.4.10.0"):
        state=True
        match='None'
        output='None'
        version='none'
        command=" /info/sys/general"
        for i in range(0,3):
            output=self.command(command)
            match = re.search(r'(Version\s+.*)\sImage',output)
            if match:
                version=match.group(1)
                break
            else:
                state=False
        if match:
            if version.replace(" ","")==threshold.replace(" ",""):
                state=True
            else:
                state=False
        return {"state":state,"value":version,"info":output,"type":self.type}



    def close(self):
        self.driver.disconnect()


#主程序入口
if __name__ == "__main__":

    ips1=['10.10.10.10']
    user='user'
    passwd='test'
    time1=time.perf_counter()
    for ip in ips1:
        print(ip)
        device=radware(ip,user,passwd)
        print(device.is_alive)
        if device.is_alive:
            #cpu=device.cpu()
            #print(cpu['value'])
            #if not cpu['state']:
            #    print('cpu',cpu)
            #mem=device.memory()
            #print(mem['value'])
            #if not mem['state']:
            #    print('mem',mem)
            #power=device.power()
            #print(power['value'])
            #if not power:
            #    print('power',power)
            #uptime=device.uptime()
            #print(uptime['value'])
            #if not uptime['state']:
            #    print('uptime',uptime)
            #fan=device.fan()
            #print(fan['value'])
            #if not fan['state']:
            #    print('fan',fan)
            #print(device.temperature())
            print(device.version())
            device.close()
        else:
            print('unconnect')
    time2=time.perf_counter()
    print(time2-time1)



