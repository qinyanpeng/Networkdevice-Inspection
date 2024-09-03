from netmiko import ConnectHandler
from datetime import timedelta
import re, time

class riverbed:
    def __init__(self,ip,username,password):
        self.type='riverbed'
        self.info={'device_type':'cisco_ios',
                   'ip':ip,
                   'username':username,
                   'password':password}
        for i in range(1,3):
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
        for i in range(1,3):
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
        command='show version'
        for i in range(0,3):
            output=self.command(command)
            match = re.findall(r'CPU load averages:\s+(\d+.\d+)\s+/',output)
            if len(match)!=0:
                break
        if len(match)==0:
            state=False
        else:
            for v in match:
                value.append(float(v))
                if float(v) > threshold:
                    state=False
        return {"state":state,"value":match,"info":output,"type":self.type}

    #内存。
    #阈值默认值：threshold=80。取内存利用率<阈值:返回True，否则为False
    def memory(self,threshold=80):
        state=True
        match=''
        output=''
        value=[]
        command='show version'
        value=''
        for i in range(0,3):
            output=self.command(command)
            match = re.search(r'System memory:\s+(\d+)\s+MB\s+used\s+/\s+\d+\s+MB\s+free\s+/\s+(\d+)\s+MB\s+total',output)
            if match:
                break
        if match:
            value=round(int(match.group(1))/int(match.group(2))*100)
            if int(value) > threshold:
                state=False
        else:
            state=False
        return {"state":state,"value":[int(value)],"info":output,"type":self.type}

    #电源巡检
    def power(self):
        state=True
        match='-'
        return {"state":state,"value":match,"info":"-","type":self.type}

    #设备启动时间
    def uptime(self,threshold=12):
        uptime_hours=-1
        output=''
        match=''
        command='show version'
        state=True
        for i in range(1,4):
            output=self.command(command)
            days=re.search(r'(\d+)d',output)
            hours=re.search(r'(\d+)h',output)
            mins=re.search(r'(\d+)m',output)
            if mins or days or hours:
                uptime_hours=0
                break
        if mins:
            uptime_hours = 0
        if days:
            uptime_hours = uptime_hours + int(days.group(1))*24
        if hours:
            uptime_hours = uptime_hours + int(hours.group(1))
        if int(uptime_hours)<=12:
            state=False
        return {"state":state,"value":uptime_hours,"info":output,"type":self.type}

    #风扇巡检
    def fan(self):
        state=True
        match=list()
        output=''
        command='show stats fan'
        value=list()
        for i in range(0,3):
            output=self.command(command)
            match = re.findall(r'\d+\s+\d+\s+\d+\s+(\w+)',output)
            if len(match)!=0:
                break
        if len(match)==0:
            state=False
        else:
            for v in match:
                if v != 'ok':
                    state=False
        return {"state":state,"value":match,"info":output,"type":self.type}


    def close(self):
        self.driver.disconnect()


#主程序入口
if __name__ == "__main__":

    ips=['10.10.10.10']
    user='uuuu'
    passwd='passwd'
    time1=time.perf_counter()
    for ip in ips:
        print(ip)
        device=riverbed(ip,user,passwd)
        print(device.is_alive)
        if device.is_alive:
            cpu=device.cpu()
            print(cpu)
            #if not cpu['state']:
            #    print('cpu',cpu)
            mem=device.memory()
            print(mem)
            #if not mem['state']:
            #    print('mem',mem)
            #power=device.power()
            #print(power)
            #if not power:
            #    print('power',power)
            #uptime=device.uptime()
            #print(uptime)
            #if not uptime['state']:
            #    print('uptime',uptime)
            #fan=device.fan()
            #print(fan)
            #if not fan['state']:
            #    print('fan',fan)
            device.close()
        else:
            print('unconnect')
    time2=time.perf_counter()
    print(time2-time1)



