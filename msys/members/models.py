from django.db import models
from django.forms import ModelForm


class MemberType(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name

class MemberCard(models.Model):
    start_date = models.DateField()
    expire_date = models.DateField()

class Member(models.Model):
    number = models.IntegerField()
    type = models.ForeignKey(MemberType)
    
    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)
    birth_date = models.DateField()
    first_seen_date = models.DateField()
    last_seen_date = models.DateField()
    
    address = models.CharField(max_length=200)
    city = models.CharField(max_length=200)
    postal_code = models.CharField(max_length=200)

    phone_number = models.CharField(max_length=200)
    email = models.CharField(max_length=200)
    emergency_contact = models.CharField(max_length=200)
    emergency_phone_number = models.CharField(max_length=200)


    def __str__(self):
        return self.first_name + " " + self.last_name

class Membership(models.Model):
    member = models.ForeignKey(Member)
    start_date = models.DateField()
    expire_date = models.DateField()

class MemberForm(ModelForm):
    class Meta:
        model = Member
        fields = ['type', 'first_name', 'last_name',
                  'birth_date', 'address', 'city',
                  'postal_code', 'phone_number', 'email',
                  'emergency_contact', 'emergency_phone_number']

