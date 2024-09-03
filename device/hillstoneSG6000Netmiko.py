#山石
from netmiko import ConnectHandler
from datetime import timedelta
import re, time

class hillstoneSG6000:
    def __init__(self,ip,username,password):
        self.type='hillstoneSG6000'
        self.info={'device_type':'cisco_nxos',
                   'ip':ip,
                   'username':username,
                   'password':password}
        try:
            self.driver=ConnectHandler(**self.info)
            self.is_alive=True
        except Exception as e:
            print(e)
            self.is_alive=False

    #CPU巡检。
    #阈值默认值：threshold=50。取cpu1分钟利用率<阈值:返回True，否则为False
    def cpu(self,threshold=70):
        state=True
        value=[]
        command="show cpu"
        output=self.driver.send_command(command)
        match = re.findall(r'Last\s+1\s+minute\s+:[ ]{0,5}(\d+.\d+)%',output)
        if len(match)==0:
            state=False
        else:
            for v in match:
                value.append(float(v))
                if float(v) > threshold:
                    state=False
        return {"state":state,"value":value,"info":output,"type":self.type}

    
    #内存巡检。
    #阈值默认值：threshold=80。取内存利用率<阈值:返回True，否则为False
    def memory(self,threshold=60):
        state=True
        value=list()
        command="show memory"
        output=self.driver.send_command(command)
        match = re.findall(r'The\s+percentage\s+of\s+memory\s+utilization:\s+(\d+)%',output)
        if len(match)==0:
            state=False
        else:
            for v in match:
                value.append(int(v))
                if int(v) > threshold:
                    state=False
                    break
        return {"state":state,"value":value,"info":output,"type":self.type}

    #电源巡检
    def power(self):
        state=True
        command="show environment | inc PS"
        output=self.driver.send_command(command)
        match = re.findall(r'PS\d+\s+(\w+)',output)
        if len(match)==0:
            state=False
        else:
            for v in match:
                if v.lower() != "fine".lower():
                    state=False
                    break
        return {"state":state,"value":match,"info":output,"type":self.type}    


    #风扇巡检
    def fan(self,threshold='fine'):
        state=True
        command="show environment | inc Fan"
        output=self.driver.send_command(command)
        match = re.findall(r'Fan\d?\s\s+(\w+)',output)
        if len(match)==0:
            state=False
        else:
            for v in match:
                if v.lower() != threshold.lower(): 
                    state=False
                    break
        return {"state":state,"value":match,"info":output,"type":self.type}

    def uptime(self,threshold=12):
        uptime_hours=-1
        state=True
        command="show version | inc  Uptime"
        output=self.driver.send_command(command)
        if output:
            uptime_hours=0
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

    #温度巡检
    def temperature(self):
        state=True
        command="show environment"
        output=self.driver.send_command(command)
        match = re.findall(r'\s+(\d+)\s+(\d+)-(\d+)',output)
        if len(match)==0:
            state=False
        else:
            for v in match:
                if int(v[0])<int(v[1]) or int(v[0])>int(v[2]):
                    match=v
                    state=False
                    break
        return {"state":state,"value":match,"info":output,"type":self.type}

    def version(self,threshold="Version 5.5"):
        state=True
        version="none"
        command="show version"
        output=''
        for i in range(0,2):
            output=self.driver.send_command(command)
            print(output)
            match=re.search(r'(Version.*)',output)
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

    Ip='10.1.2.5' #SG6000
    user='test'
    passwd='test'
    time1=time.perf_counter()
    device=hillstoneSG6000(Ip,user,passwd)
    #print(device.is_alive)
    #print(device.cpu())
    #print(device.memory())
    #print(device.power())
    #print(device.uptime())
    #print(device.fan())
    #print(device.temperature())
    print(device.version())
    device.close()
    time2=time.perf_counter()
    print(time2-time1)
