#安博通
from netmiko import ConnectHandler
from datetime import timedelta
import re, time

class ABT:
    def __init__(self,ip,username,password):
        self.type='ABT'
        self.info={'device_type':'generic_termserver',
                   'ip':ip,
                   'username':username,
                   'password':password}
        try:
            self.driver=ConnectHandler(**self.info)
            self.is_alive=True
            #if self.is_alive:
                #self.command('en\n')
        except Exception as e:
            self.is_alive=False
            print(self.info['ip'],'connect failed:',e)

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

    #CPU巡检。
    #阈值默认值：threshold=70。取cpu1分钟利用率<阈值:返回True，否则为False
    def cpu(self,threshold=70):
        state=True
        match=''
        output=''
        values=[]
        command="show cpu usage"
        for i in range(1,4):
            output=self.command(command)
            match = re.findall(r'CPU\d\s+\d+\s+(\d+)',output)
            if len(match)!=0:
                break
            time.sleep(9)
        if len(match)==0:
            state=False
        else:
            for v in match:
                value=int(v)
                values.append(value)
                if value > threshold:
                    state=False
        return {"state":state,"value":values,"info":output,"type":self.type}

    
    #内存巡检。
    #阈值默认值：threshold=80。取内存利用率<阈值:返回True，否则为False
    def memory(self,threshold=80):
        state=True
        match=None
        value=''
        output=''
        command="show mem"
        for i in range(1,5):
            output=self.command(command)
            match = re.search(r'Total\s+\d+M\s+\d+.\d+M\s+\d+.\d+M\s+(\d+.\d+)%',output)
            if match:
                value=match.group(1)
                break
            time.sleep(9)
        if match:
            if float(value) > threshold:
                state=False
            else:
                state=True
        else:
            state=False
        return {"state":state,"value":[float(value)],"info":match,"type":self.type}

    #电源巡检
    def power(self):
        state=True
        return {"state":state,"value":"-","info":"-","type":self.type}


    #风扇巡检
    def fan(self):
        state=True
        return {"state":state,"value":"-","info":"-","type":self.type}

    def uptime(self,threshold=12):
        uptime_hours=-1
        state=True
        output='' 
        command="show version"
        for i in range(1,5):
            output=self.command(command)
            days = re.search(r'(\d+)\s+days?',output)
            hours = re.search(r'(\d+)\s+hours?:\d+',output)
            mins = re.search(r'(\d+)\s+min',output)
            if days or hours or mins:
                uptime_hours=0
                break
            else:
                state=False
            time.sleep(9)

        if state:
            if days:
                uptime_hours=uptime_hours+int(days.group(1))*24
            if hours:
                uptime_hours=uptime_hours+int(hours.group(1))
            if uptime_hours <= 12:
                state=False
        return {"state":state,"value":uptime_hours,"info":output,"type":self.type}

    def version(self,threshold="ABT-EBG-V1.0-D5.4-EBG"):
        state=True
        version="none"
        command="show version"
        output=''
        for i in range(0,2):
            output=self.driver.send_command(command)
            print(output)
            match=re.search(r'is\s+(.*)\.bin\n',output)
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

    ips=['10.10.10.10']
    user='test'
    passwd='password'
    time1=time.perf_counter()
    for ip in ips:
        print(ip)
        device=ABT(ip,user,passwd)
        print(device.is_alive)
        if device.is_alive:
            cpu=device.cpu()
            print(cpu)
            #if not cpu['state']:
            #    print('cpu',cpu)
            mem=device.memory()
            print(mem)
            #if not mem['state']:
            #    print('mem',mem)
            power=device.power()
            print(power['value'])
            #if not power:
            #    print('power',power)
            uptime=device.uptime()
            print(uptime)
            #if not uptime['state']:
            #    print('uptime',uptime)
            fan=device.fan()
            print(fan['value'])
            #if not fan['state']:
            #    print('fan',fan)
            print(device.version())
            device.close()
        else:
            print('unconnect')
    time2=time.perf_counter()
    print(time2-time1)
