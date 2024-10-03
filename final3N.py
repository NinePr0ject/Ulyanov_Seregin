import os
from PIL import Image
import easyocr
import re
import numpy as np

# Функция для обработки одного файла
def process_file(img_path):
    if not os.path.isfile(img_path):
        print(f"Ошибка: файл не найден или недоступен: {img_path}")
        return
    
    results = []
    try:
        dist = distance(img_path, black_pixels(img_path))
        rez = text_out(img_path)
        text_result = ' '.join(rez)               
        uvel, shkal = extract_values(text_result)

        results.append(f"Обрабатываемый файл: {os.path.basename(img_path)}")
        results.append(f"Длинна шкилы: {dist}")
        results.append(f"Увеличение: {uvel}")
        results.append(f"Число под шкалой: {shkal}")
        if shkal:
            fraction = dist / float(re.sub(r'[a-zA-Zμ]', '', shkal)) if shkal else 1
            results.append(f"Дробь: {fraction}")
        
        print("\n".join(results))
        
        # Сохранение результатов в текстовый файл
        save_results_to_file(img_path, results)

    except Exception as e:
        print(f"Ошибка при обработке файла: {e}")

# Дополнительные функции, необходимые для обработки изображений
def black_pixels(img_path):
    img = Image.open(img_path)
    img = img.convert('RGB')
    
    width, height = img.size
    last_black_y = -1
    
    for y in range(height - 1, -1, -1):
        pixel = img.getpixel((width - 1, y))
        if pixel == (0, 0, 0):
            last_black_y = y
        else:
            break
    print(f"Координата X: {width - 1}, Координата Y: {last_black_y}")
    
    crop_img = img.crop((0, last_black_y, width, height))    
    base_name = os.path.splitext(os.path.basename(img_path))[0]    
    notif, jpgs = os.path.splitext(img_path)
    img_path_2 = (notif+"_results.jpg")
    crop_img.save(img_path_2)
    
    return last_black_y

def distance(img_path, start_y):
    img = Image.open(img_path)
    img = img.convert('RGB')
    
    width, height = img.size
    first_white_index = None
    last_white_index = None

    for x in range(width):
        pixel = img.getpixel((x, start_y))
        if pixel == (255, 255, 255):
            if first_white_index is None:
                first_white_index = x
            last_white_index = x

    if first_white_index is not None and last_white_index is not None:
        return last_white_index - first_white_index
    return 0

def text_out(img_path):
    img = Image.open(img_path)
    img = img.convert('RGB')
    img_np = np.array(img)

    reader = easyocr.Reader(["en"], gpu=False, verbose=False)
    result = reader.readtext(img_np, detail=0, blocklist='SOo')
    return result

def extract_values(text):
    matches = re.findall(r'[xX](\d+\.?\d*[kK]?)(?:[^0-9]*?)(\d+\.?\d*[a-zA-Z]*)', text)

    if matches:
        uvel, shkal = matches[0]
        shkal = shkal.replace('p', 'μ')
    else:
        uvel, shkal = None, None

    return uvel, shkal

def save_results_to_file(img_path, results, combined=False):
    if combined:
        # Имя результирующего файла
        result_file_path = os.path.join(img_path, "all_results.txt")
        
        # Записываем результаты в файл
        with open(result_file_path, 'a', encoding='utf-8') as file:
            for result in results:
                file.write(result + "\n")
    else:
        # Формируем имя текстового файла на основе имени изображения
        base_name = os.path.splitext(os.path.basename(img_path))[0]
        text_file_path = os.path.join(os.path.dirname(img_path), f"{base_name}_results.txt")
        
        # Записываем результаты в файл
        with open(text_file_path, 'w', encoding='utf-8') as file:
            for result in results:
                file.write(result + "\n")
    
    print(f"Результаты сохранены в: {result_file_path if combined else text_file_path}")

img_path="D:\Учеба\Курбаков\ПСЗИ_2\Proga/1.tif"
process_file(img_path)

