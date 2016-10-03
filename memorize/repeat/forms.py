from .models import Flashcard, List
from django import forms

class ListForm(forms.ModelForm):
    class Meta:
        model = List
        fields = ('name',)

class FlashcardForm(forms.ModelForm):
    class Meta:
        model = Flashcard
        fields = ('question','answer')


class LimitForm(forms.ModelForm):
    
    class Meta:
        model = List
        fields = ('limit',)

        
