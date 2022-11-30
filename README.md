# XMLtoCSV
### Описание

Программа преобразовывает входящий XML файл с реестром начислений в CSV. Процесс обработки данных логируется, файл лога 
располагается в текущем каталоге, в подпапке 'log/'. После успешного преобразования исходный файл перемещается 
в подпапку текущего каталога 'arh/'. Если на входе не xml-файл - он перемещается в подкаталог 'bad/'.

### Использумые технологии

[Python 3.9](https://docs.python.org/release/3.9.13/whatsnew/3.9.html)

[BeautifulSoup4 4.11.1](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)

[Pandas 1.5.2](https://pandas.pydata.org/docs/)

### Как запустить проект:

Клонировать репозиторий и перейти в него в командной строке:

```
git clone https://github.com/DoDmAnat/XMLtoCSV
```

```
cd XMLtoCSV
```

Cоздать и активировать виртуальное окружение:

```
python -m venv venv
```

```
source venv/bin/activate
```

Установить зависимости из файла requirements.txt:

```
python -m pip install --upgrade pip
```

```
pip install -r requirements.txt
```

Для преобразования XML файла в CSV необходимо запустить программу  python с параметром(путь к XML).
```
python xmltocsv.py C:/root/root/example.xml
```
