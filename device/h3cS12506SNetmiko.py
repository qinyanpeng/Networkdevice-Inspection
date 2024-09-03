#华三
from netmiko import ConnectHandler
from datetime import timedelta
import re, time

class h3cS12506S:
    def __init__(self,ip,username,password):
        self.type='h3cS12506S'
        self.info={'device_type':'hp_comware',
                   'ip':ip,
                   'username':username,
                   'password':password}
        try:
            self.driver=ConnectHandler(**self.info)
            self.is_alive=True
        except Exception as e:
            self.is_alive=False
            print(self.info['ip'],'connect failed:', e)

    #执行命令，返回回显
    def command(self,command):
        output=''
        for i in range(1,3):
            try:
                output=self.driver.send_command(command,read_timeout=20)
                break
            except Exception as e:
                print(self.info['ip'],'command failed:',i, e)
            time.sleep(10)
        return output


    #CPU巡检。
    #阈值默认值：threshold=50。取cpu1分钟利用率<阈值:返回True，否则为False
    def cpu(self,threshold=70):
        state=True
        match=''
        output=''
        value=[]
        command="display cpu-usage"
        for i in range(0,3):
            #output=self.driver.send_command(command,read_timeout=10)
            output=self.command(command)            
            match = re.findall(r'(\d+)% in last 1 minute',output)
            if len(match)>0:
                state=True
                break
            else:
                state=False
                time.sleep(5)
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
    def memory(self,threshold=80):
        state=True
        match=''
        output=''
        value=list()
        command="display memory"
        for i in range(0,3):
            #output=self.driver.send_command(command,read_timeout=10)
            output=self.command(command)
            match = re.findall(r'(\d+\.\d+)?%',output)
            if len(match)>0:
                state=True
                break
            else:
                state=False
                time.sleep(5)
        if len(match)>0:
            for v in match:
                v=round(100-float(v),1)
                value.append(int(v))
                if v > threshold:
                    state=False
        return {"state":state,"value":value,"info":output,"type":self.type}

    #电源巡检
    def power(self):
        state=True
        match=''
        output=''        
        command="display power"
        for i in range(0,3):
            #output=self.driver.send_command(command,read_timeout=10)
            output=self.command(command)
            #match = re.findall(r'\d\s+(\w+)\s+AC',output)
            match = re.findall(r'\s+\d+\s+(\w+)\s+.*\n',output)
            if len(match)>0:
                state=True
                break
            else:
                state=False
                time.sleep(5)
        if len(match)>0:
            for v in match:
                if "Normal" != v:
                    state=False
                    break
        return {"state":state,"value":match,"info":output,"type":self.type}


    #风扇巡检
    def fan(self):
        state=True
        match=''
        output=''
        command="display fan"
        for i in range(0,3):
            #output=self.driver.send_command(command,read_timeout=10)
            output=self.command(command)
            match = re.findall(r'State:\s+(\w+)',output)
            if len(match)>0:
                state=True
                break
            else:
                state=False
                time.sleep(5)
        if len(match)>0:
            for v in match:
                if v != "Normal":
                    state=False
                    break
        return {"state":state,"value":match,"info":output,"type":self.type}


    #设备启动时间
    def uptime(self,threshold=12):
        uptime_hours=-1
        match=''
        output=''
        state=False
        command="display version"

        for i in range(1,4):
            output=self.command(command)
            match = re.findall(r'(Uptime .*)\n',output)
            if len(match)!=0:
                break
            print(self.info['ip'],'命令：',command,'第'+str(i)+'次正则匹配失败，匹配内容(output,match)：',output,match)

        if len(match)!=0:
            for m in match:
                years=re.search(r'(\d+)\s+years?',m)
                weeks=re.search(r'(\d+)\s+weeks?',m)
                days=re.search(r'(\d+)\s+days?',m)
                hours=re.search(r'(\d+)\s+hours?',m)
                minutes=re.search(r'(\d+)\s+minutes?',m)
                if years or weeks or days or hours or minutes:
                    uptime_hours=0
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
                    break
                else:
                    state=True
        return {"state":state,"value":uptime_hours,"info":output,"type":self.type}


    #m-lag状态
    def mlag(self):
        state=True
        match='None'
        output='None'
        command="display m-lag role"
        for i in range(0,3):
            output=self.command(command)
            print(output)
            match1 = re.search(r'Effective role\s+(\w+)\s+(\w+)\n',output)
            match2 = re.search(r'Role priority\s+(\d+)\s+(\d+)\n',output)
            if match1 and match2:
                state=True
                break
            else:
                state=False
                self.reconnect()
        if match1 and match2:
            if (match1.group(1)=="Primary" and match2.group(1)=="100") and (match1.group(2)=="Secondary" and match2.group(2)=="200"):
                state=True
            elif (match1.group(1)=="Secondary" and match2.group(1)=="200") and (match1.group(2)=="Primary" and match2.group(2)=="100"):
                state=True
            else:
                state=False
        return {"state":state,"value":[match1,match2],"info":output,"type":self.type}

    #OSPF的状态
    def ospf(self):
        state=True
        command="dis ospf peer"
        output=self.command(command)
        match = re.findall(r'\s+(\w+)[/]\s',output)
        if len(match)==0:
            state=False
        else:
            for v in match:
                if v.lower() != "Full".lower():
                    state=False
                    break
        return {"state":state,"value":match,"info":output,"type":self.type}


    #温度
    def temperature(self):
        state=True
        match='None'
        output='None'
        command="display environment"
        for i in range(0,3):
            output=self.command(command)
            match = re.findall(r'\d+\s+\w+\s+\d+\s+(\d+)\s+\d+\s+(\d+)\s+\d+\s+NA\s+\n',output)
            if len(match)>0:
                state=True
                break
            else:
                state=False
                self.reconnect()
        if len(match)>0:
            for m in match:
                if int(m[0])>int(m[1]):
                    state=False
                    break
        return {"state":state,"value":match,"info":output,"type":self.type}

    #板卡状态
    def board(self):
        state=True
        match='None'
        output='None'
        command="display device"
        for i in range(0,3):
            output=self.command(command)
            match = re.findall(r'\d+\s+(\w+)\s+(\w+)\s+\d+\s+',output)
            if len(match)>0:
                state=True
                break
            else:
                state=False
                self.reconnect()
        if len(match)>0:
            for m in match:
                if m[0]!="NONE" and m[1] not in ["Normal","Master","Standby"]:
                    state=False
                    break
                else:
                    state=True
        return {"state":state,"value":match,"info":output,"type":self.type}

    def version(self,threshold="Version 7.1.070"):
        state=True
        match='None'
        output='None'
        version='none'
        command="display version"
        for i in range(0,3):
            output=self.command(command)
            match = re.search(r'(Version\s+.*),',output)
            #match = re.search(r'({})'.format(threshold),output)
            print(match)
            if match:
                version=match.group(1)
                break
            else:
                state=False
                self.reconnect()
        if match:
            if version.replace(" ","")==threshold.replace(" ",""):
                state=True
            else:
                state=False
        return {"state":state,"value":version,"info":output,"type":self.type}


    def close(self):
        self.driver.disconnect() 

if __name__ == "__main__":

    ips=['10.1.2.3']
    user='test'
    passwd='test'
    time1=time.perf_counter()
    for ip in Ip:
        print(ip)
        device=h3cS12506S(ip,user,passwd)
        if device.is_alive:
            #cpu=device.cpu()
            #print(cpu)
            #if not cpu['state']:
            #    print('cpu',cpu)
            #mem=device.memory()
            #print(mem)
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
            #print(device.temperature())
            #print(device.board())
            print(device.version())
            device.close()
        else:
            print('unconnect')
    time2=time.perf_counter()
    print(time2-time1)
