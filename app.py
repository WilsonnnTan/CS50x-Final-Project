import os
import re
import secrets
from datetime import datetime, timedelta
from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, lookup_detail, lookup_50stocks, usd, reset_pass_mail

# Configure application
app = Flask(__name__)

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")

email_regex = r"^[a-zA-Z0-9._%+-]+@gmail\.com$"

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""
    portfolios = db.execute(
        "SELECT * FROM finance WHERE user_id = ? AND shares > 0", session["user_id"])
    cash = db.execute("SELECT cash FROM users WHERE id = ?", session["user_id"])
    cash = cash[0]["cash"]
    total = 0

    for portfolio in portfolios:
        share = lookup(portfolio["symbol"])
        portfolio["price"] = usd(share["price"])
        total += (portfolio["shares"] * share["price"])
        portfolio["total"] = usd(portfolio["shares"] * share["price"])

    total += cash
    cashusd = usd(cash)
    totalusd = usd(total)

    return render_template("portfolio.html", cashusd=cashusd, totalusd=totalusd, portfolio=portfolios)


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
    if request.method == "POST":
        symbol = request.form.get("symbol")
        share = request.form.get("shares")

        if not symbol:
            return apology("Missing Symbol", 400)

        if not share:
            return apology("Missing Shares", 400)

        try:
            share = int(share)
        except ValueError:
            return apology("Shares must be in Integer Value", 400)

        if share < 0:
            return apology("Shares must be greater than 0", 400)

        if symbol and share:
            symbol = lookup(symbol)
            if symbol:
                cash = db.execute("SELECT cash FROM users WHERE id = ?", session["user_id"])
                cash = cash[0]["cash"]
                cash -= share * symbol["price"]
                isExist = db.execute(
                    "SELECT * FROM finance WHERE user_id = ? AND symbol = ?", session["user_id"], symbol["symbol"])

                if not isExist:
                    db.execute("INSERT INTO finance (user_id, symbol, shares) VALUES (?, ?, ?)",
                               session["user_id"], symbol['symbol'], share)
                else:
                    totalshare = db.execute(
                        "SELECT shares FROM finance WHERE user_id = ? AND symbol = ?", session["user_id"], symbol["symbol"])
                    totalshare = totalshare[0]["shares"]
                    totalshare += share
                    db.execute("UPDATE finance SET shares = ? WHERE user_id = ? AND symbol = ?",
                               totalshare, session["user_id"], symbol["symbol"])

                db.execute("UPDATE users SET cash = ? WHERE id = ?", cash, session["user_id"])
                db.execute("INSERT INTO history (user_id, symbol, shares, price) VALUES (?, ?, ?, ?)",
                           session["user_id"], symbol["symbol"], share, usd(symbol["price"]))
            else:
                return apology("Invalid Symbol", 400)

        return redirect("/")
    else:
        return render_template("buy.html")


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    histories = db.execute(
        "SELECT * FROM history WHERE user_id = ? ORDER BY transacted_at", session["user_id"])
    return render_template("history.html", histories=histories)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 400)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 400)

        # Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE username = ? OR email = ?", request.form.get("username"), request.form.get("username")
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            return apology("invalid username and/or password", 400)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""

    if request.method == "GET":
        stocks_symbol = lookup_50stocks()
        return render_template("quote.html", stocks=stocks_symbol)
    else:
        return apology("Something Went Wrong on quote")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        confpassword = request.form.get("confirmation")

        if re.match(email_regex, email):
            if not name:
                return apology("must provide username", 400)

            if not password:
                return apology("must provide password", 400)

            if not confpassword:
                return apology("must provide confirm password", 400)

            if name and password:
                if password == confpassword:
                    db_user = db.execute("SELECT username FROM users WHERE username = ? OR email = ?", name, email)
                    hash_password = generate_password_hash(password)

                    if not db_user:
                        db.execute("INSERT INTO users (username, hash, email) VALUES (?, ?, ?)",
                                name, hash_password, email)
                    else:
                        return apology("username/email already exist!!", 400)
                else:
                    return apology("password doesn't match", 400)
        else:
            return apology("Email pattern doesn't match, Must Use @gmail.com", 400)
    else:
        return render_template("register.html")

    return redirect("/login")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    if request.method == "POST":
        symbol = request.form.get("symbol")
        share = request.form.get("shares")

        if not symbol:
            return apology("Missing symbol", 400)

        if not share:
            return apology("Missing shares", 400)

        if share and symbol:
            share = int(share)
            symbol = lookup(symbol)
            cash = db.execute("SELECT cash FROM users WHERE id = ?", session["user_id"])
            cash = cash[0]["cash"]
            cash += symbol["price"] * share
            isExist = db.execute(
                "SELECT * FROM finance WHERE user_id = ? AND symbol = ? AND shares > 0", session["user_id"], symbol["symbol"])

            if not isExist:
                return apology("you dont have this shares!!", 400)
            else:
                totalshare = db.execute(
                    "SELECT shares FROM finance WHERE user_id = ? AND symbol = ?", session["user_id"], symbol["symbol"])
                totalshare = totalshare[0]["shares"]

                if totalshare < share:
                    return apology("you don't have enough shares!!", 400)
                else:
                    totalshare -= share

                db.execute("UPDATE finance SET shares = ? WHERE user_id = ? AND symbol = ?",
                           totalshare, session["user_id"], symbol["symbol"])

            db.execute("UPDATE users SET cash = ? WHERE id = ?", cash, session["user_id"])
            db.execute("INSERT INTO history (user_id, symbol, shares, price) VALUES (?, ?, ?, ?)",
                       session["user_id"], symbol["symbol"], -share, usd(symbol["price"]))
        return redirect("/")
    else:
        symbols = db.execute(
            "SELECT DISTINCT symbol FROM finance WHERE user_id = ? AND shares > 0", session["user_id"])
        return render_template("sell.html", symbols=symbols)

@app.route("/reset_password_email", methods=["GET", "POST"])
def reset_password_email():
    if request.method == "GET":
        if request.args.get("token"):
            reset_user = db.execute("SELECT * FROM users WHERE reset_token = ?", request.args.get("token"))
            if len(reset_user) != 1:
                return apology("Token not valid", 400)
            else:
                current_time = datetime.now()
                token_expire_str = reset_user[0]["expired_at"]
                token_expire = datetime.strptime(token_expire_str, "%Y-%m-%d %H:%M:%S")
                if token_expire < current_time:
                    return apology("token expired", 400)
                else:
                    return render_template("reset_password.html", token=reset_user[0]["reset_token"])
        else:
            return render_template("reset_password_email.html")
    else:
        email = request.form.get("email")
        if not re.match(email_regex, email):
            return apology("email pattern doesn't match (must use @gmail.com)", 400)
        else:
            user = db.execute("SELECT * FROM users WHERE email = ?", email)
            if user:
                token = secrets.token_hex(16)
                expired_at = datetime.now() + timedelta(seconds=90)
                db.execute("UPDATE users SET reset_token = ?, expired_at =? WHERE email = ?", token, expired_at, email)
                url = "https://reimagined-umbrella-4j7rpj74gxrrf7p66-5000.app.github.dev/reset_password_email?token=" + token # this can be upgraded if web is deployed by using web specific URL
                reset_pass_mail(email, url)
                return redirect("/")
            else:
                return apology("Email doesn't exist in database", 400)


@app.route("/reset", methods=["POST"])
def reset():
    if request.method == "POST":
        form = request.form
        token = form.get("token")
        user = db.execute("SELECT * FROM users WHERE reset_token = ?", token)
        token_expire_str = user[0]["expired_at"]
        token_expire = datetime.strptime(token_expire_str, "%Y-%m-%d %H:%M:%S")
        if datetime.now() > token_expire:
            return apology("Token Expired, Must Resend Link!!", 400)
        else:
            password = form.get("password")
            confirmation = form.get("confirmation")
            if password != confirmation:
                return apology("password don't match", 400)
            else:
                hashed_password = generate_password_hash(password)
                isWorking = db.execute("UPDATE users SET hash = ? WHERE reset_token = ?", hashed_password, token)
                if isWorking == 1:
                    db.execute("UPDATE users SET reset_token =  NULL WHERE reset_token = ?", token)
                    return redirect("/login")
                else:
                    return apology("Update Password Failed", 500)

    else:
        return apology("Nuh uh", 400)

@app.route("/stock_detail", methods=["GET", "POST"])
def stock_detail():
    if request.method == "GET":
        symbol = request.args.get("symbol")
    elif request.method == "POST":
        symbol = request.form.get("symbol")

    detail = lookup_detail(symbol)
    if detail:
        return render_template("detail.html", detail=detail)
    else:
        return apology("Symbol INVALID")


@app.route("/delete_acc", methods=["GET"])
def delete_acc():
    if request.method == "GET":
        db.execute("DELETE FROM history WHERE user_id = ?", session["user_id"])
        db.execute("DELETE FROM finance WHERE user_id = ?", session["user_id"])
        db.execute("DELETE FROM users WHERE id = ?", session["user_id"])
        session.clear()
        return redirect("/")
    else:
        return apology("PAGE NOT FOUND", 404)
