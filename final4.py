import customtkinter as ctk
from tkinter import filedialog
import os
from PIL import Image
import easyocr
import re
import numpy as np
from threading import Thread

# Глобальная переменная для хранения выбранного пути
path_x = ""

# Функция для выбора файла
def choose_file():
    global path_x
    file_path = filedialog.askopenfilename()
    if file_path:
        path_x = file_path
        print("Путь к файлу:", path_x)
        thread = Thread(target=process_single_file, args=(path_x,))
        thread.start()

# Функция для выбора папки
def choose_folder():
    global path_x
    folder_path = filedialog.askdirectory()
    if folder_path:
        path_x = folder_path
        print("Путь к папке:", path_x)
        thread = Thread(target=process_all_files, args=(path_x,))
        thread.start()

# Функция для обработки одного файла
def process_single_file(image_path):
    if not os.path.isfile(image_path):
        print(f"Ошибка: файл не найден или недоступен: {image_path}")
        return
    
    results = []
    try:
        black_pixels_y, image_path_2 = black_pixels(image_path)
        dist = distance_white(image_path, black_pixels_y)
        rez = text_out(image_path_2)
        text_result = ' '.join(rez)               
        uvel, shkal = extract_values(text_result)

        results.append(f"Обрабатываемый файл: {os.path.basename(image_path)}")
        results.append(f"Длинна шкилы: {dist}")
        results.append(f"Увеличение: {uvel}")
        results.append(f"Число под шкалой: {shkal}")
        if shkal:
            fraction = dist / float(re.sub(r'[a-zA-Zμ]', '', shkal)) if shkal else 1
            results.append(f"Дробь: {fraction}")
        
        print("\n".join(results))
        
        # Сохранение результатов в текстовый файл
        save_results_to_file(image_path, results)

    except Exception as e:
        print(f"Ошибка при обработке файла: {e}")

# Функция для обработки всех файлов в папке
def process_all_files(directory):
    print(directory)
    all_results = []  # Список для хранения результатов всех файлов
    for filename in os.listdir(directory):
        if filename.endswith('.tif'):
            image_path = os.path.join(directory, filename)
            print(f"Обработка файла: {filename}")
            results = process_single_file(image_path)
            if results:  # Если результаты не пусты
                all_results.extend(results)  # Добавляем результаты

                # Добавляем разделитель между результатами
                all_results.append("\n" + "="*30 + "\n")

    # Сохраняем все результаты в один файл
    if all_results:
        save_results_to_file(directory, all_results, combined=True)

# Дополнительные функции, необходимые для обработки изображений
def black_pixels(image_path):
    img = Image.open(image_path)
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
    
    
    obrezka_img = img.crop((0, last_black_y, width, height))
    
    base_name = os.path.splitext(os.path.basename(image_path))[0]
    
    no_tif, jpgs = os.path.splitext(image_path)
    image_path_2 = (no_tif+"_results.jpg")
    obrezka_img.save(image_path_2)
    print(image_path_2)
    
    return last_black_y, image_path_2

def distance_white(image_path, start_y):
    img = Image.open(image_path)
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

def text_out(image_path):
    img = Image.open(image_path)
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

def save_results_to_file(image_path, results, combined=False):
    if combined:
        # Имя результирующего файла
        result_file_path = os.path.join(image_path, "all_results.txt")
        
        # Записываем результаты в файл
        with open(result_file_path, 'a', encoding='utf-8') as file:
            for result in results:
                file.write(result + "\n")
    else:
        # Формируем имя текстового файла на основе имени изображения
        base_name = os.path.splitext(os.path.basename(image_path))[0]
        text_file_path = os.path.join(os.path.dirname(image_path), f"{base_name}_results.txt")
        
        # Записываем результаты в файл
        with open(text_file_path, 'w', encoding='utf-8') as file:
            for result in results:
                file.write(result + "\n")
    
    print(f"Результаты сохранены в: {result_file_path if combined else text_file_path}")

# Создание основного окна
app = ctk.CTk()
app.title("Выбор файла или папки")
app.geometry("300x200")

# Кнопка для выбора файла
file_button = ctk.CTkButton(app, text="Файл", command=choose_file, width=200, height=60, font=("Helvetica", 20))
file_button.pack(pady=20)

# Кнопка для выбора папки
folder_button = ctk.CTkButton(app, text="Папка", command=choose_folder, width=200, height=60, font=("Helvetica", 20))
folder_button.pack(pady=20)

# Запуск приложения
app.mainloop()
