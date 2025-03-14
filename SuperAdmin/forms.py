import requests
from django import forms
from .models import Feedback, MenuItem

# class FeedbackForm(forms.ModelForm):
#     category = forms.ChoiceField(
#         choices=[('', 'Select Category')] + MenuItem.CATEGORY_CHOICES,
#         required=False,  # This should not be required in form validation
#         widget=forms.Select(attrs={'class': 'form-control', 'id': 'category-dropdown'})
#     )
    
#     menu_item = forms.ModelChoiceField(
#         queryset=MenuItem.objects.none(),
#         widget=forms.Select(attrs={'class': 'form-control', 'id': 'menu-item-dropdown'}),
#         required=True
#     )

#     class Meta:
#         model = Feedback  # Ensure only model fields are in Meta
#         fields = ['menu_item', 'name', 'email', 'phone', 'message']  # Exclude `category`

    # def validate_word(self, word):
    #     """
    #     Check if a word exists using Datamuse API.
    #     Returns True for valid words, False otherwise.
    #     """
    #     try:
    #         response = requests.get(f"https://api.datamuse.com/words?sp={word}&max=1", timeout=5)
    #         response.raise_for_status()
    #         return bool(response.json())
    #     except requests.RequestException as e:
    #         print(f"API error: {e}")  # For debugging purposes
    #         raise forms.ValidationError("Error checking word validity. Please try again later.")

    # def clean_message(self):
    #     message = self.cleaned_data.get('message')
    #     words = message.split()

    #     # Validate each word in the message
    #     invalid_words = [word for word in words if not self.validate_word(word.strip().lower())]

    #     if invalid_words:
    #         raise forms.ValidationError(
    #             f"The following words don't seem valid: {', '.join(invalid_words)}."
    #         )
    #     return message


class MenuItemForm(forms.ModelForm):
    class Meta:
        model = MenuItem
        fields = ['name', 'description', 'category', 'price', 'is_available', 'image']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            'is_available': forms.CheckboxInput(attrs={'class': 'style= "margin-left: .25rem;"'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
        }