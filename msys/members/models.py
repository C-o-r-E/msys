"""
Models

The classes defined here are essential to Django's ORM magic

"""

import datetime
from django.db import models
from django.forms import ModelForm
from django.forms import Select, SelectMultiple, TextInput
from django.forms import DateInput, NumberInput, TimeInput
from django.forms import CheckboxSelectMultiple, Textarea
from django.forms import ClearableFileInput


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
    type = models.ForeignKey(MemberType, models.PROTECT)

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

    brief_notes = models.CharField(max_length=200, null=True, blank=True)
    
    photo = models.ImageField(upload_to="images/", blank=True)

    @property
    def full_name(self):
        return str(self)

    @property
    def memberships(self):
        return self.membership_set

    def has_active_membership(self):
        """
        Check to see if the Member has an active Membership

        Returns True if there is at least one Membership associated with the Member
        that has not yet expired.
        """
        m_ships = Membership.objects.filter(member=self.pk)

        for ship in m_ships:
            if ship.is_active():
                return True

        return False

    def __str__(self):
        return self.first_name + " " + self.last_name

class Membership(models.Model):
    """
    Class representing a membership contract.

    One member may have a history of expired memberships in the database.
    """
    member = models.ForeignKey(Member, models.PROTECT)
    start_date = models.DateField()
    expire_date = models.DateField()

    stripe_subscription_code = models.CharField(max_length=200, null=True, blank=True)

    def is_active(self):
        """
        Check if the membership has expired or not

        Returns True if the membership start date is earlier than the current date and
        the membership end date is in the future.
        """
        today = datetime.date.today()
        if self.start_date <= today and self.expire_date > today:
            return True

        return False

    def __str__(self):
        ret = str(self.member) + ": " + str(self.start_date) + " to " + str(self.expire_date)

        if self.expire_date < datetime.date.today():
            ret += ' (expired)'
        else:
            delta = self.expire_date - datetime.date.today()
            ret += ' (' + str(delta.days) + ' remaining)'

        return ret

class Promotion(models.Model):
    """
    Class representing a type or classification of promotion that was offered.
    """

    name = models.CharField(max_length=200)
    quantity = models.IntegerField()

    def __str__(self):
        return str(self.name)

class Promo_item(models.Model):
    """
    Class representing the a "coupon" or some kind of promotional item. It could be
    a one time membership, special status, or multiple use tickets.
    """

    promo = models.ForeignKey(Promotion, models.PROTECT)
    member = models.ForeignKey(Member, models.PROTECT)
    used = models.IntegerField()
    total = models.IntegerField()

    def __str__(self):
        ret = "promo: {} ({}) {}/{}".format(self.promo, self.member, self.used, self.total)
        return ret

class Promo_sub(models.Model):
    """
    Class to indicate which memberships are created from or associated with promotions
    """

    promo = models.ForeignKey(Promotion, models.PROTECT)
    membership = models.ForeignKey(Membership, models.PROTECT)

    def __str__(self):
        ret = "{} <-> {}".format(self.promo, self.membership)
        return ret

class AccessCard(models.Model):
    """
    Class representing the card (RFID or unique token) that Members may have

    Members may have one or more AccessCards.

    AccessCards can be associated with AccessGroups for providing access at groups of times.
    """
    member = models.ForeignKey(Member, models.PROTECT)
    unique_id = models.CharField(max_length=30)

    def numeric(self):
        """Returns a numeric representation of the unique id associated with the object"""
        byte_list = self.unique_id.split()
        num = 0
        for b_byte in byte_list:
            num = num << 8
            num = num + int(b_byte, base=16)

        return num

    def has_access_now(self):
        """Simplified wrapper for has_access_at_time(...)"""
        return self.has_access_at_time(datetime.datetime.now().date(),
                                       datetime.datetime.now().time())

#    def has_access_now(self, node) -> bool:

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
    group = models.ForeignKey(AccessGroup, models.PROTECT)

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

    member = models.ForeignKey(Member, models.PROTECT)
    day = models.CharField(max_length=8,
                           choices=DAY_CHOICES,
                           default='sat')
    start = models.TimeField(default=datetime.time.min)
    end = models.TimeField(default=datetime.time.max)

    def __str__(self):
        ret = self.day + ' from ' + str(self.start) + ' to ' + str(self.end)
        ret += ' (' + str(self.member) + ')'
        return ret

############### Logs #############

class LogEvent(models.Model):
    """
    Record of a change made to the system
    """

    date = models.DateField()
    time = models.TimeField()
    text = models.TextField()

    @staticmethod
    def log_now(txt):

        log = LogEvent()
        log.date = datetime.date.today()
        log.time = datetime.datetime.now().time()

        log.text = txt
        log.save()

    def __str__(self):
        ret = "{} {} || {}".format(self.date, self.time, self.text)
        return ret


class LogAccessRequest(models.Model):
    """
    Record of access requests made to the system
    """
    date = models.DateField()
    time = models.TimeField()
    text = models.TextField()

    @staticmethod
    def log_now(txt):

        log = LogAccessRequest()
        log.date = datetime.date.today()
        log.time = datetime.datetime.now().time()

        log.text = txt
        log.save()

    def __str__(self):
        ret = "{} {} || {}".format(self.date, self.time, self.text)
        return ret

class LogCheckIn(models.Model):
    """
    Record of check-ins performed by the members
    """
    date = models.DateField()
    time = models.TimeField()
    text = models.TextField()

    @staticmethod
    def log_now(txt):
        log = LogCheckIn()
        log.date = datetime.date.today()
        log.time = datetime.datetime.now().time()

        log.text = txt
        log.save()
    
    def __str__(self):
        ret = "{} {} || {}".format(self.date, self.time, self.text)
        return ret


############### Reports #############

class IncidentReport(models.Model):
    """
    Report of an incident that occured.
    """

    post_date = models.DateField()
    post_time = models.TimeField()

    report_date = models.DateField()
    report_time = models.TimeField()

    effected_members = models.ManyToManyField(Member, related_name="incident_effected")
    staff_on_duty = models.ManyToManyField(Member, related_name="incident_witness")

    description = models.TextField()
    damage = models.TextField()
    root_cause = models.TextField()
    mitigation = models.TextField()
    actions_taken = models.TextField()
    actions_todo = models.TextField()

    def __str__(self):
        simple_time = str(self.post_time).split('.')[0]
        ret = "Incident Report: {} {}".format(self.post_date, simple_time)
        return ret

class IncidentReportForm(ModelForm):
    class Meta:
        model = IncidentReport
        fields = ['report_date', 'report_time', 'effected_members', 'staff_on_duty',
                  'description', 'damage', 'root_cause', 'mitigation', 'actions_taken', 'actions_todo']

        labels = {
            'report_date': 'Date when the incident happened:',
            'report_time': 'Time when incident occured (HH:MM:SS):',
            'effected_members': 'Select the members who were involved in the incident (select multiple):',
            'staff_on_duty': 'Select the staff members on duty at the time (select multiple):',
            'description': 'Briefly describe the incident:',
            'damage': 'List any/all resulting injury or damage:',
            'root_cause': 'Describe what factors lead to this incident. Why doesn\'t it normally happen?',
            'mitigation': 'What can be done to prevent this kind of incident:',
            'actions_taken': 'What actions were taken in responce to this incident:',
            'actions_todo': 'What actions still need to be done:',
        }

        widgets = {'report_date': DateInput(attrs={'class': 'form-control datepicker'}),
                   'report_time': TimeInput(attrs={'class': 'form-control timepicker'}),
                   'effected_members': SelectMultiple(attrs={'class': 'form-control selectpicker',
                                                             'data-style': 'btn-primary'}),
                   'staff_on_duty': SelectMultiple(attrs={'class': 'form-control selectpicker',
                                                          'data-style': 'btn-primary'}),
                   'description': Textarea(attrs={'class': 'form-control'}),
                   'damage': Textarea(attrs={'class': 'form-control'}),
                   'root_cause': Textarea(attrs={'class': 'form-control'}),
                   'mitigation': Textarea(attrs={'class': 'form-control'}),
                   'actions_taken': Textarea(attrs={'class': 'form-control'}),
                   'actions_todo': Textarea(attrs={'class': 'form-control'}),
        }

# class EndPoint(models.Model):
#     name = models.CharField(max_length=200)
#     key = models.UUIDField(default=uuid.uuid4)

############### Forms #############

class MemberForm(ModelForm):
    class Meta:
        model = Member
        fields = ['type', 'first_name', 'last_name',
                  'birth_date', 'address', 'city',
                  'postal_code', 'phone_number', 'email',
                  'emergency_contact', 'emergency_phone_number',
                  'stripe_customer_code','brief_notes',
                  'photo']
        labels = {
            'birth_date': 'Birthdate (MM/DD/YYYY)',
            'stripe_customer_code': 'Stripe customer code (Leave blank if none)',
            'brief_notes': 'Notes (keep it brief - 200 characters max)'
        }

        widgets = {'type': Select(attrs={'class': 'form-control'}),
                   'first_name': TextInput(attrs={'class': 'form-control'}),
                   'last_name': TextInput(attrs={'class': 'form-control'}),
                   'birth_date': DateInput(attrs={'class': 'form-control datepicker'}),
                   'address': TextInput(attrs={'class': 'form-control'}),
                   'city': TextInput(attrs={'class': 'form-control'}),
                   'postal_code': TextInput(attrs={'class': 'form-control'}),
                   'phone_number': TextInput(attrs={'class': 'form-control'}),
                   'email': TextInput(attrs={'class': 'form-control'}),
                   'emergency_contact': TextInput(attrs={'class': 'form-control'}),
                   'emergency_phone_number': TextInput(attrs={'class': 'form-control'}),
                   'stripe_customer_code': TextInput(attrs={'class': 'form-control'}),
                   'brief_notes': TextInput(attrs={'class': 'form-control'}),
                   'photo': ClearableFileInput(attrs={'class': 'form-control'}),
        }

class MembershipForm(ModelForm):
    class Meta:
        model = Membership
        fields = ['member',
                  'start_date', 'expire_date',
                  'stripe_subscription_code']
        widgets = {'member': Select(attrs={'class': 'form-control'}),
                   'start_date': DateInput(attrs={'class': 'form-control datepicker'}),
                   'expire_date': DateInput(attrs={'class': 'form-control datepicker'}),
                   'stripe_subscription_code': TextInput(attrs={'class': 'form-control'}),
                  }
        labels = {'start_date': 'Start Date (MM/DD/YYYY):',
                  'expire_date': 'Expire Date (MM/DD/YYYY):',
                }

class PromoForm(ModelForm):
    class Meta:
        model = Promotion
        fields = ['name', 'quantity']
        widgets = {'name': TextInput(attrs={'class': 'form-control'}),
                   'quantity': NumberInput(attrs={'class': 'form-control'}), }

class PromoItemForm(ModelForm):
    class Meta:
        model = Promo_item
        fields = ['promo', 'member', 'used', 'total']
        widgets = {'promo': Select(attrs={'class': 'form-control'}),
                   'member': Select(attrs={'class': 'form-control'}),
                   'used': NumberInput(attrs={'class': 'form-control'}),
                   'total': NumberInput(attrs={'class': 'form-control'})}

class CardForm(ModelForm):
    class Meta:
        model = AccessCard
        fields = ['member',
                  'unique_id']
        widgets = {'member': Select(attrs={'class': 'form-control'}),
                   'unique_id': TextInput(attrs={'class': 'form-control'}),}

class BlockForm(ModelForm):
    class Meta:
        model = AccessBlock
        fields = ['member',
                  'day',
                  'start',
                  'end']
