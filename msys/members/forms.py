from django import forms
#from member.models import Member

#class MemberModelForm(forms.Form):
#    fname = forms.CharField(label='First name', max_length=100)
#    lname = forms.CharField(label='Last name', max_length=100)


class AddGroupToCardForm(forms.Form):
	groups = forms.MultipleChoiceField()
