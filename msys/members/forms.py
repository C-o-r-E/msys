from django import forms
#from member.models import Member

#maybe delete this file?

class MemberModelForm(forms.Form):
    fname = forms.CharField(label='First name', max_length=100)
    lname = forms.CharField(label='Last name', max_length=100)
