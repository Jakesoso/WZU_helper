# -*- coding:utf-8 -*-

"""

    #url-信息查询xxcx
    url_tjkbcx = 'http://jwc3.wzu.edu.cn/tjkbcx.aspx?' + username + '&xm=' + xm + '&gnmkdm=N121601'  # 各专业班级课表
    url_xsfxkbcx = 'http://jwc3.wzu.edu.cn/xsfxkbcx.aspx?' + username + '&xm=' + xm + '&gnmkdm=N121602'  # 学生辅修双专业课表
    url_xskbcx = 'http://jwc3.wzu.edu.cn/xskbcx.aspx?' + username + '&xm=' + xm + '&gnmkdm=N121603'  # 学生个人课表
    url_xskscx = 'http://jwc3.wzu.edu.cn/xskscx.aspx?' + username + '&xm=' + xm + '&gnmkdm=N121604'  # 学生考试查询
    url_xscjcx = 'http://jwc3.wzu.edu.cn/xscjcx.aspx?' + username + '&xm=' + xm + '&gnmkdm=N121605'  # 学生大学成绩查询
    url_xsdjkscx = 'http://jwc3.wzu.edu.cn/xsdjkscx.aspx?' + username + '&xm=' + xm + '&gnmkdm=N121606'  # 学生等级考试查询

"""

import binascii
import re
import requests
from pyDes import ECB, PAD_PKCS5, des
from bs4 import BeautifulSoup
import urllib3



class Student:
    def __init__(self, username1, name, stu_class, faculty, major):
        self.username = username1
        self.name = name
        self.stu_class = stu_class
        self.faculty = faculty
        self.major = major


class Class:
    def __init__(self, name, type, mon, tue, wed, thu, fri):
        self.name = name
        self.type = type
        self.mon = mon
        self.tue = tue
        self.wed = wed
        self.thu = thu
        self.fri = fri


headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,'
              'application/signed-exchange;v=b3;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
    'Cache-Control': 'max-age=0',
    'Connection': 'keep-alive',
    'Content-Type': 'application/x-www-form-urlencoded',
}


# des解密
def des_encrypt(s, key):
    """
    DES 加密
    :param key: 秘钥
    :param s: 原始字符串
    :return: 加密后字符串，16进制
    """
    secret_key = key
    k = des(secret_key, mode=ECB, pad=None, padmode=PAD_PKCS5)
    en = k.encrypt(s, padmode=PAD_PKCS5)
    return en  # 得到加密后的16位进制密码 <class 'bytes'>


def encrypt(pd, key):
    """
    密码加密过程：
    1 从认证页面中可获得base64格式的秘钥
    2 将秘钥解码成bytes格式
    3 输入明文密码
    4 通过des加密明文密码
    5 返回base64编码格式的加密后密码
    :param pd: 明文密码
    :param key: 秘钥
    :return: 加密后的密码（base64格式）
    """
    key = binascii.a2b_base64(key.encode('utf-8'))  # 先解码 <class 'bytes'>
    pd_bytes = des_encrypt(pd, key)  # 得到加密后的16位进制密码 <class 'bytes'>
    pd_base64 = binascii.b2a_base64(pd_bytes, newline=False).decode('utf-8')
    return pd_base64


# 登录内网门户
def login_hall(username, password):

    session.headers = headers

    # 访问任意网址，返回包含认证页面链接的内容（自动跳转）
    url = 'https://source.wzu.edu.cn/login'
    resp = session.get(url, verify=False)

    # 提取认证链接并访问，经历一次重定向得到认证页面，且会返回一个cookie值：session
    croypto = re.search(r'"login-croypto">(.*?)<', resp.text, re.S).group(1)
    execution = re.search(r'"login-page-flowkey">(.*?)<', resp.text, re.S).group(1)

    # 构建post数据 填入自己的学号 密码
    data = {
        'username': username,  # 学号
        'type': 'UsernamePassword',
        '_eventId': 'submit',
        'geolocation': '',
        'execution': execution,
        'captcha_code': '',
        'croypto': croypto,  # 密钥 base64格式
        'password': encrypt(password, croypto)  # 密码 经过des加密 base64格式
    }

    # 提交cookie，进行登录(重定向)
    session.cookies.update({'isPortal': 'false'})
    url = 'https://source.wzu.edu.cn/login'
    resp = session.post(url, data=data)

    # 传出状态
    return resp.status_code


# 登录教务系统
def login_zhengfang(session):
    url = 'http://hall.wzu.edu.cn/visit/dab247c354d64695a1ae6ad714011fa6'
    resp = session.get(url)

    # 获取姓名
    name = (re.search(r'"xhxm">(.*?)同学', resp.text, re.S).group(1))

    # 打印提示
    if resp.status_code == 200:
        print('-----------------------')
        print(name + '同学你好' + '，请输入数字以继续操作!')
        print("1) 查看个人课表\n2) 查看公选课列表")
        key = input("我的选择是：")
    else:
        print('登录失败！请重试，检查账号密码，在校园网环境下登录')

    # 教务系统进一步操作
    if key == '1':
        zhengfang_xxcx_xskbcx(name)
    if key == '2':
        zhengfang_enroll_course(name)


# 学生个人课表查询
def zhengfang_xxcx_xskbcx(name):
    url = 'http://jwc3.wzu.edu.cn/xskbcx.aspx?' + 'xh=' + str(username) + '&xm=' + name + '&gnmkdm=N121603'
    resp = session.get(url)

    soup = BeautifulSoup(resp.text, 'html.parser')
    tr = soup.select('tr')

    # 输出课表
    for j in range(4, 17):
        fir = tr[j].select('td')
        if j == 4 or j == 9 or j == 14:
            for i in range(2, len(fir)):
                if fir[i].get_text() != ' ':
                    print(fir[i].get_text())
        else:
            for i in range(1, len(fir)):
                if fir[i].get_text() != ' ':
                    print(fir[i].get_text())


def zhengfang_enroll_course(name):
    url = 'http://jwc3.wzu.edu.cn/xf_xsqxxxk.aspx?' + 'xh=' + str(username) + '&gnmkdm=N121112'
    # url = 'http://jwc3.wzu.edu.cn/xf_xsqxxxk.aspx?xh=21210160116&xm=%C2%C0%F6%CE%BD%DC&gnmkdm=N121112'
    # headers['Referer'] = 'http://jwc3.wzu.edu.cn/xf_xsqxxxk.aspx?xh=21210160116&xm=%C2%C0%F6%CE%BD%DC&gnmkdm=N121112'

    resp = session.get(url)

    # 校区信息(北校区 学院路校区 南校区 温州医科大学 在线学习)
    ddl_xqbs = '1'

    # 构建post数据，获取符合当前条件的选课
    viewstate = re.search(r'name="__VIEWSTATE" value="(.*?)" />', resp.text, re.S).group(1)
    data = {
        '__EVENTTARGET': '',
        '__EVENTARGUMENT': '',
        '__VIEWSTATE': viewstate,
        '__VIEWSTATEGENERATOR': '03DFB912',
        'ddl_kcxz': '',
        'ddl_ywyl': '',  # 有无余量
        'ddl_kcgs': '',  # 课程归属
        'ddl_xqbs': ddl_xqbs,  # 校区信息
        'ddl_sksj': '',
        'TextBox1': '',
        'dpkcmcGrid:txtChoosePage': '1',
        'dpkcmcGrid:txtPageSize': '200',
    }

    # 获取选课科目
    resp = session.post(url, data=data)

    soup = BeautifulSoup(resp.text, 'html.parser')
    html_selected = str(soup.findAll('table', id='DataGrid2'))  # 已选科目
    html_all = str(soup.findAll('table', id='kcmcGrid'))
    html_all = re.findall(r'top=60\'\)">(.*?)</a>', html_all, re.S)
    # html_selected =

    # 输出所有选课结果
    print('-----------------------')
    print('  【科目   老师】')
    count = 0
    num = 1
    for each in html_all:
        count += 1
        if (count % 2 != 0):
            print(num, each, end=' ')
        if (count % 2 == 0):
            print(each, end='\n')
            num += 1

    # id = 1;
    # 提交选课结果
    # class_id = 'kcmcGrid:_ctl' + str(id) + ':xk'

    # data['Button1'] = '  提交  '.encode('gb2312')

    # data['kcmcGrid:_ctl2:xk'] = 'on'
    # data['kcmcGrid:_ctl2:xk'] = 'on'  # 确认选课
    # data['Button1'] = '  提交  '

    # resp = session.post(url, data=data)  # 提交

    # print(resp)

    # print(resp.text)


if __name__ == '__main__':
    # 禁用HTTP警告
    urllib3.disable_warnings()

    # 打印提示
    print('-----温州大学门户助手-----')

    # 获取账号密码
    username = input("请输入学号：")
    password = input("请输入密码：")

    # 登录门户
    session = requests.session()
    status_code = login_hall(username, password)
    if status_code != 200:
        print('登录失败！请重试，检查账号密码，在校园网环境下登录')
    else:
        print('-----------------------')
        print('成功登录内网门户大厅，请输入序号以继续')
        print('1) 教务系统')
        key = input("我选择：")

        # 判断门户操作
        if key == '1':
            login_zhengfang(session)

    print('-----------------------')
    key = input("按任意键以退出")