# 数据中心
region1={
"D":"数据中心1",
"P":"数据中心2",
}

# 所属业务区
region2={
"YW1":"业务一区",
"SJ3":"数据三区",
}


# 用于多套用户名密码的情况，与下方devices['authtype']对应，最终在main.py->check()函数中使用。
authtypes={
  "auth1":{"username": "user","password": "1111"},
  "auth2":{"username": "user","password": "2222"},
  }



# devices 是设备列表
# name:             约定特殊含义名称，D-YW1-KS01' 含义：D 数据中心1，YW1 业务一区。（对应上方region1、region2。）
# ip:               设备ip
# key:              设备型号，main.py文件中check()函数会根据key字段匹配巡检类，与device目录中设备类函数对应。
# base_version:     基线版本，低于基线版本会视为不满足要求
# authtype:         用户名密码（对应上面authtypes）
# check:            巡检项（1：检查；0：不检查）举例：'cpu':1 巡检cpu，'temperature':0 不巡检温度
# check['version']: 对应check_version.py，其他巡检对应main.py

devices=[
{'name':'D-YW1-KS01', 'ip':'10.0.2.1', 'key':'ruijieS7808C', 'base_version':'RGOS12.5(4)B0202', 'authtype': 'auth1','check':{'cpu':1,'mem':1,'power':1,'fan':1,'uptime':1,'temperature':0,'board':1,'bgp':0,'ospf':0,'mlag':0,'irf':0,'version':1,}},
]
