'''
Run this file if you wish to manually bill a specific student using TutorBiller.

To do so, you can update the bill_student method in the main function with the following arguments
bill_student("sandbox" or "production", email of tutor, email of student to bill, course name,
                                                                date string in the format "Nov 25, 2022" (note the
                                                                abbreviated month), session duration in minutes, hourly
                                                                rate of course)
For example,
    billed, invoice_id, invoice_version, emailed = bill_student("sandbox", "tutoremail@gmail.com",
                                                                "studentemail@test.com", "Calculus I", "Nov 25, 2022",
                                                                60, 33)
'''

from invoice_engine import InvoiceEngine
from typing import Text, Tuple


def filter_email(student_email: Text) -> Text:
    emails = {"cms8hernandez@gmail.com": "ria_santoro@yahoo.com", "pjmitchell@email.wm.edu": "s1ken@hotmail.com",
              "mlausev5@gmail.com": "mlausev@icloud.com"}
    updated_email = emails.get(student_email)
    if updated_email:
        filtered_email = updated_email
    else:
        filtered_email = student_email
    return filtered_email


def bill_student(environment: Text, tutor_email: Text, student_email: Text, course: Text, session_date: Text,
                 session_minutes: int, price: int) -> Tuple[bool, Text, int, bool]:
    ie = InvoiceEngine(environment)
    student_email = filter_email(student_email)
    # returns a tuple of billed, invoice_id, invoice_version, and emailed variables
    return ie.bill_student(tutor_email, student_email, course, session_date, session_minutes, price)


def main() -> None:
    billed, invoice_id, invoice_version, emailed = bill_student("sandbox", "zacknawrocki@gmail.com",
                                                                "test@test.com", "Calculus I", "Nov 25, 2022", 60, 33)
    print(billed, invoice_id, invoice_version, emailed)


if __name__ == "__main__":
    main()
