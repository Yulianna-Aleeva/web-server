from django.urls import path
from catalog.views import (
    ProductListView,
    ContactsView,
    ProductDetailView,
    ProductCreateView,
    AiInitView,
    AiChatView,
)

app_name = 'catalog'

urlpatterns = [
    path('', ProductListView.as_view(), name='home'),
    path('contacts/', ContactsView.as_view(), name='contacts'),
    path('products/<int:pk>/', ProductDetailView.as_view(), name='product_detail'),
    path('products/create/', ProductCreateView.as_view(), name='product_create'),
    path('api/ai-init/', AiInitView.as_view(), name='ai_init'),
    path('api/ai-chat/', AiChatView.as_view(), name='ai_chat'),
]
