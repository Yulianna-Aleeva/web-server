import json
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from .forms import ProductForm
from .models import Product, Contact, Category, Feedback
from datetime import datetime
from django.views.decorators.csrf import csrf_exempt
from ai_logic import get_ai_response
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, DetailView, CreateView, TemplateView, View, UpdateView, DeleteView
from django.utils.decorators import method_decorator
from django.db.models import Q


class ProductListView(ListView):
    model = Product
    template_name = 'catalog/home.html'
    paginate_by = 3

    def get_queryset(self):
        return Product.objects.select_related('category').filter(is_available=True).order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cats = {c.name.lower(): c.id for c in Category.objects.all()}
        context['cat_aroma'] = cats.get('ароматерапия', '')
        context['cat_spa'] = cats.get('спа и массаж', '')
        context['cat_sleep'] = cats.get('сон и уют', '')
        return context


class ProductDetailView(DetailView):
    model = Product
    template_name = 'catalog/product_detail.html'
    context_object_name = 'product'


class ProductCreateView(CreateView):
    model = Product
    form_class = ProductForm
    template_name = 'catalog/product_form.html'
    success_url = reverse_lazy('catalog:home')


class ProductUpdateView(UpdateView):
    model = Product
    form_class = ProductForm
    template_name = 'catalog/product_form.html'

    def get_success_url(self):
        return reverse('catalog:product_detail', args=[self.object.pk])


class ProductDeleteView(DeleteView):
    model = Product
    template_name = 'catalog/product_confirm_delete.html'
    success_url = reverse_lazy('catalog:home')


class ContactsView(TemplateView):
    template_name = 'catalog/contacts.html'

    def post(self, request, *args, **kwargs):
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        message = request.POST.get('message', '').strip()

        if name and email and message:
            Feedback.objects.create(name=name, email=email, message=message)
            return render(request, self.template_name, {'success': True})

        return render(request, self.template_name, {'error': 'Заполните все поля формы.'})


class CatalogListView(ListView):
    model = Product
    template_name = 'catalog/catalog_list.html'
    context_object_name = 'products'

    def get_paginate_by(self, queryset):
        per_page = self.request.GET.get('per_page', '6')
        if per_page == 'all':
            return None
        try:
            return int(per_page)
        except ValueError:
            return 6

    def get_queryset(self):
        queryset = Product.objects.select_related('category').all()

        # Фильтр по категории
        category_id = self.request.GET.get('category')
        if category_id and category_id.isdigit():
            queryset = queryset.filter(category_id=int(category_id))

        # Поиск по названию и описанию
        query = self.request.GET.get('q', '').strip()
        if query:
            queryset = queryset.filter(
                Q(name__icontains=query) | Q(description__icontains=query)
            )

        # Сортировка
        sort = self.request.GET.get('sort', '-created_at')
        allowed_sorts = {
            '-created_at': '-created_at',
            'price_asc': 'price',
            'price_desc': '-price',
            'name': 'name',
        }
        return queryset.order_by(allowed_sorts.get(sort, '-created_at'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['selected_category'] = self.request.GET.get('category', '')
        context['selected_sort'] = self.request.GET.get('sort', '-created_at')
        context['selected_per_page'] = self.request.GET.get('per_page', '6')
        context['search_query'] = self.request.GET.get('q', '')
        return context


# --- ИИ-Ассистент ---

class AiInitView(View):
    def get(self, request, *args, **kwargs):
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


@method_decorator(csrf_exempt, name='dispatch')
class AiChatView(View):
    def post(self, request, *args, **kwargs):
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
