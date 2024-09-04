# 网络设备巡检脚本
#### 脚本介绍
- 脚本通过SSH方式对网络设备进行巡检，运行run.sh或者check_version.sh启动脚本后，巡检完成后结果以excel文件输出到report目录中。
- 巡检项的阈值在device目录下类函数中设定。
- 巡检结果判断逻辑在各个设备的脚本中，对操作系统版本有敏感性，版本不同可能需要调整判断逻辑。
- 搭配定时任务可实现自动巡检。
- 发送邮件需在sendmail.py中配置发送邮箱信息
#### 目录介绍
── README.md
├── check_version.py 							#版本巡检入库脚本入口脚本为check_version.py			
├── check_version.sh 						 	#版本巡检启动脚本，运行check_version.py，方便打印日志。
├── config.py 									  #配置文件：设备信息、位置、用户名密码
├── device 										    #各设备巡检代码
│   ├── ABTNetmiko.py
│   ├── DPADX3000TSGSNetmiko.py
│   ├── F5.py
│   ├── F5VE.py
│   ├── ZCTTNetmiko.py
│   ├── ZDNSNetmiko.py
│   ├── cisco4431Netmiko.py
│   ├── ciscoASA5585Netmiko.py
│   ├── ciscoASR1000Netmiko.py
│   ├── ciscoN5kNetmiko.py
│   ├── ciscoN7kNetmiko.py
│   ├── fortigate301Netmiko.py
│   ├── h3cF1070Netmiko.py
│   ├── h3cMSR56Netmiko.py
│   ├── h3cS10500Netmiko.py
│   ├── h3cS12500SNetmiko.py
│   ├── h3cS12506SNetmiko.py
│   ├── h3cS6800Netmiko.py
│   ├── h3cS7503Netmiko.py
│   ├── h3cSr6604Netmiko.py
│   ├── h3cSw5560Netmiko.py
│   ├── hillstoneSG6000Netmiko.py
│   ├── huaweiAR6300Netmiko.py
│   ├── huaweiCE16804Netmiko.py
│   ├── huaweiCE6881Netmiko.py
│   ├── huaweiFw6555Netmiko.py
│   ├── huaweiFw9560Netmiko.py
│   ├── huaweiUSG6300ENetmiko.py
│   ├── radwareNetmiko.py
│   ├── riverbedNetmiko.py
│   ├── ruijieRSR50X84Netmiko.py
│   ├── ruijieS5750CNetmiko.py
│   ├── ruijieS6120Netmiko.py
│   ├── ruijieS7808CNetmiko.py
│   └── sangforNetmiko.py
├── log											            #存放run.sh/check_version.sh启动脚本日志
├── main.py										          #除version之外的cpu、内存、电源等巡检入口脚本
├── report 										          #存放巡检结果
├── run.sh                              #main.py启动的脚本
└── sendemail.py								        #发送邮件脚本，需配置发送邮箱信息
#### 已适配巡检网络设备：
- 思科: cisco4431 , ciscoASR1000 , ciscoN7k , ciscoASA5585 , ciscoN5k
- 华三: h3cF1070 , h3cS10500 ,  h3cS12506S , h3cS7503 , h3cSw5560 ,  h3cMSR56 , h3cS12500S , h3cS6800 , h3cSr6604
- 华为:huaweiAR6300 , huaweiCE6881 , huaweiFw9560 huaweiCE16804 ,  huaweiFw6555 , huaweiUSG6300E
- 锐捷:ruijieRSR50X84 , ruijieS5750C , ruijieS6120 , ruijieS7808C
- F5: F5 , F5VE
- 山石: hillstoneSG6000
- 迪普: DPADX3000TSGS
- 飞塔: fortigate301
- 深信服: sangfor
- 中创信测: ZCTT
- ZDNS
- Radware
- 安博通
#### 已适配巡检项：
- cpu
- 内存
- 电源
- 风扇
- 运行时间
- 温度
- 板卡
- OSPF
- BGP
- M-LAG
- IRF
- 版本
#### 除版本之外的cpu、内存、电源等巡检入口脚本为main.py
#### 版本巡检入库脚本入口脚本为check_version.py
