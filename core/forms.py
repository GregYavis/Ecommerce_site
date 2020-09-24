from django import forms
from django_countries.fields import CountryField
from  django_countries.widgets import CountrySelectWidget

class CheckoutForm(forms.Form):
    PAYMENT_CHOICES = (
        ('S', 'Stripe'),
        ('P', 'PayPal')
    )
    street_address = forms.CharField(widget=forms.TextInput(attrs={
        'placeholder': '1234 Main st'}))
    apartment_address = forms.CharField(required=False,
                                        widget=forms.TextInput(attrs={
                                            'placeholder': 'Apartment'}))
    country = CountryField(blank_label='(select country)').formfield(
        widget = CountrySelectWidget(attrs={'class':'custom-select d-block '
                                                    'w-100'}))
    zip_code = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control'}))
    same_billing_address = forms.BooleanField(required=False,widget=forms.CheckboxInput(
        attrs={'class':'custom-control-input'}))
    save_info = forms.BooleanField(required=False,
                                   widget=forms.CheckboxInput(
        attrs={'class':'custom-control-input'}))
    payment_option = forms.ChoiceField(widget=forms.RadioSelect,
                                       choices=PAYMENT_CHOICES)
