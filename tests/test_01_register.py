import unittest
import ddt
from random import randint
from datetime import datetime
from common.handler_requests import visit_api
from middleware.handler import Handler, MysqlHandlerMid

excel = Handler.excel
cases = excel.read_sheet('register')
logger = Handler.logger
host = Handler.yaml_conf['project']['host']


@ddt.ddt
class TestRegister(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        logger.info('开始执行测试')

    @classmethod
    def tearDownClass(cls):
        logger.info('测试执行完成')

    @ddt.data(*cases)
    def test_register(self, case_info):
        method = case_info['method']
        url = host + case_info['url']
        headers = eval(case_info['headers'])

        data = Handler().replace_data(case_info['data'])
        data = eval(data)

        expected_resp = eval(case_info['expected_resp'])
        actual_resp = visit_api(method, url, headers, json=data)

        try:
            for k, v in expected_resp.items():
                self.assertEqual(actual_resp[k], v)
            if actual_resp['code'] == 0:
                # 使用封装默认的 fetchall 查询，查询到则结果为列表套字典，查询不到则结果为空元组
                query_normal = MysqlHandlerMid().query('select * from futureloan.member where mobile_phone = "{}";'.format(data['mobile_phone']), False)
                self.assertTrue(query_normal)               # 此条断言通过表示：查询到了手机号为 XXX 的记录，但是否仅有一条不能确定
                self.assertTrue(len(query_normal) == 1)     # 通过列表长度为 1，确认手机号为 XXX 的记录仅有一条
                self.assertTrue(query_normal[0]['leave_amount'] == 0)
                self.assertTrue(int(str(datetime.now()).split(':')[1])-int(str(query_normal[0]['reg_time']).split(':')[1]) <= 1)  # 注册时间验证
                if '*' in case_info['title']:  # 用例 3 额外标记，进行不同断言
                    self.assertTrue(query_normal[0]['type'] == 1)  # 不传 type，是否为普通会员
                    self.assertTrue(query_normal[0]['reg_name'] == '小柠檬')  # 不传 reg_name，是否注册名为小柠檬
                else:
                    self.assertEqual(query_normal[0]['type'], data['type'])  # 用例 1、2
                    self.assertEqual(query_normal[0]['reg_name'], data['reg_name'])  # 用例 1、2
            else:  # 异常用例
                if '$' not in case_info['title']:  # 除重复注册、手机号为空外的异常用例，需查库验证会不会异常插入到数据库
                    query_exceptional = MysqlHandlerMid().query('SELECT * from futureloan.member WHERE mobile_phone = "{}";'.format(data['mobile_phone']), False)
                    self.assertFalse(query_exceptional)
            excel.write_data('register', case_info['case_id']+1, 8, '通过')
            logger.info('第 {} 条用例通过'.format(case_info['case_id']))
        # 添加 KeyError 异常处理：当接口返回缺少应有字段，也代表用例不能通过
        except (AssertionError, KeyError) as e:
            excel.write_data('register', case_info['case_id']+1, 8, '不通过')
            logger.error('第 {} 条用例不通过'.format(case_info['case_id']))
            raise e


if __name__ == '__main__':
    unittest.main()

# 一条断言失败，这条断言后面的代码不会执行
# 一条用例多条断言：所有断言都成功时，用例才会通过，任一个断言失败了，用例都不会通过
