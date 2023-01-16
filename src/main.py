import datetime
import imaplib
import json
import os
import socket
import time
import traceback
from threading import Thread
from gi.repository import GLib
from imap_tools import A, MailBox, MailboxLoginError, MailboxLogoutError
from pydbus import SystemBus
from dotenv import load_dotenv



def on_incoming_email(signal, msg):
    signalGroupId = json.loads(os.environ['SIGNAL_GROUP_ID'])

    subject = msg.subject
    body = msg.text
    sender = msg.from_
    cc = ', '.join(msg.cc)
    bcc = ', '.join(msg.bcc)
    date = ''
    try:
        date = datetime.datetime.strptime(
            msg.date_str, '%a, %d %b %Y %H:%M:%S %z')
        # add one hour to turn it into GMT+1
        date = date + datetime.timedelta(hours=1)
        date = date.strftime('%d %b %H:%M')
    except:
        print(f'BOT: Failed to convert email date "{msg.date_str}"')
        date = msg.date_str

    signalMsg = [
        f'Data: {date}\n',
        f'Od: {sender}\n',
        f'CC: {cc}\n' if cc else '',
        f'BCC: {bcc}\n' if bcc else '',
        f'Tytuł: {subject}\n',
        '💌\n',
        body
    ]

    signal.sendGroupMessage(''.join(signalMsg), [], signalGroupId)
    print(f"BOT: Message forwarded to Signal (sent at {date})")


def start_emails_fetching(signal, on_incoming_email_closure):
    # https://github.com/ikvk/imap_tools/blob/06e8fb8b2ad99737e25dc0b542a9e0afeef47788/examples/idle.py#L19-L47
    host = os.environ['IMAP_HOST']
    username = os.environ['IMAP_USER']
    password = os.environ['IMAP_PASSWORD']
    done = False

    print(f"BOT: Start emails fetching for {username}...")

    while not done:
        connection_start_time = time.monotonic()
        connection_live_time = 0.0
        try:
            with MailBox(host).login(username, password, 'INBOX') as mailbox:
                print('@@ new connection', time.asctime())
                while connection_live_time < 29 * 60:
                    try:
                        responses = mailbox.idle.wait(timeout=3 * 60)
                        print(time.asctime(), 'IDLE responses:', responses)
                        if responses:
                            for msg in mailbox.fetch(A(seen=False)):
                                on_incoming_email_closure(signal, msg)
                    except KeyboardInterrupt:
                        print('~KeyboardInterrupt')
                        done = True
                        break
                    connection_live_time = time.monotonic() - connection_start_time
        except (TimeoutError, ConnectionError,
                imaplib.IMAP4.abort, MailboxLoginError, MailboxLogoutError,
                socket.herror, socket.gaierror, socket.timeout) as e:
            print(
                f'## Error\n{e}\n{traceback.format_exc()}\nreconnect in a minute...')
            time.sleep(60)


def main():
    load_dotenv()
    loop = GLib.MainLoop()
    bus = SystemBus()
    signal = bus.get('org.asamk.Signal')

    # start_emails_fetching
    thread = Thread(target=start_emails_fetching,
                    args=(signal, on_incoming_email))
    thread.start()

    loop.run()


main()
