from allauth.account.forms import SignupForm
from django import forms
from django.contrib.auth import get_user_model
from .models import Profile

class SignupForm(SignupForm):
    full_name = forms.CharField(label='ФИО', max_length=150, required=False)

    def save(self, request):
        user = super().save(request)
        fio = self.cleaned_data.get('full_name', '')
        if hasattr(user, 'profile'):
            user.profile.full_name = fio
            user.profile.save()
        return user


User = get_user_model()

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ["full_name", "phone", "address"]
        widgets = {
            "full_name": forms.TextInput(attrs={"class":"pf-field","name":"fio","placeholder":"ИВАН ИВАНОВИЧ ИВАНОВ"}),
            "phone":     forms.TextInput(attrs={"class":"pf-field","name":"phone","placeholder":"+7 XXX XXX XX XX","maxlength":"18"}),
            "address":   forms.Textarea(attrs={"class":"pf-field pf-area","name":"address","rows":"3","placeholder":"Г. МОСКВА, …"}),
        }

class UserEmailForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["email"]
        widgets = {"email": forms.EmailInput(attrs={"class":"pf-field","name":"email","placeholder":"MAIL@MAIL.RU"})}

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if User.objects.exclude(pk=self.instance.pk).filter(email__iexact=email).exists():
            raise forms.ValidationError("Этот email уже используется.")
        return email
