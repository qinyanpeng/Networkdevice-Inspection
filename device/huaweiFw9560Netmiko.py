#华为
from netmiko import ConnectHandler
from datetime import timedelta
import re, time

class huaweiFw9560:
    def __init__(self,ip,username,password):
        self.type='huaweiFw9560',
        self.info={'device_type':'hp_comware',
                   'ip':ip,
                   'username':username,
                   'password':password}
        try:
            self.driver=ConnectHandler(**self.info,conn_timeout=10)
            self.is_alive=True
            if self.is_alive:
                self.driver.send_command("screen-length 0 temporary")
        except:
            self.is_alive=False

    #CPU巡检。
    #阈值默认值：threshold=70。取cpu1分钟利用率<阈值:返回True，否则为False
    def cpu(self,threshold=70):
        state=True
        value=[]
        self.driver.send_command("screen-length 0 temporary")
        command="display cpu-usage"
        output=self.driver.send_command(command,use_textfsm=True,read_timeout=10)
        match = re.findall(r'one minute: (\d+)%',output)
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
        value=[]
        command="display memory-usage"
        output=self.driver.send_command(command,use_textfsm=True)
        match = re.findall(r'Memory Using Percentage Is: (\d+)%',output)
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
        output=self.driver.send_command(command)
        match = re.findall(r'DC\s\s+(\w*)\s\s+',output)
        if len(match)==0:
            state=False
        else:
            for v in match:
                if v != "Normal":
                    state=False
                    break
        return {"state":state,"value":match,"info":output,"type":self.type}

    #风扇巡检
    def fan(self,threshold=90):
        state=True
        command="display fan"
        output=self.driver.send_command(command,use_textfsm=True)
        match = re.findall(r'\s(\d+)%',output)
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
        hours=-1
        state=True
        command="display version"
        output=self.driver.send_command(command,use_textfsm=True)
        match = re.findall(r'uptime is (\d+) days?, (\d+) hours?,',output)
        if len(match)==0:
            state=False
        else:
            hours=int(match[0][0])*24+int(match[0][1])
            if hours <= 12:
                state=False
        return {"state":state,"value":hours,"info":output,"type":self.type}


    def temperature(self):
        state=True
        command="display temperature lpu"
        output=''
        for i in range(0,2):
            output=self.driver.send_command(command)
            print(output)
            match = re.findall(r'(.*\d+\s+\d+.*)\n',output)
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
                if "NORMAL" not in v and ":" not in v:
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
            match = re.findall(r'(\d+\s+\w+\s+.*)',output)
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

    def version(self,threshold="V500R005C20SPC500"):
        state=True
        version="none"
        command="dis version"
        output=''
        for i in range(0,2):
            output=self.driver.send_command(command)
            match=re.search(r'[(]USG9560\s+(.*)[)]',output)
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

    Ip='10.0.2.1'
    user='test'
    passwd='test'
    time1=time.perf_counter()
    device=huaweiFw9560(Ip,user,passwd)
    print(device.is_alive)
    #device.cpu()
    #device.memory()
    #print(device.power())
    #print(device.uptime())
    #print(device.fan())
    #print(device.temperature())
    #print(device.board())
    print(device.version())
    device.close()
    time2=time.perf_counter()
    print(time2-time1)
