from datetime import datetime, timedelta
from typing import Text, Tuple, Mapping
import square.client


class ManageInvoices:
    def __init__(self, client: square.client.Client) -> None:
        self.client = client
        self.due_in_n_days = 7
        with open("invoice_message.txt", "r") as f:
            self.message = f.read()
        self.month_abbr = {"Jan": "01", "Feb": "02", "Mar": "03", "Apr": "04", "May": "05", "Jun": "06", "Jul": "07",
                           "Aug": "08", "Sep": "09", "Oct": "10", "Nov": "11", "Dec": "12"}
        self.reminders = [{"relative_scheduled_days": -1}, {"relative_scheduled_days": 0},
                          {"relative_scheduled_days": 3}]

    def draft_invoice(self, customer_id: Text, order_id: Text, tutor_email: Text,
                      session_date: Text) -> Tuple[bool, Text, int]:
        # Make due n days in the future
        dt = datetime.now()
        td = timedelta(days=self.due_in_n_days)
        due_date_dt = dt + td
        due_date = due_date_dt.strftime("%Y-%m-%d")

        tutor_id = f"@{tutor_email.split('@')[0]}"
        invoice_id = ""
        drafted = False

        valid_date_str, session_date_str = self.generate_session_date_str(session_date)
        if not valid_date_str:
            return False, invoice_id, -1

        # Body of create_invoice API call, excluding saved cards on file
        body: Mapping = {
            "invoice": {
                "order_id": order_id,
                "primary_recipient": {
                    "customer_id": customer_id
                },
                "payment_requests": [
                    {
                        "request_type": "BALANCE",
                        "due_date": due_date,
                        "reminders": self.reminders
                    }
                ],
                "delivery_method": "EMAIL",
                "title": f"Troy Tutors Session with {tutor_id}",
                "description": self.message,
                "accepted_payment_methods": {
                    "card": True
                },
                "sale_or_service_date": session_date_str,
                "store_payment_method_enabled": True
            },
        }

        # Get the customer's latest card on file to charge. If no card exists, the variables will not
        # be added as fields to the API call.
        latest_card_id, automatic_payment_source = self.get_latest_card_on_file(customer_id)
        if latest_card_id != "" and automatic_payment_source != "":
            body["invoice"]["payment_requests"][0]["card_id"] = latest_card_id
            body["invoice"]["payment_requests"][0]["automatic_payment_source"] = automatic_payment_source

        # Create an invoice draft
        res = self.client.invoices.create_invoice(body=body)

        if res.is_success():
            drafted = True
            invoice_id = res.body["invoice"]["id"]
            invoice_version = res.body["invoice"]["version"]
        elif res.is_error():
            print(res.errors)

        return drafted, invoice_id, invoice_version

    def generate_session_date_str(self, session_date: Text) -> Tuple[bool, Text]:
        session_datelist = session_date.split(" ")
        session_month = self.month_abbr.get(session_datelist[0].strip())
        if not session_month:
            print("Invalid month")
            return False, ""

        # Add 0 in front of single digit days
        session_day = session_datelist[1].strip(",").strip()
        if len(session_day) == 1:
            session_day = "0" + session_day

        session_year = session_datelist[2].strip()

        full_date_str = f"{session_year}-{session_month}-{session_day}"
        return True, full_date_str

    def get_latest_card_on_file(self, customer_id: Text) -> Tuple[Text, Text]:
        latest_card_id = ""
        automatic_payment_source = ""
        res = self.client.cards.list_cards(
            customer_id=customer_id,
            sort_order="DESC"
        )
        if res.is_success():
            # Check if cards key exists in dictionary (not {}) and that there is at
            # least one active card currently saved on file (not {"cards": []})
            cards = []
            if "cards" in res.body:
                cards = res.body["cards"]
            if len(cards) > 0:
                latest_card_id = cards[0]["id"]
                automatic_payment_source = "CARD_ON_FILE"
        elif res.is_error():
            print(res.errors)
        return latest_card_id, automatic_payment_source

    def publish_invoice(self, invoice_id: Text, invoice_version: int) -> Tuple[bool, Text, int]:
        published = False
        # API call to publish an invoice draft
        res = self.client.invoices.publish_invoice(
            invoice_id=invoice_id,
            body={
                "version": invoice_version,
            }
        )

        if res.is_success():
            published = True
            invoice_id = res.body["invoice"]["id"]
            invoice_version = res.body["invoice"]["version"]
        elif res.is_error():
            print(res.errors)

        return published, invoice_id, invoice_version
