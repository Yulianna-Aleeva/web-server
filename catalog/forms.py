from django import forms
from .models import Product
from django.core.exceptions import ValidationError

FORBIDDEN_WORDS = [
    'казино',
    'криптовалюта',
    'крипта',
    'биржа',
    'дешево',
    'бесплатно',
    'обман',
    'полиция',
    'радар',
]


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description', 'image', 'category', 'price', 'is_available']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.update({'class': 'form-check-input'})
            else:
                field.widget.attrs.update({'class': 'form-control'})

        self.fields['name'].widget.attrs.update({'placeholder': 'Введите название товара'})
        self.fields['description'].widget.attrs.update({
            'placeholder': 'Опишите товар',
            'rows': 4,
        })
        self.fields['price'].widget.attrs.update({'placeholder': 'Например: 590'})

    def _check_forbidden_words(self, value, field_label):
        if not value:
            return value
        lower_value = value.lower()
        for word in FORBIDDEN_WORDS:
            if word in lower_value:
                raise ValidationError(
                    f'Поле «{field_label}» содержит запрещённое слово: «{word}».'
                )
        return value

    def clean_name(self):
        name = self.cleaned_data.get('name')
        return self._check_forbidden_words(name, 'Наименование')

    def clean_description(self):
        description = self.cleaned_data.get('description')
        return self._check_forbidden_words(description, 'Описание')

    def clean_price(self):
        price = self.cleaned_data.get('price')
        if price is not None and price < 0:
            raise ValidationError('Цена товара не может быть отрицательной.')
        return price

    def clean_image(self):
        image = self.cleaned_data.get('image')
        if image and hasattr(image, 'content_type'):
            if image.content_type not in ('image/jpeg', 'image/png'):
                raise ValidationError('Допустимы только изображения в формате JPEG или PNG.')
            if image.size > 5 * 1024 * 1024:
                raise ValidationError('Размер изображения не должен превышать 5 МБ.')
        return image
