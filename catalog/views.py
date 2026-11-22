from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, JsonResponse
from django.core.paginator import Paginator
from .forms import ProductForm
from .models import Product, Contact
import json
from datetime import datetime
from django.views.decorators.csrf import csrf_exempt
from ai_logic import get_ai_response


def home(request):
    # products_list = Product.objects.all()
    products_list = Product.objects.select_related('category').order_by('-created_at')
    paginator = Paginator(products_list, 3)  # по 3 товара на страницу
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    latest_products = Product.objects.order_by('-created_at')[:5]
    print("Последние 5 товаров:", latest_products)
    return render(request, 'catalog/home.html', {'page_obj': page_obj})


def contacts(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')
        print(f"Имя: {name}\nEmail: {email}\nСообщение: {message}")
        return HttpResponse("""
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <title>Успешно</title>
</head>
<body style="font-family: sans-serif; text-align: center; margin-top: 50px; background-color: #f8f9fa;">
    <h3>Данные успешно отправлены и сохранены!</h3>
    <p style="color: #6c757d;">Вы вернётесь на главную страницу через <span id="timer" style="font-weight: bold;">3</span> сек...</p>
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
        """)
    contact = Contact.objects.first()
    return render(request, 'catalog/contacts.html', {'contact': contact})


def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'catalog/product_detail.html', {'product': product})


def product_create(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('catalog:home')
    else:
        form = ProductForm()
    return render(request, 'catalog/product_form.html', {'form': form})


def ai_init(request):
    current_hour = datetime.now().hour
    if 6 <= current_hour < 12:
        greeting = "Доброе утро"
    elif 12 <= current_hour < 18:
        greeting = "Добрый день"
    elif 18 <= current_hour < 23:
        greeting = "Добрый вечер"
    else:
        greeting = "Доброй ночи"
    return HttpResponse(
        f"{greeting}! Я твой ИИ-помощник магазина MY-RELAX. Чем я могу помочь?",
        content_type="text/plain; charset=utf-8"
    )


@csrf_exempt
def ai_chat(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body.decode("utf-8"))
            user_text = data.get("message", "").strip()
            history = data.get("history", [])
            context = data.get("context", {})
            if not isinstance(history, list):
                history = []
            if not isinstance(context, dict):
                context = {}
        except (UnicodeDecodeError, json.JSONDecodeError):
            return JsonResponse({"reply": "Некорректный формат запроса."}, status=400)

        if not user_text:
            return JsonResponse({"reply": "Введите сообщение."}, status=400)

        reply = get_ai_response(user_text, history, context)
        return JsonResponse({"reply": reply})
    return JsonResponse({"reply": "Метод не поддерживается."}, status=405)
