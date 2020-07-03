import unittest
import ddt
from datetime import datetime
from jsonpath import jsonpath
from common.handler_requests import visit_api
from middleware.handler import Handler

excel = Handler.excel
cases = excel.read_sheet('login')
logger = Handler.logger
host = Handler.yaml_conf['project']['host']


@ddt.ddt
class TestLogin(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        logger.info('开始执行测试')

    @classmethod
    def tearDownClass(cls):
        logger.info('测试执行完成')

    @ddt.data(*cases)
    def test_login(self, case_info):
        headers = eval(case_info['headers'])
        data = eval(case_info['data'])
        url = host+case_info['url']
        expected_resp = eval(case_info['expected_resp'])
        actual_resp = visit_api(case_info['method'], url, headers, json=data)
        try:
            for k, v in expected_resp.items():
                self.assertEqual(actual_resp[k], v)
            if actual_resp['code'] == 0:
                # 接口返回手机号应与登录手机号一致
                self.assertEqual(actual_resp['data']['mobile_phone'], data['mobile_phone'])
                # 验证接口能正常返回 token 值
                self.assertTrue(jsonpath(actual_resp, '$..token')[0])
                # 验证 token 类型与说明文档一致
                self.assertTrue(jsonpath(actual_resp, '$..token_type')[0] == 'Bearer')
                # 安全考虑，验证 token 失效时间
                if int(str(datetime.now()).split(':')[1]) >= 55:
                    self.assertTrue(int(jsonpath(actual_resp, '$..expires_in')[0].split(':')[1])+55 == int(str(datetime.now()).split(':')[1]))
                else:
                    self.assertTrue(int(jsonpath(actual_resp, '$..expires_in')[0].split(':')[1]) == int(str(datetime.now()).split(':')[1])+5)
            excel.write_data('login', case_info['case_id']+1, 8, '通过')
            logger.info('第 {} 条用例通过'.format(case_info['case_id']))
        # 添加 KeyError 异常处理：当接口返回缺少应有字段，也代表用例不能通过
        except (AssertionError, KeyError) as e:
            excel.write_data('login', case_info['case_id']+1, 8, '不通过')
            logger.error('第 {} 条用例不通过'.format(case_info['case_id']))
            raise e


if __name__ == '__main__':
    unittest.main()
