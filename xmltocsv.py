import logging
import os
import shutil
import numpy as np
import pandas as pd

from sys import argv
from chardet.universaldetector import UniversalDetector
from bs4 import BeautifulSoup

file_path = argv[1] # Запуск программы с параметром
dir_path = ''.join((os.path.split(file_path)[:1]))
file_name = os.path.splitext(os.path.basename(file_path))[0]

if not os.path.isdir(dir_path + '/log'):
    os.mkdir(dir_path + '/log')
logging.basicConfig(
    level=logging.INFO,
    filename=os.path.join(dir_path + "/log", 'main.log'),
    format='%(asctime)s, %(levelname)s, %(name)s, %(message)s'
)


def convert_xml_to_csv(xml_file: str) -> None:
    """Преобразование XML файла в CSV"""
    # Получаем кодировку файла
    detector = UniversalDetector()
    with open(xml_file, "rb") as enco:
        for line in enco:
            detector.feed(line)
            if detector.done:
                break
        detector.close()
    encoding = detector.result['encoding']
    logging.info(f"Кодировка файла xml - {encoding}")
    # Парсинг данных
    with open(xml_file, encoding=encoding) as file:
        src = file.read().encode(encoding)
    logging.info("Началось извлечение данных xml")
    soup = BeautifulSoup(src, "xml")
    str_list = soup.select_one("ИнфЧаст").select("Плательщик")
    date = soup.select_one("СлЧаст").select_one("ОбщСвСч").select_one(
        "ИдФайл").select_one("ДатаФайл").text

    rows = []
    for item in str_list:
        personal_acc = item.find("ЛицСч").text
        if personal_acc.strip() == "":
            personal_acc = np.nan
        full_name = item.find("ФИО").text
        address = item.find("Адрес").text
        period = item.find("Период").text
        if period.strip() == "":
            period = np.nan
        amount = item.find("Сумма").text
        if amount != "{:.2f}".format(float(amount)):
            amount = np.nan
        rows.append({"file_name": file_name,
                     "date": date,
                     "personal_acc": personal_acc,
                     "full_name": full_name,
                     "address": address,
                     "period": period,
                     "amount": amount})

    df = pd.DataFrame(rows)

    # Проверка на отсутствие ключевых реквизитов
    if df["personal_acc"].isna().any():
        drop_index = df[df["personal_acc"].isna()].index.tolist()
        logging.error(f"Не загружены строки {drop_index} - "
                      f"отсутствует ключевой реквизит 'ЛицСч'")
        df = df.dropna(subset=["personal_acc"])
    if df["period"].isna().any():
        drop_index = df[df["period"].isna()].index.tolist()
        logging.error(f"Не загружены строки {drop_index} - "
                      f"отсутствует ключевой реквизит 'Период'")
        df = df.dropna(subset=["period"])

    # Проверка формата поля 'Сумма'
    if df["amount"].isna().any():
        drop_index = df[df["amount"].isna()].index.tolist()
        logging.error(
            f"Не загружены строки {drop_index} - "
            f"неверный формат в поле 'Cумма'")
        df = df.dropna(subset=["amount"])

    # Проверка формата поля 'Период'
    if df["period"].isna().any():
        drop_index = df.index[df["period"].isna()].tolist()
        logging.error(
            f"Строки {drop_index} не загружены - неверный формат даты")
        df = df.drop(index=drop_index)
        df["period"] = df["period"].dt.strftime('%m%Y')

    # Проверка и удаление дубликатов
    if df.duplicated(subset=["personal_acc", "period"], keep=False).any():
        get_duplicate = df.duplicated(subset=["personal_acc", "period"],
                                      keep=False)
        logging.warning(
            'Исключены дубликаты записей по ключам "ЛицСч", "Период":' +
            str(df[get_duplicate]["personal_acc"] + '; ' +
                df[get_duplicate]["period"])
        )
        df = df.drop_duplicates(subset=["personal_acc", "period"], keep=False)

    # Сохранение данных в CSV
    df.to_csv(f"{file_name}.csv", index=False, header=False, encoding=encoding,
              sep=';')
    logging.info('csv-файл успешно создан')
    if not os.path.isdir(dir_path + '/arh'):
        os.mkdir(dir_path + '/arh')
    new_location_xml = dir_path + '/arh/' + file_name + '.xml'
    shutil.move(xml_file, new_location_xml)


def check_file(xml_file: str) -> bool:
    """Проверка файла на существование и соответствие расширения"""
    file_format = os.path.splitext(xml_file)[1]
    if os.path.exists(xml_file):
        if file_format != '.xml':
            if not os.path.isdir(dir_path + '/bad'):
                os.mkdir(dir_path + '/bad')
            logging.critical("Невозможно обработать файл с таким расширением")
            new_location_xml = dir_path + '/bad/' + file_name + file_format
            shutil.move(xml_file, new_location_xml)
            return False
        return True
    else:
        logging.critical("Нет такого файла")
        return False


def main():
    """Главная функция"""
    if check_file(file_path):
        try:
            convert_xml_to_csv(file_path)
        except Exception:
            logging.critical("Ошибка запуска, проверьте установленные "
                             "библиотеки либо содержимое XML файла")
    else:
        print("Подходящий файл не найден")


if __name__ == "__main__":
    main()
