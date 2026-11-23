import os
import uuid
import requests
import urllib3
from typing import Any
from catalog.models import Category

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

TOKEN_URL = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"
CHAT_URL = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"


def build_knowledge() -> str:
    lines = [
        "Магазин товаров для релакса и отдыха MY-RELAX.",
        "Разделы сайта: / — главная, /catalog/ — каталог с фильтрацией по категориям и поиском, "
        "/blogs/ — блог с полезными статьями, /contacts/ — контакты и обратная связь.",
        "\nКатегории и актуальные товары из каталога:",
    ]

    categories = Category.objects.prefetch_related("product_set").all()
    if not categories.exists():
        lines.append("Категории пока не заполнены.")
        return "\n".join(lines)

    for category in categories:
        lines.append(
            f"\nКатегория «{category.name}» (/catalog/?category={category.pk}): "
            f"{category.description or 'товары для отдыха и релакса'}"
        )
        products = category.product_set.all()

        if not products:
            lines.append("- В этой категории пока нет товаров.")
        for product in products:
            status = "в наличии" if getattr(product, "is_available", True) else "нет в наличии"
            lines.append(
                f"- {product.name} (/products/{product.pk}/): {product.description} "
                f"Цена: {product.price} ₽ ({status})."
            )

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
        "Ты — дружелюбный ИИ-консультант интернет-магазина товаров для релакса и отдыха MY-RELAX.\n"
        "Помогай покупателям подобрать эфирные масла, свечи, благовония, морскую соль, бомбочки для ванны, "
        "массажёры, травяные чаи и маски для сна.\n"
        "Отвечай строго на основе предоставленной базы знаний, кратко и лаконично (1–3 предложения).\n"
        "НИКОГДА не выдумывай товары или цены от себя.\n\n"
        "РАЗРЕШЕННЫЕ ССЫЛКИ:\n"
        "Ты можешь использовать ссылки ТОЛЬКО в формате Markdown и только для этих разделов или конкретных товаров:\n"
        "- Весь каталог товаров: [Каталог](/catalog/)\n"
        "- Конкретная категория (подставь ID из базы): [Название категории](/catalog/?category=ID)\n"
        "- Карточка конкретного товара (подставь ID из базы): [Название товара](/products/ID/)\n"
        "- Почитать статьи о релаксе: [Блог](/blogs/)\n"
        "- Обратиться в поддержку: [Контакты](/contacts/)\n"
        "Любые другие ссылки, включая ссылки на главную страницу `(/)`, ЗАПРЕЩЕНЫ.\n\n"
        "=== БАЗА ЗНАНИЙ ===\n"
        f"{build_knowledge()}"
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
                "temperature": 0.2,
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
