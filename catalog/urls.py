from django.urls import path
from catalog.views import (
    ProductListView,
    ProductDetailView,
    ProductCreateView,
    ProductUpdateView,
    ProductDeleteView,
    CatalogListView,
    ContactsView,
    AiInitView,
    AiChatView,
)

app_name = 'catalog'

urlpatterns = [
    path('', ProductListView.as_view(), name='home'),
    path('products/<int:pk>/', ProductDetailView.as_view(), name='product_detail'),
    path('products/create/', ProductCreateView.as_view(), name='product_create'),
    path('products/<int:pk>/update/', ProductUpdateView.as_view(), name='product_update'),
    path('products/<int:pk>/delete/', ProductDeleteView.as_view(), name='product_delete'),
    path('catalog/', CatalogListView.as_view(), name='catalog_list'),
    path('contacts/', ContactsView.as_view(), name='contacts'),
    path('api/ai-init/', AiInitView.as_view(), name='ai_init'),
    path('api/ai-chat/', AiChatView.as_view(), name='ai_chat'),
]
