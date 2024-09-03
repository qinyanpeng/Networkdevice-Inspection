from netmiko import ConnectHandler
from datetime import timedelta
import re, time

class ciscoN7k:
    def __init__(self,ip,username,password):
        self.type='ciscoN7k',
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
    #阈值默认值：threshold=70。取cpu1分钟利用率<阈值:返回True，否则为False
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
        return {"state":state,"value":value,"info":output,"type":self.type}

    
    #内存巡检。
    #阈值默认值：threshold=80。取内存利用率<阈值:返回True，否则为False
    def memory(self,threshold=60):
        state=True
        value=list()
        command="show system resources | inc Memory"
        output=self.driver.send_command(command)
        match = re.findall(r'Memory\s+usage:\s+(\d+)K\s+total,\s+(\d+)K\s+used',output)
        if len(match)==0:
            state=False
        else:
            for v in match:
                per=round((int(v[1])/int(v[0]))*100)
                value.append(per)
                if per > threshold:
                    state=False
        return {"state":state,"value":value,"info":output,"type":self.type}

    #电源巡检
    def power(self):
        state=True
        command="show environment power | inc AC"
        output=self.driver.send_command(command)
        match = re.findall(r'\s+(\w*)\s+\n',output)
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
        match = re.findall(r'\s+(\w*)\s+\n',output)
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
        command="show environment temperature"
        output=''
        for i in range(0,2):
            output=self.driver.send_command(command)
            print(output)
            match=re.findall(r'(\d+\s+\d+\s+\d+\s+\w+\s+)\n?',output)
            print(match)
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
                if "Ok" not in v:
                    match=v
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
            match=re.findall(r'(\d+\s+\d+\s+.*N77.*)',output)
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
                if "ok" in v or "active" in v or "standby" in v:
                    state=True
                else:
                    state=False
                    match=v
                    break
        return {"state":state,"value":match,"info":output,"type":self.type}

    def version(self,threshold="version 8.4(8)"):
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

    #光功率
    def transceiver(self):
        rtxState=False
        match='None'
        output='None'
        value={}
        rtxdata=''
        command="show interface brief"
        for i in range(1,2):
            output=self.driver.send_command(command)
            match = re.findall(r'(\w+\d+/\d+)\s+[1-]+\s+\w+\s+\w+\s+(\w+)\s+(\w+)\s+.*\n',output)
            if len(match)>0:
                print("【output】",self.info["ip"],output,match)
                break
            else:
                print(self.info['ip'],'命令：',command,'第'+str(i)+'次正则匹配失败，匹配内容(output,match)：',output,match)
        if len(match)>0:
            for m in match:
                output1='-'
                link1=m[1]
                link2=m[2]
                interface=m[0]
                rtxdata={"rx":"-","rxHigh":"-","rxLow":"-","tx":"-","txHigh":"-","txLow":"-","rtxState":False,"output":output1}
                if link2=="Administratively" or link2=="SFP":
                    rtxdata={"rx":"-","rxHigh":"-","rxLow":"-","tx":"-","txHigh":"-","txLow":"-","rtxState":True,"output":output1}
                else:
                    command1="show interface {} transceiver details".format(interface)
                    for i in range(1,3):
                        output1=self.driver.send_command(command1)
                        print("【output detail port】",self.info["ip"],output1,)
                        if "absent" in output1 or "The transceiver does not support this function" in output1:
                            rtxdata={"rx":'-',"rxHigh":"-","rxLow":"-","tx":"-","txHigh":"-","txLow":"-","rtxState":True,"output":output1}
                            break
                        else:
                            txMatch=re.search(r'Tx\s+Power\s+(-?\d+.\d+)\s+dBm\s+-?\d+.\d+\s+dBm\s+-?\d+.\d+\s+dBm\s+(-?\d+.\d+)\s+dBm\s+(-?\d+.\d+)\s+dBm',output1)
                            rxMatch=re.search(r'Rx\s+Power\s+(-?\d+.\d+)\s+dBm\s+-?\d+.\d+\s+dBm\s+-?\d+.\d+\s+dBm\s+(-?\d+.\d+)\s+dBm\s+(-?\d+.\d+)\s+dBm',output1)
 
                            if txMatch and rxMatch:
                                rx=float(rxMatch.group(1))
                                tx=float(txMatch.group(1))

                                rxHigh=float(rxMatch.group(2))
                                txHigh=float(txMatch.group(2))

                                rxLow=float(rxMatch.group(3))
                                txLow=float(txMatch.group(3))

                                if link1=="down":
                                    link1=="DOWN"
                                    rtxState=True

                                if link1=="up":
                                    link1=="UP"
                                    if rx<=rxHigh and rx>=rxLow and tx<=txHigh and tx>=txLow:
                                        rtxState=True
                                rtxdata={"rx":rx,"rxHigh":rxHigh,"rxLow":rxLow,"tx":tx,"txHigh":txHigh,"txLow":txLow,"rtxState":rtxState,"output":output1}
                                break
                            else:
                                print("{} 第{}次取值异常,output:{}".format(self.info["ip"],i,output1))
                                rtxdata={"rx":"-","rxHigh":"-","rxLow":"-","tx":"-","txHigh":"-","txLow":"-","rtxState":False,"output":output1}
                value[interface]={"link":link1,**rtxdata}

        return {"value":value,"type":self.type,"ip":self.info["ip"]}


    def close(self):
        self.driver.disconnect() 

if __name__ == "__main__":

    Ip='10.1.2.3' 
    user='test'
    passwd='test'
    time1=time.perf_counter()
    device=ciscoN7k(Ip,user,passwd)
    #print(device.is_alive)
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
