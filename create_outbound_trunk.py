import base64
import json
import os
import secrets
import string
import urllib.error
import urllib.parse
import urllib.request
import re
import subprocess
from dotenv import load_dotenv

load_dotenv()

TWILIO_API_BASE = "https://api.twilio.com/2010-04-01"
TWILIO_TRUNKING_BASE = "https://trunking.twilio.com/v1"


def require_env(name: str, default: str | None = None) -> str:
    value = os.getenv(name, default)
    if not value:
        raise SystemExit(f"Missing required environment variable: {name}")
    return value


def generate_sip_username() -> str:
    return f"lk-{secrets.token_hex(4)}"


def generate_sip_password(length: int = 16) -> str:
    if length < 12:
        length = 12

    chars = [
        secrets.choice(string.ascii_lowercase),
        secrets.choice(string.ascii_uppercase),
        secrets.choice(string.digits),
    ]
    pool = string.ascii_letters + string.digits
    chars.extend(secrets.choice(pool) for _ in range(length - len(chars)))
    secrets.SystemRandom().shuffle(chars)
    return "".join(chars)


def post_form(url: str, account_sid: str, auth_token: str, data: dict) -> dict:
    body = urllib.parse.urlencode(data).encode("utf-8")
    auth = base64.b64encode(f"{account_sid}:{auth_token}".encode("utf-8")).decode("ascii")

    req = urllib.request.Request(url, data=body, method="POST")
    req.add_header("Authorization", f"Basic {auth}")
    req.add_header("Content-Type", "application/x-www-form-urlencoded")
    req.add_header("Accept", "application/json")

    try:
        with urllib.request.urlopen(req) as resp:
            raw = resp.read().decode("utf-8")
            return json.loads(raw) if raw else {}
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8", errors="replace")
        raise SystemExit(f"HTTP {e.code} calling {url}\n{error_body}") from e


def get_json(url: str, account_sid: str, auth_token: str) -> dict:
    auth = base64.b64encode(f"{account_sid}:{auth_token}".encode("utf-8")).decode("ascii")

    req = urllib.request.Request(url, method="GET")
    req.add_header("Authorization", f"Basic {auth}")
    req.add_header("Accept", "application/json")

    try:
        with urllib.request.urlopen(req) as resp:
            raw = resp.read().decode("utf-8")
            return json.loads(raw) if raw else {}
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8", errors="replace")
        raise SystemExit(f"HTTP {e.code} calling {url}\n{error_body}") from e


def delete_url(url: str, account_sid: str, auth_token: str) -> dict:
    auth = base64.b64encode(f"{account_sid}:{auth_token}".encode("utf-8")).decode("ascii")

    req = urllib.request.Request(url, method="DELETE")
    req.add_header("Authorization", f"Basic {auth}")
    req.add_header("Accept", "application/json")

    try:
        with urllib.request.urlopen(req) as resp:
            raw = resp.read().decode("utf-8")
            return json.loads(raw) if raw else {}
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8", errors="replace")
        raise SystemExit(f"HTTP {e.code} calling {url}\n{error_body}") from e


def delete_existing_sip_trunk(account_sid: str, auth_token: str) -> None:
    trunks_url = f"{TWILIO_TRUNKING_BASE}/Trunks"
    data = get_json(trunks_url, account_sid, auth_token)

    trunks = data.get("trunks", [])
    if not trunks:
        print("No existing trunk found to delete.")
        return

    for trunk in trunks:
        trunk_sid = trunk.get("sid")
        trunk_friendly_name = trunk.get("friendly_name") or trunk.get("friendlyName")

        if trunk_sid:
            delete_url(f"{TWILIO_TRUNKING_BASE}/Trunks/{trunk_sid}", account_sid, auth_token)
            print(f"Deleted existing trunk: {trunk_sid} ({trunk_friendly_name})")


def delete_existing_sip_credential_list(account_sid: str, auth_token: str, friendly_name: str) -> None:
    url = f"{TWILIO_API_BASE}/Accounts/{account_sid}/SIP/CredentialLists.json"
    data = get_json(url, account_sid, auth_token)

    credential_lists = data.get("credential_lists", [])
    for cl in credential_lists:
        cl_name = cl.get("friendly_name") or cl.get("friendlyName")
        cl_sid = cl.get("sid")

        if cl_sid and cl_name == friendly_name:
            delete_url(
                f"{TWILIO_API_BASE}/Accounts/{account_sid}/SIP/CredentialLists/{cl_sid}.json",
                account_sid,
                auth_token,
            )
            print(f"Deleted existing credential list: {cl_sid} ({cl_name})")
            return

    print("No existing credential list found to delete.")


def create_twilio_trunk(account_sid: str, auth_token: str, domain_name: str, friendly_name: str) -> dict:
    url = f"{TWILIO_TRUNKING_BASE}/Trunks"
    payload = {
        "friendlyName": friendly_name,
        "domainName": domain_name,
    }
    return post_form(url, account_sid, auth_token, payload)


def create_sip_credential_list(account_sid: str, auth_token: str, friendly_name: str) -> dict:
    url = f"{TWILIO_API_BASE}/Accounts/{account_sid}/SIP/CredentialLists.json"
    payload = {"FriendlyName": friendly_name}
    return post_form(url, account_sid, auth_token, payload)


def create_sip_credential(account_sid: str, auth_token: str, credential_list_sid: str, username: str, password: str) -> dict:
    url = f"{TWILIO_API_BASE}/Accounts/{account_sid}/SIP/CredentialLists/{credential_list_sid}/Credentials.json"
    payload = {
        "Username": username,
        "Password": password,
    }
    return post_form(url, account_sid, auth_token, payload)


def attach_credential_list_to_trunk(account_sid: str, auth_token: str, trunk_sid: str, credential_list_sid: str) -> dict:
    url = f"{TWILIO_TRUNKING_BASE}/Trunks/{trunk_sid}/CredentialLists"
    payload = {"CredentialListSid": credential_list_sid}
    return post_form(url, account_sid, auth_token, payload)


def create_livekit_outbound_trunk(livekit_url, livekit_api_key, livekit_api_secret,
                                  trunk_domain, phone_number, sip_username, sip_password):
    trunk_data = {
        "trunk": {
            "name": "LiveKit Outbound Trunk",
            "address": trunk_domain,
            "numbers": [phone_number],
            "authUsername": sip_username,
            "authPassword": sip_password
        }
    }

    with open("outbound_trunk.json", "w") as f:
        json.dump(trunk_data, f, indent=4)

    result = subprocess.run(
        [
            "lk", "sip", "outbound", "create", "outbound_trunk.json",
            "--url", livekit_url.replace("wss", "https"),
            "--api-key", livekit_api_key,
            "--api-secret", livekit_api_secret,
        ],
        capture_output=True,
        text=True,
        cwd=os.getcwd(),
    )

    if result.returncode != 0:
        print(f"Error executing command: {result.stderr}")
        print(f"Command output: {result.stdout}")
        return None

    print(result.stdout)
    match = re.search(r'ST_\w+', result.stdout)
    if match:
        outbound_trunk_sid = match.group(0)
        print(f"Created outbound trunk with SID: {outbound_trunk_sid}")
        return outbound_trunk_sid
    else:
        print("Could not find outbound trunk SID in output.")
        return None

def main() -> None:
    account_sid = require_env("TWILIO_ACCOUNT_SID")
    auth_token = require_env("TWILIO_AUTH_TOKEN")

    trunk_name = os.getenv("TWILIO_TRUNK_FRIENDLY_NAME", "LiveKit Outbound Trunk")

    # delete any existing trunk
    delete_existing_sip_trunk(account_sid, auth_token)

    trunk_domain = os.getenv("TWILIO_TRUNK_DOMAIN_NAME")
    if not trunk_domain:
        trunk_domain = f"livekit-{secrets.token_hex(4)}.pstn.twilio.com"

    if not trunk_domain.endswith("pstn.twilio.com"):
        raise SystemExit("TWILIO_TRUNK_DOMAIN_NAME must end with pstn.twilio.com")

    credential_list_name = os.getenv("TWILIO_CREDENTIAL_LIST_FRIENDLY_NAME", "LiveKit Outbound Credentials")

    sip_username = os.getenv("TWILIO_SIP_USERNAME") or generate_sip_username()
    sip_password = os.getenv("TWILIO_SIP_PASSWORD") or generate_sip_password()

    trunk = create_twilio_trunk(account_sid, auth_token, trunk_domain, trunk_name)
    trunk_sid = trunk.get("sid")
    if not trunk_sid:
        raise SystemExit(f"Could not read trunk SID from response: {trunk}")

    delete_existing_sip_credential_list(account_sid, auth_token, credential_list_name)
    credential_list = create_sip_credential_list(account_sid, auth_token, credential_list_name)
    credential_list_sid = credential_list.get("sid")
    if not credential_list_sid:
        raise SystemExit(f"Could not read credential list SID from response: {credential_list}")

    credential = create_sip_credential(
        account_sid,
        auth_token,
        credential_list_sid,
        sip_username,
        sip_password,
    )
    credential_sid = credential.get("sid")
    if not credential_sid:
        raise SystemExit(f"Could not read credential SID from response: {credential}")

    association = attach_credential_list_to_trunk(
        account_sid,
        auth_token,
        trunk_sid,
        credential_list_sid,
    )

    livekit_url = os.getenv("LIVEKIT_URL")
    livekit_api_key = os.getenv("LIVEKIT_API_KEY")
    livekit_api_secret = os.getenv("LIVEKIT_API_SECRET")
    phone_number = os.getenv("TWILIO_PHONE_NUMBER")

    livekit_outbound_trunk_sid = create_livekit_outbound_trunk(
        livekit_url,
        livekit_api_key,
        livekit_api_secret,
        trunk_domain,
        phone_number,
        sip_username,
        sip_password,
    )

    print("Twilio outbound SIP trunk setup complete\n")
    print(f"Trunk SID: {trunk_sid}")
    print(f"Trunk domain: {trunk_domain}")
    print(f"Credential List SID: {credential_list_sid}")
    print(f"SIP Credential SID: {credential_sid}")
    print(f"Username: {sip_username}")
    print(f"Password: {sip_password}")
    print("\nUse these values in LiveKit later:")
    print(f'  address: "{trunk_domain}"')
    print(f'  auth_username: "{sip_username}"')
    print(f'  auth_password: "{sip_password}"')
    print(f"LiveKit outbound trunk SID: {livekit_outbound_trunk_sid}")
    print(f"\nAssociation response: {association}")


if __name__ == "__main__":
    main()