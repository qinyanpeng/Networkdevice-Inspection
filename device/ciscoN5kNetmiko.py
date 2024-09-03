from netmiko import ConnectHandler
from datetime import timedelta
import re, time

class ciscoN5k:
    def __init__(self,ip,username,password):
        self.type='ciscoN5k',
        self.info={'device_type':'cisco_nxos',
                   'ip':ip,
                   'username':username,
                   'password':password}
        try:
            self.driver=ConnectHandler(**self.info)
            self.is_alive=True
        except:
            self.is_alive=False

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
        return {"state":state,"value":match,"info":output,"type":self.type}

    
    #内存巡检。
    #阈值默认值：threshold=80。取内存利用率<阈值:返回True，否则为False
    def memory(self,threshold=60):
        state=True
        value=[]
        command="show system resources | inc Memory"
        output=self.driver.send_command(command)
        match = re.findall(r'Memory\s+usage:\s+(\d+)K\s+total,\s+(\d+)K\s+used',output)
        if len(match)==0:
            state=False
        else:
            for v in match:
                per=round((int(v[1])/int(v[0]))*100)
                value.append(int(per))
                if per > threshold:
                    state=False
        return {"state":state,"value":value,"info":output,"type":self.type}

    #电源巡检
    def power(self):
        state=True
        command="show environment power"
        output=self.driver.send_command(command)
        match = re.findall(r'AC\s+\d+.\d+\s+\d+.\d+\s+(\w*)',output)
        if len(match)==0:
            state=False
        else:
            for v in match:
                if v.lower() != "ok".lower():
                    state=False
                    break
        return {"state":state,"value":match,"info":output,"type":self.type} 


    #风扇巡检
    def fan(self):
        state=True
        command="show environment fan"
        output=self.driver.send_command(command)
        match = re.findall(r'--\s+(\w+)[ ]{0,10}\n',output)
        if len(match)==0:
            state=False
        else:
            for v in match:
                if v.lower() != "ok".lower():
                    state=False
                    break
        return {"state":state,"value":match,"info":output,"type":self.type}

    def uptime(self,threshold=12):
        hours=-1
        state=True
        command="show system uptime"
        output=self.driver.send_command(command)
        match = re.findall(r'System\s+uptime:\s+(\d+)\s+days?,\s+(\d+)\s+hours?,',output)
        if len(match)==0:
            state=False
        else:
            hours=int(match[0][0])*24+int(match[0][1])
            if hours <= 12:
                state=False
        return {"state":state,"value":hours,"info":output,"type":self.type}

    def ospf(self):
        state=True
        command="show ip ospf neighbors vrf all"
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
        command="show environment temperature | include 0"
        output=''
        for i in range(0,2):
            output=self.driver.send_command(command)
            print(output)
            match=output.splitlines()
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
                if "ok" not in v:
                    state=False
                    break
                else:
                    state=True
        return {"state":state,"value":match,"info":output,"type":self.type}

    def board(self):
        state=True
        command="show module"
        output=''
        for i in range(0,2):
            output=self.driver.send_command(command)
            print(output)
            match=re.findall(r'(\d+\s+\d+\s+\w+\s+.*)',output)
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
                if "ok" in v or "active" in v:
                    state=True
                else:
                    state=False
                    match=v
                    break
        return {"state":state,"value":match,"info":output,"type":self.type}

    def version(self,threshold="version 7.3(8)N1(1)"):
        state=True
        version="none"
        command="show version | inc version"
        output=''
        for i in range(0,2):
            output=self.driver.send_command(command)
            print(output)
            match=re.search(r'system:\s+(version.*)\n',output)
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
    device=ciscoN5k(Ip,user,passwd)
    print(device.is_alive)
    #print(device.cpu())
    #print(device.memory())
    #print(device.power())
    #print(device.uptime())
    #print(device.fan())
    #print(device.ospf())
    #print(device.temperature())
    #print(device.board())
    print(device.version())
    device.close()
    time2=time.perf_counter()
    print(time2-time1)
