from notifications.whatsapp import WhatsAppNotifier


def test_whatsapp_message():

    notifier = WhatsAppNotifier()

    message = (
        "BANK NIFTY RSI TEST\n\n"
        "WhatsApp connection successful."
    )

    sids = notifier.send(message)

    assert len(sids) == 2

    print()
    print("WhatsApp message sent.")
    print("Message SIDs:")

    for sid in sids:
        print(sid)