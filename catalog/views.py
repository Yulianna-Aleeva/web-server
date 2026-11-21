from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.core.paginator import Paginator
from .forms import ProductForm
from .models import Product, Contact


def home(request):
    products_list = Product.objects.all()
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
