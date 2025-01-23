# Stocks Trading WebApp

## Demo Video:
[Link to Demo Video](https://youtu.be/jBBXri_KNqQ)

---

## Description:
This project is an enhanced version of the **CS50x Finance** problem set, where I have implemented new features to improve the user experience and increase the app's functionality. The primary upgrades focus on security and real-time stock data integration.

---

## Key Features:

### 1. Password Reset via Email
- **Enhanced Security**: Users can reset their password securely via email, reducing the risk of unauthorized access and improving user convenience.
- **Password Recovery**: When users forget their password, they can request a reset link sent directly to their registered email address, allowing them to regain access to their accounts easily.

### 2. Stock Detail View
- **Comprehensive Stock Information**: Users can now view detailed data for each stock, not just track prices. This includes key metrics such as stock volume, price history, and more.
- **Real-Time Data**: Stock data is retrieved in real-time from a third-party API, ensuring users always see the most up-to-date information.

### 3. Real-Time Data Integration
- **Live Updates**: Stock data is fetched from reliable financial APIs like Alpha Vantage or Yahoo Finance, ensuring the information displayed is always accurate and current.
- **Smooth User Experience**: Stock prices and other relevant details are automatically updated in real-time for seamless interaction.

---

## Technologies Used:

- **Frontend**:
  - **HTML** for structure
  - **CSS** for styling
  - **JavaScript** for interactivity
- **Backend**:
  - **Python** (Flask) for server-side logic
- **Database**:
  - **SQL** (SQLite) for data storage and management
- **API Integration**:
  - Fetching real-time stock data through APIs (Polygon.io)
- **Email Integration**:
  - **SMTP** server for password reset functionality

---

## File Details:

### `finance.db`
This database schema consists of three tables:
- **Users**: Stores user details, including `id`, `username`, hashed password (`hash`), `email`, a reset token (`reset_token`) for password recovery, its expiration timestamp (`expired_at`), and a default cash balance.
- **Finance**: Links to the users table through `user_id` and tracks stock ownership, storing details such as the stock symbol and the number of shares owned.
- **History**: References the users table via `user_id` and records transaction details, including the stock symbol, number of shares traded, price, and the transaction timestamp.

This schema efficiently manages user accounts, portfolios, and transaction histories.

---

### `helpers.py`
This Python script includes utility functions and configurations for a Flask-based web application:
- **API Integration**: Fetches stock market data using `lookup_detail` and `lookup_50stocks`, which retrieve detailed ticker information and the latest 50 active stocks, respectively, leveraging APIs like Polygon.io.
- **Email Functionality**: `reset_pass_mail` constructs and sends an HTML email using the `smtplib` library for password recovery.
- **Security**: The email sender details and API key for the stock market data are securely accessed via environment variables.

This modular setup supports robust user interactions, email notifications, and external data lookups for enhanced functionality.

---

### `app.py`
This Python Flask application implements a stock trading platform where users can buy, sell, and manage their portfolios, while also incorporating features like user registration, authentication, password reset, and email notifications.

#### Key Functionalities of app.py:
- **User Authentication and Session Management**:
  - Users can register (`/register`), log in (`/login`), and log out (`/logout`).
  - Secure access to features like buying, selling, and viewing portfolios using the `@login_required` decorator.
  - Sessions managed with Flask-Session and cookies.

- **Stock Management**:
  - Look up stock quotes (`/quote`), view stock details (`/stock_detail`), and buy (`/buy`) or sell (`/sell`) shares.
  - Stock data fetched via APIs (`lookup` and `lookup_detail`).
  - Home page (`/`) shows current stocks, their value, and total portfolio worth.
  - Transaction history (`/history`) logs all operations for user review.

- **Password Reset**:
  - Users can request a password reset link via email (`/reset_password_email`), generating a unique token and expiration time.
  - Reset link redirects to `/reset`, allowing users to set a new password after verifying the token.

- **Error Handling and Input Validation**:
  - Ensures valid email formats and positive integers for shares.
  - Handles errors gracefully with informative messages using the `apology` function.

- **Templating and Filters**:
  - Renders dynamic web pages with Jinja2 templates.
