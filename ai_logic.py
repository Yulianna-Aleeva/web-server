import json
import os
import re
import uuid
from typing import Any

import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

CATEGORY_META = {
    "cookies": (
        "Печеньки (игровая валюта), покупается за рубли",
        "Можно найти на Главной странице или в разделе Категории → Печеньки",
    ),
    "hints": (
        "Подсказки для игр, покупаются за печеньки",
        "Можно найти на Главной странице или в разделе Категории → Подсказки",
    ),
    "toys": (
        "Реплики игр (реальные товары), покупаются за рубли",
        "Можно найти на Главной странице или в разделе Категории → Реплики игр",
    ),
}

TOKEN_URL = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"
CHAT_URL = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"


def _parse_js_object(text: str, const_name: str) -> dict:
    match = re.search(rf"const {const_name}\s*=\s*(\{{.*?\}});", text, re.S)
    if not match:
        return {}
    js_object = match.group(1)
    js_object = re.sub(r"([{\s,])([A-Za-z_][A-Za-z0-9_]*)\s*:", r'\1"\2":', js_object)
    js_object = js_object.replace("'", '"')
    js_object = re.sub(r",\s*([\]}])", r"\1", js_object)
    return dict(json.loads(js_object))


def load_catalog() -> dict:
    path = os.path.join("static", "js", "products.js")
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as file:
        return _parse_js_object(file.read(), "CATALOG_DATA")


def load_emojis() -> dict:
    path = os.path.join("static", "js", "emojis.js")
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as file:
        return _parse_js_object(file.read(), "EMOJIS")


def build_knowledge() -> str:
    catalog = load_catalog()
    emojis = load_emojis()
    lines = [
        "Магазин MY-RELAX.",
        "Разделы сайта: / — главная, /categories — категории, /orders — заказы, /contacts — контакты.",
        "\nКаталог товаров:",
    ]
    for key, items in catalog.items():
        title, url = CATEGORY_META.get(key, (key, "/categories"))
        lines.append(f"\n{title} — {url}")
        for item in items:
            name = item.get("name", "")
            desc = item.get("desc")
            price = item.get("price", "")
            currency_key = item.get("currency", "")
            currency = emojis.get(currency_key, currency_key)
            if desc:
                lines.append(f"- {name}: {desc}. Цена: {price} {currency}")
            else:
                lines.append(f"- {name}: цена {price} {currency}")
    return "\n".join(lines)


def build_user_context(context: dict[Any, Any] | None = None) -> str:
    context = context if isinstance(context, dict) else {}
    emojis = load_emojis()
    rub, cookie = emojis.get("RUBLE", "RUBLE"), emojis.get("COOKIE", "COOKIE")

    def s(value, limit=60):
        return str(value)[:limit]

    def items(key, limit):
        value = context.get(key)
        return [x for x in value[:limit] if isinstance(x, dict)] if isinstance(value, list) else []

    balance = context.get("balance")
    balance = balance if isinstance(balance, dict) else {}

    lines = [
        "\nКонтекст сессии:",
        f"Баланс: {s(balance.get('rubles', 0))} {rub} и {s(balance.get('cookies', 0))} {cookie}.",
        "Как покупать: Печеньки — кнопка «Купить» (списываются рубли); Подсказки — кнопка «Добавить» "
        "(списываются печеньки, подсказка попадает в игру); Реплики игр — «В корзину», затем «Оформить заказ» "
        "на странице Заказы (списываются рубли). "
        "Пополнить рубли — плитки +100 / +500 / +1000 в блоке «Пополнить» внизу меню слева.",
    ]

    cart = items("cart", 20)
    if cart:
        lines.append(f"Корзина (итого {s(context.get('cart_total', 0))} {rub}):")
        lines += [f"- {s(c.get('name'))} × {s(c.get('qty'))} = {s(c.get('sum'))} {rub}" for c in cart]
    else:
        lines.append("Корзина пуста.")

    orders = items("orders", 10)
    if orders:
        lines.append("Последние заказы (новые сверху):")
        for o in orders:
            currency = emojis.get(s(o.get("currency", "")), s(o.get("currency", "")))
            lines.append(
                f"- #{s(o.get('number'))}: {s(o.get('name'))} ({s(o.get('category'))}) — "
                f"{s(o.get('price'))} {currency}, {s(o.get('status'))}"
            )
    else:
        lines.append("Заказов пока нет.")

    inventory = items("inventory", 20)
    if inventory:
        lines.append("Подсказки в игре: " + ", ".join(f"{s(i.get('name'))} × {s(i.get('qty'))}" for i in inventory))

    return "\n".join(lines)


def _load_credentials() -> str:
    if os.path.exists(".env"):
        with open(".env", "r", encoding="utf-8") as file:
            for line in file:
                if line.startswith("GIGACHAT_CREDENTIALS="):
                    return line.split("=", 1)[1].strip()
    return os.getenv("GIGACHAT_CREDENTIALS", "").strip()


def get_ai_response(user_text: str, history: list[Any] | None = None, context: dict[Any, Any] | None = None) -> str:
    credentials = _load_credentials()
    if not credentials:
        return "Данные доступа GigaChat не настроены."

    system_prompt = (
        "Ты — ИИ-консультант интернет-магазина для игрового сайта "
        "MY-RELAX.\n"
        "Отвечай строго на основе предоставленной базы знаний, "
        "кратко и лаконично (1-2 предложения).\n"
        "НИКОГДА не выдумывай информацию от себя.\n\n"
        "ЖЁСТКИЕ ШАБЛОНЫ ОТВЕТОВ (ОТВЕЧАЙ СТРОГО ТАК):\n"
        "1. Если пользователь спрашивает «где баланс», «где мой баланс», "
        "«сколько у меня печенек» или задает любой вопрос про "
        "местонахождение баланса рублей или печенек — ты обязан "
        "ответить строго этой фразой и ни словом больше:\n"
        "«Твой баланс рублей и печенек указан в левом меню сайта "
        "(в самом низу).»\n"
        "Запрещено делать слова из этой фразы ссылками. "
        "Не используй Markdown.\n\n"
        "РАЗРЕШЕННЫЕ ССЫЛКИ:\n"
        "Ты можешь использовать ссылки ТОЛЬКО в формате Markdown "
        "и только для этих разделов:\n"
        "- Купить валюту: [Печеньки](/categories#cookies)\n"
        "- Купить подсказки: [Подсказки](/categories#hints)\n"
        "- Купить реплики игр: [Реплики игр](/categories#toys)\n"
        "- Посмотреть заказы: [Заказы](/orders)\n"
        "- Обратиться в поддержку: [Контакты](/contacts)\n"
        "Любые другие ссылки, включая ссылки на главную страницу `(/)` "
        "или на слово «баланс», полностью ЗАПРЕЩЕНЫ.\n\n"
        "=== БАЗА ЗНАНИЙ ===\n"
        f"{build_knowledge()}\n"
        f"{build_user_context(context)}"
    )

    messages = [{"role": "system", "content": system_prompt}]
    for item in history or []:
        role = item.get("role")
        content = str(item.get("content", ""))[:500]
        if role in ("user", "assistant") and content:
            messages.append({"role": role, "content": content})
    messages.append({"role": "user", "content": user_text})

    try:
        token_response = requests.post(
            TOKEN_URL,
            headers={
                "Authorization": f"Basic {credentials}",
                "RqUID": str(uuid.uuid4()),
                "Content-Type": "application/x-www-form-urlencoded",
            },
            data={"scope": "GIGACHAT_API_PERS"},
            verify=False,
            timeout=20,
        )
        token_response.raise_for_status()
        access_token = token_response.json()["access_token"]

        chat_response = requests.post(
            CHAT_URL,
            headers={
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
            },
            json={
                "model": "GigaChat",
                "messages": messages,
                "temperature": 0.1,
                "max_tokens": 300,
            },
            verify=False,
            timeout=60,
        )
        chat_response.raise_for_status()

        return str(chat_response.json()["choices"][0]["message"]["content"]).strip()

    except requests.Timeout:
        return "GigaChat не ответил вовремя."
    except requests.RequestException:
        return "Не удалось подключиться к GigaChat API. Проверьте GIGACHAT_CREDENTIALS в .env файле."
    except (KeyError, IndexError, ValueError):
        return "Сервер ИИ вернул некорректный ответ."
