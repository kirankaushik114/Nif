import os
import smtplib

from email.message import EmailMessage

from dotenv import load_dotenv

from config.settings import (
    EMAIL_ENABLED,
    EMAIL_TO_ALL_RECIPIENTS,
)


load_dotenv()


class EmailNotifier:

    def __init__(self):

        self.enabled = (
            EMAIL_ENABLED
        )

        self.smtp_server = os.getenv(
            "EMAIL_SMTP_SERVER",
            "smtp.gmail.com",
        )

        self.smtp_port = int(
            os.getenv(
                "EMAIL_SMTP_PORT",
                "587",
            )
        )

        self.sender = os.getenv(
            "EMAIL_SENDER",
            "",
        )

        self.password = os.getenv(
            "EMAIL_PASSWORD",
            "",
        )

        self.recipients = [
            os.getenv(
                "EMAIL_RECIPIENT_1"
            ),
            os.getenv(
                "EMAIL_RECIPIENT_2"
            ),
        ]

        self.recipients = [
            email
            for email in self.recipients
            if email
        ]

        if not self.enabled:

            return

        if not self.sender:

            raise ValueError(
                "EMAIL_SENDER is missing."
            )

        if not self.password:

            raise ValueError(
                "EMAIL_PASSWORD is missing."
            )

        if not self.recipients:

            raise ValueError(
                "No email recipients configured."
            )

    def send(
        self,
        subject,
        body,
    ):

        if not self.enabled:

            return []

        message = EmailMessage()

        message["From"] = (
            self.sender
        )

        message["Subject"] = (
            subject
        )

        message.set_content(
            body
        )

        results = []

        with smtplib.SMTP(
            self.smtp_server,
            self.smtp_port,
        ) as server:

            server.starttls()

            server.login(
                self.sender,
                self.password,
            )

            if EMAIL_TO_ALL_RECIPIENTS:

                for recipient in self.recipients:

                    message["To"] = (
                        recipient
                    )

                    server.send_message(
                        message
                    )

                    del message["To"]

                    results.append(
                        recipient
                    )

            else:

                recipient = (
                    self.recipients[0]
                )

                message["To"] = (
                    recipient
                )

                server.send_message(
                    message
                )

                results.append(
                    recipient
                )

        return results