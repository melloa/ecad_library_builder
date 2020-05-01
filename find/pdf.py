from pdfminer.pdfinterp import PDFResourceManager,PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from io import BytesIO
def search(path, s):
    manager = PDFResourceManager()
    retstr = BytesIO()
    layout = LAParams(all_texts=True)
    device = TextConverter(manager, retstr, laparams=layout)
    filepath = open(path, 'rb')
    interpreter = PDFPageInterpreter(manager, device)
    page_number = 1
    for page in PDFPage.get_pages(filepath, check_extractable=True):
        interpreter.process_page(page)
        text = str(retstr.getvalue())
        if text.find(s) != -1:
            return page_number
        page += 1
    filepath.close()
    device.close()
    retstr.close()
    return -1

if __name__ == "__main__":
    print(search("/home/seb/Downloads/ZL40264-Data-Sheet.pdf", "Functional Block Diagram"))