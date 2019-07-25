import time
import os

from zipfile import ZipFile, ZIP_DEFLATED


class FileHelper():
    def __init__(self):
        pass

    def zip_json(self, utf8_data=''):
        current_time = int(time.time())
        temp_file = '{}.txt'.format(current_time)

        target = open(temp_file, 'w')
        target.write(utf8_data.encode('utf-8'))
        target.close()

        zip_name = './data/{}.zip'.format(current_time)
        with ZipFile(zip_name, 'w', ZIP_DEFLATED) as my_zip:
            my_zip.write(temp_file)

        os.remove(temp_file)
        return zip_name

    def read_file(self, file_path=''):
        if not os.path.isfile(file_path):
            file = open(file_path, 'w+')
            file.close()
            return ''

        file = open(file_path, 'r')
        content = file.read()
        file.close()
        return content
