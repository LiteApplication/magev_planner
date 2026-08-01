from email.policy import SMTP
import json
import logging
import os
import socket
import ssl
import time
import threading
from queue import Queue
from datetime import datetime
import locale
from dotenv import load_dotenv
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.utils import parseaddr
from sqlmodel import select
from shared_planner.db.models import (
    Setting,
    Reservation,
    Notification,
    User,
    Enterprise,
)
from shared_planner.db.settings import get
from shared_planner.db.session import SessionLock
from shared_planner.week import monday_str
from shared_planner.ics import create_ics
from shared_planner import tz
from shared_planner.logs import setup_logging
from shared_planner.mail_render import (
    get_template_markdown,
    get_template_subject,
    markdown_to_html,
    wrap_in_shell,
)

# Load environment variables from .env file
load_dotenv()

SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_USE_TLS = os.getenv("SMTP_USE_TLS", "false").lower() in ("true", "1", "y", "yes")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
SMTP_TIMEOUT = float(os.getenv("SMTP_TIMEOUT", 15))
TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), "..", "templates")

logger = logging.getLogger(__name__)

SUBJECTS = {
    "password_reset": "[MAGEV] Réinitialisation de mot de passe",
    "notification.reservation_created": "[MAGEV] Confirmation de votre réservation à notre opération paquets cadeaux",
    "notification.reminder": "[MAGEV] Rappel de réservation",
    "notification.reservation_modified": "[MAGEV] Modification de votre réservation",
    "notification.reservation_cancelled": "[MAGEV] Annulation de votre réservation",
    "notification.reservation_reassigned_old": "[MAGEV] Réservation supprimée",
    "notification.reservation_reassigned_new": "[MAGEV] Nouvelle réservation",
    "first_mail": "[MAGEV] Bienvenue sur notre plateforme de réservation",
    "notification.admin.reservation_created": "[ADMIN] Nouvelle réservation",
    "notification.admin.reservation_modified": "[ADMIN] Modification de réservation",
    "notification.admin.reservation_cancelled": "[ADMIN] Annulation de réservation",
    "notification.admin.new_user": "[ADMIN] Nouvel utilisateur",
}

mail_queue = Queue()
# Set locale to French
locale.setlocale(locale.LC_TIME, "fr_FR.UTF-8")


def mask_email(email: str) -> str:
    """Keep only the first letter of the local part, plus the full domain."""
    local, sep, domain = (email or "").partition("@")
    if not sep:
        return f"{local[:1]}***" if local else "***"
    return f"{local[:1]}***@{domain}"


class SMTPConfigurationError(RuntimeError):
    """The SMTP server could not be reached, negotiated with, or logged into."""


def smtp_connect() -> smtplib.SMTP:
    """Open an SMTP connection, authenticating if credentials are configured.

    Every failure is translated into a SMTPConfigurationError saying which step
    failed, so a startup failure is readable without a traceback.
    """
    if not SMTP_SERVER:
        raise SMTPConfigurationError("missing env var: SMTP_SERVER")
    # An empty user *and* password means an open relay such as the dev MailHog
    # container, where AUTH must be skipped entirely.
    if bool(SMTP_USER) != bool(SMTP_PASSWORD):
        raise SMTPConfigurationError(
            "SMTP_USER and SMTP_PASSWORD must be both set or both empty"
        )

    target = f"{SMTP_SERVER}:{SMTP_PORT}"
    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=SMTP_TIMEOUT)
    except socket.gaierror as e:
        raise SMTPConfigurationError(f"cannot resolve host {SMTP_SERVER!r}: {e}") from e
    except (socket.timeout, TimeoutError) as e:
        raise SMTPConfigurationError(
            f"connect to {target} timed out after {SMTP_TIMEOUT:g}s"
        ) from e
    except ConnectionRefusedError as e:
        raise SMTPConfigurationError(f"connection refused by {target}") from e
    except OSError as e:
        raise SMTPConfigurationError(f"cannot connect to {target}: {e}") from e
    except smtplib.SMTPException as e:
        raise SMTPConfigurationError(f"bad SMTP greeting from {target}: {e}") from e

    try:
        if SMTP_USE_TLS:
            try:
                server.starttls()
            except smtplib.SMTPNotSupportedError as e:
                raise SMTPConfigurationError(
                    f"{target} does not support STARTTLS, but SMTP_USE_TLS is set"
                ) from e
            except ssl.SSLError as e:
                raise SMTPConfigurationError(
                    f"TLS handshake with {target} failed: {e}"
                ) from e

        if not SMTP_USER:
            return server

        try:
            server.login(SMTP_USER, SMTP_PASSWORD)
        except smtplib.SMTPAuthenticationError as e:
            raise SMTPConfigurationError(
                f"{target} rejected credentials for {SMTP_USER!r}: "
                f"{e.smtp_code} {e.smtp_error.decode(errors='replace')}"
            ) from e
        except smtplib.SMTPNotSupportedError as e:
            raise SMTPConfigurationError(f"{target} does not support AUTH: {e}") from e
        except smtplib.SMTPException as e:
            raise SMTPConfigurationError(
                f"login to {target} as {SMTP_USER!r} failed: {e}"
            ) from e
        except OSError as e:
            raise SMTPConfigurationError(
                f"connection to {target} dropped during login: {e}"
            ) from e
    except BaseException:
        server.close()
        raise

    return server


def check_smtp_connection() -> None:
    """Connect and authenticate once, to fail fast on a bad SMTP config."""
    logger.info(
        "Checking SMTP %s:%s (TLS %s, user %s)",
        SMTP_SERVER,
        SMTP_PORT,
        "on" if SMTP_USE_TLS else "off",
        SMTP_USER or "<anonymous>",
    )
    try:
        server = smtp_connect()
    except SMTPConfigurationError as e:
        logger.error("SMTP check failed: %s", e)
        raise
    try:
        server.quit()
    except smtplib.SMTPException:
        server.close()
    logger.info("SMTP check OK")


def d(value, format_type="date"):
    # Stored datetimes are UTC; render them in the configured server timezone.
    dt = tz.utc_to_local(datetime.strptime(value, "%Y-%m-%d %H:%M"))
    if format_type == "date":
        return dt.strftime("%d %B %Y")
    elif format_type == "time":
        return dt.strftime("%H:%M")
    elif format_type == "datetime":
        return dt.strftime("%d %B %Y %H:%M")
    elif format_type == "long":
        return dt.strftime("%A %d %B %Y %H:%M")
    elif format_type == "short":
        return dt.strftime("%d/%m/%Y %H:%M")
    else:
        return value


def send_mail(name: str, email: str, template: str, data: dict):
    # Subject and body both fall back to the codebase default when not overridden.
    subject = get_template_subject(template, SUBJECTS.get(template, "Notification"))
    template_content = get_template_markdown(template)
    send_rendered_mail(name, email, subject, template_content, data)


def send_rendered_mail(
    name: str, email: str, subject: str, template_content: str, data: dict
):
    """Substitute ``data`` into the given markdown, wrap it and send the email.

    Used both by the mailer daemon (with the stored template) and by the admin
    preview/test endpoints (with an unsaved draft).
    """
    for key, value in data.items():
        if key.startswith("date-"):
            value = d(value)
        elif key.startswith("time-"):
            value = d(value, "time")
        elif key.startswith("datetime-"):
            value = d(value, "datetime")
        elif key.startswith("datetime_long-"):
            value = d(value, "long")
        elif key.startswith("datetime_short-"):
            value = d(value, "short")
        elif key.endswith("duration"):
            hours = int(value // 60)
            minutes = value % 60
            value = (f"{hours}h" if hours > 0 else "") + (
                f"{minutes}min" if minutes > 0 else ""
            )
        template_content = template_content.replace(f"{{{key}}}", str(value))

    # Markdown -> HTML, then wrap in the styled shell. base_domain / admin_mail
    # are substituted last so they fill placeholders in both content and shell.
    template_content = wrap_in_shell(markdown_to_html(template_content))
    template_content = template_content.replace(
        "{base_domain}", get("base_domain").value
    ).replace("{admin_mail}", get("admin_mail").value)

    msg = MIMEMultipart()
    msg["From"] = get("mail_from").value
    msg["To"] = f"{name} <{email}>"
    msg["Subject"] = subject

    # If the data contains an ICS event, create the ICS file and attach it to the email
    if "ics" in data:
        ics_content = create_ics(**data["ics"])
        ics = MIMEText(ics_content, "calendar; method=REQUEST")
        ics.add_header("Content-Disposition", "attachment; filename=invitation.ics")
        msg.attach(ics)

    msg.attach(MIMEText(template_content, "html"))

    if get("block_all_emails").asBool():
        logger.info("Email to %s blocked by setting", mask_email(email))
        return

    logger.info("Sending email to %s (%s)", mask_email(email), subject)
    # Envelope sender: the SMTP account when authenticated, otherwise the
    # bare address out of mail_from (which may carry a display name).
    sender = SMTP_USER or parseaddr(msg["From"])[1]
    try:
        with smtp_connect() as server:
            server.sendmail(sender, email, msg.as_string())
            logger.info("Email sent to %s", mask_email(email))
    except Exception as e:
        logger.error("Failed to send email to %s: %s", mask_email(email), e)


def queue_mail(name, email, template, data):
    mail_queue.put((name, email, template, data))


def queue_reminders():
    email_notification_before = get("email_notification_before").asInt()
    if email_notification_before == -1:
        return
    with SessionLock() as session:
        to_send = Reservation.find_unsent_reminders(session, email_notification_before)
        for reservation in to_send:
            enterprise = session.exec(
                select(Enterprise).where(Enterprise.name == reservation.user.group)
            ).first()
            session.add(
                Notification.create(
                    user=reservation.user,
                    message="notification.reminder",
                    data={
                        "datetime-start_time": reservation.start_time.strftime(
                            "%Y-%m-%d %H:%M"
                        ),
                        "duration": (
                            reservation.end_time - reservation.start_time
                        ).total_seconds()
                        // 60,
                        "shop": reservation.shop.name,
                        "maps_link": reservation.shop.maps_link,
                        "enterprise_message": enterprise.reminder_message
                        if enterprise
                        else "",
                        "ics": reservation.ics_data(),
                    },
                    route=f"/shops/{reservation.shop_id}/{monday_str(tz.utc_to_local(reservation.start_time))}",
                    is_reminder=True,
                    mail=True,
                )
            )
            reservation.reminder_sent = True
            session.add(reservation)
        session.commit()


def queue_notifications():
    with SessionLock() as session:
        unsent = Notification.find_unsent(session)
        # Group notifications by user
        notifications = {}
        for notification in unsent:
            if notification.user_id not in notifications:
                notifications[notification.user_id] = []
            notifications[notification.user_id].append(notification)
        for user_id, user_notifications in notifications.items():
            if user_id is None:
                continue
            user = session.get(User, user_id)
            for notification in user_notifications:
                data = json.loads(notification.data) if notification.data else {}
                if notification.route:
                    data["route"] = notification.route
                queue_mail(
                    user.full_name,
                    user.email,
                    notification.message,
                    data,
                )
                notification.mail_sent = True
                session.add(notification)
            session.commit()
        admin_mails = notifications.get(None, [])
        for notification in admin_mails:
            data = json.loads(notification.data) if notification.data else {}
            if notification.route:
                data["route"] = notification.route
            for admin in User.get_admins(session):
                queue_mail(
                    admin.full_name,
                    admin.email,
                    notification.message,
                    data,
                )
            notification.mail_sent = True
            session.add(notification)
        session.commit()


def stop_mailer_daemon():
    global daemon_running
    daemon_running = False
    daemon_thread.join()


def mailer_daemon():
    while daemon_running:
        if not mail_queue.empty():
            name, email, template, data = mail_queue.get()
            if data is None:
                data = {}
            send_mail(name, email, template, data)
        time.sleep(get("email_daemon_delay").asInt())
        queue_reminders()
        queue_notifications()


def start_mailer_daemon():
    """Start the daemon thread. Raises SMTPConfigurationError if SMTP is unusable."""
    global daemon_running, daemon_thread
    if get("block_all_emails").asBool():
        logger.warning("block_all_emails is set, skipping SMTP check")
    else:
        check_smtp_connection()
    daemon_running = True
    daemon_thread = threading.Thread(target=mailer_daemon, daemon=True)
    daemon_thread.start()


def main():
    setup_logging()
    try:
        start_mailer_daemon()
    except SMTPConfigurationError:
        raise SystemExit(1)
    # Keep the main thread alive
    while True:
        time.sleep(1)


def serve_mail():
    from http.server import BaseHTTPRequestHandler, HTTPServer
    import sys

    if len(sys.argv) < 2:
        print("Usage: python mailer_daemon.py <template> <data>")
        sys.exit(1)

    template = sys.argv[1]
    data = {}
    for arg in sys.argv[2:]:
        key, value = arg.split("=")
        data[key] = value

    class MailHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            template_content = get_template_markdown(template)
            for key, value in data.items():
                template_content = template_content.replace(f"{{{key}}}", str(value))
            template_content = wrap_in_shell(markdown_to_html(template_content))
            template_content = template_content.replace(
                "{base_domain}", get("base_domain").value
            ).replace("{admin_mail}", get("admin_mail").value)
            self.wfile.write(template_content.encode())

        def log_message(self, format, *args):
            pass

    server = HTTPServer(("localhost", 12345), MailHandler)
    port = server.server_address[1]
    print(f"Server started on http://localhost:{port}")
    server.serve_forever()


# Example usage
if __name__ == "__main__":
    main()
