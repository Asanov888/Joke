from os import system, path, mkdir, getcwd
from bs4 import BeautifulSoup
import httpx
import json
from datetime import datetime, timedelta
from fake_useragent import UserAgent
import re
import threading
import time
import cv2
from pytesseract import pytesseract

on_start = ''' _____        _       ______                          
|_   _|      | |      |  _  \                         
  | |    ___ | |  ___ | | | | _   _  _ __ ___   _ __  
  | |   / _ \| | / _ \| | | || | | || '_ ` _ \ | '_ \ 
  | |  |  __/| ||  __/| |/ / | |_| || | | | | || |_) |
  \_/   \___||_| \___||___/   \__,_||_| |_| |_|| .__/ 
                                               | |    
Updated by DeCoded                             |_|    
'''

antipublic = set()

def transliterate(text, translit_dict):
    result = []
    for char in text:
        if char in translit_dict:
            result.append(translit_dict[char])
        else:
            result.append(char)
    return ''.join(result)

def transliterate_name(name):
    if not re.search('[а-яА-Я]', name):
        return name
    alphabet = {
        'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'yo', 'ж': 'zh', 'з': 'z',
        'и': 'i', 'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm', 'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r',
        'с': 's', 'т': 't', 'у': 'u', 'ф': 'f', 'х': 'kh', 'ц': 'ts', 'ч': 'ch', 'ш': 'sh', 'щ': 'sch',
        'ъ': '', 'ы': 'y', 'ь': '', 'э': 'e', 'ю': 'yu', 'я': 'ya',
        'А': 'A', 'Б': 'B', 'В': 'V', 'Г': 'G', 'Д': 'D', 'Е': 'E', 'Ё': 'Yo', 'Ж': 'Zh', 'З': 'Z',
        'И': 'I', 'Й': 'Y', 'К': 'K', 'Л': 'L', 'М': 'M', 'Н': 'N', 'О': 'O', 'П': 'P', 'Р': 'R',
        'С': 'S', 'Т': 'T', 'У': 'U', 'Ф': 'F', 'Х': 'Kh', 'Ц': 'Ts', 'Ч': 'Ch', 'Ш': 'Sh', 'Щ': 'Sch',
        'Ъ': '', 'Ы': 'Y', 'Ь': '', 'Э': 'E', 'Ю': 'Yu', 'Я': 'Ya'
    }

    return transliterate(name, alphabet)
    

class cs:
    INFO = '\033[93m'
    GREEN = '\033[92m'
    END = '\033[0m'

User_Agent = f'{UserAgent().random}'

_ = system("cls")
print(on_start)
unchecked_name = input(f"{cs.INFO}Name: ")
age = input("Age: ")
offset = input("Offset: ")
now = datetime.now()
start = int((now - timedelta(days=int(age)*30)).month)
print(f"Search from: 01.{start:02}{cs.END}")


MAX_THREADS = 30

def download_photos(name, day, month, offset):
    HEADERS = {
        'User-Agent': User_Agent
    }
    url = f"https://telegra.ph/{name}-{month}-{day}{offset}"
    response = httpx.get(url, headers=HEADERS)
    soup = BeautifulSoup(response.content, 'html.parser')

    items = soup.findAll('img')
    photos = []
    for item in items:
        src = item.get('src')
        if "http" not in src and src not in antipublic:
            photos.append(f"https://telegra.ph{src}")
            antipublic.add(src)
    if photos:
        print(f"{cs.GREEN}DOWNLOAD PHOTOS | Start | {day}.{month}{offset}{cs.END}")
        if not path.isdir(f"{getcwd()}\\images"):
            mkdir(f"{getcwd()}\\images")
        if not path.isdir(f"{getcwd()}\\images\\{name}"):
            mkdir(f"{getcwd()}\\images\\{name}")
        if not path.isdir(f"{getcwd()}\\images\\{name}\\{day}_{month}_{offset[1:]}"):
            mkdir(f"{getcwd()}\\images\\{name}\\{day}_{month}_{offset[1:]}")
        for i in range(len(photos)):
            try:
                response = httpx.get(photos[i], headers=HEADERS)
                extension = photos[i].split('.')[-1]
                with open(
                    f"images/{name}/{day}_{month}_{offset[1:]}/{month}_{day}_{offset[1:]}_{i}.{extension}",
                    "wb",
                ) as file:
                    file.write(response.content)
            except:
                pass

# Define a function to check if a video contains visible text
def video_contains_text(video_path):
    cap = cv2.VideoCapture(video_path)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    success, frame = cap.read()

    for _ in range(frame_count):
        try:
            text = pytesseract.image_to_string(frame)
        except pytesseract.TesseractNotFoundError:
            print(f"{cs.INFO}Tesseract не найден, установите Tesseract-OCR для Windows: https://tesseract-ocr.github.io/tessdoc/ {cs.END}")
            exit()
        if text and not text.isspace():
            for detect in ['onion', 'present', 'porno', 'com', 'session']:
                if detect in text.lower():
                    return True
        success, frame = cap.read()
    return False

# Modify the download_videos function as follows:
def download_videos(name, day, month, offset):
    HEADERS = {
        'User-Agent': User_Agent
    }
    url = f"https://telegra.ph/{name}-{month}-{day}{offset}"
    response = httpx.get(url, headers=HEADERS)
    soup = BeautifulSoup(response.content, 'html.parser')

    items_vid = soup.findAll('video')
    videos = []
    for item in items_vid:
        src = item.get('src')
        if "http" not in src and src not in antipublic:
            video_url = f"https://telegra.ph{src}"
            antipublic.add(src)
            if not video_contains_text(video_url):
                videos.append(video_url)

    if videos:
        print(f"{cs.GREEN}DOWNLOAD VIDEOS | Start | {day}.{month}{offset}{cs.END}")
        if not path.isdir(f"{getcwd()}\\images"):
            mkdir(f"{getcwd()}\\images")
        if not path.isdir(f"{getcwd()}\\images\\{name}"):
            mkdir(f"{getcwd()}\\images\\{name}")
        if not path.isdir(f"{getcwd()}\\images\\{name}\\{day}_{month}_{offset[1:]}"):
            mkdir(f"{getcwd()}\\images\\{name}\\{day}_{month}_{offset[1:]}")
        for i, video_url in enumerate(videos):
            try:
                response = httpx.get(video_url, headers=HEADERS)
                extension = video_url.split('.')[-1]
                with open(
                    f"images/{name}/{day}_{month}_{offset[1:]}/{month}_{day}_{offset[1:]}_{i}.{extension}",
                    "wb",
                ) as file:
                    file.write(response.content)
            except:
                pass

def parse(name, day, month, offset):
    download_photos(name, day, month, offset)
    download_videos(name, day, month, offset)

    media_links = list(antipublic)

    current_date = datetime.now().strftime("%Y-%m-%d")
    file_name = f"links_{current_date}.txt"

    # Write media links to the file
    with open(file_name, "w") as file:
        for link in media_links:
            file.write(f'https://telegra.ph{link}' + "\n")

def main():
    print("")
    threads = []
    for _month in range(start, now.month):
        for _day in range(1, 31):
            for _offset in range(1, int(offset) + 1):
                if _offset == 1:
                    t = threading.Thread(target=parse, args=(name, f"{_day:02}", f"{_month:02}", ""), daemon=True)
                else:
                    t = threading.Thread(target=parse, args=(name, f"{_day:02}", f"{_month:02}", f"-{_offset}"), daemon=True)
                threads.append(t)
                t.start()
                while threading.active_count() > MAX_THREADS:
                    time.sleep(1)
    
    for t in threads:
        t.join()

if __name__ == "__main__":
    name = transliterate_name(unchecked_name)
    main()
