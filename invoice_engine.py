from email.mime.multipart import MIMEMultipart
from manage_customers import ManageCustomers
from manage_invoices import ManageInvoices
from typing import Text, Tuple, Mapping
from manage_orders import ManageOrders
from email.mime.text import MIMEText
from square.client import Client
from datetime import datetime
import smtplib
import pytz
import ssl
import os


class InvoiceEngine:
    def __init__(self, environment: Text) -> None:
        if environment == "production":
            self.access_token = os.getenv("production_access_token")
            self.location_id = os.getenv("production_location_id")
        # if sandbox environment specified, or unrecognized command, default to sandbox
        else:
            self.access_token = os.getenv("sandbox_access_token")
            self.location_id = os.getenv("sandbox_location_id")
        self.client = Client(
            access_token=self.access_token,
            environment=environment
        )
        self.email_info : Mapping[Text, Text] = {"smtp_server": os.getenv("smtp_server"),
                                                 "sender_email": os.getenv("sender_email"),
                                                 "password": os.getenv("password"), "port": os.getenv("port")}
        self.customers = ManageCustomers(self.client)
        self.orders = ManageOrders(self.client)
        self.invoices = ManageInvoices(self.client)

    def bill_student(self, tutor_email: Text, student_email: Text, course: Text, session_date: Text,
                     session_minutes: int, price: int, send_email: bool=True) -> Tuple[bool, Text, int, bool]:
        # Make all emails in lowercase to prevent creating new profiles of emails with different punctuation
        tutor_email = tutor_email.lower()
        student_email = student_email.lower()

        # Create a customer, if customer doesn't already exist
        print("Creating a customer or finding an existing customer...")
        successful_call, customer_id, already_existed = self.customers.create_customer(student_email)
        if not successful_call:
            return False, "", -1, False
        print("Success")

        # Create an order for the invoice (what was paid for, total price based on course and duration)
        print("Creating an order...")
        created, order_id = self.orders.create_order(self.location_id, customer_id, course, session_minutes,
                                                     price, student_email)
        if not created:
            return False, "", -1, False
        print("Success")

        # Draft an invoice
        print("Drafting an invoice...")
        drafted, invoice_id, invoice_version = self.invoices.draft_invoice(customer_id, order_id,
                                                                           tutor_email, session_date)
        if not drafted:
            return False, "", -1, False
        print("Success")

        # Publish an invoice
        print("Publishing an invoice...")
        published, invoice_id, invoice_version = self.invoices.publish_invoice(invoice_id, invoice_version)
        if published:
            print("Success")

        # Send a confirmation email
        emailed = False
        if send_email:
            print("Sending an email...")
            emailed = self.send_confirmation_email(tutor_email, student_email, course, session_date, session_minutes)
            if emailed:
                print("Success")

        return published, invoice_id, invoice_version, emailed

    def send_confirmation_email(self, tutor_email: Text, student_email: Text, course: Text,
                                session_date: Text, session_minutes: int) -> bool:
        # Send confirmation email to tutor who made the billing call, for record keeping
        smtp_server = self.email_info["smtp_server"]
        port = int(self.email_info["port"])
        sender_email: Text = self.email_info["sender_email"]
        receiver_email: Text = tutor_email
        password = self.email_info[f"password"]
        tutor_id = f"{tutor_email.split('@')[0]}"
        student_id = f"{student_email.split('@')[0]}"
        et = pytz.timezone('US/Eastern')
        now = datetime.now().astimezone(et)
        now_str = now.strftime("on %B %d, %Y at %I:%M %p %Z")

        message = MIMEMultipart("alternative")
        message["Subject"] = f"Your Troy Tutors Billing Submission, @{tutor_id}"
        message["From"] = sender_email
        message["To"] = receiver_email
        body_text = (f"Hi, @{tutor_id}, this email is for your record keeping.\n\n"
                     f"You have just billed @{student_id} for {session_minutes} minutes "
                     f"in {course}. The date of the session occurred on {session_date} "
                     f"and you have submitted the billing {now_str}.\n\n"
                     "You should expect to see your direct deposit on the last day "
                     "of this month. If something in this email looks incorrect, or you made "
                     "a mistake in your billing submission, please contact either Zack or Ed "
                     "ASAP. If you do not end up receiving this confirmation email during a "
                     "future billing submission, please contact Zack or Ed first before attempting "
                     "to resubmit a billing.\n\n"
                     "Thank you,\nThe Troy Tutors Billing Team")
        body = MIMEText(body_text, "plain")
        message.attach(body)

        # Create secure connection with server and send email
        try:
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
                server.login(sender_email, password)
                server.sendmail(sender_email, receiver_email, message.as_string())
            emailed = True
        except Exception as e:
            print(e)
            emailed = False

        return emailed
