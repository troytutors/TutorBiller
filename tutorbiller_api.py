'''
Leave this file running, so it can handle incoming requests from the Troy Tutors billing page
and bill students
'''

from flask import Flask, request, jsonify, abort
from invoice_engine import InvoiceEngine
from typing import Text, Mapping, Tuple
from gevent.pywsgi import WSGIServer
from dotenv import load_dotenv
import os


app = Flask(__name__)


def are_valid_keys(billing_info: Mapping[Text, Text]) -> Tuple[Text, Text]:
    keys = ["secret_key", "environment", "tutor_email", "student_email", "course", "session_date",
            "session_minutes", "price"]
    valid, key = True, ""
    for k in keys:
        if k not in billing_info:
            valid, key = False, k
            break
    return valid, key


def filter_email(student_email: Text) -> Text:
    # Quick fix for accounts where the billing email address are different than the Troy Tutors email address
    emails = {"cms8hernandez@gmail.com": "ria_santoro@yahoo.com", "pjmitchell@email.wm.edu": "s1ken@hotmail.com",
              "mlausev5@gmail.com": "mlausev@icloud.com"}
    updated_email = emails.get(student_email)
    if updated_email:
        filtered_email = updated_email
    else:
        filtered_email = student_email
    return filtered_email


@app.route("/", methods=["GET"])
def index():
    return jsonify("available")


@app.route("/bill", methods=["POST"])
def bill_student():
    billing_info = request.get_json()
    valid_keys = are_valid_keys(billing_info)
    if not valid_keys[0]:
        return jsonify({"Missing key": valid_keys[1]})
    if billing_info["secret_key"] != os.getenv("secret_key"):
        abort(403, description="Invalid secret key.")
    try:
        ie = InvoiceEngine(billing_info.get("environment"))
        student_email = filter_email(billing_info.get("student_email"))
        res = ie.bill_student(billing_info.get("tutor_email"), student_email,
                              billing_info.get("course"), billing_info.get("session_date"),
                              billing_info.get("session_minutes"), billing_info.get("price"))
        res_json = jsonify({"billed": res[0], "invoice_id": res[1], "invoice_version": res[2], "emailed": res[3]})
    except Exception as e:
        print(e)
        res_json = jsonify(e)
    return res_json


def main() -> None:
    # Load environment variables
    load_dotenv()
    # Start server
    http_server = WSGIServer(("", 5000), app)
    http_server.serve_forever()


if __name__ == '__main__':
    main()
