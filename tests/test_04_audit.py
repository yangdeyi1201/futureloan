import unittest
import ddt
from common.handler_requests import visit_api
from middleware.handler import Handler, MysqlHandlerMid

excel = Handler.excel
cases = excel.read_sheet('audit')
logger = Handler.logger
host = Handler.yaml_conf['project']['host']


@ddt.ddt
class TestAudit(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        logger.info('开始执行测试')

    @classmethod
    def tearDownClass(cls):
        logger.info('测试执行完毕')

    @ddt.data(*cases)
    def test_audit(self, case_info):
        method = case_info['method']
        url = host+case_info['url']

        headers = Handler().replace_data(case_info['headers'])
        headers = eval(headers)

        data = Handler().replace_data(case_info['data'])
        data = eval(data)

        sql = 'select `status` from futureloan.loan where id = {};'.format(data['loan_id'])

        if '*' not in case_info['title']:
            bid_info_before = MysqlHandlerMid().query(sql)

        expected_resp = eval(case_info['expected_resp'])
        actual_resp = visit_api(method, url, headers, json=data)

        try:
            for k, v in expected_resp.items():
                self.assertEqual(actual_resp[k], v)

            if actual_resp['code'] == 0:
                bid_info = MysqlHandlerMid().query(sql)
                if data['approved_or_not'] is True:
                    self.assertTrue(bid_info['status'] == 2)
                elif data['approved_or_not'] is False:
                    self.assertTrue(bid_info['status'] == 5)
            else:
                if case_info['case_id'] in (5, 6, 7, 8, 9, 10):
                    bid_info_after = MysqlHandlerMid().query(sql)
                    self.assertEqual(bid_info_after['status'], bid_info_before['status'])
            excel.write_data('audit', case_info['case_id'] + 1, 8, '通过')
            logger.info('第{}条用例通过'.format(case_info['case_id']))
        except (AssertionError, KeyError) as e:
            excel.write_data('audit', case_info['case_id']+1, 8, '不通过')
            logger.error('第{}条用例不通过'.format(case_info['case_id']))
            raise e


if __name__ == '__main__':
    unittest.main()
