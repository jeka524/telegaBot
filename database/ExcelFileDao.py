import openpyxl


class Entity:

    def __init__(self, photos: str, text: str, link: str):
        self.photos = photos.replace(" ", "").split(",")
        self.text = text
        self.link = link


class ExcelFileDao:

    def __init__(self, file_path):
        self.wb = openpyxl.load_workbook(file_path)
        self.sheet = self.wb.active

    def get_row(self, row_index) -> list:
        # self.sheet.cell_value(0, row_index)
        return list(self.sheet.rows)[row_index]

    def get_rows_number(self):
        # self.sheet.celcell_value(0, 0)
        return len(list(self.sheet.rows))

    def get_row_entity(self, row_index) -> Entity:
        row = self.get_row(row_index)
        return Entity(row[0].value, row[1].value, row[2].value)


if __name__ == '__main__':
    test = ExcelFileDao("../data.xlsx")
    x = test.get_rows_number()
    print(x)
    x = test.get_row(0)
    print(x)
    x = test.get_row_entity(0)
    print(x.photos)
