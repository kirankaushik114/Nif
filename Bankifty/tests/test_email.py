from notifications.email import EmailNotifier


def test_email_message():

    notifier = EmailNotifier()

    recipients = notifier.send(
        subject="BANK NIFTY RSI TEST",
        body=(
            "BANK NIFTY RSI TEST\n\n"
            "Email connection successful."
        ),
    )

    assert len(recipients) == 2

    print()
    print("Email sent successfully.")
    print("Recipients:")

    for recipient in recipients:
        print(recipient)