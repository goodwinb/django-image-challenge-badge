from django import forms
from django.contrib.auth.models import User
from lefty.lefty_app.models import Badge
import re
import tagging


class ChallengeForm(forms.Form):
    choices = Badge.objects.all()
    badge = forms.ModelChoiceField(
                         queryset=choices, widget=forms.RadioSelect, empty_label=None
                    )
    name = forms.CharField(max_length=60)


class FeedbackForm(forms.Form):
    message = forms.CharField(widget=forms.Textarea())
    email = forms.EmailField(required=False)

    
class FindChallengesForm(forms.Form):
    name = forms.CharField(max_length=50, required=False)


class ImageForm(forms.Form):
    image = forms.ImageField()
    title = forms.CharField(max_length=60)
    tags = forms.CharField(max_length=1000, required=False)


class RegistrationForm(forms.Form):
    username = forms.CharField(max_length=30)
    email = forms.EmailField()
    password1 = forms.CharField(
      max_length=30,
      widget=forms.PasswordInput(render_value=False)
    )
    password2 = forms.CharField(
      max_length=30,
      widget=forms.PasswordInput(render_value=False)
    )

    def clean_username(self):
        try:
            User.objects.get(username=self.cleaned_data['username'])
        except User.DoesNotExist:
            return self.cleaned_data['username']
        raise forms.ValidationError('This username is already in use '
                                    'please choose another.')

    def clean_password2(self):
      if 'password1' in self.cleaned_data:
        password1 = self.cleaned_data['password1']
        password2 = self.cleaned_data['password2']
        if password1 == password2:
          return password2
      raise forms.ValidationError('Passwords do not match.')


class SearchForm(forms.Form):
    title = forms.CharField(max_length=50, required=False)
    tag = forms.CharField(max_length=50, required=False)   
