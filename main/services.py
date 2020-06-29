import imaplib
import email
import time
import datetime

def get_notifications(conf_data):
    tfhour = time.strptime(str(datetime.datetime.now().time().hour) + ":" + str(datetime.datetime.now().time().minute), "%H:%M")
    twhour_now = time.strftime( "%I:%M", tfhour)
    raw_data = notification_scraper(conf_data)
    final_data = []
    if raw_data == 0:
        return 0, final_data
    for i in range (3):
        split_data = []
        split_data = raw_data[i].split("////")
        split_data.append(str(twhour_now))
        if len(split_data) == 4:
            final_data.append(split_data)

    total_notifications = len(final_data)
    return total_notifications, final_data

def notification_scraper(conf_data):
    try:
        text, email_acc, psswd = conf_data.split('\n')
    except:
        print("Can't read config file, make sure you followed the instructions")
        return 0
    mail = imaplib.IMAP4_SSL('imap.gmail.com')
    mail.login(email_acc,psswd)
    mail.select('inbox')

    result, data = mail.search(None, 'ALL')
    mail_ids = data[0]

    id_list = mail_ids.split()   
    first_email_id = int(id_list[0])
    latest_email_id = int(id_list[-1])

    final_list = []

    for i in range(latest_email_id,latest_email_id-4, -1):
        result, data = mail.fetch(str(i), '(RFC822)' )
        for response_part in data:
            if isinstance(response_part, tuple):
                # from_bytes, not from_string
                msg = email.message_from_bytes(response_part[1])
                email_subject = msg['subject']
                final_list.append(email_subject)

    return final_list
