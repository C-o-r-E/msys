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

    from members.models import Member, MemberType, Membership

    print("done.")

    #Do we have any member types
    total_types = len(MemberType.objects.all())
    if total_types == 0:
        print("No types found. Creating \"Member\".")
        mtype = MemberType(name="Member")
        mtype.save()
        print("done.")

    mtype = MemberType.objects.get(name__iexact="Member")

    #Delete all the Members and Memberships
    print('delete all Memberships...')
    Membership.objects.all().delete()
    print('delete all Members...')
    Member.objects.all().delete()

    with open('members.csv', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            fname = row['First Name']
            lname = row['Last Name']

            if len(fname) == 0 and len(lname) == 0:
                #print('skipping (', fname, lname, ')', len(fname), len(lname))
                print('Skipping empty row')
                continue
            
            print('[', fname, lname, ']')

            #lets try to add the person to the database
            m = Member(number = Member.objects.all().count() + 1,
                       type = mtype,
                       first_name = fname,
                       last_name = lname,
                       birth_date = row['Birthdate'],
                       first_seen_date = row['Created On'],
                       last_seen_date = datetime.date.today(),
                       address = row['Address'],
                       city = row['City'],
                       postal_code = row['Postal Code'],
                       phone_number = row['Contact #'],
                       email = row['Email'],
                       emergency_contact = row['Emergency Contact'],
                       emergency_phone_number = row['Emergency Phone'],
                       stripe_customer_code = row['Stripe cus_ code'])
            if len(m.birth_date) == 0:
                m.birth_date = datetime.date.today()
            try:
                m.save()
            except django.core.exceptions.ValidationError:
                print('error: skipping', fname, lname)
                raise

            #attempt to make a membership
            try:
                #for empty strings on expire date
                if not row['Last day of Membership']:
                    last_day = datetime.date.today()
                else:

                    last_day = datetime.datetime.strptime(row['Last day of Membership'], '%Y-%m-%d').date()
                    if last_day > datetime.date.today():
                        ms = Membership(member = m,
                                        start_date = datetime.date.today(),
                                        expire_date = last_day,
                                        stripe_subscription_code = row['Stripe Membership sub_ code'])
                        ms.save()
            except ValueError:
                print('\t could not parse date: [', row['Last day of Membership'], ']')
                pass
            #end for loop
                
