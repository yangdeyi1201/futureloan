import openpyxl


class ExcelHandler(object):
    def __init__(self, excel_path):
        self.path = excel_path
        self.workbook = None

    def open_excel(self):
        """打开 excel 文件"""
        workbook = openpyxl.load_workbook(self.path)
        self.workbook = workbook
        return workbook

    def get_sheet(self, sheet_name):
        """获取表单"""
        workbook = self.open_excel()
        sheet = workbook[sheet_name]
        return sheet

    def read_sheet(self, sheet_name):
        """读取表单数据"""
        sheet = self.get_sheet(sheet_name)

        rows = list(sheet.rows)

        headers = []
        for title in rows[0]:
            headers.append(title.value)

        cases = []
        for row in rows[1:]:
            case = {}
            for index, cell in enumerate(row):
                case[headers[index]] = cell.value
            cases.append(case)

        return cases

    def write_data(self, sheet_name, row, column, data):
        """向表单某一单元格写入数据"""
        sheet = self.get_sheet(sheet_name)
        sheet.cell(row, column).value = data
        self.workbook.save(self.path)
        self.workbook.close()

    def close_excel(self):
        """关闭 excel 文件"""
        self.workbook.close()
