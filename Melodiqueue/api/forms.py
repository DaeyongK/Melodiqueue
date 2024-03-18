from django import forms
from django.core.exceptions import ValidationError

class UploadFileForm(forms.Form):
    def validate_file_size(value):
        if value.size > 10485760 * 5:
            raise ValidationError()
    file = forms.FileField(validators=[validate_file_size], widget=forms.FileInput(attrs={'accept': '.pdf'}))