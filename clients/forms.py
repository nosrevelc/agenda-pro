# clients/forms.py
from django import forms
import phonenumbers
from .models import Client

class ClientForm(forms.ModelForm):
    phone = forms.CharField(
        label='Telefone',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ex: +55 (11) 99999-9999'
        }),
        help_text='Digite o número com código do país. Ex: +55 (11) 99999-9999'
    )
    
    def clean_phone(self):
        """
        Valida e formata o número de telefone
        """
        phone = self.cleaned_data.get('phone')
        
        try:
            # Tenta parsear o número
            parsed_number = phonenumbers.parse(phone, None)
            
            # Verifica se o número é válido
            if not phonenumbers.is_valid_number(parsed_number):
                raise forms.ValidationError('Número de telefone inválido')
            
            # Formata o número no formato internacional
            formatted_number = phonenumbers.format_number(
                parsed_number, 
                phonenumbers.PhoneNumberFormat.INTERNATIONAL
            )
            
            return formatted_number
        
        except phonenumbers.phonenumberutil.NumberParseException:
            raise forms.ValidationError('Formato de número de telefone inválido')
    
    class Meta:
        model = Client
        fields = [
            'name', 
            'phone', 
            'email', 
            'preferred_communication', 
            'is_blacklisted'
        ]