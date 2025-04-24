import cv2
import pyaudio
import numpy as np
import threading
import time
import os
from dotenv import load_dotenv
import telebot

# Загрузка env
load_dotenv("/home/pi3/cv22/config/.env")

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
SOUND_THRESHOLD = float(os.getenv("SOUND_THRESHOLD", 0.1))
DEVICE_INDEX = 2  #id микро
CASCADE_PATH = "/home/pi3/cv22/models/haarcascade_russian_plate_number.xml"

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

# Флаги
sound_detected = False
plate_detected = False

#  камера(параметры)
cap = cv2.VideoCapture(0)
plate_cascade = cv2.CascadeClassifier(CASCADE_PATH)

def monitor_sound():
    global sound_detected
    p = pyaudio.PyAudio()

    while True:
        try:
            stream = p.open(format=pyaudio.paInt16,
                            channels=1,
                            rate=44100,
                            input=True,
                            input_device_index=DEVICE_INDEX,
                            frames_per_buffer=1024)

            while True:
                data = np.frombuffer(stream.read(1024, exception_on_overflow=False), dtype=np.int16)
                volume = np.linalg.norm(data) / 1024

                if volume > SOUND_THRESHOLD:
                    print(f"[SOUND] Громкий звук обнаружен: Громкость: {volume:.3f}")
                    sound_detected = True

                time.sleep(0.01)

        except Exception as e:
            print(f"[ERROR] Ошибка (звукк: {e}")
            time.sleep(2)
        finally:
            try:
                stream.stop_stream()
                stream.close()
            except:
                pass

def monitor_camera():
    global plate_detected
    while True:
        ret, frame = cap.read()
        if not ret:
            continue

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        plates = plate_cascade.detectMultiScale(gray, 1.3, 5)

        if len(plates) > 0:
            print(f"[PLATE] Обнаружен номерной знак!")
            plate_detected = True

        

        time.sleep(0.05)

def save_and_send_video():
    print("[ACTION] Сохраняю видео 5 секунд...")
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter('output.avi', fourcc, 20.0, (640, 480))

    start_time = time.time()
    while time.time() - start_time < 5:  # пишем n секунд видео (5)
        ret, frame = cap.read()
        if ret:
            out.write(frame)

    out.release()

    print("[ACTION] Отправляю видео в Telegram...")
    with open('output.avi', 'rb') as video:
        bot.send_video(TELEGRAM_CHAT_ID, video)

    print("[ACTION] Видео отправлено. Продолжаю работать...")

def main_loop():
    global sound_detected, plate_detected

    while True:
        if sound_detected and plate_detected:
            save_and_send_video()
            sound_detected = False
            plate_detected = False
        else:
            #  продолжаем слушать и смотреть кадры
            time.sleep(0.1)

if __name__ == "__main__":
    print("[INFO] Запуск системы мониторинга...")

    # Параллельно запускаем поток звука и поток камеры
    sound_thread = threading.Thread(target=monitor_sound, daemon=True)
    camera_thread = threading.Thread(target=monitor_camera, daemon=True)

    sound_thread.start()
    camera_thread.start()

    # Основной цикл
    main_loop()
