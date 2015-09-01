#!/usr/bin/env python
import os
import sys
import django
import datetime

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "msys.settings")

    print("Setting up django...")
    django.setup()

    from members.models import Member, MemberType

    print("done.")

    #Do we have any member types
    total_types = len(MemberType.objects.all())
    if total_types == 0:
        print("No types found. Creating \"Member\".")
        mtype = MemberType(name="Member")
        mtype.save()
        print("done.")

    mtype = MemberType.objects.get(name__iexact="Member")
    
    total_mem = len(Member.objects.all())
    m1 = Member(number = total_mem+1,
                type = mtype,
                first_name = "Corey",
                last_name = "Clayton",
                birth_date = "1961-10-30",
                first_seen_date = datetime.date.today(),
                last_seen_date = datetime.date.today(),
                address = "206 Comber",
                city = "Dorval",
                postal_code = "H9S 2Y4",
                phone_number = "5142611046",
                email = "can.of.tuna@gmail.com",
                emergency_contact = "Meaghan Mueller",
                emergency_phone_number = "5146181390")
    m1.save()
