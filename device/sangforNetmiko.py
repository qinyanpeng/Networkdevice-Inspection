#深信服
from netmiko import ConnectHandler
from datetime import timedelta
import re, time

class sangfor:
    def __init__(self,ip,username,password):
        self.type='sangfor'
        self.info={'device_type':'linux',
                   'ip':ip,
                   'username':username,
                   'password':password}
        try:
            self.driver=ConnectHandler(**self.info)
            self.is_alive=True
        except Exception as e:
            self.is_alive=False
            print(self.info['ip'],'connect failed:', e)

    #执行命令，返回回显
    def command(self,command):
        output=''
        for i in range(1,5):
            try:
                output=self.driver.send_command(command,read_timeout=20)
                break
            except Exception as e:
                print(self.info['ip'],command,'command failed:',i, e)
            time.sleep(10)
        return output

    #重新连接设备
    def reconnect(self):
        self.close()
        try:
            self.driver=ConnectHandler(**self.info)
            self.is_alive=True
        except Exception as e:
            self.is_alive=False
            print(self.info['ip'],'connect failed:', e)
 

    #CPU巡检。
    #阈值默认值：threshold=70。取cpu1分钟利用率<阈值:返回True，否则为False
    def cpu(self,threshold=70):
        state=True
        match=''
        output=''
        values=[]
        command="top"
        for i in range(1,6):
            output=self.command(command)
            matchline=re.search(r'(Cpu.*\n)',output)
            match = re.findall(r'(\d+.\d+)%id,',output)
            if len(match)!=0:
                break
            print(self.info['ip'],'命令：',command,'第'+str(i)+'次正则匹配失败，匹配内容(output,match)：',output,match)
            time.sleep(9)
            self.reconnect()
        #print(match)
        if len(match)==0:
            state=False
        else:
            for v in match:
                value=round(100-float(v),2)
                values.append(value)
                if value > threshold:
                    state=False
        return {"state":state,"value":values,"info":match,"type":self.type}

    
    #内存巡检。
    #阈值默认值：threshold=80。取内存利用率<阈值:返回True，否则为False
    def memory(self,threshold=80):
        state=True
        match=None
        value=''
        output=''
        command="top"
        for i in range(1,6):
            output=self.command(command)
            match = re.search(r'Mem:\s+(\d+)k\s+total, (\d+)k\s+used,',output)
            if match:
                value=round(int(match.group(2))/int(match.group(1))*100)
                break
            print(self.info['ip'],'命令：',command,'第'+str(i)+'次正则匹配失败，匹配内容(output,match)：',output,match)
            time.sleep(9)
            self.reconnect()
        if match:
            value=round(int(match.group(2))/int(match.group(1))*100)
            if value > threshold:
                state=False
            else:
                state=True
        else:
            state=False
        return {"state":state,"value":[value],"info":match,"type":self.type}

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
        command="uptime"
        for i in range(1,6):
            output=self.command(command)
            days = re.search(r'up\s+(\d+)\s+days?',output)
            hours = re.search(r'(\d+)?:\d+',output)
            mins = re.search(r'(\d+)\s+min',output)
            if days or hours or mins:
                uptime_hours=0
                break
            else:
                state=False
                print(self.info['ip'],'命令：',command,'第'+str(i)+'次正则匹配失败，匹配内容(output,days,hours,mins)：',output,days,hours,mins)
            time.sleep(9)
            self.reconnect()

        if state:
            if days:
                uptime_hours=uptime_hours+int(days.group(1))*24
            if hours:
                uptime_hours=uptime_hours+int(hours.group(1))
            if uptime_hours <= threshold:
                state=False
        return {"state":state,"value":uptime_hours,"info":output,"type":self.type}

    def version(self):
        uptime_hours=-1
        state=True
        output=''
        command="cat /app/appversion"
        for i in range(1,6):
            output=self.command(command)
            print(output)

    def close(self):
        self.driver.disconnect() 

if __name__ == "__main__":

    ips=['10.10.10.10']
    user='user'
    passwd='test'
    time1=time.perf_counter()
    for ip in ips:
        print(ip)
        device=sangfor(ip,user,passwd)
        if device.is_alive:
            cpu=device.cpu()
            print(cpu)
            #if not cpu['state']:
            #    print('cpu',cpu)
            mem=device.memory()
            print(mem)
            #if not mem['state']:
            #    print('mem',mem)
            #power=device.power()
            #print(power['value'])
            #if not power:
            #    print('power',power)
            uptime=device.uptime()
            print(uptime)
            #if not uptime['state']:
            #    print('uptime',uptime)
            #fan=device.fan()
            #print(fan['value'])
            #if not fan['state']:
            #    print('fan',fan)
            print(device.version())
            device.close()
        else:
            print('unconnect')
    time2=time.perf_counter()
    print(time2-time1)
