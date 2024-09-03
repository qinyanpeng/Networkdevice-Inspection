#华为
from netmiko import ConnectHandler
from datetime import timedelta
import re, time

class huaweiUSG6300E:
    def __init__(self,ip,username,password):
        self.type='huaweiUSG6300E'
        self.info={'device_type':'hp_comware',
                   'ip':ip,
                   'username':username,
                   'password':password}
        #self.driver=ConnectHandler(**self.info,conn_timeout=10)
        try:
            self.driver=ConnectHandler(**self.info,conn_timeout=10)
            self.is_alive=True
            if self.is_alive:
                self.driver.send_command("screen-length 0 temporary")
        except:
            self.is_alive=False

    #执行命令，返回回显
    def command(self,command):
        output=''
        for i in range(0,3):
            try:
                output=self.driver.send_command(command,use_textfsm=True,read_timeout=20)
                state=True
                break
            except:
                state=False
            time.sleep(10)
        return output

    #CPU巡检。
    #阈值默认值：threshold=70。取cpu1分钟利用率<阈值:返回True，否则为False
    def cpu(self,threshold=70):
        state=True
        command="display cpu-usage"
        output=''
        value=[]
        for i in range(0,3):
            output=self.command(command)
            match = re.findall(r'one\s+minute:\s+(\d+.\d)%\s',output)
            if len(match)!=0:
                break
        if len(match)==0:
            state=False
        else:
            for v in match:
                value.append(float(v))
                if float(v) > threshold:
                    state=False
        return {"state":state,"value":value,"info":output,"type":self.type}

    
    #内存巡检。
    #阈值默认值：threshold=70。取内存利用率<阈值:返回True，否则为False
    def memory(self,threshold=70):
        state=True
        command="display memory-usage"
        output=''
        value=[]
        for i in range(0,3):
            output=self.command(command)
            match = re.findall(r'Memory Using Percentage Is: (\d+)%',output)
            if len(match)!=0:
                break
        if len(match)==0:
            state=False
        else:
            for v in match:
                value.append(float(v))
                if float(v) > threshold:
                    state=False
        return {"state":state,"value":value,"info":output,"type":self.type}

    #电源巡检
    def power(self):
        state=True
        command="display power"
        output=''
        for i in range(0,3):
            output=self.command(command)
            match = re.findall(r'AC\s+(\w+)\s+',output)
            if len(match)!=0:
                break
        if len(match)==0:
            state=False
        else:
            for v in match:
                if v != "Supply":
                    state=False
                    break
        return {"state":state,"value":match,"info":output,"type":self.type}

    #风扇巡检
    def fan(self,threshold=90):
        state=True
        command="display fan"
        output=''
        for i in range(0,3):
            output=self.command(command)
            match = re.findall(r'\s(\d+)%',output)
            if len(match)!=0:
                break
        if len(match)==0:
            state=False
        else:
            for v in match:
                if int(v) > threshold:
                    state=False
                    break
        return {"state":state,"value":match,"info":output,"type":self.type}

    #设备启动时间
    def uptime(self,threshold=12):
        uptime_hours=-1
        state=True
        command="display version | include uptime"
        output=self.driver.send_command(command,use_textfsm=True)
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

    def temperature(self):
        state=True
        command="display temperature all"
        output=''
        for i in range(0,2):
            output=self.command(command)
            print(output)
            match = re.findall(r'(.*\d+\s+\-\s+.*)\n',output)
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
                    state=False
                    break
                else:
                    state=True
        return {"state":state,"value":match,"info":output,"type":self.type}

    #板卡状态
    def board(self):
        state=True
        match='None'
        output='None'
        command="display device"
        for i in range(0,2):
            output=self.driver.send_command(command)
            match = re.findall(r'(\d+\s+\-\s+.*)',output)
            if len(match)>0:
                state=True
                break
            else:
                state=False
        if len(match)>0:
            for m in match:
                if "Normal" not in m:
                    match=m
                    state=False
                    break
                else:
                    state=True
        return {"state":state,"value":match,"info":output,"type":self.type}

    def version(self,threshold="V600R007C20SPC600"):
        state=True
        version="none"
        command="dis version"
        output=''
        for i in range(0,2):
            output=self.driver.send_command(command)
            match=re.search(r'[(]USG6500E\s+(.*)[)]',output)
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
    device=huaweiUSG6300E(Ip,user,passwd)
    print(device.is_alive)
    #print(device.cpu()['value'])
    #print(device.memory()['value'])
    #print(device.power()['value'])
    #print(device.uptime()['value'])
    #print(device.fan()['value'])
    #print(device.temperature())
    #print(device.board())
    print(device.version())
    device.close()
    time2=time.perf_counter()
    print(time2-time1)
