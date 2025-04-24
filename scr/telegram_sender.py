import telebot

class TelegramSender:
    def __init__(self, token, chat_id):
        self.bot = telebot.TeleBot(token)
        self.chat_id = chat_id

    def send_video(self, file_path):
        with open(file_path, "rb") as video:
            self.bot.send_document(self.chat_id, video)  # Отправляем  файлом чтобы не  падать на больших объеме


