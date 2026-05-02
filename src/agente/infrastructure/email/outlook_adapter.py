import imaplib
import smtplib
import email as email_lib
import tempfile
import os
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from src.agente.domain.ports import EmailPort, EmailReaderPort
from src.agente.domain.entities import CorreoEntrante

_IMAP_HOST = "imap-mail.outlook.com"
_IMAP_PORT = 993
_SMTP_HOST = "smtp-mail.outlook.com"
_SMTP_PORT = 587


class OutlookSMTPAdapter(EmailPort):
    def __init__(self, address: str, password: str):
        self._address = address
        self._password = password

    def send(self, to: str, subject: str, body: str) -> None:
        msg = MIMEMultipart()
        msg["From"] = self._address
        msg["To"] = to
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain", "utf-8"))

        with smtplib.SMTP(_SMTP_HOST, _SMTP_PORT) as server:
            server.ehlo()
            server.starttls()
            server.login(self._address, self._password)
            server.sendmail(self._address, to, msg.as_string())


class OutlookIMAPAdapter(EmailReaderPort):
    def __init__(self, address: str, password: str, folder: str = "INBOX"):
        self._address = address
        self._password = password
        self._folder = folder

    def fetch_unread(self) -> list[CorreoEntrante]:
        correos = []
        with imaplib.IMAP4_SSL(_IMAP_HOST, _IMAP_PORT) as imap:
            imap.login(self._address, self._password)
            imap.select(self._folder)
            _, uids = imap.search(None, "UNSEEN")
            for uid in uids[0].split():
                _, data = imap.fetch(uid, "(RFC822)")
                msg = email_lib.message_from_bytes(data[0][1])
                correos.append(self._parse(uid.decode(), msg))
        return correos

    def mark_as_read(self, uid: str) -> None:
        with imaplib.IMAP4_SSL(_IMAP_HOST, _IMAP_PORT) as imap:
            imap.login(self._address, self._password)
            imap.select(self._folder)
            imap.store(uid, "+FLAGS", "\\Seen")

    def _parse(self, uid: str, msg) -> CorreoEntrante:
        asunto = email_lib.header.decode_header(msg["Subject"] or "")[0]
        asunto_str = asunto[0].decode(asunto[1] or "utf-8") if isinstance(asunto[0], bytes) else asunto[0]

        cuerpo = ""
        adjuntos = []
        for part in msg.walk():
            ct = part.get_content_type()
            cd = str(part.get("Content-Disposition", ""))
            if ct == "text/plain" and "attachment" not in cd:
                cuerpo = part.get_payload(decode=True).decode("utf-8", errors="replace")
            elif "attachment" in cd:
                filename = part.get_filename()
                if filename and filename.lower().endswith(".pdf"):
                    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf", prefix="outlook_")
                    tmp.write(part.get_payload(decode=True))
                    tmp.close()
                    adjuntos.append(tmp.name)

        fecha_str = msg.get("Date", "")
        try:
            from email.utils import parsedate_to_datetime
            fecha = parsedate_to_datetime(fecha_str)
        except Exception:
            fecha = datetime.now()

        return CorreoEntrante(
            uid=uid,
            asunto=asunto_str,
            cuerpo=cuerpo,
            remitente=msg.get("From", ""),
            adjuntos=adjuntos,
            fecha=fecha,
        )
