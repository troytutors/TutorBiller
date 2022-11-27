from typing import Text, Tuple
import square.client


class ManageOrders:
    def __init__(self, client: square.client.Client) -> None:
        self.client = client

    def create_order(self, location_id: Text, customer_id: Text, course: Text, session_minutes: int,
                     price: int, student_email: Text) -> Tuple[bool, Text]:
        order_name = f"{course} Tutoring ({session_minutes} min)"
        # Convert hourly dollar rate to minute rate, given session minutes, in cents
        total_price = round(price / 60 * session_minutes * 100)
        order_id = ""
        created = False

        body = {
            "order": {
                "location_id": location_id,
                "customer_id": customer_id,
                "line_items": [
                    {
                        "name": order_name,
                        "quantity": "1",
                        "base_price_money": {
                            "amount": total_price,
                            "currency": "USD"
                        }
                    }
                ],
                "service_charges": [
                    {
                        "name": "Service Fee",
                        "percentage": "3.9",
                        "calculation_phase": "TOTAL_PHASE",
                        "taxable": False
                    }
                ]
            },
        }

        # Hardcoded, remove after December and remove student_email argument from function
        if student_email == "discount@test.com" or student_email == "ria_santoro@yahoo.com" or student_email == "shaika3@rpi.edu":
            body["order"]["discounts"] = [{"name": "Pro Discount", "percentage": "10"}]

        res = self.client.orders.create_order(
            body=body
        )
        if res.is_success():
            created = True
            order_id = res.body["order"]["id"]
        elif res.is_error():
            print(res.errors)

        return created, order_id
