from django import forms
from members.models import AccessGroup
#from member.models import Member

#class MemberModelForm(forms.Form):
#    fname = forms.CharField(label='First name', max_length=100)
#    lname = forms.CharField(label='Last name', max_length=100)


class AddGroupToCardForm(forms.Form):
	#This is some voodo for being able to build dynamic choices
	#See: http://stackoverflow.com/questions/3419997/creating-a-dynamic-choice-field
	def __init__(self, *args, **kwargs):
		super(AddGroupToCardForm, self).__init__(*args, **kwargs)
		self.fields['groups'] = forms.MultipleChoiceField(
			choices=[(o.id, str(o)) for o in AccessGroup.objects.all()]
			)

