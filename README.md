# TutorBiller
Automated Square Invoice Submission Software

### Installation

Poetry is used to manage package dependencies. Learn how to install
Poetry on your computer [here](https://python-poetry.org/docs/).

After you have poetry, run
```poetry install```
in the root of the project.

### Configure Environment Variables
This code depends on secure credentials used to access the Troy Tutors Square account, Troy Tutors'
email address, and the secret_key for the /bill API call. For this reason, you must first fill in the
relevant credentials in the .env file before running TutorBiller.

### Square
You can always monitor your Square invoices [here](https://squareup.com/dashboard/invoices/overview).
The "sandbox" environment is a testing account for Square, while the "production" environment uses our
official Square account to bill students. You can access Square API credentials, logs, documentation,
access the sandbox dashboard, and more [here](https://developer.squareup.com/us/en).

### Running the API
If you are using TutorBiller to handle incoming billing requests, from the Troy Tutors Billing page,
you will want to use the API and leave it running. To launch the API, run

```poetry run python tutor_biller.py```

Here is how you could make a POST billing API request in Python using TutorBiller.
```python
import requests

url = "http://localhost:5000/bill" # url if running locally
# Refer to example below, under Manual Billing, to see examples of these variables
body = {"secret_key": secret_key, "environment": environment, "tutor_email": tutor_email, "student_email": student_email, "course": course,"session_date": session_date, "session_minutes": session_minutes, "price": price}
response = requests.post(url, json=body)

print(response.status_code)
print(response.json())
```

You can test out the API with the provided Jupyter Notebook. After starting the API, also run
```poetry run jupyter notebook```, and run the blocks in ```test_api_calls.ipynb```, with the email
of your choice.

### Manual Billing
If you ever wish to manually bill a customer, you could either do so from the Square dashboard
or by updating and running the code with

```poetry run python bill_student_script.py```

To do so, you can update the bill_student method in the main function with the following arguments

```
bill_student("sandbox" or "production", email of tutor, email of student to bill, course name,
             date string in the format "Nov 25, 2022" (note the abbreviated month), session
             duration in minutes, hourly rate of course)
```

For example,
```python
billed, invoice_id, invoice_version, emailed = bill_student("sandbox", "tutoremail@gmail.com",
                                                            "studentemail@test.com", "Calculus I", "Nov 25, 2022",
                                                            60, 33)
```