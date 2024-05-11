import os
import json
import logging
from pathlib import Path

from dotenv import load_dotenv
from requests.sessions import Session

(Path(__file__).parent / "logs").mkdir(exist_ok=True)

import encrypt

load_dotenv()

logging.basicConfig(
    filename=(Path(__file__).parent / "logs" / "router-reboot.log").resolve(),
    format="%(asctime)s %(levelname)s %(message)s",
    level=logging.INFO,
)

BASE_URL = os.getenv("ROUTER_BASE_URL")
assert type(BASE_URL) is str
PASSWORD = os.getenv("ROUTER_PASSWORD")
assert type(PASSWORD) is str

logging.info("ROUTER_BASE_URL=%s", BASE_URL)
logging.info("ROUTER_PASSWORD=%s", PASSWORD[0] + "*" * (len(PASSWORD) - 1))


def login(session: Session):
    loginBody = encrypt.encryptData(
        {
            "oldPassword": PASSWORD,
            "ChangePassword": False,
        }
    )
    logging.info("Logging in with POST /php/ajaxSet_Password.php")
    response = session.post(
        BASE_URL + "/php/ajaxSet_Password.php",
        data={"configInfo": json.dumps(loginBody)},
    )
    response_json = response.json()

    if response_json["p_status"] != "Match":
        logging.error("Could not login, got %s", response.text)
        raise Exception("Could not login, got " + response.text)

    logging.info("Login successful")
    session.headers["CSRF_NONCE"] = response_json["nonce"]


def reboot(session: Session):
    logging.info("Rebooting with POST /php/user_data.php")
    response = session.post(
        BASE_URL + "/php/user_data.php",
        data={"userData": json.dumps({"reboot": "restart"}), "opType": "WRITE"},
    )
    if "success" not in response.text:
        logging.error("Reboot not successful, got %s", response.text)
        raise Exception("Could not reboot router: " + response.text)

    logging.info("Reboot scheduled")


# Probably not necessary but the web interface does it, too
def logout(session: Session):
    logging.info("Logging out")
    session.get(BASE_URL + "/php/logout.php")


with Session() as session:
    session.headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:126.0) Gecko/20100101 Firefox/126.0",
        "Accept": "application/json",
        "Referer": BASE_URL,
        "Origin": BASE_URL,
        "CSRF_NONCE": "undefined",
    }

    login(session)
    reboot(session)
    logout(session)
