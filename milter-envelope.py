#!/usr/bin/env python3
import Milter
import email.utils
import time
import os
import pwd
import grp
import time

try:
    from systemd import journal

    def log_message(message):
        journal.send(message, SYSLOG_IDENTIFIER="milter-envelope")
except ImportError:
    def log_message(message):
        subprocess.run(['logger', '-t', 'milter-envelope'], input=message.encode())

class EnvelopeMilter(Milter.Base):
    def __init__(self):
        self.id = Milter.uniqueID()
        self.mail_from = None
        self.header_from = None

    def envfrom(self, f, *str):
        self.mail_from = f
        return Milter.CONTINUE

    def header(self, name, value):
        if name.lower() == "from":
            self.header_from = value
        return Milter.CONTINUE

    def eom(self):
        try:
            log_message(f"[{self.id}] Envelope-From: {self.mail_from}, Header-From: {self.header_from or 'N/A'}")

#            available = dir(self)
#            log_message(f"[{self.id}] available methods: {available}")

            if self.mail_from and self.header_from:
                hdr_addr = email.utils.parseaddr(self.header_from)[1]
                log_message(f"header parsed: {email.utils.parseaddr(self.header_from)}")
                if hdr_addr and hdr_addr.lower() != self.mail_from.lower():
                    self.chgfrom(hdr_addr)
                    log_message(f"[{self.id}] Envelope-From changed from {self.mail_from} to {hdr_addr}")

        except Exception as e:
            log_message(f"[{self.id}] ERROR writing log: {e}")
        return Milter.CONTINUE

def main():
    socketname = "/var/spool/postfix/milter-envelope.sock"
    timeout = 600

    Milter.factory = EnvelopeMilter
    Milter.set_flags(Milter.ADDHDRS)
#    Milter.runmilter("EnvelopeMilter", "unix:" + socketname, timeout)

    # Starte Milter in eigenem Thread
    import threading
    def run():
        Milter.runmilter("EnvelopeMilter", "unix:" + socketname, timeout)
    t = threading.Thread(target=run)
    t.start()

    # Warte kurz, bis der Socket erstellt wurde
    for _ in range(10):
        if os.path.exists(socketname):
            break
        time.sleep(0.1)

    # Rechte anpassen
    try:
        uid = pwd.getpwnam('postfix').pw_uid
        gid = grp.getgrnam('postfix').gr_gid
        os.chown(socketname, uid, gid)
        os.chmod(socketname, 0o660)
    except Exception as e:
        print("Fehler beim Setzen der Socket-Rechte:", e)

    t.join()

if __name__ == "__main__":
    main()
