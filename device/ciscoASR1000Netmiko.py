from netmiko import ConnectHandler
from datetime import timedelta
import re, time

class ciscoASR1000:
    def __init__(self,ip,username,password):
        self.type='ciscoASR1000',
        self.info={'device_type':'cisco_nxos',
                   'ip':ip,
                   'username':username,
                   'password':password}
        try:
            self.driver=ConnectHandler(**self.info)
            self.is_alive=True
        except Exception as e:
            self.is_alive=False
            print(self.info['ip'],'connect failed:', e)

    #CPU巡检。
    #阈值默认值：threshold=50。取cpu1分钟利用率<阈值:返回True，否则为False
    def cpu(self,threshold=70):
        state=True
        value=[]
        command="show processes cpu | inc CPU"
        output=self.driver.send_command(command)
        match = re.findall(r'one minute:\s+(\d+)%',output)
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
        value=list()
        command="show processes memory | inc Processor"
        output=self.driver.send_command(command)
        match = re.findall(r'Processor\s+Pool\s+Total:\s(\d+)\s+Used:\s+(\d+)\s+',output)
        if len(match)==0:
            state=False
        else:
            for v in match:
                per=round((int(v[1])/int(v[0]))*100)
                value.append(int(per))
                if int(per) > threshold:
                    state=False
        return {"state":state,"value":value,"info":output,"type":self.type}

    #电源巡检
    def power(self):
        state=True
        command="show environment | inc DC"
        output=self.driver.send_command(command)
        match = re.findall(r'PEM\s+Vout\s+(\w*)\s+',output)
        if len(match)==0:
            state=False
        else:
            for v in match:
                if v.lower() != "Normal".lower():
                    state=False
                    break
        return {"state":state,"value":match,"info":output,"type":self.type}


    #风扇巡检
    def fan(self,threshold=90):
        state=True
        command="show environment | inc Fan"
        output=self.driver.send_command(command)
        match = re.findall(r'Fan\s+Speed\s+(\d+)%',output)
        if len(match)==0:
            state=False
        else:
            for v in match:
                if int(v) >= threshold:
                    state=False
                    break
        return {"state":state,"value":match,"info":output,"type":self.type}

    def uptime(self,threshold=12):
        uptime_hours=-1
        state=True
        command="show version | inc  uptime"
        output=self.driver.send_command(command)
        #match = re.findall(r'uptime\s+is\s+(\d+)\s+years?,\s+(\d+)\s+weeks?,\s+(\d+)\s+days?,\s+(d+)\s+hours?,',output)
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
        return {"state":state,"value":uptime_hours,"info":output,"type":self.type}

    def ospf(self):
        state=True
        command="show ip ospf neighbor"
        output=self.driver.send_command(command)
        match = re.findall(r'\s+(\w+)[/]\s',output)
        if len(match)==0:
            state=False
        else:
            for v in match:
                if v.lower() != "Full".lower():
                    state=False
                    break
        return {"state":state,"value":match,"info":output,"type":self.type}

    def temperature(self):
        state=True
        command="show environment all | inc Temp"
        output=''
        for i in range(0,2):
            output=self.driver.send_command(command)
            print(output)
            match=re.findall(r'\s+\w+\s+\d+\s+Celsius\n?',output)
            print(match)
            if len(match)!=0:
                state=True
                break
            else:
                print(self.info['ip'],"command:",command,'第'+str(i)+'次正则匹配失败，匹配内容(output,match)：',output,match)
                state=False
                time.sleep(10)
        if len(match)==0:
            state=False
        else:
            for v in match:
                if "Normal" not in v:
                    match=v
                    state=False
                    break
                else:
                    state=True
        return {"state":state,"value":match,"info":output,"type":self.type}

    def version(self,threshold="Version 15.5(3)S6"):
        state=True
        version="none"
        command="show version | inc SOFTWARE"
        output=''
        for i in range(0,2):
            output=self.driver.send_command(command)
            print(output)
            match=re.search(r'(Version.*),',output)
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

    Ip='10.1.2.3' 
    user='test'
    passwd='test'
    time1=time.perf_counter()
    device=ciscoASR1000(Ip,user,passwd)
    print(device.is_alive)
    #print(device.cpu())
    #print(device.memory())
    #print(device.power())
    #print(device.uptime())
    #print(device.temperature())
    #print(device.fan())
    print(device.version())
    device.close()
    time2=time.perf_counter()
    print(time2-time1)
