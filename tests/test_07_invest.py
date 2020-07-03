import unittest
import ddt
from decimal import Decimal
from datetime import datetime
from middleware.handler import Handler, MysqlHandlerMid
from common.handler_requests import visit_api

excel = Handler.excel
cases = excel.read_sheet('invest')

logger = Handler.logger
host = Handler.yaml_conf['project']['host']


@ddt.ddt
class TestInvest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # 查询投资账户余额
        cls.sql_leaveamount = 'select leave_amount from futureloan.member where id = {};'.format(Handler.investor_id)
        # 查询投资账户投资/流水/回款记录条数
        cls.sql_count_invest = 'select count(id) from futureloan.invest where member_id = {};'.format(Handler.investor_id)
        cls.sql_count_financelog = 'select count(id) from futureloan.financelog where pay_member_id = {};'.format(Handler.investor_id)
        cls.sql_count_repayment = 'select count(r.id) from futureloan.repayment r, futureloan.invest i where r.invest_id = i.id and i.member_id = {};'.format(Handler.investor_id)
        logger.info('开始执行测试')

    @classmethod
    def tearDownClass(cls):
        logger.info('测试执行完毕')

    def setUp(self):
        # 每条用例执行之前，向投资账户预充值 10000
        Handler.recharge_investor(10000)
        # 每条用例执行之前，先获取投资账户投资前的余额
        self.leaveamount_before = MysqlHandlerMid().query(self.sql_leaveamount)['leave_amount']
        # 每条用例执行之前，先查询投资账户投资/流水/回款记录条数
        self.invest_count_before = MysqlHandlerMid().query(self.sql_count_invest)['count(id)']
        self.financelog_count_before = MysqlHandlerMid().query(self.sql_count_financelog)['count(id)']
        self.repayment_count_before = MysqlHandlerMid().query(self.sql_count_repayment)['count(r.id)']
        # 每条用例执行之前，先进行加标
        Handler.add()

    def tearDown(self):
        # 每条用例执行完后，将投资账号余额清零
        MysqlHandlerMid().query('update futureloan.member set leave_amount = 0 where id = {};'.format(Handler.investor_id))

    @ddt.data(*cases)
    def test_invest(self, case_info):
        method = case_info['method']
        url = host+case_info['url']

        if '#' in case_info['title']:
            self.setUp()

        headers = Handler().replace_data(case_info['headers'])
        headers = eval(headers)

        data = Handler().replace_data(case_info['data'])
        data = eval(data)

        expected_resp = eval(case_info['expected_resp'])
        actual_resp = visit_api(method, url, headers, json=data)

        # 查询投资账号投资后余额、投资/流水/回款记录条数
        leaveamount_after = MysqlHandlerMid().query(self.sql_leaveamount)['leave_amount']
        invest_count_after = MysqlHandlerMid().query(self.sql_count_invest)['count(id)']
        financelog_count_after = MysqlHandlerMid().query(self.sql_count_financelog)['count(id)']
        repayment_count_after = MysqlHandlerMid().query(self.sql_count_repayment)['count(r.id)']

        try:
            for k, v in expected_resp.items():
                self.assertEqual(actual_resp[k], v)

            if actual_resp['code'] == 0:
                # 一、验证投资账号：最新投资记录，数据库字段信息正确
                sql = 'select * from futureloan.invest where member_id = {} order by create_time desc;'.format(data['member_id'])
                invest_info = MysqlHandlerMid().query(sql)
                self.assertTrue(invest_count_after == self.invest_count_before + 1)
                self.assertEqual(invest_info['loan_id'], data['loan_id'])
                self.assertEqual(invest_info['amount'], Decimal(str(data['amount'])))
                self.assertTrue(invest_info['is_valid'] == 1)
                self.assertTrue(int(str(datetime.now()).split(':')[1]) - int(str(invest_info['create_time']).split(':')[1]) <= 1)

                # 二、验证投资后：标状态信息变化正常
                loan_info = MysqlHandlerMid().query('select status from futureloan.loan where member_id = {} order by create_time desc'.format(Handler.borrower_id))
                # 非满标投资，标状态保持为 2
                if '#' not in case_info['title']:
                    self.assertTrue(loan_info['status'] == 2)
                # 满标投资，标状态变为 3
                else:
                    self.assertTrue(loan_info['status'] == 3)

                # 三、验证投资账号：余额变动正确
                self.assertTrue(self.leaveamount_before-Decimal(str(data['amount'])) == leaveamount_after)

                # 四、验证投资账号：最新流水记录，数据库字段信息正确
                financelog_info = MysqlHandlerMid().query('select * from futureloan.financelog where pay_member_id = {} order by create_time desc;'.format(data['member_id']))
                self.assertTrue(financelog_count_after == self.financelog_count_before + 1)
                self.assertEqual(financelog_info['pay_member_id'], data['member_id'])
                self.assertEqual(financelog_info['income_member_id'], Handler.borrower_id)
                self.assertEqual(financelog_info['amount'], Decimal(str(data['amount'])))
                self.assertTrue(financelog_info['income_member_money'] == Decimal(str(0)))
                self.assertTrue(self.leaveamount_before - Decimal(str(data['amount'])) == financelog_info['pay_member_money'])
                self.assertTrue(financelog_info['status'] == 1)
                self.assertTrue(int(str(datetime.now()).split(':')[1]) - int(str(financelog_info['create_time']).split(':')[1]) <= 1)

                # 五、验证投资账号：投资标满标后，回款记录信息正确
                if '#' not in case_info['title']:
                    self.assertEqual(repayment_count_after, self.repayment_count_before)
                else:
                    self.assertTrue(repayment_count_after == self.repayment_count_before + 3)
            else:
                # 验证异常投资：投资前后投资账户余额、投资/流水/回款记录条数不变
                self.assertEqual(self.leaveamount_before, leaveamount_after)
                self.assertEqual(self.invest_count_before, invest_count_after)
                self.assertEqual(self.financelog_count_before, financelog_count_after)
                self.assertEqual(self.repayment_count_before, repayment_count_after)
            excel.write_data('invest', case_info['case_id'] + 1, 8, '通过')
            logger.info('第 {} 条用例通过'.format(case_info['case_id']))
        except (AssertionError, KeyError) as e:
            excel.write_data('invest', case_info['case_id']+1, 8, '不通过')
            logger.error('第 {} 条用例不通过'.format(case_info['case_id']))
            raise e


if __name__ == '__main__':
    unittest.main()
