from django import forms

class ContactForm(forms.Form):
    name = forms.CharField(max_length=100, required=True, label='Your Name')
    email = forms.EmailField(required=True, label='Your Email')
    subject = forms.CharField(max_length=150, required=True)
    message = forms.CharField(widget=forms.Textarea, required=True)

class SignupForm(forms.Form):
    email = forms.EmailField(required=True, label='Email Address')
    password1 = forms.CharField(widget=forms.PasswordInput, label='Password', required=True)
    password2 = forms.CharField(widget=forms.PasswordInput, label='Confirm Password', required=True)

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            self.add_error('password2', "Passwords do not match.")
        return cleaned_data
