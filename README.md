# Router reboot

Use this if it helps. Also see <https://github.com/diveflo/arris-tg3442>.

Works on my router:

```plain
Standard specification compliant	: DOCSIS 3.1
Hardware version	: 11
Software version	: AR01.04.055.06.07_040722_7245.SIP.10.LG.X1
```

## Installation

```bash
python3 -m venv .
pip3 install -r requirements.txt
cp .env.template .env
```

Then modify `.env`: Set the password to the password used in the admin interface, and, if necessary, modify the base url.

## Usage

```bash
python3 router-reboot.py
```

## Run automatically

If you want to run this every day, you can use cron jobs.

Using `crontab -e`, add the following line:

```plain
0 3 * * * /path/to/router-reboot/bin/python3 /path/to/router-reboot/router-reboot.py # Runs every day at 3 am
```
