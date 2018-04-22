
from django import forms
from django.utils.translation import ugettext_lazy as _
from login.models import *
from django.contrib.auth.forms import AuthenticationForm
from django.forms.widgets import PasswordInput


class RegistrationForm(forms.Form):
    username = forms.RegexField(
        regex=r'^\w+$',
        widget=forms.TextInput(attrs=dict(required=True, max_length=30, placeholder="Username")),
        error_messages={'invalid': _("Username must contain only letters, numbers and underscores.")}
    )

    email = forms.EmailField(
        widget=forms.EmailInput(attrs=dict(required=True, max_length=30, placeholder="Email"))
    )

    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs=dict(required=True, max_length=30, render_value=False, placeholder="Password"))
    )

    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs=dict(required=True, max_length=30, render_value=False,
                                              placeholder="Re-Enter Password"))
    )

    fname = forms.CharField(
        widget=forms.TextInput(attrs=dict(required=True, max_length=30, placeholder="First Name"))
    )

    lname = forms.CharField(
        widget=forms.TextInput(attrs=dict(required=True, max_length=30, placeholder="Last Name"))
    )

    def clean_username(self):
        try:
            User.objects.get(username__exact=self.cleaned_data['username'])
        except User.DoesNotExist:
            return self.cleaned_data['username']
        raise forms.ValidationError(_("Username already exists. Please try another one."))

    def clean(self):
        if 'password1' in self.cleaned_data and 'password2' in self.cleaned_data:
            if self.cleaned_data['password1'] != self.cleaned_data['password2']:
                raise forms.ValidationError(_("The two password fields did not match."))


class AddSource(forms.Form):
    name = forms.CharField(
        widget=forms.TextInput(attrs=dict(required=True, max_length=300, placeholder="Name"))
    )

    rss_url = forms.URLField(
        widget=forms.URLInput(attrs=dict(required=True, max_length=300, placeholder="URL"))
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(AddSource, self).__init__(*args, **kwargs)

    def clean(self):
        try:
            Sourcing.objects.get(
                rss_url__exact=self.cleaned_data['rss_url'], created_by_id=self.user.id
            )

        except Sourcing.DoesNotExist:
            return self.cleaned_data
        raise forms.ValidationError(_("This Url already exist"))


class EditSource(forms.Form):
    name = forms.CharField(
        widget=forms.TextInput(attrs=dict(required=True, max_length=300, placeholder="Name"))
    )

    rss_url = forms.URLField(
        widget=forms.URLInput(attrs=dict(required=True, max_length=300, placeholder="URL"))
    )

    item_id = forms.CharField(required=False)

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(EditSource, self).__init__(*args, **kwargs)


class AddStory(forms.Form):
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(AddStory, self).__init__(*args, **kwargs)
        # Creates a field Source, that queries databse for
        if self.user.is_staff or self.user.is_superuser:
            self.fields['source'] = forms.ModelChoiceField(queryset=Sourcing.objects.all())
        else:
            self.fields['source'] = forms.ModelChoiceField(queryset=Sourcing.objects.filter(created_by_id=self.user.id))

    title = forms.CharField(
        widget=forms.TextInput(attrs=dict(required=True, max_length=50, placeholder='Title'))
    )

    body = forms.CharField(
        widget=forms.TextInput(attrs=dict(required=True, placeholder="Body"))
    )

    pub_date = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs=dict(placeholder="Date Format YYYY-mm-dd HH:MM:SS "),
                                   format=['%Y-%m-%d %H:%M:%S.%f'])
    )

    url = forms.URLField(
        widget=forms.URLInput(attrs=dict(required=True, placeholder='URL'))
    )

    def clean(self):
        try:
            Stories.objects.get(
                url=self.cleaned_data['url'], source_id=self.cleaned_data['source'].id
            )
        except Stories.DoesNotExist:
            return self.cleaned_data
        raise forms.ValidationError(_("Same Url under this Source already Exists"))


class CustomAuthForm(AuthenticationForm):
    username = forms.RegexField(regex=r'^\w+$',
                                widget=forms.TextInput(attrs=dict(
                                    required=True,
                                    max_length=30,
                                    placeholder="Username")),
                                )

    password = forms.CharField(
        widget=PasswordInput(attrs=dict(required=True, placeholder='Password')))



class EditStory(forms.Form):
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(EditStory, self).__init__(*args, **kwargs)

        if self.user.is_staff or self.user.is_superuser:
            self.fields['source'] = forms.ModelChoiceField(queryset=Sourcing.objects.all())
        else:
            self.fields['source'] = forms.ModelChoiceField(queryset=Sourcing.objects.filter(created_by_id=self.user.id))

    title = forms.CharField(
        widget=forms.TextInput(attrs=dict(required=True, max_length=50, placeholder='Title'))
    )

    body = forms.CharField(
        widget=forms.TextInput(attrs=dict(required=True, placeholder="Body"))
    )

    pub_date = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs=dict(placeholder="Date Format YYYY-mm-dd HH:MM:SS"),
                                   format=['%Y-%m-%d %H:%M:%S.%f'])
    )

    url = forms.URLField(
        widget=forms.URLInput(attrs=dict(required=True, placeholder='URL'))
    )

    item_id = forms.CharField(required=False)
