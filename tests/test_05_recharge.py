import unittest
import ddt
from decimal import Decimal
from datetime import datetime
from middleware.handler import Handler, MysqlHandlerMid
from common.handler_requests import visit_api

excel = Handler.excel
cases = excel.read_sheet('recharge')
logger = Handler.logger
mobile_phone = Handler.yaml_conf['investor']['mobile_phone']
host = Handler.yaml_conf['project']['host']


@ddt.ddt
class TestRecharge(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sql = 'select leave_amount from futureloan.member where mobile_phone = "{}";'.format(mobile_phone)
        logger.info('开始执行测试')

    @classmethod
    def tearDownClass(cls):
        logger.info('测试执行完毕')

    def setUp(self):
        self.leaveamount_before = MysqlHandlerMid().query(self.sql)['leave_amount']

    @ddt.data(*cases)
    def test_recharge(self, case_info):
        method = case_info['method']
        url = host+case_info['url']

        headers = Handler().replace_data(case_info['headers'])
        headers = eval(headers)

        data = Handler().replace_data(case_info['data'])
        data = eval(data)

        expected_resp = eval(case_info['expected_resp'])
        actual_resp = visit_api(method, url, headers, json=data)

        leaveamount_after = MysqlHandlerMid().query(self.sql)['leave_amount']

        try:
            for k, v in expected_resp.items():
                self.assertEqual(actual_resp[k], v)

            if actual_resp['code'] == 0:
                self.assertTrue(self.leaveamount_before + Decimal(str(data['amount'])) == leaveamount_after)
                self.assertTrue(self.leaveamount_before + Decimal(str(data['amount'])) == Decimal(str(actual_resp['data']['leave_amount'])))
                query_data = MysqlHandlerMid().query('select * from futureloan.financelog where income_member_id = {} order by create_time desc;'.format(Handler.investor_id))
                self.assertTrue(query_data)
                self.assertEqual(query_data['income_member_id'], Handler.investor_id)
                self.assertEqual(query_data['amount'], Decimal(str(data['amount'])))
                self.assertTrue(self.leaveamount_before + Decimal(str(data['amount'])) == query_data['income_member_money'])
                self.assertTrue(query_data['status'] == 1)
                self.assertTrue(int(str(datetime.now()).split(':')[1])-int(str(query_data['create_time']).split(':')[1]) <= 1)
            else:  # 异常用例，需查库验证，测试账户充值前后余额保持不变
                self.assertEqual(self.leaveamount_before, leaveamount_after)
            excel.write_data('recharge', case_info['case_id'] + 1, 8, '通过')
            logger.info('第 {} 条用例通过'.format(case_info['case_id']))
        except (AssertionError, KeyError) as e:
            excel.write_data('recharge', case_info['case_id']+1, 8, '不通过')
            logger.error('第 {} 条用例不通过'.format(case_info['case_id']))
            raise e


if __name__ == '__main__':
    unittest.main()
