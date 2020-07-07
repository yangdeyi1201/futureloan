import re
from config import paths
from random import randint
from jsonpath import jsonpath
from common.handler_yaml import read_yaml
from common.handler_log import get_logger
from common.handler_excel import ExcelHandler
from common.handler_mysql import MysqlHandler
from common.handler_requests import visit_api


class MysqlHandlerMid(MysqlHandler):
    def __init__(self):
        __db_config = Handler.yaml_conf['db']
        super().__init__(host=__db_config['host'], port=__db_config['port'],
                         user=__db_config['user'], password=__db_config['password'],
                         charset=__db_config['charset'])


class Handler:
    yaml_conf = read_yaml(paths.CONFIG_PATH/'config.yaml')

    __log_config = yaml_conf['log']
    logger = get_logger(logger_level=__log_config['logger_level'],
                        console_level=__log_config['console_level'],
                        file_level=__log_config['file_level'],
                        file_path=paths.LOGS_PATH/__log_config['filename'])

    excel = ExcelHandler(paths.DATA_PATH / yaml_conf['excel']['filename'])

    __project_config = yaml_conf['project']
    investor_id = __project_config['investor_id']
    borrower_id = __project_config['borrower_id']
    administrator_id = __project_config['administrator_id']

    @property
    def investor_token(self):
        method = 'post'
        url = Handler.yaml_conf['project']['host'] + '/member/login'
        headers = {'X-Lemonban-Media-Type': 'lemonban.v2'}
        user = Handler.yaml_conf['investor']
        resp = visit_api(method, url, headers, json=user)
        token_type = jsonpath(resp, '$..token_type')[0]
        token_str = jsonpath(resp, '$..token')[0]
        return ' '.join([token_type, token_str])

    @property
    def administrator_token(self):
        method = 'post'
        url = Handler.yaml_conf['project']['host'] + '/member/login'
        headers = {'X-Lemonban-Media-Type': 'lemonban.v2'}
        user = Handler.yaml_conf['administrator']
        resp = visit_api(method, url, headers, json=user)
        token_type = jsonpath(resp, '$..token_type')[0]
        token_str = jsonpath(resp, '$..token')[0]
        return ' '.join([token_type, token_str])

    @property
    def borrower_token(self):
        method = 'post'
        url = Handler.yaml_conf['project']['host'] + '/member/login'
        headers = {'X-Lemonban-Media-Type': 'lemonban.v2'}
        user = Handler.yaml_conf['borrower']
        resp = visit_api(method, url, headers, json=user)
        token_type = jsonpath(resp, '$..token_type')[0]
        token_str = jsonpath(resp, '$..token')[0]
        return ' '.join([token_type, token_str])

    @staticmethod
    def recharge_investor(amount):
        """投资测试账户充值"""
        method = 'post'
        url = Handler.yaml_conf['project']['host'] + '/member/recharge'
        investor_token = Handler().investor_token
        headers = {'X-Lemonban-Media-Type': 'lemonban.v2', 'Authorization': investor_token}
        investor_id = Handler.yaml_conf['project']['investor_id']
        data = {'member_id': investor_id, 'amount': amount}
        visit_api(method, url, headers, json=data)
        return None

    @staticmethod
    def recharge_borrower(amount):
        """借款测试账户充值"""
        method = 'post'
        url = Handler.yaml_conf['project']['host'] + '/member/recharge'
        borrower_token = Handler().borrower_token
        headers = {'X-Lemonban-Media-Type': 'lemonban.v2', 'Authorization': borrower_token}
        borrower_id = Handler.yaml_conf['project']['borrower_id']
        data = {'member_id': borrower_id, 'amount': amount}
        visit_api(method, url, headers, json=data)
        return None

    @staticmethod
    def add():
        """为借款测试账户加一个标"""
        method = 'post'
        url = Handler.yaml_conf['project']['host'] + '/loan/add'
        borrower_token = Handler().borrower_token
        headers = {'X-Lemonban-Media-Type': 'lemonban.v2', 'Authorization': borrower_token}
        borrower_id = Handler.yaml_conf['project']['borrower_id']
        data = {'member_id': borrower_id, 'title': '开烧烤店', 'amount': 15000, 'loan_rate': 12, 'loan_term': 3,
                'loan_date_type': 1, 'bidding_days': 5}
        visit_api(method, url, headers, json=data)
        return None

    @staticmethod
    def audit(loan_id, audit_status):
        """管理员测试账户审核一个标"""
        method = 'patch'
        url = Handler.yaml_conf['project']['host'] + '/loan/audit'
        administrator_token = Handler().administrator_token
        headers = {'X-Lemonban-Media-Type': 'lemonban.v2', 'Authorization': administrator_token}
        data = {'loan_id': loan_id, 'approved_or_not': audit_status}
        visit_api(method, url, headers, json=data)
        return None

    @property
    def pass_loan_id(self):
        sql = 'select id from futureloan.loan where member_id = {} and `status` = 1 order by create_time desc;'.format(Handler.borrower_id)
        loan_id = MysqlHandlerMid().query(sql)['id']
        self.audit(loan_id, True)
        return loan_id

    @property
    def not_exist_loan_id(self):
        sql = 'select max(id) from futureloan.loan;'
        max_loan_id = MysqlHandlerMid().query(sql)['max(id)']
        not_exist_loan_id = max_loan_id+1
        return not_exist_loan_id

    @property
    def loan_id_status_1(self):
        sql = 'select id from futureloan.loan where member_id = {} and `status` = 1 order by create_time desc;'.format(Handler.borrower_id)
        loan_id = MysqlHandlerMid().query(sql)['id']
        return loan_id

    @property
    def loan_id_status_5(self):
        sql = 'select id from futureloan.loan where member_id = {} and `status` = 1 order by create_time desc;'.format(Handler.borrower_id)
        loan_id = MysqlHandlerMid().query(sql)['id']
        self.audit(loan_id, False)
        return loan_id

    @property
    def not_exist_investor_id(self):
        sql = 'select max(id) from futureloan.member;'
        max_member_id = MysqlHandlerMid().query(sql)['max(id)']
        not_exist_investor_id = max_member_id+1
        return not_exist_investor_id

    def replace_data(self, data):
        """正则替换"""
        pattern = r'#(.*?)#'
        while re.search(pattern, data):
            key = re.search(pattern, data).group(1)
            value = getattr(self, key, '')
            data = re.sub(pattern, str(value), data, count=1)
        return data

    @property
    def register_mobile(self):
        """随机生成一个可用于正常注册的手机号"""
        while True:
            num = randint(10000000, 99999999)
            random_mobile = '158' + str(num)  # 使用手机常用号段，避免号段异常不能用于正常注册
            query_data = MysqlHandlerMid().query(
                'select * from futureloan.member where mobile_phone = "{}"'.format(random_mobile), False)
            if not query_data:  # 生成的随机手机号，若已存在于数据库，则会返回重新生成，直至生成手机号不存在于库时返回该手机号用于正常注册
                return random_mobile


if __name__ == '__main__':
    m_str = '{"member_id":#investor_id#,"loan_id":#pass_loan_id#,"amount":#money#}'
    a = Handler().replace_data(m_str)
    print(a)
