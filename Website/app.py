#imports
from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import smtplib
from sqlite3 import Error
from flask_bcrypt import Bcrypt
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

app = Flask(__name__)

DATABASE = "emails.db"
sender_email = '_REDACTED_'
password = '_REDACTED_'
subject = 'Tsunami Warning!'
bcrypt = Bcrypt(app)

def open_database(database):
    return sqlite3.connect(database)
 

def create_connection(db_file):
    try:
        # Create a connection to the SQLite database file
        connection = sqlite3.connect(db_file)
        return connection
    except Error as e:
        print(e)
        return None


def send_email(wave_height):
    # Build message using argument
    body = f'Get to higher ground, Tsunami detected with max wave height of {wave_height}'

    # Fetch emails
    db = open_database(DATABASE)
    cur = db.cursor()
    cur.execute("SELECT email FROM recipients")
    recipients = cur.fetchall()
    db.close()

    # Filter out None values and extract emails
    bcc_emails = [recipient[0] for recipient in recipients if recipient[0] is not None]

    if not bcc_emails:
        print("No valid recipients found.")
        return

    # Connect to SMTP
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(sender_email, password)

    # Compose email
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    # Set Bcc header
    msg['Bcc'] = ", ".join(bcc_emails)

    try:
        # Send the email
        server.sendmail(sender_email, bcc_emails, msg.as_string())
        print('Email sent successfully!')
    except Exception as e:
        print(f'Failed to send email: {str(e)}')

    # Close connection
    server.quit()
    print("Sent email!")


@app.route('/', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form.get('email')

        # Open a connection to the database
        con = open_database(DATABASE)

        # Check if the email already exists in the database
        cur = con.cursor()
        cur.execute("SELECT COUNT(*) FROM recipients WHERE email = ?", (email,))
        result = cur.fetchone()[0]
        if result > 0:
            con.close()
            return redirect(url_for('signup', error='Email is already used'))

        # If the email is not already in the database, insert it
        query = "INSERT INTO recipients (email) VALUES (?)"
        try:
            cur.execute(query, (email,))
            con.commit()
        except Error as e:
            print(e)
            con.rollback()
            con.close()
            return redirect(url_for('signup', error='An error occurred during sign up'))

        con.close()

    return render_template('signup.html')

# This function is a secret url with a form on it with height and key inputs
# it will check if the key entered is correct and then trigger the emails to be sent out with the function from above.
@app.route('/triggerpage2b2wc', methods=['GET', 'POST'])
def triggerpage2b2wc():
    if request.method == 'POST':
        key = request.form.get('key')
        wave_height = request.form.get('height')
        if key == "_REDACTED_":
            print(key, wave_height)
            send_email(wave_height)
        else:
            print("no")
    return render_template('triggerpage2b2wc.html')

#tsunami info
@app.route('/tsunamiinfo', methods=['GET', 'POST'])
def tsunamiinfo():

    return render_template('tsunamiinfo.html')


if __name__ == '__main__':
    # Start the Flask application
    app.run(host="0.0.0.0", port=8000)

