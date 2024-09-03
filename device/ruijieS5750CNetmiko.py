#锐捷
from netmiko import ConnectHandler
from datetime import timedelta
import re, time

class ruijieS5750C:
    def __init__(self,ip,username,password):
        self.type='ruijie'
        self.info={'device_type':'ruijie_os',
                   'ip':ip,
                   'username':username,
                   'password':password}
        try:
            self.driver=ConnectHandler(**self.info)
            self.is_alive=True
        except:
            self.is_alive=False

    #重新连接设备
    def reconnect(self):
        self.close()
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
                print(self.info['ip'],command,'command failed:',i, e)
            time.sleep(10)
        return output

    #CPU。
    #阈值默认值：threshold=70。取cpu1分钟利用率<阈值:返回True，否则为False
    def cpu(self,threshold=70):
        state=True
        match=''
        output=''
        value=[]
        command="show cpu | include one"
        for i in range(0,5):
            try:
                output=self.driver.send_command(command,read_timeout=20)
                #print(output)
                state=True
                break 
            except:
                state=False
            time.sleep(1)
        match = re.findall(r'one\s+minute:\s+(\d+.\d+)%',output)
        if len(match)==0:
            state=False
        else:
            for v in match:
                value.append(float(v))
                if float(v) > threshold:
                    state=False
        return {"state":state,"value":value,"info":output,"type":self.type}

    #内存。
    #阈值默认值：threshold=60。取内存利用率<阈值:返回True，否则为False
    def memory(self,threshold=60):
        state=True
        match=''
        output=''
        value=list()
        command="show memory | include Memory"
        for i in range(0,3):
            try:
                output=self.driver.send_command(command)
                state=True
                break
            except:
                state=False
        match = re.findall(r'(\d+\.\d+)%\s+used',output)
        if len(match)==0:
            state=False
        else:
            for v in match:
                v=float(v)
                value.append(v)
                if v > threshold:
                    state=False
        return {"state":state,"value":value,"info":output,"type":self.type}

    #电源巡检
    def power(self):
        state=True
        match=''
        output=''
        command="show power"
        for i in range(0,3):
            try:
                output=self.driver.send_command(command)
                state=True
                break
            except:
                state=False
        #print(output)
        match = re.findall(r'(\d+.*)',output)
        print(match)
        if len(match)==0:
            state=False
        else:
            for v in match:
                spl=v.split()
                if len(spl)>4 and spl[1]!="N/A" and spl[2]!="ok":
                    state=False
                    break
        return {"state":state,"value":match,"info":output,"type":self.type}

    #设备启动时间
    def uptime(self,threshold=12):
        uptime_hours=-1
        match='None'
        output='None'
        state=True
        command="show version | inc  uptime"
        for i in range(0,3):
            try:
                output=self.driver.send_command(command)
                state=True
                break
            except:
                state=False
        #print(output)
        match=re.findall(r'System\s+uptime\s+:\s+(\d+):(\d+)',output)
        if len(match)==0:
            state=False
        else:
            uptime_hours=int(match[0][0])*24+int(match[0][1])
        if uptime_hours<=12:
            state=False
        return {"state":state,"value":str(uptime_hours),"info":output,"type":self.type}

    #风扇巡检
    def fan(self):
        state=True
        match='None'
        output='None'
        command="show fan"
        for i in range(0,3):
            try:
                output=self.driver.send_command(command)
                state=True
                break
            except:
                state=False
        print(output)
        match = re.findall(r'(\d/?.*)',output)
        if len(match)==0:
            state=False
        else:
            for v in match:
                if "ok" not in v:
                    state=False
                    break
        return {"state":state,"value":match,"info":output,"type":self.type}

    #温度
    def temperature(self):
        state=True
        command="show temperature"
        output=''
        for i in range(0,2):
            output=self.driver.send_command(command)
            print(output)
            match = re.findall(r'(.*\s+\d+\s+.*)\n',output)
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

    #板卡
    def board(self):
        state=True
        command="show version slots  | exc none"
        output=''
        for i in range(0,2):
            output=self.driver.send_command(command)
            print(output)
            match = re.findall(r'(\d+\s+.*)',output)
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
                if "running" in v or "master" in v or "backup" in v or "candidate" in v:
                    state=True
                else:
                    state=False
                    match=v
                    break
        return {"state":state,"value":match,"info":output,"type":self.type}

    def version(self,threshold="RGOS 11.4(1)B74P7"):
        state=True
        version="none"
        command="show version | inc RGOS"
        output=''
        for i in range(0,2):
            output=self.driver.send_command(command)
            print(output)
            match=re.search(r'(RGOS\s+.*)\n',output)
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


#主程序入口
if __name__ == "__main__":

    ips=["10.10.10.10"]
    user='test'
    passwd='test'
    time1=time.perf_counter()
    for ip in ips:
        print(ip)
        device=ruijieS5750C(ip,user,passwd)
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



