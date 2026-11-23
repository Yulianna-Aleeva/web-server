from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from .forms import ProductForm
from .models import Product, Contact
import json
from datetime import datetime
from django.views.decorators.csrf import csrf_exempt
from ai_logic import get_ai_response
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, DetailView, CreateView, TemplateView, View, UpdateView, DeleteView
from django.utils.decorators import method_decorator


class ProductListView(ListView):
    model = Product
    template_name = 'catalog/home.html'
    paginate_by = 3

    def get_queryset(self):
        return Product.objects.select_related('category').order_by('-created_at')


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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['contact'] = Contact.objects.first()
        return context

    def post(self, request, *args, **kwargs):
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')
        print(f"Новое сообщение с сайта: {name} ({email}) -> {message}")
        context = self.get_context_data(**kwargs)
        context['success'] = True
        return render(request, self.template_name, context)


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
