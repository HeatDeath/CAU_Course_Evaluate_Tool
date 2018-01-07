import requests
from lxml import etree
from urllib import parse


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
    return parse.quote(string.encode('gb2312'))


# 具体课程评估 post data
def get_question_dict(my_page_source):
    my_selector = etree.HTML(my_page_source)
    question_dict = dict()
    question_num = len(my_selector.xpath('//table[@id="tblView"]//tr[@align="left"]'))
    # 问题编号与分数
    for j in range(question_num):
        question_name = my_selector.xpath(
            '((//table[@id="tblView"]//tr[@align="left"])[{}]/following-sibling::tr[1]//input)[1]/@name'.format(j + 1))[
            0]
        evaluate_grade = my_selector.xpath(
            '((//table[@id="tblView"]//tr[@align="left"])[{}]/following-sibling::tr[1]//input)[1]/@value'.format(
                j + 1))[0]

        question_dict[question_name] = evaluate_grade
    # evaluate_str = 'The teacher has given me inspiration and guidance in setting up my outlook on life and values. ' \
    #                'This course has improved my ability to comprehensively use my knowledge and analyze and solve ' \
    #                'problems. Thank you, teacher!'
    # 之前没想清楚编码的问题，现在可以中文评价了
    evaluate_str = '老师在我树立人生观、价值观方面给予了正确的启发和引领，这门课程提升了我综合运用所学知识，分析和解决问题的能力。谢谢老师！'
    evaluate_content = evaluate_str.encode('gb2312')
    question_dict['zgpj'] = evaluate_content
    return question_dict


def get_user_msg():
    print('-------------------')
    print('说明：')
    print('1、请输入正确的学号和密码，本程序无法检测学号密码是否匹配（因为我懒得写检测的部分了）')
    print('2、默认五星好评，如果对某些老师有“特别”的关照的话，可以提前自行评估，或是运行本程序后自行修改')
    print('3、本程序设计的初衷：每学期上那么多的课，每门课要选择 13 个分数，好麻烦呀好麻烦。遂...')
    print('4、其实不进行课程评价也是可以看到本学期成绩的，在教务系统-综合查询页面，选择左侧本学期成绩即可')
    print('-------------------')
    username = input("请在此处输入学号（回车结束输入）：")
    paasword = input("请在此处输入密码（回车结束输入）：")

    # 账号密码
    account_dict = {
        'zjh': username,
        'mm': paasword
    }

    return account_dict


if __name__ == '__main__':
    print('====================================')

    print('✧*｡٩(ˊωˋ*)و✧*｡')
    print('------ 欢迎使用 CAU 课程评估助手 ------')

    print('====================================')

    user_msg = get_user_msg()
    session = requests.session()

    # 登录教务系统
    login_url = 'http://urpjw.cau.edu.cn/loginAction.do'
    session.post(login_url, data=user_msg)

    # 跳转到课程评价【列表】页面，获取页面源码
    evaluate_list_url = 'http://urpjw.cau.edu.cn/jxpgXsAction.do?oper=listWj'
    page_source_code = session.get(evaluate_list_url).text

    # xpath 解析
    selector = etree.HTML(page_source_code)
    course_list = selector.xpath('//tr[@onmouseout="this.className=\'even\';"]//img/@name')

    # 需要评价的课程数量
    course_num = len(course_list)

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

    print('课程评估进行中ing...')
    print('请稍后')
    print('====================================')

    for i in range(course_num):
        try:
            evaluate_page_url = 'http://urpjw.cau.edu.cn/jxpgXsAction.do'
            page_source = session.post(evaluate_page_url,
                                       data={**course_msg[i], **open_evaluate_page_dict,
                                             **course_msg_url_encode[i]}).text

            evaluate_post_url = 'http://urpjw.cau.edu.cn/jxpgXsAction.do?oper=wjpg'

            session.post(evaluate_post_url, data={**course_msg[i], **get_question_dict(page_source)})

            print('【' + course_chinese_msg[i]['bprm'] + '】老师的：【' + course_chinese_msg[i]['pgnrm'] + '】已评估完毕~  (｡◕∀◕｡)')

        except:
            print('【' + course_chinese_msg[i]['bprm'] + '】老师的：【' + course_chinese_msg[i]['pgnrm'] + '】评估失败！ (°ཀ°)')
            pass
    print('====================================')
    print('本学期的课程已经全部评估完成，感谢使用。我们下学期再见 (*´∀`)~♥')
