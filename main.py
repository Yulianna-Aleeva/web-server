import json
import mimetypes
import os
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import unquote, urlparse

from ai_logic import get_ai_response

HOST_NAME = "localhost"
SERVER_PORT = 8085


def greeting_time() -> str:
    """Возвращает приветствие в зависимости от текущего времени суток."""
    current_hour = datetime.now().hour
    if 6 <= current_hour < 12:
        return "Доброе утро"
    elif 12 <= current_hour < 18:
        return "Добрый день"
    elif 18 <= current_hour < 23:
        return "Добрый вечер"
    else:
        return "Доброй ночи"


class MyServer(BaseHTTPRequestHandler):

    def send_bytes(self, content: bytes, content_type: str, status: int = 200):
        """Отправка байтового ответа с заголовками."""
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def send_json(self, data: dict, status: int = 200):
        """Отправка JSON-ответа."""
        content = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_bytes(content, "application/json; charset=utf-8", status)

    def do_POST(self):
        """Обработка входящих POST-запросов (форма контактов и чат с ИИ)."""
        path = urlparse(self.path).path

        try:
            content_length = int(self.headers.get("Content-Length", 0))
        except ValueError:
            self.send_error(400, "Invalid Content-Length")
            return

        if content_length > 50000:
            self.send_error(413, "Request Too Large")
            return

        if path == "/api/ai-chat":
            try:
                body = self.rfile.read(content_length)
                data = json.loads(body.decode("utf-8"))
                user_text = data.get("message", "").strip()
                history = data.get("history", [])
                context = data.get("context", {})
                if not isinstance(history, list):
                    history = []
                if not isinstance(context, dict):
                    context = {}
            except (UnicodeDecodeError, json.JSONDecodeError):
                self.send_json({"reply": "Некорректный формат запроса."}, 400)
                return

            if not user_text:
                self.send_json({"reply": "Введите сообщение."}, 400)
                return

            reply = get_ai_response(user_text, history, context)
            self.send_json({"reply": reply})
            return

        if path == "/contacts":
            post_data = self.rfile.read(content_length).decode("utf-8")
            decoded_data = unquote(post_data)
            print(f"Принятые данные: {decoded_data}")

            try:
                with open("messages.txt", "a", encoding="utf-8") as file:
                    file.write(decoded_data + "\n")
            except OSError:
                self.send_error(500, "Message Save Error")
                return

            response = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <title>Успешно</title>
</head>
<body style="font-family: sans-serif; text-align: center; margin-top: 50px; background-color: #f8f9fa;">
    <h3>Данные успешно отправлены и сохранены!</h3>
    <p style="color: #6c757d;">Вы вернётесь на главную страницу через "
    u"<span id=\"timer\" style=\"font-weight: bold;\">3</span> сек...</p>
    <script>
        let count = 3;
        const timerElement = document.getElementById("timer");
        const interval = setInterval(() => {
            count--;
            timerElement.textContent = count;
            if (count <= 0) {
                clearInterval(interval);
                window.location.href = "/";
            }
        }, 1000);
    </script>
</body>
</html>
"""
            self.send_bytes(response.encode("utf-8"), "text/html; charset=utf-8")
            return

        self.send_error(404, "Not Found")

    def do_GET(self):
        """Обработка входящих GET-запросов (маршрутизация страниц, статики и API)."""
        parsed_url = urlparse(self.path)
        path = parsed_url.path

        # Базовая директория проекта для безопасного поиска файлов
        base_dir = os.path.dirname(os.path.abspath(__file__))

        if path.startswith("/static/"):
            # Формируем безопасный путь к файлу статики
            file_path = os.path.join(base_dir, path.lstrip("/"))
            if not os.path.isfile(file_path):
                self.send_error(404, "File Not Found")
                return

            # Автоматически определяем тип файла (картинки, стили, скрипты, шрифты)
            content_type, _ = mimetypes.guess_type(file_path)
            if not content_type:
                content_type = "application/octet-stream"
            # Дописываем кодировку для текстовых файлов
            if "text/" in content_type or content_type == "application/javascript":
                content_type += "; charset=utf-8"

            try:
                with open(file_path, "rb") as file:
                    self.send_bytes(file.read(), content_type)
            except OSError:
                self.send_error(500, "File Read Error")
            return

        pages = {
            "/": "index.html",
            "/categories": "categories.html",
            "/orders": "orders.html",
            "/contacts": "contacts.html",
        }

        if path in pages:
            page_path = os.path.join(base_dir, pages[path])
            try:
                with open(page_path, "rb") as file:
                    self.send_bytes(file.read(), "text/html; charset=utf-8")
            except OSError:
                self.send_error(404, "Page Not Found")
            return

        if path == "/api/ai-init":
            greeting = greeting_time()
            response = f"{greeting}! Я твой ИИ-помощник магазина MY-RELAX. Чем я могу помочь?"
            self.send_bytes(response.encode("utf-8"), "text/plain; charset=utf-8")
            return

        self.send_error(404, "Page Not Found")


if __name__ == "__main__":
    web_server = ThreadingHTTPServer((HOST_NAME, SERVER_PORT), MyServer)
    print(f"Server started http://{HOST_NAME}:{SERVER_PORT}")

    try:
        web_server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        web_server.server_close()
        print("Server stopped.")
