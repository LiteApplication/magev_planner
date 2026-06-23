"""Render markdown email templates to styled HTML.

Templates are markdown. Defaults live in ``templates/markdown/<name>.md`` and may
be overridden per-template by an admin-edited row in the ``MailTemplate`` table.

Custom syntax on top of markdown:
- ``[[ url | label ]]`` becomes a styled button (an ``<a>`` styled like a button).
- ``![alt](url)`` is standard markdown and renders as a responsive ``<img>``.

The rendered content is wrapped in ``templates/email_template.html`` (``{content}``)
for consistent styling.
"""

import os
import re

import markdown as md_lib

from shared_planner.db.models import MailTemplate
from shared_planner.db.session import SessionLock

TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), "..", "templates")
MARKDOWN_DIR = os.path.join(TEMPLATE_DIR, "markdown")

# All editable email templates (the `template` argument passed to send_mail).
TEMPLATE_NAMES = [
    "first_mail",
    "password_reset",
    "notification.reminder",
    "notification.reservation_created",
    "notification.reservation_cancelled",
    "notification.reservation_modified",
    "notification.reservation_reassigned_new",
    "notification.reservation_reassigned_old",
    "notification.admin.new_user",
    "notification.admin.reservation_created",
    "notification.admin.reservation_modified",
    "notification.admin.reservation_cancelled",
]

_BUTTON_RE = re.compile(r"\[\[\s*(.+?)\s*\|\s*(.+?)\s*\]\]", re.DOTALL)
_BUTTON_HTML = (
    '<a href="{url}" target="_blank" '
    'style="display:inline-block;margin:6px 0;padding:10px 20px;'
    "background-color:#0c4f97;color:#ffffff;text-decoration:none;"
    'border-radius:5px;font-weight:bold;">{text}</a>'
)

with open(os.path.join(TEMPLATE_DIR, "email_template.html"), "r") as _f:
    EMAIL_SHELL = _f.read()


def default_markdown(name: str) -> str:
    """Read the codebase default markdown for a template."""
    path = os.path.join(MARKDOWN_DIR, f"{name}.md")
    with open(path, "r") as f:
        return f.read()


def get_template_markdown(name: str) -> str:
    """Return the admin override if present, else the codebase default."""
    with SessionLock() as session:
        override = session.get(MailTemplate, name)
        if override is not None:
            return override.content
    return default_markdown(name)


def _render_buttons(text: str) -> str:
    return _BUTTON_RE.sub(
        lambda m: _BUTTON_HTML.format(url=m.group(1).strip(), text=m.group(2).strip()),
        text,
    )


def markdown_to_html(md_text: str) -> str:
    """Convert (already placeholder-substituted) markdown to email-ready HTML."""
    html = _render_buttons(md_text)
    html = md_lib.markdown(html, extensions=["extra", "nl2br", "sane_lists"])
    # Make images responsive in email clients.
    html = html.replace("<img ", '<img style="max-width:100%;height:auto;" ')
    return html


def wrap_in_shell(content_html: str) -> str:
    return EMAIL_SHELL.replace("{content}", content_html)
