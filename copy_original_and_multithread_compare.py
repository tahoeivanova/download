from threading import Thread
from shutil import copy
import os
import os.path as osp
from time import ctime
import logging
from tqdm import tqdm
import atexit
# logger = logging.getLogger()
logging.basicConfig(filename='copy.log', level=logging.DEBUG)

dataset_src = '/home/dataset_src' # исходный датасет


# конечный путь для обычного копирования
dataset_dst_simple = '/home/dataset_dst_simple'
# конечный путь для многопоточного копирования
dataset_dst_threads = '/home/dataset_dst_multithread'

def create_dir(dir_name):
    try:
        os.mkdir(dir_name)
    except FileExistsError:
        pass
create_dir(dataset_dst_simple) # Создаем конечные папки, если не созданы
create_dir(dataset_dst_threads)


img_names =os.listdir(dataset_src) # Перечисляем все изображения в исходном фолдере
img_paths_src = ([osp.join(dataset_src, img_name) for img_name in img_names]) # Получаем список абсолютных путей

img_paths_dst_simple = ([osp.join(dataset_dst_simple, img_name) for img_name in img_names]) # Получаем список абсолютных путей исходного фолдера и конечного для обычного копирования
img_paths_dst_threads = ([osp.join(dataset_dst_threads, img_name) for img_name in img_names]) # Получаем список абсолютных путей исходного фолдера и конечного для многопоточного

# Делаем пару из исходного пути и конечного
# ('/home/path_src/img_.png', '/home/path_dst/img_.png'')
img_paths_simple = list(zip(img_paths_src, img_paths_dst_simple))
img_paths_threads = list(zip(img_paths_src, img_paths_dst_threads))

# функция копирования файла
def copy_file(img_paths):
    copy(img_paths[0], img_paths[1])


def main():
    logging.debug(f'Начало обычного копирования {ctime()}')
    for img_path in tqdm(img_paths_simple):
        copy_file(img_path)
    logging.debug(f'Конец обычного копирования {ctime()}')

    logging.debug(f'Начало многопоточного копирования {ctime()}')
    for img_path in tqdm(img_paths_threads):
        Thread(target=copy_file, args=(img_path,)).start()
    logging.debug(f'Конец многопоточного копирования {ctime()}')

# @atexit.register
# def _atexit():
#     print('ALL DONE')

if __name__ == '__main__':
    main()

