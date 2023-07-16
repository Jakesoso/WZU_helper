import re
import requests
from bs4 import BeautifulSoup
import urllib3
from encrypt import encrypt
import pandas as pd


"""

    #url-信息查询xxcx
    url_tjkbcx = 'http://jwc3.wzu.edu.cn/tjkbcx.aspx?' + username + '&xm=' + xm + '&gnmkdm=N121601'  # 各专业班级课表
    url_xsfxkbcx = 'http://jwc3.wzu.edu.cn/xsfxkbcx.aspx?' + username + '&xm=' + xm + '&gnmkdm=N121602'  # 学生辅修双专业课表
    url_xskbcx = 'http://jwc3.wzu.edu.cn/xskbcx.aspx?' + username + '&xm=' + xm + '&gnmkdm=N121603'  # 学生个人课表
    url_xskscx = 'http://jwc3.wzu.edu.cn/xskscx.aspx?' + username + '&xm=' + xm + '&gnmkdm=N121604'  # 学生考试查询
    url_xscjcx = 'http://jwc3.wzu.edu.cn/xscjcx.aspx?' + username + '&xm=' + xm + '&gnmkdm=N121605'  # 学生大学成绩查询
    url_xsdjkscx = 'http://jwc3.wzu.edu.cn/xsdjkscx.aspx?' + username + '&xm=' + xm + '&gnmkdm=N121606'  # 学生等级考试查询

"""


# 登录教务系统
def login_zhengfang(stu_id, password):
    # 禁用HTTP警告
    urllib3.disable_warnings()

    session = requests.session()
    session.headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/114.0.0.0 Safari/537.36 Edg/114.0.1823.67'
    }

    # 访问任意网址，返回包含认证页面链接的内容（自动跳转）
    url = 'https://source.wzu.edu.cn/login'
    resp = session.get(url, verify=False)

    # 提取认证链接并访问，经历一次重定向得到认证页面，且会返回一个cookie值：session
    croypto = re.search(r'"login-croypto">(.*?)<', resp.text, re.S).group(1)
    execution = re.search(r'"login-page-flowkey">(.*?)<', resp.text, re.S).group(1)

    # 构建post数据 填入自己的学号 密码
    data = {
        'username': stu_id,  # 学号
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
    resp_hall = session.post(url, data=data)

    url = 'http://hall.wzu.edu.cn/visit/dab247c354d64695a1ae6ad714011fa6'
    resp_zhengfang = session.get(url)

    name = re.search(r'"xhxm">(.*?)同学', resp_zhengfang.text, re.S).group(1)

    # 返回状态和session
    return [resp_hall.status_code, resp_zhengfang.status_code, session, name, stu_id]


# 学生个人课表查询
def get_course_timetable(session, name, stu_id):
    url = 'http://jwc3.wzu.edu.cn/xskbcx.aspx?' + 'xh=' + str(stu_id) + '&xm=' + name + '&gnmkdm=N121603'
    resp = session.get(url)

    tables = pd.read_html(resp.text)
    tables[1].to_excel(r'个人课表.xlsx')
    print('个人课表已经保存到本地!')


# 选课
def enroll_course(session, name, stu_id):
    url = 'http://jwc3.wzu.edu.cn/xf_xsqxxxk.aspx?' + 'xh=' + str(stu_id) + '&gnmkdm=N121112'
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


# 成绩查询
def get_test_score(session, name, stu_id):
    url = 'http://jwc3.wzu.edu.cn/xscjcx.aspx?' + 'xh=' + str(stu_id) + '&xm=' + name + '&gnmkdm=N121605'
    resp = session.get(url)

    viewstate = re.search(r'name="__VIEWSTATE" value="(.*?)" />', resp.text, re.S).group(1)
    data = {
        '__EVENTTARGET': '',
        '__EVENTARGUMENT': '',
        '__VIEWSTATE': viewstate,
        'hidLanguage': '',
        'ddlXN': '',
        'ddlXQ': '',
        'ddl_kcxz': '',
        'btn_zcj': '%C0%FA%C4%EA%B3%C9%BC%A8'
    }

    resp = session.post(url, data=data)

    tables = pd.read_html(resp.text)
    tables[1].to_excel(r'个人成绩.xlsx')
    print('个人成绩已经保存到本地!')