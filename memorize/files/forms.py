from django import forms
from .fields import ListTextWidget

class SendFileForm(forms.Form):
    file = forms.FileField()

class AddImageForm(forms.Form):
    file = forms.ImageField() 

class NewDirForm(forms.Form):
    dir_name = forms.CharField()

class ShareForm(forms.Form):
    username = forms.CharField(required=True)

    def __init__(self, *args, **kwargs):
        _user_list = kwargs.pop('data_list', None)
        super(ShareForm, self).__init__(*args, **kwargs)

    # the "name" parameter will allow you to use the same widget more than once in the same
    # form, not setting this parameter differently will cuse all inputs display the
    # same list.
        self.fields['username'].widget = ListTextWidget(data_list=_user_list, name='user-list')
