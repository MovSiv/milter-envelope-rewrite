# milter-envelope-rewrite
Postfix milter for rewriting envelope sender address based on header from address.
Usefull for grommunio mailserver and send-as mails. 

# Installation
## Prerequisites
```
zypper install gcc python3-devel make python3-pip sendmail-devel python3-systemd
pip install pymilter
mkdir -p /usr/local/lib/milter
```

## systemd service file
create `/etc/systemd/system/milter-envelope.service`. 

create milter skript: `/usr/local/lib/milter/milter-envelope.py`

## postfix 
add or modify these postfix settings in `/etc/postfix/main.cf`

```
smtpd_milters = unix:/var/spool/postfix/milter-envelope.sock
non_smtpd_milters = $smtpd_milters
milter_default_action = accept
```
if you have more smtpd_milters, you can seperate the list with milter1, milter2, milter3, etc.

## activate/restart daemons
```
systemctl daemon-reload
systemctl enable milter-envelope.service
systemctl start milter-envelope.service

systemctl reload postfix
```

# Logs
Logs entries of the script can be viewed in `journalctl`

# Disclaimer
use on you own risk ;)
