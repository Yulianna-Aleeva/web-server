import os
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .forms import BlogForm
from .models import Blog
from django.conf import settings
from django.core.mail import send_mail


class BlogListView(ListView):
    model = Blog
    template_name = 'blogs/blog_list.html'
    context_object_name = 'blogs'

    def get_queryset(self):
        return Blog.objects.filter(is_published=True).order_by('-created_at')


class BlogDetailView(DetailView):
    model = Blog
    template_name = 'blogs/blog_detail.html'
    context_object_name = 'blog'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        obj.views_count += 1
        obj.save(update_fields=['views_count'])

        if obj.views_count == 100:
            send_mail(
                subject='Ура! Статья набрала 100 просмотров',
                message=f'Поздравляем! Ваша статья «{obj.title}» достигла отметки в 100 просмотров на сайте MY-RELAX!',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[os.getenv('EMAIL_HOST_USER') or 'admin@my-relax.ru'],
                fail_silently=True,
            )
        return obj


class BlogCreateView(CreateView):
    model = Blog
    form_class = BlogForm
    template_name = 'blogs/blog_form.html'
    success_url = reverse_lazy('blogs:blog_list')


class BlogUpdateView(UpdateView):
    model = Blog
    form_class = BlogForm
    template_name = 'blogs/blog_form.html'

    def get_success_url(self):
        return reverse('blogs:blog_detail', kwargs={'pk': self.object.pk})


class BlogDeleteView(DeleteView):
    model = Blog
    template_name = 'blogs/blog_confirm_delete.html'
    success_url = reverse_lazy('blogs:blog_list')
