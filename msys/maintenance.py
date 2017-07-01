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
        backup_URI = settings.BASE_DIR + "/backup/db.{}.sqlite3".format(ts)
        cmd = "cp {} {}".format(db_URI, backup_URI)
        self._do_cmd(cmd)

        cmd = "xz {}".format(backup_URI)
        self._do_cmd(cmd)

        # finally send an email with the backup
        date = datetime.datetime.now().strftime("%Y-%m-%d")
        email = EmailMessage(
            subject="Database Backup for {}".format(date),
            body="Please find attached the most recent backup of the MSYS database.",
            from_email="mr_saturn@heliosmakerspace.ca",
            to=["corey@heliosmakerspace.ca"]
        )

        email.attach_file("{}.xz".format(backup_URI))
        email.send()

        return True

### end Maintenence class

def main():
    """
    Main entry point to script. Will carry out all maintenance.
    """
    print("Starting maintenance....")

    m = Maintenence()
    m.do_db_backup()

    print("Maintenence complete!")

if __name__ == '__main__':
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "msys.settings")
    os.environ['DJANGO_SETTINGS_MODULE'] = 'msys.settings'

    print("Setting up django...")
    django.setup()
    main()
