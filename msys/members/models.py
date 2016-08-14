"""
Models

The classes defined here are essential to Django's ORM magic

"""

import datetime
from django.db import models
from django.forms import ModelForm


class MemberType(models.Model):
    """
    For users to define custom types of members. Perhaps Staff or Guests...
    """
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name

class MemberCard(models.Model):
    """
    Obsolete -- See AccessCard

    TODO: remove
    """
    start_date = models.DateField()
    expire_date = models.DateField()

class Member(models.Model):
    """
    A member of the org.

    Members can be associated with one or more memberships.

    In general, all the important info about each member is contained in this class.
    """
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

    stripe_customer_code = models.CharField(max_length=200, null=True, blank=True)

    def has_access_now(self):
        """
        Method for checking if the member can access the space right now.

        Returns True if the member has access, False otherwise.
        """
        day2day = {'mon': 0,
                   'tues': 1,
                   'wed': 2,
                   'thurs': 3,
                   'fri': 4,
                   'sat': 5,
                   'sun': 6
                  }
        #get a list of access blocks owned by the member
        a_list = AccessBlock.objects.filter(member=self)
        for block in a_list:
            if block.day == 'all':
                #now just check if we are between times
                t_now = datetime.datetime.now().time()
                if block.start < t_now and t_now < block.end:
                    return True

            elif block.day in day2day:
                if day2day[block.day] == datetime.date.today().weekday():
                    t_now = datetime.datetime.now().time()
                    if block.start < t_now and t_now < block.end:
                        return True
        return False

    def __str__(self):
        return self.first_name + " " + self.last_name

class Membership(models.Model):
    """
    Class representing a membership contract.

    One member may have a history of expired memberships in the database.
    """
    member = models.ForeignKey(Member)
    start_date = models.DateField()
    expire_date = models.DateField()

    stripe_subscription_code = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        ret = str(self.member) + ": " + str(self.start_date) + " to " + str(self.expire_date)

        if self.expire_date < datetime.date.today():
            ret += ' (expired)'
        else:
            delta = self.expire_date - datetime.date.today()
            ret += ' (' + str(delta.days) + ' remaining)'

        return ret

class AccessCard(models.Model):
    """
    Class representing the card (RFID or unique token) that Members may have

    Members may have one or more AccessCards.

    AccessCards can be associated with AccessGroups for providing access at groups of times.
    """
    member = models.ForeignKey(Member)
    unique_id = models.CharField(max_length=30)

    def numeric(self):
        """Returns a numeric representation of the unique id associated with the object"""
        byte_list = self.unique_id.split()
        num = 0
        for b_byte in byte_list:
            num = num << 8
            num = num + int(b_byte, base=16)

        return num

    def has_access_at_time(self, date, time):
        """
        Check if this card grants access at a given date and time

        Params:
        date -- a datetime.date object representing the date to check
        time -- a datetime.time object representing the time to check

        TODO: consider simplifying the parameters
        """
        day2day = {'mon': 0,
                   'tues': 1,
                   'wed': 2,
                   'thurs': 3,
                   'fri': 4,
                   'sat': 5,
                   'sun': 6
                  }#Todo: this code should not be replicated in more than one place!!
        #get a list of AGs linked to this card
        ag_set = self.accessgroup_set.all()
        for agroup in ag_set:
            #now get the TBs linked to the AG
            tb_set = TimeBlock.objects.filter(group=agroup)
            for tblock in tb_set:
                if date.weekday() == day2day[tblock.day] and time >= tblock.start and time <= tblock.end:
                    return True
                else:
                    continue
        return False



    def __str__(self):
        ret = self.unique_id
        ret += ' (' + str(self.member) + ')'
        return ret

class AccessGroup(models.Model):
    """
    AccessGroups are a many-to-many relationship between AccessCards and TimeBlocks
    """
    name = models.CharField(max_length=200)
    card = models.ManyToManyField(AccessCard, null=True, blank=True)

    def __str__(self):
        return str(self.name)

class TimeBlock(models.Model):
    """
    Represents a block of time during the week.

    TimeBlocks are not aware of specific calendar dates. Instead this class represents a 
    weekday and time that will come and go each week.
    """
    DAY_CHOICES = (
        ('mon', 'Monday'),
        ('tues', 'Tuesday'),
        ('wed', 'Wednesday'),
        ('thurs', 'Thursday'),
        ('fri', 'Friday'),
        ('sat', 'Saturday'),
        ('sun', 'Sunday'),
    )
    day = models.CharField(max_length=8,
                           choices=DAY_CHOICES,
                           default='sat')
    start = models.TimeField(default=datetime.time.min)
    end = models.TimeField(default=datetime.time.max)
    group = models.ForeignKey(AccessGroup)

    def __str__(self):
        return '{} from {} to {}'.format(self.day, self.start, self.end)

class AccessBlock(models.Model):
    """
    OBSOLETE -- See AccessGroup and TimeBlock

    TODO: remove
    """
    DAY_CHOICES = (
        ('mon', 'Monday'),
        ('tues', 'Tuesday'),
        ('wed', 'Wednesday'),
        ('thurs', 'Thursday'),
        ('fri', 'Friday'),
        ('sat', 'Saturday'),
        ('sun', 'Sunday'),
        ('all', 'Every Day'),
    )

    member = models.ForeignKey(Member)
    day = models.CharField(max_length=8,
                           choices=DAY_CHOICES,
                           default='sat')
    start = models.TimeField(default=datetime.time.min)
    end = models.TimeField(default=datetime.time.max)

    def __str__(self):
        ret = self.day + ' from ' + str(self.start) + ' to ' + str(self.end)
        ret += ' (' + str(self.member) + ')'
        return ret



    ############### Forms #############

class MemberForm(ModelForm):
    class Meta:
        model = Member
        fields = ['type', 'first_name', 'last_name',
                  'birth_date', 'address', 'city',
                  'postal_code', 'phone_number', 'email',
                  'emergency_contact', 'emergency_phone_number',
                  'stripe_customer_code']
        labels = {
            'birth_date': 'Birthdate (YYYY-MM-DD)'
        }

class MembershipForm(ModelForm):
    class Meta:
        model = Membership
        fields = ['member',
                  'start_date', 'expire_date',
                  'stripe_subscription_code']

class CardForm(ModelForm):
    class Meta:
        model = AccessCard
        fields = ['member',
                  'unique_id']

class BlockForm(ModelForm):
    class Meta:
        model = AccessBlock
        fields = ['member',
                  'day',
                  'start',
                  'end']
