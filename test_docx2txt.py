import docx2txt
# TODO: Таблицы из файла *.docx плохо созраняются (обычным сплошным текстом)

# text = docx2txt.process("./files/text_01_03.docx")
# print(text)

text = docx2txt.process("./files/DM4.docx", "files/")
print(text)  # 18 Задание с таблицами и графом (картинка)
