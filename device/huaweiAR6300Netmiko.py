#华为
from netmiko import ConnectHandler
from datetime import timedelta
import re, time

class huaweiAR6300:
    def __init__(self,ip,username,password):
        self.type='huaweiAR6300'
        self.info={'device_type':'hp_comware',
                   'ip':ip,
                   'username':username,
                   'password':password}
        #self.driver=ConnectHandler(**self.info,conn_timeout=10)
        try:
            self.driver=ConnectHandler(**self.info,conn_timeout=10)
            self.is_alive=True
            #if self.is_alive:
            self.driver.send_command("screen-length 0 temporary")
        except Exception as e:
            self.is_alive=False
            print(self.info['ip'],'connect failed:', e)

    #重新连接设备
    def reconnect(self):
        self.close()
        time.sleep(5)
        try:
            self.driver=ConnectHandler(**self.info,conn_timeout=10)
            self.is_alive=True
            self.driver.send_command("screen-length 0 temporary")
        except Exception as e:
            self.is_alive=False
            print(self.info['ip'],'reconnect failed:', e)
        time.sleep(3)

    #执行命令，返回回显
    def command(self,command):
        output=''
        for i in range(0,3):
            try:
                output=self.driver.send_command(command,use_textfsm=True,read_timeout=20)
                break
            except Exception as e:
                print(self.info['ip'],command,'command failed:',i, e)
            time.sleep(3)
        return output

    #CPU巡检。
    #阈值默认值：threshold=70。取cpu1分钟利用率<阈值:返回True，否则为False
    def cpu(self,threshold=70):
        state=True
        command="display cpu-usage"
        value=[]
        output=''
        for i in range(0,4):
            output=self.command(command)
            match = re.findall(r'one\s+minute:\s+(\d+.\d)%\s',output)
            if len(match)>0:
                state=True
                for v in match:
                    value.append(float(v))
                    if float(v) > threshold:
                        state=False
                        break
                break
            else:
               print(self.info['ip'],"command:",command,'第'+str(i)+'次正则匹配失败，匹配内容(output,match)：',output,match)
               state=False
               self.reconnect()
               time.sleep(5)
        return {"state":state,"value":value,"info":output,"type":self.type}

    
    #内存巡检。
    #阈值默认值：threshold=80。取内存利用率<阈值:返回True，否则为False
    def memory(self,threshold=60):
        state=True
        command="display memory-usage"
        value=[]
        output=''
        for i in range(0,5):
            output=self.command(command)
            match = re.findall(r'Memory Using Percentage Is: (\d+)%',output)
            if len(match)!=0:
                state=True
                break
            else:
                time.sleep(5)
                print(self.info['ip'],"command:",command,'第'+str(i)+'次正则匹配失败，匹配内容(output,match)：',output,match)
                state=False
                self.reconnect()
                time.sleep(2)

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
        match=list()
        output=''
        for i in range(0,5):
            output=self.command(command)
            match = re.findall(r'\s\s+\d+\s\s+(\w*)\s\s+AC',output)
            if len(match)!=0:
                state=True
                break
            else:
                print(self.info['ip'],"command:",command,'第'+str(i)+'次正则匹配失败，匹配内容(output,match)：',output,match)
                state=False
                self.reconnect()
        if len(match)==0:
            state=False
        else:
            for v in match:
                if v != "YES":
                    state=False
                    break
        return {"state":state,"value":match,"info":output,"type":self.type}

    #风扇巡检
    def fan(self,threshold=90):
        state=True
        command="display fan"
        output=''
        for i in range(0,5):
            output=self.command(command)
            match = re.findall(r'\s(\d+)%',output)
            if len(match)!=0:
                state=True
                break
            else:
                print(self.info['ip'],"command:",command,'第'+str(i)+'次正则匹配失败，匹配内容(output,match)：',output,match)
                state=False
                self.reconnect()
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
        command="display version"
        output=''
        for i in range(0,8):
            output=self.driver.send_command(command,use_textfsm=True)
            match = re.findall(r'(uptime.*)\n',output)
            if len(match)!=0:
                state=True
                break
            else:
                print(self.info['ip'],"command:",command,'第'+str(i)+'次正则匹配失败，匹配内容(output,match)：',output,match)
                state=False
            self.reconnect()
        if len(match)!=0:
            for v in match:
                uptime_hours=0
                years=re.search(r'(\d+)\s+years?',v)
                weeks=re.search(r'(\d+)\s+weeks?',v)
                days=re.search(r'(\d+)\s+days?',v)
                hours=re.search(r'(\d+)\s+hours?',v)
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

    #BGP状态和运行时间
    def bgp(self):
        state=True
        uptime_hours=-1
        uptime_list=[]
        command="dis bgp peer"
        for i in range(0,8):
            output=self.driver.send_command(command)
            match = re.findall(r'(\d+.\d+.\d+.\d+\s+\d+\s+\d+.*)',output)
            if len(match)==0:
                state=False
                print(self.info['ip'],"command:",command,'第'+str(i)+'次正则匹配失败，匹配内容(output,match)：',output,match)
            else:
                state=True
                break
            self.reconnect()
        if len(match)>0:
            for v in match:
                if  "Established" not in v:
                    state=False
                    break
                hours=re.search(r'(\d+)h',v)
                minutes=re.search(r'(\d+)m',v)
                if minutes or hours:
                    uptime_hours=0
                if hours:
                    uptime_hours = uptime_hours + int(hours.group(1))
                uptime_list.append(uptime_hours)
                if int(uptime_hours)<=12:
                    state=False
                    break
                else:
                    state=True
        return {"state":state,"value":[uptime_list,match],"info":output,"type":self.type}

    #OSPF
    def ospf(self):
        state=True
        command="dis ospf peer bri"
        output=''
        for i in range(0,8):
            output=self.command(command)
            match = re.findall(r'(\d+.\d+.\d+.\d+.*\d+.\d+.\d+.\d+.*)\n',output)
            if len(match)!=0:
                state=True
                break
            else:
                print(self.info['ip'],"command:",command,'第'+str(i)+'次正则匹配失败，匹配内容(output,match)：',output,match)
                state=False
            self.reconnect()
        if len(match)==0:
            state=False
        else:
            for v in match:
                if "Full" not in v:
                    state=False
                    break
        return {"state":state,"value":match,"info":output,"type":self.type}


    def temperature(self):
        state=True
        command="display temperature all"
        output=''
        for i in range(0,5):
            output=self.command(command)
            #print(output)
            match = re.findall(r'(.*\d+\s+)\n',output)
            if len(match)!=0:
                state=True
                break
            else:
                print(self.info['ip'],"command:",command,'第'+str(i)+'次正则匹配失败，匹配内容(output,match)：',output,match)
                state=False
            self.reconnect()
        if len(match)==0:
            state=False
        else:
            for v in match:
                if "NORMAL" not in v:
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
        for i in range(0,5):
            output=self.command(command)
            match = re.findall(r'(\d+\s+.*)',output)
            if len(match)>0:
                state=True
                break
            else:
                state=False
                print(self.info['ip'],"command:",command,'第'+str(i)+'次正则匹配失败，匹配内容(output,match)：',output,match)
            self.reconnect()

        if len(match)>0:
            for m in match:
                if "Normal" not in m:
                    match=m
                    state=False
                    break
                else:
                    state=True
        return {"state":state,"value":match,"info":output,"type":self.type}

    def version(self,threshold="V300R023C00SPC100"):
        state=True
        version="none"
        command="dis version"
        output=''
        for i in range(0,5):
            output=self.driver.send_command(command)
            #print(output)
            match=re.search(r'[(]AR6300\s+(.*)[)]',output)
            if match:
                state=True
                version=match.group(1)
                break
            else:
                print(self.info['ip'],"command:",command,'第'+str(i)+'次正则匹配失败，匹配内容(output,match)：',output,match)
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

    Ip='10.1.2.1'
    user='test'
    passwd='test'
    time1=time.perf_counter()
    device=huaweiAR6300(Ip,user,passwd)
    print("connect:",device.is_alive)
    for i in (0,3):
        device.reconnect()
        print(device.ospf())
    '''
    print(device.cpu())
    print(device.memory())
    print(device.power())
    print(device.uptime())
    print(device.fan())
    print(device.bgp())
    print(device.temperature())
    print(device.board())
    print(device.version())
    '''
    device.close()
    time2=time.perf_counter()
    print(time2-time1)
