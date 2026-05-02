import imaplib
import email
from email.header import decode_header
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

BASE_DIR = Path(__file__).parent
CONFIG_PATH = BASE_DIR / "config.json"
LAST_RUN_PATH = BASE_DIR / "last_run.json"


def load_config():
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def get_last_run():
    if LAST_RUN_PATH.exists():
        with open(LAST_RUN_PATH, "r") as f:
            data = json.load(f)
            return datetime.fromisoformat(data["last_run"])
    return None


def save_last_run():
    with open(LAST_RUN_PATH, "w") as f:
        json.dump({"last_run": datetime.now(timezone.utc).isoformat()}, f)


def decode_mime_header(header):
    if header is None:
        return ""
    parts = decode_header(header)
    decoded = []
    for part, charset in parts:
        if isinstance(part, bytes):
            decoded.append(part.decode(charset or "utf-8", errors="replace"))
        else:
            decoded.append(part)
    return "".join(decoded)


def get_email_body(msg):
    body = ""
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            if content_type == "text/plain":
                payload = part.get_payload(decode=True)
                if payload:
                    charset = part.get_content_charset() or "utf-8"
                    body += payload.decode(charset, errors="replace")
            elif content_type == "text/html" and not body:
                payload = part.get_payload(decode=True)
                if payload:
                    charset = part.get_content_charset() or "utf-8"
                    body += payload.decode(charset, errors="replace")
    else:
        payload = msg.get_payload(decode=True)
        if payload:
            charset = msg.get_content_charset() or "utf-8"
            body = payload.decode(charset, errors="replace")
    return body


def check_keywords(text, keywords):
    text_lower = text.lower()
    found = []
    for kw in keywords:
        if kw.lower() in text_lower:
            found.append(kw)
    return found


def check_patterns(text, patterns):
    found = []
    for pattern in patterns:
        if re.search(pattern, text, re.IGNORECASE):
            found.append(pattern)
    return found


def connect_imap(config):
    imap_cfg = config["imap"]
    mail = imaplib.IMAP4_SSL(imap_cfg["host"], imap_cfg["port"])
    mail.login(imap_cfg["email"], os.environ["EMAIL_SCRAPER_PASSWORD"])
    return mail


def fetch_emails_since(mail, since_dt):
    mail.select("INBOX")
    date_str = since_dt.strftime("%d-%b-%Y")
    _, msg_ids = mail.search(None, f'(SINCE "{date_str}")')
    if not msg_ids[0]:
        return []

    emails = []
    for num in msg_ids[0].split():
        _, data = mail.fetch(num, "(RFC822)")
        raw = data[0][1]
        msg = email.message_from_bytes(raw)

        date_header = msg.get("Date")
        if date_header:
            msg_date = email.utils.parsedate_to_datetime(date_header)
            if msg_date.tzinfo is None:
                msg_date = msg_date.replace(tzinfo=timezone.utc)
            if msg_date < since_dt:
                continue

        emails.append(msg)
    return emails


def scan_email(msg, keywords, patterns):
    subject = decode_mime_header(msg.get("Subject"))
    sender = decode_mime_header(msg.get("From"))
    body = get_email_body(msg)
    full_text = f"{subject} {body}"

    kw_hits = check_keywords(full_text, keywords)
    pattern_hits = check_patterns(full_text, patterns)

    if kw_hits or pattern_hits:
        return {
            "subject": subject,
            "from": sender,
            "date": msg.get("Date"),
            "keyword_matches": kw_hits,
            "pattern_matches": pattern_hits,
        }
    return None



def main():
    config = load_config()
    keywords = config["keywords"]
    patterns = config.get("patterns", [])

    if "EMAIL_SCRAPER_PASSWORD" not in os.environ:
        print("ERROR: Set EMAIL_SCRAPER_PASSWORD environment variable")
        print("  e.g. export EMAIL_SCRAPER_PASSWORD='your_app_password'")
        return

    last_run = get_last_run()
    if last_run is None:
        default_hours = config.get("default_hours_back", 24)
        from datetime import timedelta
        last_run = datetime.now(timezone.utc) - timedelta(hours=default_hours)
        print(f"First run — checking last {default_hours} hours")
    else:
        print(f"Last run: {last_run.isoformat()}")

    print(f"Connecting to {config['imap']['host']}...")
    mail = connect_imap(config)

    print("Fetching emails...")
    emails = fetch_emails_since(mail, last_run)
    print(f"Found {len(emails)} email(s) since last run")

    important = []
    for msg in emails:
        result = scan_email(msg, keywords, patterns)
        if result:
            important.append(result)

    if important:
        print(f"\n{'='*60}")
        print(f"  {len(important)} IMPORTANT EMAIL(S) FOUND")
        print(f"{'='*60}\n")
        for i, hit in enumerate(important, 1):
            print(f"[{i}] {hit['subject']}")
            print(f"    From: {hit['from']}")
            print(f"    Date: {hit['date']}")
            if hit["keyword_matches"]:
                print(f"    Keywords: {', '.join(hit['keyword_matches'])}")
            if hit["pattern_matches"]:
                print(f"    Patterns: {', '.join(hit['pattern_matches'])}")
            print()
    else:
        print("\nNo important emails found.")

    mail.logout()
    save_last_run()
    print("Done.")

    # Send Windows toast notification
    if "--notify" in sys.argv:
        try:
            import subprocess
            if important:
                subjects = "\\n".join(
                    hit["subject"][:60] for hit in important[:5]
                )
                extra = f"\\n...and {len(important) - 5} more" if len(important) > 5 else ""
                msg = subjects + extra
                title = f"Email Scraper: {len(important)} important email(s)"
            else:
                msg = "No important emails found."
                title = "Email Scraper"

            ps_script = (
                f'[void] [System.Reflection.Assembly]::LoadWithPartialName("System.Windows.Forms");'
                f"$n = New-Object System.Windows.Forms.NotifyIcon;"
                f'$n.Icon = [System.Drawing.SystemIcons]::Information;'
                f"$n.BalloonTipTitle = '{title}';"
                f"$n.BalloonTipText = '{msg}';"
                f"$n.BalloonTipIcon = 'Info';"
                f"$n.Visible = $True;"
                f"$n.ShowBalloonTip(10000);"
                f"Start-Sleep -Seconds 5;"
                f"$n.Dispose()"
            )
            subprocess.Popen(
                ["powershell", "-WindowStyle", "Hidden", "-Command", ps_script],
                creationflags=0x08000000,
            )
            print("Notification sent.")
        except Exception as e:
            print(f"Notification failed: {e}")


if __name__ == "__main__":
    main()
