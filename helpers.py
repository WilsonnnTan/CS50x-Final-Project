import requests
import smtplib
import os
from flask import redirect, render_template, session
from functools import wraps
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def apology(message, code=400):
    """Render message as an apology to user."""

    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [
            ("-", "--"),
            (" ", "-"),
            ("_", "__"),
            ("?", "~q"),
            ("%", "~p"),
            ("#", "~h"),
            ("/", "~s"),
            ('"', "''"),
        ]:
            s = s.replace(old, new)
        return s

    return render_template("apology.html", top=code, bottom=escape(message)), code


def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/latest/patterns/viewdecorators/
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)

    return decorated_function


def lookup(symbol):
    """Look up quote for symbol."""
    url = f"https://finance.cs50.io/quote?symbol={symbol.upper()}"

    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for HTTP error responses
        quote_data = response.json()
        return {
            "name": quote_data["companyName"],
            "price": quote_data["latestPrice"],
            "symbol": symbol.upper(),
        }
    except requests.RequestException as e:
        print(f"Request error: {e}")
    except (KeyError, ValueError) as e:
        print(f"Data parsing error: {e}")
    return None

apikey = os.getenv('APIKEY_MarketData')

def lookup_detail(symbol):
    url_detail = f"https://api.polygon.io/v3/reference/tickers/{symbol}?apiKey={apikey}"
    try:
        response_detail = requests.get(url_detail)
        response_detail.raise_for_status()
        quote_detail = response_detail.json()

        return {
            "results": quote_detail["results"]
        }
    except requests.RequestException as e:
        print(f"Request error: {e}")
    except (KeyError, ValueError) as e:
        print(f"Data parsing error: {e}")
    return None

def lookup_50stocks():
    url = f"https://api.polygon.io/v3/reference/tickers?market=stocks&active=true&order=desc&limit=50&sort=last_updated_utc&apiKey={apikey}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        quotes = response.json()

        take_ticker = []

        for quote in quotes["results"]:
            take_ticker.append(quote["ticker"])

        return take_ticker
    except requests.RequestException as e:
        print(f"Request error: {e}")
    except (KeyError, ValueError) as e:
        print(f"Data parsing error: {e}")
    return None

def usd(value):
    """Format value as USD."""
    return f"${value:,.2f}"

# taking this code from gpt and documentation
sender = os.getenv('MAIL_USERNAME')
subject = "Reset Password Request"
server = smtplib.SMTP("smtp.gmail.com", 587)
server.starttls()
server.login(sender, os.getenv('MAIL_PASSWORD'))

def reset_pass_mail(email, url):
    # Construct the HTML message
    message = f"""\
    <html>
        <body>
            <p>Click this link to reset your password:</p>
            <a href="{url}">Reset Password</a>
        </body>
    </html>
    """

    # Create a MIMEMultipart message
    msg = MIMEMultipart()
    msg['From'] = sender
    msg['To'] = email
    msg['Subject'] = subject

    # Attach the HTML message to the email
    msg.attach(MIMEText(message, 'html'))

    # Send the email
    server.sendmail(sender, email, msg.as_string())
