import pymysql
from pymysql.cursors import DictCursor


class MysqlHandler:
    def __init__(self, host='120.78.128.25', port=3306,
                 user='future', password='123456', charset='utf8', cursorclass=DictCursor):
        conn = pymysql.connect(host=host, port=port,
                               user=user, password=password, charset=charset, cursorclass=cursorclass)
        cursor = conn.cursor()
        self.conn = conn
        self.cursor = cursor
        return

    def query(self, sql, one=True):
        self.cursor.execute(sql)
        self.conn.commit()  # 提交事务
        if one:
            # fetchone 查询不到：所有游标类都是返回 None；查询到：仅返回查询结果的首条记录(字典游标类：一个字典表示，默认游标类：一个元组表示)
            data = self.cursor.fetchone()
        else:
            # fetchall 查询不到：所有游标类都是返回空元组；查询到：字典游标类返回列表套字典(每个字典表示一条记录)，默认游标类返回元组套元组(嵌套的每个元组表示一条记录)
            data = self.cursor.fetchall()
        return data

    def close(self):
        self.cursor.close()
        self.conn.close()
