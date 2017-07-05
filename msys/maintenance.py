#!/usr/bin/env python3
"""
Maintenance

This is where regularly scheduled functionality will be defined. Reports and backups are examples of maintenance.

The main() entry point and sentinel are defined at the bottom of this file.
"""

import os
import datetime
from pathlib import Path

import django
from django.conf import settings
from django.core.mail import EmailMessage

import stripe
from time import sleep


class Maintenence:
    """
    Maintenence class. This class will contain functionality for doing regular operations. It will also contain some information that is useful for logging purporses

    Why a class? -- Encapsulation :)
    """

    def __init__(self):
        self.mlog_data = ""

    def mlog(self, *args, **kwargs):
        """
        Maintenence log; Will output text via stdout and also keep an internal copy
        """
        ts = datetime.datetime.now().strftime("[%Y-%m-%d %H:%M:%S]: ")
        line = ts + " ".join(map(str,args))
        print(line, **kwargs)
        self.mlog_data += "\n" + line

    def _do_cmd(self, cmd):
        """
        Run a command using the OS shell
        """

        self.mlog("do_cmd: [{}]".format(cmd))
        return os.system(cmd)

    def do_db_backup(self):
        """
        Performs a database backup. For now this is simply going to copy the db.sqlite3 database file and send it off to a remote store.

        Returns True if successful otherwise False
        """

        self.mlog("base directory: {}".format(settings.BASE_DIR))

        # fist see if we can find the db file
        db_URI = settings.DATABASES['default']['NAME']
        self.mlog("got db path from django settings: [{}]".format(db_URI))

        db_path = Path(db_URI)
        if not db_path.is_file():
            self.mlog("db file does not exist on file system!")
            return False

        # now we will blindly ask the OS to copy our db and compress it
        ts = datetime.datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
        self.backup_URI = settings.BASE_DIR + "/backup/db.{}.sqlite3".format(ts)
        cmd = "cp {} {}".format(db_URI, self.backup_URI)
        self._do_cmd(cmd)

        cmd = "xz {}".format(self.backup_URI)
        self._do_cmd(cmd)

        # finally send an email with the backup
        date = datetime.datetime.now().strftime("%Y-%m-%d")
        email = EmailMessage(
            subject="Database Backup for {}".format(date),
            body="Please find attached the most recent backup of the MSYS database.",
            from_email="mr_saturn@heliosmakerspace.ca",
            to=["corey@heliosmakerspace.ca"]
        )

        email.attach_file("{}.xz".format(self.backup_URI))
        email.send()

        return True

    def do_report(self):
        """
        Generate the automated member report
        """
        from members.models import Member, Membership, MemberType
        stripe.api_key = settings.STRIPE_KEY

        report = ""
        date = datetime.datetime.now().strftime("%Y-%m-%d")

        # First some general stats

        total_members = Member.objects.all()
        active_members = []
        active_non_staff = []
        no_stripe = []
        multi_active = []
        promo_ppl = [] #this is a list of membership objects
        zombies = []

        for m in total_members:
            if m.has_active_membership():
                active_members.append(m)

        staff_t = MemberType.objects.get(name="Staff")

        for m in active_members:
            if m.type != staff_t:
                active_non_staff.append(m)

        for m in active_non_staff:
            if m.stripe_customer_code.startswith("cus") == False:
                no_stripe.append(m)

        for m in no_stripe:
            m_count = 0
            for ship in m.membership_set.all():
                if ship.is_active():
                    m_count += 1
            if m_count > 1:
                multi_active.append(m)

        for m in no_stripe:
            p_count = 0
            for ship in m.membership_set.all():
                if ship.promo_sub_set.count() > 0 and ship.is_active():
                    promo_ppl.append(ship)
                    p_count += 1
            if p_count == 0:
                zombies.append(m)

        report += "\n\n"

        # end general stats

        report += "Automated Membership report for {}\n\n".format(date)
        report += "Total Members in database: {}\n".format(len(total_members))
        report += "\"Active\" members: {}\n".format(len(active_members))
        report += "Active not including staff: {}\n".format(len(active_non_staff))
        report += "Active non-staff without Stripe IDs: {}\n".format(len(no_stripe))
        report += "Non-staff w/o Stripe with n > 1 active memberships: {}\n".format(len(multi_active))
        report += "Non-staff w/o Stripe with active promotion memberships: {}\n".format(len(promo_ppl))
        report += "Those memberships being:\n"
        for p in promo_ppl:
            report += "\t{} \t ( ".format(p)
            for s in p.promo_sub_set.all():
                report += "{} ".format(s.promo.name)
            report += " )\n"
        report += "\nActive Non-staff w/o Stripe, no promotion (paid cash? zombies? action required?): {}\n".format(
            len(zombies))
        report += "Those members are:\n"
        for z in zombies:
            report += "\t{}\n".format(z)

        # Stripe related stats

        m_list = Member.objects.exclude(stripe_customer_code__exact='').exclude(stripe_customer_code__exact=None)
        report += "Members with Stripe IDs: {}\n".format(len(m_list))

        bad_lst = []
        bad_active = []
        err_lst = []
        idx = 1

        for mem in m_list:
            sleep(0.1)
            print("stripe q: {}/{}".format(idx, len(m_list)))
            idx += 1
            try:
                cus = stripe.Customer.retrieve(mem.stripe_customer_code)
                cus_d = cus.to_dict()
                if cus_d['delinquent']:
                    bad_lst.append(mem)
                    if mem.has_active_membership():
                        bad_active.append(mem)

            except stripe.error.InvalidRequestError as e:
                print("error on member {}: {}".format(mem, e))
                err_lst.append({'member': mem, 'error': e})
                pass

        if len(bad_active) > 0:
            report += "\n\nThere are {} active delinquent members (failed payment on Stripe):\n".format(len(bad_active))
            for m in bad_active:
                report += "\t{} (#:{})\n".format(m, m.number)
        else:
            report += "\n\nThere are {} delinquent members ({} of which are active)\n".format(len(bad_lst), len(bad_active))

        if len(err_lst) > 0:
            report += "\n\nThere are {} members that have invalid data (check Stripe ID):\n".format(len(err_lst))
            for m in err_lst:
                report += "\t{} (#:{}) {}\n".format(m['member'], m['member'].number, m['error'])
        else:
            report += "\n\nThere are no invalid Stripe IDs.\n"


        report += "\n\nThe following subscriptions have 'unpaid' status. This usually means that Stripe was unable to charge the card associated with the subscriptions.\n"
        unpaid = stripe.Subscription.list(status="unpaid").to_dict()
        up_data = unpaid.get("data")
        for z in up_data:
            report += "\t{}: [{}]\n".format(z.get("id"), z.get("plan").get("name"))

        self.mlog("Generated report. Length = {}".format(len(report)))

        # Send the email

        ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        report_subject = "Automated Membership Report for {} [TEST]".format(ts)
        self.mlog("sending email [{}]...".format(report_subject))
        report_email = EmailMessage(
            subject=report_subject,
            body=report,
            from_email='mr_saturn@heliosmakerspace.ca',
            to=['corey@heliosmakerspace.ca'],
        )

        report_email.send()
        self.mlog("sent!")


### end Maintenence class

def main():
    """
    Main entry point to script. Will carry out all maintenance.
    """
    print("Starting maintenance....")

    m = Maintenence()
    m.do_db_backup()
    m.do_report()

    print("Maintenence complete!")

if __name__ == '__main__':
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "msys.settings")
    os.environ['DJANGO_SETTINGS_MODULE'] = 'msys.settings'

    print("Setting up django...")
    django.setup()
    main()
