# coding: utf-8

from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
import smtplib
from email.mime.text import MIMEText


###发送邮件
####################################################
####  【必要配置: username，passwd，mail_host】   ####
####################################################
#:param username: 邮箱账号 xx@163.com
#:param passwd: 邮箱密码
#:param recv: 邮箱接收人地址，多个账号以逗号隔开
#:param title: 邮件标题
#:param content: 邮件内容
#:param mail_host: 邮箱服务器
#:param port: 端口号


def sendemail(username='test.163.com', passwd='password', recv=None, title='网络设备巡检报告', content='', mail_host='stmp.163.com', port=25, file=None):

    if file:
        msg = MIMEMultipart()

        # 构建正文
        part_text = MIMEText(content,'html','utf-8')
        msg.attach(part_text)  # 把正文加到邮件体里面去

        # 构建邮件附件
        part_attach1 = MIMEApplication(open(file, 'rb').read())  # 打开附件
        part_attach1.add_header('Content-Disposition', 'attachment', filename=file)  # 为附件命名
        msg.attach(part_attach1)  # 添加附件
    else:
        msg = MIMEText(content,'html','utf-8')  # 邮件内容
    msg['Subject'] = title  # 邮件主题
    msg['From'] = username  # 发送者账号
    msg['To'] = ','.join(recv)  # 接收者账号列表
    smtp = smtplib.SMTP(mail_host, port=port)
    smtp.starttls()
    smtp.login(username, passwd)  # 登录
    smtp.sendmail(username, recv, msg.as_string())
    smtp.quit()

#主程序入口【测试发邮件】
if __name__ == "__main__":
    html='''
        <table><tr><th>a</th><th>b</th></tr>
        <tr><td>aa</td><td>bb</td></tr></table>
        '''

    sendemail(recv=['test.mail.com'],content=html)
