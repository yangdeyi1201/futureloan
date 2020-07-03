import unittest
from libs.HTMLTest import HTMLTestRunner
from config import paths
from datetime import datetime  # 导入时间处理模块


loader = unittest.TestLoader()
test_suit = loader.discover(paths.TESTS_PATH)

ts = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')  # 生成当前时间戳字符串

# html 测试报告
with open(paths.REPORTS_PATH/'前程贷接口测试报告-{}.html'.format(ts), 'wb') as f:
    runner = HTMLTestRunner(f, tester='杨德义', title='前程贷接口测试报告')
    runner.run(test_suit)


# 文本测试报告
# with open(paths.REPORTS_PATH/'前程贷接口测试报告-{}.txt'.format(ts), 'w', encoding='UTF-8') as f:
#     runner = unittest.TextTestRunner(f)
#     runner.run(test_suit)


# 控制台查看结果
# runner = unittest.TextTestRunner()
# runner.run(test_suit)
