from sendmail_container import FormDataRequest


def send_email(email_form: FormDataRequest) -> None:
    email_form.submit()
