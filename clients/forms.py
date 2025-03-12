from django import forms
from .models import Client

class ClientForm(forms.ModelForm):
    phone = forms.CharField(
        label='Telefone',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '(00) 00000-0000'
        }),
        help_text='Digite um número no formato: (XX) XXXXX-XXXX'
    )
    
    email = forms.EmailField(
        label='E-mail',
        required=False,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'exemplo@email.com'
        })
    )
    
    name = forms.CharField(
        label='Nome',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nome completo'
        })
    )
    
    preferred_communication = forms.ChoiceField(
        label='Meio de Comunicação Preferido',
        choices=Client.COMMUNICATION_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    
    is_blacklisted = forms.BooleanField(
        label='Marcar como lista negra',
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )
    
    class Meta:
        model = Client
        fields = [
            'name', 
            'phone', 
            'email', 
            'preferred_communication', 
            'is_blacklisted'
        ]
        
    def clean_phone(self):
        """
        Método para validar e formatar o número de telefone
        """
        phone = self.cleaned_data.get('phone')
        # Remove todos os caracteres não numéricos
        phone = ''.join(filter(str.isdigit, phone))
        
        # Verifica se o número tem entre 10 e 11 dígitos
        if len(phone) < 10 or len(phone) > 11:
            raise forms.ValidationError('Número de telefone inválido')
        
        # Formata o número
        if len(phone) == 10:
            formatted_phone = f'({phone[:2]}) {phone[2:6]}-{phone[6:]}'
        else:
            formatted_phone = f'({phone[:2]}) {phone[2:7]}-{phone[7:]}'
        
        return formatted_phone