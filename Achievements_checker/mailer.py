import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class Mailer:
    def __init__(self, sender, pwd, boilerplate = None):
        self.SENDER = sender
        self.PWD = pwd
        self.SUBJECT = "New achievements for your games have been added"

        self.boilerplate = boilerplate

        if self.boilerplate == None:
            self.boilerplate = "This is an automatic message, please do not respond.\nNew achievements are available for games on your list:\n"

        self.smtp_server = 'smtp.gmail.com'
        self.smtp_port = 587
        
    def sendMessage(self, to, message_list):
        message = self.createMessage(to, message_list)

        try:
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.SENDER , self.PWD)
            server.sendmail(self.SENDER , to, message.as_string())
            print("Email sent successfully.")

        except Exception as e:
            print(f"Failed to send email: {e}")

        finally:
            server.quit()

    def createMessage(self, to, message_list):
        message = MIMEMultipart()
        message['From'] = self.SENDER
        message['To'] = to
        message['Subject'] = self.SUBJECT

        body = MIMEText(self.boilerplate + '\n' + '\n'.join(message_list))
        message.attach(body)

        return message
