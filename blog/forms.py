from django import forms


class SearchForm(forms.Form):
    q = forms.CharField(
        label='Поиск по публикациям',
        max_length=100,
        required=False,
        widget=forms.TextInput(
            attrs={
                'placeholder': 'Введите запрос…',
                'class': 'search-input',
            }
        ),
    )
