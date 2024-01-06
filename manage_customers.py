from typing import Text, Tuple
import square.client


class ManageCustomers:
    def __init__(self, client: square.client.Client) -> None:
        self.client = client

    def create_customer(self, email: Text) -> Tuple[bool, Text, bool]:
        # Do not create a new customer, if the customer already exists
        successful_call, customer_id, already_existed = self.customer_exists(email)
        if not successful_call or already_existed:
            return successful_call, customer_id, already_existed

        firstname = "@"
        lastname = f"{email.split('@')[0]}"

        res = self.client.customers.create_customer(
            body = {
                "given_name": firstname,
                "family_name": lastname,
                "email_address": email
            }
        )
        if res.is_success():
            successful_call = True
            customer_id = res.body["customer"]["id"]
        elif res.is_error():
            successful_call = False
            print(res.errors)

        return successful_call, customer_id, already_existed

    def customer_exists(self, email: Text) -> Tuple[bool, Text, bool]:
        # Customer is said to exist, should an existing customer share the email
        # we are currently billing to. If the customer were to change his/her email on
        # Troy Tutors, this would currently mean we are claiming the customer does not
        # exist, we are creating a new billing account, and potential saved cards on
        # file will not be used to charge the customer.
        exists = False
        customer_id = ""
        try:
            # Customers are returned using pagination. The list_customers endpoint must be called
            # until there are no more cursors.
            res = self.client.customers.list_customers()
            customers = res.body["customers"]
            while res.body.get("cursor"):
                res = self.client.customers.list_customers(cursor=res.body["cursor"])
                customers += res.body["customers"]
            successful_call = True

            for customer in customers:
                if "email_address" in customer and customer["email_address"] == email:
                    customer_id = customer["id"]
                    exists = True
                    break
        except:
            successful_call = False

        return successful_call, customer_id, exists
