# -*- coding: utf-8 -*-
#!/usr/bin/env python
import csv
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

    with open('members.csv', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            fname = row['First name']
            lname = row['Last Name']

            if len(fname) == 0 and len(lname) == 0:
                #print('skipping (', fname, lname, ')', len(fname), len(lname))
                print('Skipping empty row')
            else:
                print('[', fname, lname, ']')

                #lets try to add the person to the database
                m = Member(number = Member.objects.all().count() + 1,
                           type = mtype,
                           first_name = fname,
                           last_name = lname,
                           birth_date = row['Birthdate'],
                           first_seen_date = datetime.date.today(),
                           last_seen_date = datetime.date.today(),
                           address = row['Address'],
                           city = row['City'],
                           postal_code = row['Postal Code'],
                           phone_number = row['Contact #'],
                           email = row['Email'],
                           emergency_contact = row['Emergency Contact'],
                           emergency_phone_number = row['Emergency Phone'])
                if len(m.birth_date) == 0:
                    m.birth_date = datetime.date.today()
                try:
                    m.save()
                except django.core.exceptions.ValidationError:
                    print('error: skipping', fname, lname)
                    raise
                    
                
