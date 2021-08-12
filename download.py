import os
import logging
from urllib.parse import urlparse

import requests
import time
from tqdm import tqdm

import requests
import shutil
import tempfile

def ensure_content_length(
    url, *args, method='GET', session=None, max_size=100000*1024*1024,  # 100Гб  максимальный размер для скачивания
    **kwargs
):
    kwargs['stream'] = True
    session = session or requests.Session()
    r = session.request(method, url, *args, **kwargs)
    if 'Content-Length' not in r.headers:
        # stream content into a temporary file so we can get the real size
        spool = tempfile.SpooledTemporaryFile(max_size)
        shutil.copyfileobj(r.raw, spool)
        r.headers['Content-Length'] = str(spool.tell())
        spool.seek(0)
        # replace the original socket with our temporary file
        r.raw._fp.close()
        r.raw._fp = spool
    return r

logger = logging.getLogger()
logging.basicConfig(level=logging.INFO)


def download(url: str, file_path='', auth=None,  attempts=1000000):
    """Downloads a URL content into a file (with large file support by streaming)

    :param url: URL to download
    :param file_path: Local file name to contain the data downloaded
    :param attempts: Number of attempts
    :return: New file path. Empty string if the download failed
    """
    if not file_path:
        file_path = os.path.realpath(os.path.basename(url))
    logger.info(f'Downloading {url} content to {file_path}')
    url_sections = urlparse(url)
    if not url_sections.scheme:
        logger.debug('The given url is missing a scheme. Adding http scheme')
        url = f'http://{url}'
        logger.debug(f'New url: {url}')
    for attempt in range(1, attempts+1):
        try:
            if attempt > 1:
                time.sleep(10)  # 10 seconds wait time between downloads

            with open(file_path, 'ab') as out_file: # mode ab - добавляет в бинарном режиме
                headers = {}
                pos = out_file.tell() # узнает размер уже скачанного

                if pos:
                    headers['Range'] = f'bytes={pos}-' # добавляет в headers место, с которого начинать скачивать
                with ensure_content_length(url, headers=headers, auth=auth, stream=True) as response:

                    response.raise_for_status()
                    print(int(response.headers['Content-Length'])//(1024*1024), 'МБ')
                    total_size = int(response.headers.get('content-length'))  # получаем размер файла по url
                    logger.info(f'Скачано {pos//(1024*1024)} MB, осталось скачать {total_size//(1024*1024)} МБ ({round(total_size/(1024*1024*1000), 2)} ГБ)')

                    for chunk in tqdm(response.iter_content(chunk_size=1024*1024), total=total_size//(1024*1024), unit='MB'):  # 1MB chunks
                        out_file.write(chunk)
                logger.info('Download finished successfully')


                return file_path
        except Exception as ex:
            logger.error(f'Attempt #{attempt} failed with error: {ex}')
    return ''



if __name__ == "__main__":
    
    login = ''
    password = ''
    auth = (login, password)
    url ='https://github.com/openvinotoolkit/cvat/archive/refs/heads/develop.zip'



    path_ = '/home/local/Documents'
    filename = '2021_07_30.zip'
    file_path = os.path.join(path_, filename)
    download(url, file_path,auth=auth)
