#华三
from netmiko import ConnectHandler
from datetime import timedelta
import re, time

class h3cF1070:
    def __init__(self,ip,username,password):
        self.type="h3cF1070"
        self.info={'device_type':'hp_comware',
                   'ip':ip,
                   'username':username,
                   'password':password}
        try:
            self.driver=ConnectHandler(**self.info)
            self.is_alive=True
        except:
            self.is_alive=False


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

    #CPU巡检。
    #阈值默认值：threshold=50。取cpu1分钟利用率<阈值:返回True，否则为False
    def cpu(self,threshold=70):
        state=True
        output=None
        match=None
        value=[]
        command="display cpu-usage"
        #output=self.driver.send_command(command,use_textfsm=True)
        output=self.command(command)
        match = re.findall(r'(\d+)% in last 1 minute',output)
        if len(match)==0:
            state=False
        else:
            for v in match:
                value.append(int(v))
                if int(v) > threshold:
                    state=False
        return {"state":state,"value":value,"info":output,"type":self.type}

    
    #内存巡检。
    #阈值默认值：threshold=80。取内存利用率<阈值:返回True，否则为False
    def memory(self,threshold=60):
        state=True
        output=None
        value=list()
        command="display memory"
        output=self.driver.send_command(command,use_textfsm=True)
        match = re.findall(r'(\d+\.\d+)?%',output)
        if len(match)==0:
            state=False
        else:
            for v in match:
                v=round(100-float(v))
                value.append(int(v))
                if v > threshold:
                    state=False
        return {"state":state,"value":value,"info":output,"type":self.type}

    #电源巡检
    def power(self):
        state=True
        output=None
        match=None
        command="display power"
        output=self.driver.send_command(command,use_textfsm=True)
        match = re.findall(r'Status:\s+(\w+)\s+',output)
        if len(match)==0:
            state=False
        else:
            for v in match:
                if v.lower() != "Normal".lower():
                    state=False
                    break
        return {"state":state,"value":match,"info":output,"type":self.type}


    #风扇巡检
    def fan(self):
        state=True
        output=None
        match=None
        command="display fan"
        output=self.driver.send_command(command,use_textfsm=True)
        match = re.findall(r'Status:\s+(\w+)\s+',output)
        if len(match)==0:
            state=False
        else:
            for v in match:
                if v.lower() != "Normal".lower():
                    state=False
                    break
        return {"state":state,"value":match,"info":output,"type":self.type}

    def uptime(self,threshold=12):
        hours=-1
        state=True
        command="display version | inc day"
        output=self.driver.send_command(command,use_textfsm=True)
        match = re.findall(r'H3C\s+SecPath\s+F1070\s+uptime\s+is\s+(\d+) weeks?,\s+(\d+)\s+days?,\s+(\d+)\s+hours?,',output)
        if len(match)==0:
            state=False
        else:
            hours=int(match[0][0])*7*24+int(match[0][1])*24+int(match[0][2])
            if hours <= 12:
                state=False
        return {"state":state,"value":hours,"info":output,"type":self.type}

    #温度
    def temperature(self):
        state=True
        match='None'
        output='None'
        command="display environment"
        for i in range(0,3):
            output=self.command(command)
            match = re.findall(r'\d+\s+\w+\s+\d+\s+(\d+)\s+\-?\d+\s+(\d+)\s+\d+\s+NA\n',output)
            print(match)
            if len(match)>0:
                state=True
                break
            else:
                state=False
    #            self.reconnect()
        if len(match)>0:
            for m in match:
                if int(m[0])>int(m[1]):
                    state=False
                    break
        return {"state":state,"value":match,"info":output,"type":self.type}

    def version(self,threshold="Version 7.1.070"):
        state=True
        match='None'
        output='None'
        version='none'
        command="display version | inc Version"
        for i in range(0,1):
            output=self.command(command)
            match = re.search(r'(Version\s+.*),',output)
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

if __name__ == "__main__":

    Ip='10.1.2.3'
    user='user'
    passwd='test'
    time1=time.perf_counter()
    device=h3cF1070(Ip,user,passwd)
    #print(device.is_alive)
    #print(device.cpu())
    #print(device.memory())
    ##print(device.power())
    #print(device.uptime())
    #print(device.fan())
    #print(device.temperature())
    print(device.version())
    device.close()
    time2=time.perf_counter()
    print(time2-time1)
