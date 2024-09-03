# 网络设备巡检脚本
#### 脚本介绍
- 脚本通过SSH方式对网络设备进行巡检，运行run.sh或者check_version.sh启动脚本后，巡检完成后结果以excel文件输出到report目录中。
- 巡检项的阈值在device类中设定。
- 搭配定时任务可实现自动巡检。
#### 已适配巡检网络设备：
- 思科: cisco4431 , ciscoASR1000 , ciscoN7k , ciscoASA5585 , ciscoN5k
- 华三: h3cF1070 , h3cS10500 ,  h3cS12506S , h3cS7503 , h3cSw5560 ,  h3cMSR56 , h3cS12500S , h3cS6800 , h3cSr6604
- 华为:huaweiAR6300 , huaweiCE6881 , huaweiFw9560 huaweiCE16804 ,  huaweiFw6555 , huaweiUSG6300E
- 锐捷:ruijieRSR50X84 , ruijieS5750C , ruijieS6120 , ruijieS7808C
- F5: F5 , F5VE
- 山石: hillstoneSG6000
- 迪普: DPADX3000TSGSNetmiko
- 飞塔: fortigate301
- 深信服:sangfor
- 中创信测:ZCTT
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