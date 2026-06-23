from email.policy import SMTP
import json
import os
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
from shared_planner.mail_render import (
    get_template_markdown,
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
TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), "..", "templates")

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
    subject = SUBJECTS.get(template, "Notification")

    # Load the markdown source (admin override or codebase default).
    template_content = get_template_markdown(template)

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
        print(f"Email to {email} blocked by setting")
        return

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            if SMTP_USE_TLS:
                server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.sendmail(SMTP_USER, email, msg.as_string())
            print(f"Email sent to {email}")
    except Exception as e:
        print(f"Failed to send email to {email}: {e}")


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
    global daemon_running, daemon_thread
    daemon_running = True
    daemon_thread = threading.Thread(target=mailer_daemon, daemon=True)
    daemon_thread.start()


def main():
    start_mailer_daemon()
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
