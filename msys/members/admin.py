from django.contrib import admin
from members.forms import MemberModelForm
from members.models import Member, MemberType, Membership, AccessBlock, AccessCard

admin.site.register( (Member, MemberType, Membership, AccessBlock, AccessCard) )

