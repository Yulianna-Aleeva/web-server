from django.urls import path
from catalog.views import home, contacts, product_detail, product_create, ai_init, ai_chat

app_name = 'catalog'

urlpatterns = [
    path('', home, name='home'),
    path('contacts/', contacts, name='contacts'),
    path('products/<int:pk>/', product_detail, name='product_detail'),
    path('products/create/', product_create, name='product_create'),
    path('api/ai-init', ai_init, name='ai_init'),
    path('api/ai-chat', ai_chat, name='ai_chat'),
]
