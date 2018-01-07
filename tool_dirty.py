import requests
from lxml import etree
import urllib


def label_attr_transform(label_attr):
    split_result = label_attr.split('#@')
    course_dict = dict()
    course_dict['wjbm'] = split_result[0]
    course_dict['bpr'] = split_result[1]
    course_dict['pgnr'] = split_result[-1]
    return course_dict

def label_attr_chinese_encode(label_attr):
    split_result = label_attr.split('#@')
    course_dict = dict()
    course_dict['wjmc'] = url_encode(split_result[3])
    course_dict['bprm'] = url_encode(split_result[2])
    course_dict['pgnrm'] = url_encode(split_result[4])
    return course_dict

def label_attr_chinese(label_attr):
    split_result = label_attr.split('#@')
    course_dict = dict()
    course_dict['wjmc'] = split_result[3]
    course_dict['bprm'] = split_result[2]
    course_dict['pgnrm'] = split_result[4]
    return course_dict

def url_encode(string):
    return urllib.parse.quote(string.encode('gb2312'))

def url_decode(string):
    return urllib.parse.quote(string).decode('gb2312')



def get_question_dict(my_page_source):
    my_selector = etree.HTML(my_page_source)
    question_dict = dict()
    question_num = len(my_selector.xpath('//table[@id="tblView"]//tr[@align="left"]'))
    for j in range(question_num):
        question_name = my_selector.xpath(
            '((//table[@id="tblView"]//tr[@align="left"])[{}]/following-sibling::tr[1]//input)[1]/@name'.format(j + 1))[0]
        # print(question_name)
        evaluate_grade = my_selector.xpath(
            '((//table[@id="tblView"]//tr[@align="left"])[{}]/following-sibling::tr[1]//input)[1]/@value'.format(j + 1))[0]
        # print(evaluate_grade)
        # print('-------------------')

        question_dict[question_name] = evaluate_grade
    evaluate_str = '老师在我树立人生观、价值观方面给予了启发和引领，这门课提升了我综合运用所学知识，分析和解决问题的能力，谢谢老师！:)'
    evaluate_content = url_encode(evaluate_str)
    question_dict['zgpj'] = evaluate_content
    return question_dict


session = requests.session()

# 账号密码
account_dict = {
    'zjh': '********',
    'mm': '******'
}

# 登录教务系统
login_url = 'http://urpjw.cau.edu.cn/loginAction.do'
session.post(login_url, data=account_dict)

# 跳转到课程评价【列表】页面，获取页面源码
evaluate_list_url = 'http://urpjw.cau.edu.cn/jxpgXsAction.do?oper=listWj'
page_source_code = session.get(evaluate_list_url).text

# xpath 解析
selector = etree.HTML(page_source_code)
course_list = selector.xpath('//tr[@onmouseout="this.className=\'even\';"]//img/@name')

# 需要评价的课程数量
course_num = len(course_list)

# print(course_list)

# 具体课程评价 post 用到的 data
course_msg = list(map(label_attr_transform, course_list))

# 跳转到具体课程 post 的 data
course_msg_url_encode = list(map(label_attr_chinese_encode, course_list))
open_evaluate_page_dict = {
    'oper': 'wjShow',
    'pageSize': '20',
    'page': '1',
    'currentPage': '1',
    'pageNo:': ''
}

course_chinese_msg = list(map(label_attr_chinese, course_list))

for i in range(course_num):
    try:
        evaluate_page_url = 'http://urpjw.cau.edu.cn/jxpgXsAction.do'
        page_source = session.post(evaluate_page_url,
                                   data={**course_msg[i], **open_evaluate_page_dict, **course_msg_url_encode[i]}).text

        # print({**course_msg[0], **open_evaluate_page_dict, **course_msg_url_encode[0]})
        # fw = open('eva_page.html', 'w', encoding='gb2312')
        # fw.write(page_source)
        # fw.close()

        # --------------------

        print({**course_msg[i],**get_question_dict(page_source)})
        evaluate_post_url = 'http://urpjw.cau.edu.cn/jxpgXsAction.do?oper=wjpg'
        # session.post(evaluate_post_url, data={**course_msg[i],**get_question_dict(page_source)})
        print(course_chinese_msg[i]['bprm'] + '老师的：' + course_chinese_msg[i]['pgnrm'] + '已经评估完毕~  (｡◕∀◕｡)')

    except:
        print(course_chinese_msg[i]['bprm'] + '老师的：' + course_chinese_msg[i]['pgnrm'] + '评估失败！ (°ཀ°)')
        pass
