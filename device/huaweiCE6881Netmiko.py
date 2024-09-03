#华为
from netmiko import ConnectHandler
from datetime import timedelta
import re, time

class huaweiCE6881:
    def __init__(self,ip,username,password):
        self.type='huaweiCE6881'
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
        except Exception as e:
            self.is_alive=False
            print(self.info['ip'],'connect failed:', e)

    #执行命令，返回回显
    def command(self,command):
        output=''
        for i in range(0,3):
            try:
                output=self.driver.send_command(command,use_textfsm=True,read_timeout=20)
                break
            except Exception as e:
                print(self.info['ip'],command,'command failed:',i, e)
            time.sleep(10)
        return output

    #CPU巡检。
    #阈值默认值：threshold=70。取cpu1分钟利用率<阈值:返回True，否则为False
    def cpu(self,threshold=70):
        state=True
        command="display cpu"
        value=[]
        output=''
        for i in range(0,4):
            output=self.command(command)
            match = re.findall(r'cpu\d+\s+(\d+)%\s',output)
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
               time.sleep(10)
        return {"state":state,"value":value,"info":output,"type":self.type}

    
    #内存巡检。
    #阈值默认值：threshold=80。取内存利用率<阈值:返回True，否则为False
    def memory(self,threshold=60):
        state=True
        command="display memory"
        value=[]
        output=''
        for i in range(0,4):
            output=self.command(command)
            match = re.findall(r'Memory Using Percentage:\s+(\d+)%',output)
            if len(match)!=0:
                state=True
                break
            else:
                time.sleep(10)
                print(self.info['ip'],"command:",command,'第'+str(i)+'次正则匹配失败，匹配内容(output,match)：',output,match)
                state=False
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
        command="display device"
        match=list()
        output=''
        for i in range(0,4):
            output=self.command(command)
            match = re.findall(r'(PWR\d+.*)\n',output)
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
        return {"state":state,"value":match,"info":output,"type":self.type}

    #风扇巡检
    def fan(self,threshold=90):
        state=True
        command="display device"
        output=''
        for i in range(0,4):
            output=self.command(command)
            match = re.findall(r'(FAN\d+.*)\n',output)
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
            match = re.findall(r'(uptime .*)\n',output)
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

    #OSPF
    def ospf(self):
        state=True
        command="dis ospf peer bri"
        output=''
        for i in range(0,4):
            output=self.command(command)
            match = re.findall(r'(\d+.\d+.\d+.\d+.*\d+.\d+.\d+.\d+.*)\n',output)
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
                if "Full" not in v:
                    state=False
                    break
        return {"state":state,"value":match,"info":output,"type":self.type}

    def mlag(self):
        state=True
        match='None'
        output='None'
        command="display dfs-group 1 m-lag"
        for i in range(0,3):
            output=self.command(command)
            match2 = re.findall(r'Priority\s+:\s+(\d+)\n',output)
            match1 = re.findall(r'State\s+:\s+(\w+)\n',output)
            if len(match1)==2 and len(match2)==2:
                state=True
                break
            else:
                state=False
                #self.reconnect()
        if len(match1)==2 and len(match2)==2:
            if (match1[0]=="Master" and match2[0]=="150") and (match1[1]=="Backup" and match2[1]=="120"):
                print(match1[0],match2[0])
                state=True
            elif (match1[0]=="Backup" and match2[0]=="120") and (match1[1]=="Master" and match2[1]=="150"):
                state=True
            else:
                state=False
        return {"state":state,"value":[match1,match2],"info":output,"type":self.type}



    def temperature(self):
        state=True
        command="display device temperature all"
        output=''
        for i in range(0,2):
            output=self.command(command)
            print(output)
            match = re.findall(r'(.*\d+\s+)\n',output)
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
        command="display device board"
        for i in range(0,2):
            output=self.command(command)
            match = re.findall(r'(\d+\s+.*)',output)
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

    def version(self,threshold="V200R022C00SPC500"):
        state=True
        version="none"
        command="dis version"
        output=''
        for i in range(0,2):
            output=self.driver.send_command(command)
            match=re.search(r'[(]CE6881\s+(.*)[)]',output)
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

    Ip='10.1.2.2'
    user='test'
    passwd='test'
    time1=time.perf_counter()
    device=huaweiCE6881(Ip,user,passwd)
    print(device.is_alive)
    #print(device.cpu())
    #print(device.memory())
    #print(device.power())
    #print(device.uptime())
    #print(device.fan())
    #print(device.ospf())
    #print(device.mlag())
    #print(device.temperature())
    #print(device.board())
    print(device.version())
    device.close()
    time2=time.perf_counter()
    print(time2-time1)
