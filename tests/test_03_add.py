import unittest
import ddt
from decimal import Decimal
from datetime import datetime
from common.handler_requests import visit_api
from middleware.handler import Handler, MysqlHandlerMid

excel = Handler.excel
cases = excel.read_sheet('add')
logger = Handler.logger
host = Handler.yaml_conf['project']['host']


@ddt.ddt
class TestAdd(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sql = 'select count(*) from futureloan.loan where member_id = {};'.format(Handler.borrower_id)
        logger.info('开始执行测试')

    @classmethod
    def tearDownClass(cls):
        logger.info('测试执行完毕')

    def setUp(self):
        self.bid_before = MysqlHandlerMid().query(self.sql)['count(*)']

    @ddt.data(*cases)
    def test_add(self, case_info):
        method = case_info['method']
        url = host+case_info['url']

        headers = Handler().replace_data(case_info['headers'])
        headers = eval(headers)

        data = Handler().replace_data(case_info['data'])
        data = eval(data)

        expected_resp = eval(case_info['expected_resp'])
        actual_resp = visit_api(method, url, headers, json=data)

        bid_after = MysqlHandlerMid().query(self.sql)['count(*)']

        try:
            for k, v in expected_resp.items():
                self.assertEqual(actual_resp[k], v)

            if actual_resp['code'] == 0:
                self.assertTrue(bid_after == self.bid_before+1)

                bid_info = MysqlHandlerMid().query('select * from futureloan.loan where member_id = {} order by create_time desc;'.format(Handler.borrower_id))
                self.assertTrue(bid_info['member_id'], Handler.borrower_id)
                self.assertEqual(bid_info['title'], data['title'])
                self.assertEqual(bid_info['amount'], Decimal(str(data['amount'])))
                self.assertEqual(bid_info['loan_rate'], Decimal(str(data['loan_rate'])))
                self.assertEqual(bid_info['loan_term'], data['loan_term'])
                self.assertEqual(bid_info['loan_date_type'], data['loan_date_type'])
                # self.assertEqual(bid_info['bidding_days'], data['bidding_days'])
                self.assertTrue(int(str(datetime.now()).split(':')[1])-int(str(bid_info['create_time']).split(':')[1]) <= 1)
                self.assertFalse(bid_info['bidding_start_time'])
                self.assertFalse(bid_info['full_time'])
                self.assertTrue(bid_info['status'] == 1)
            else:
                self.assertEqual(self.bid_before, bid_after)
            excel.write_data('add', case_info['case_id'] + 1, 8, '通过')
            logger.info('第 {} 条用例通过'.format(case_info['case_id']))
        except (AssertionError, KeyError) as e:
            excel.write_data('add', case_info['case_id']+1, 8, '不通过')
            logger.error('第 {} 条用例不通过'.format(case_info['case_id']))
            raise e
