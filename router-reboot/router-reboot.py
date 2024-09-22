import os
import json
import logging
from pathlib import Path

from dotenv import load_dotenv
from requests.sessions import Session

import encrypt

load_dotenv()

LOGS_DIR = Path(__file__).parent.parent / "logs"
LOGS_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    filename=LOGS_DIR / "router-reboot.log",
    format="%(asctime)s %(levelname)s %(message)s",
    level=logging.INFO,
)


def login(session: Session, base_url: str):
    loginBody = encrypt.encryptData(
        {
            "oldPassword": password,
            "ChangePassword": False,
        }
    )
    logging.info("Logging in with POST /php/ajaxSet_Password.php")
    response = session.post(
        base_url + "/php/ajaxSet_Password.php",
        data={"configInfo": json.dumps(loginBody)},
    )
    response_json = response.json()

    if response_json["p_status"] != "Match":
        logging.error("Could not login, got %s", response.text)
        raise Exception("Could not login, got " + response.text)

    logging.info("Login successful")
    session.headers["CSRF_NONCE"] = response_json["nonce"]


def reboot(session: Session, base_url: str):
    logging.info("Rebooting with POST /php/user_data.php")
    response = session.post(
        base_url + "/php/user_data.php",
        data={"userData": json.dumps({"reboot": "restart"}), "opType": "WRITE"},
    )
    if "success" not in response.text:
        logging.error("Reboot not successful, got %s", response.text)
        raise Exception("Could not reboot router: " + response.text)

    logging.info("Reboot scheduled")


# Probably not necessary but the web interface does it, too
def logout(session: Session, base_url: str):
    logging.info("Logging out")
    session.get(base_url + "/php/logout.php")


if __name__ == "__main__":
    base_url = os.getenv("ROUTER_BASE_URL")
    assert type(base_url) is str
    password = os.getenv("ROUTER_PASSWORD")
    assert type(password) is str

    logging.info("ROUTER_BASE_URL=%s", base_url)
    logging.info("ROUTER_PASSWORD=%s", password[0] + "*" * (len(password) - 1))

    with Session() as session:
        session.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:126.0) Gecko/20100101 Firefox/126.0",
            "Accept": "application/json",
            "Referer": base_url,
            "Origin": base_url,
            "CSRF_NONCE": "undefined",
        }

        login(session, base_url)
        reboot(session, base_url)
        logout(session, base_url)
