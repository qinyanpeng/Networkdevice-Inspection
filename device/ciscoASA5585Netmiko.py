from netmiko import ConnectHandler
from datetime import timedelta
import re, time

class ciscoASA5585:
    def __init__(self,ip,username,password):
        self.type='ciscoASA5585',
        self.info={'device_type':'cisco_asa',
                   'ip':ip,
                   'username':username,
                   'password':password,
                   'secret':password}
        try:
            self.driver=ConnectHandler(**self.info)
            self.driver.enable()
            self.is_alive=True
        except:
            self.is_alive=False

    #执行命令，返回回显
    def command(self,command):
        output=''
        for i in range(0,3):
            try:
                output=self.driver.send_command(command,read_timeout=20)
                state=True
                break
            except:
                state=False
            time.sleep(10)
        return output

    #CPU巡检。
    #阈值默认值：threshold=50。取cpu1分钟利用率<阈值:返回True，否则为False
    def cpu(self,threshold=60):
        state=True
        value=[]
        command="show cpu"
        for i in range(0,3):
            output=self.command(command)
            match = re.findall(r'minute:\s+(\d+)%',output)
            if len(match)>0:
                break
        if len(match)==0:
            state=False
        else:
            for v in match:
                value.append(int(v))
                if int(v) > threshold:
                    state=False
        return {"state":state,"value":value,"info":output,"type":self.type}

    
    #内存巡检。
    #阈值默认值：threshold=70。取内存利用率<阈值:返回True，否则为False
    def memory(self,threshold=60):
        state=True
        value=[]
        command="show memory | inc Used"
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
        value=list()
        command="show environment power-supplies"
        for i in range(0,3):
            output=self.command(command)
            match = re.search(r'Power Input:\n\s+-+\n\s+Left\s+Slot\s+[(]PS0[)]:\s+(\w+)\n\s+Right\s+Slot\s+[(]PS1[)]:\s+(\w+)\n',output)
            if match:
                break
        if match:
            value.append(match.group(1))
            value.append(match.group(2))
            if match.group(1).lower() != "OK".lower() or match.group(2).lower() != "OK".lower():
                state=False
        else:
            state=False
        return {"state":state,"value":value,"info":output,"type":self.type} 


    #风扇巡检
    def fan(self):
        state=True
        command="show environment fans"
        for i in range(0,3):
            output=self.command(command)
            match = re.findall(r'RPM\s+-\s+(\w+)\s+',output)
            if len(match)>0:
                break
            else:
                state=False
        if len(match)==0:
            state=False
        else:
            for v in match:
                if v.lower() != "OK".lower():
                    state=False
                    break
        return {"state":state,"value":match,"info":output,"type":self.type}

    def uptime(self,threshold=12):
        uptime_hours=0
        state=True
        command="show version | inc up"
        for i in range(0,3):
            output=self.command(command)
            if output:
                outputsplit=output.split("\n")
                for l in outputsplit:
                    if "failover" in l:
                        outputsplit.remove(l)
                output="\n".join(outputsplit)
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
                break
            else:
                state=False
        if uptime_hours<=threshold:
            state=False
        return {"state":state,"value":uptime_hours,"info":output,"type":self.type}

    def temperature(self):
        state=True
        command="show environment temperature | inc Temperature "
        output=''
        for i in range(0,2):
            output=self.driver.send_command(command)
            print(output)
            match=re.findall(r'(.*-.*)',output)
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
                if "OK" not in v:
                    match=v
                    state=False
                    break
                else:
                    state=True
        return {"state":state,"value":match,"info":output,"type":self.type}

    def version(self,threshold="Version 9.8(4.20)"):
        state=True
        version="none"
        command="show version | inc Version"
        output=''
        for i in range(0,2):
            output=self.driver.send_command(command)
            print(output)
            match=re.search(r'Software\s+(Version.*)\n',output)
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
    device=ciscoASA5585(Ip,user,passwd)
    print(device.is_alive)
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
