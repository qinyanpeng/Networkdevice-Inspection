#ZDNS设备
from netmiko import ConnectHandler
from datetime import timedelta
import re, time, base64

class ZDNS:
    def __init__(self,ip,username,password):
        self.type='ZDNS'
        self.output=None
        self.info={'device_type':'linux',
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
        self.output=self.command('top -n 1')

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
        value=''
        for i in range(0,3):
            matchline=re.search(r'(Cpu.*\n)',self.output)
            match = re.search(r'(\d+.\d+)%',matchline.group(1))
            if match:
                break
        if match:
            value=float(match.group(1))
            if value > threshold:
                state=False
        else:
            state=False
        return {"state":state,"value":[value],"info":match,"type":self.type}

    #内存。
    #阈值默认值：threshold=80。取内存利用率<阈值:返回True，否则为False
    def memory(self,threshold=80):
        state=True
        match=''
        value=''
        for i in range(1,4):
            matchline = re.search(r'(Mem.*\n)',self.output)
            match = re.findall(r'(\d+)k',matchline.group(1))
            matchline1 = re.search(r'(Swap.*\n)',self.output)
            match1 = re.findall(r'(\d+)k',matchline1.group(1))
            if match:
                break
        if match and match1:
            value=round((int(match[1])-int(match[3])-int(match1[3]))/int(match[0])*100)
            if int(value) > threshold:
                state=False
        else:
            state=False
        return {"state":state,"value":[value],"info":match,"type":self.type}


    #设备启动时间
    def uptime(self,threshold=12):
        uptime_hours=-1
        match=''
        state=True
        for i in range(1,4):
            output=self.output
            match=re.search(r'up\s+(\d+)',output)
            if match:
                match_min=re.search(r'up\s+(\d+)\s+min,',output)
                match_days=re.search(r'up\s+(\d+)\s+days?,',output)
                match_hours=re.search(r'\s+(\d+):\d+,',output)
                uptime_hours=0
                break
            else:
                state=False
        if match_min:
            uptime_hours=0
            state=False
        if match_hours:
            uptime_hours = int(match_hours.group(1))
        if match_days:
            uptime_hours = uptime_hours+int(match_days.group(1))*24
        if int(uptime_hours)<=12:
            state=False
        info=[match,match_min,match_days,match_hours]
        return {"state":state,"value":uptime_hours,"info":info,"type":self.type}


    #电源巡检
    def power(self):
        state=True
        return {"state":state,"value":"-","info":"-","type":self.type}


    #风扇巡检
    def fan(self):
        state=True
        return {"state":state,"value":"-","info":"-","type":self.type}


    #温度巡检
    def temperature(self):
        state=True
        return {"state":state,"value":"-","info":"-","type":self.type}


    def version(self,threshold="3.11.2.13"):
        state=True
        match='None'
        output='None'
        version='none'
        command="display systeminfo"
        for i in range(0,3):
            output=self.command(command)
            match = re.search(r'[(](.*)[)]',output)
            #match = re.search(r'({})'.format(threshold),output)
            print(match)
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

    ips1=['10.0.10.10']
    user='uuuu'
    ZDNSPasswd='passwd'
    passwd=base64.b64decode(ZDNSPasswd)
    print(passwd)
    time1=time.perf_counter()
    for ip in ips1:
        print(ip)
        device=ZDNS(ip,user,passwd)
        print(device.is_alive)
        if device.is_alive:
            cpu=device.cpu()
            print(cpu)
            #if not cpu['state']:
            #    print('cpu',cpu['value'])
            mem=device.memory()
            print(mem)
            #if not mem['state']:
            #    print('mem',mem['value'])
            #power=device.power()
            #print(power)
            #if not power:
            #    print('power',power)
            uptime=device.uptime()
            print(uptime)
            #if not uptime['state']:
            #    print('uptime',uptime)
            #fan=device.fan()
            #print(fan)
            #if not fan['state']:
            #    print('fan',fan)
            print(device.version())
            device.close()
        else:
            print('unconnect')
    time2=time.perf_counter()
    print(time2-time1)



