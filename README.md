# Splitwise Clone

## Overview

The Splitwise Clone is a web application designed to help users manage and split expenses among groups, such as roommates, friends, or colleagues.  
It allows users to track shared expenses, calculate balances, and settle debts, making group financial management easier and more transparent.

---

## Features

- **User Authentication**: Secure login and registration system.
- **Group Management**: Create and manage groups for different events or shared expenses.
- **Expense Tracking**: Add and categorize expenses, specifying who paid and how the cost should be split.
- **Balance Calculation**: Automatically calculates each member's balance and suggests settlements.
- **Responsive Design**: Optimized for both desktop and mobile devices.

---

## Technologies Used

- **Frontend**: HTML, CSS, JavaScript, React.js
- **Backend**: Python, Django
- **Database**: SQLite
- **Authentication**: Django's built-in authentication system

---

## Installation

### Prerequisites

- Python 3.x  
- pip (Python package installer)  
- git  

### Steps

1. **Clone the repository**

```bash
git clone https://github.com/sanidhya19/Splitwise-Clone.git
cd Splitwise-Clone
```

2. **Set up a virtual environment:**

python -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`


Install dependencies:

pip install -r requirements.txt


Apply migrations:

python manage.py migrate


Run the development server:

python manage.py runserver


Visit http://127.0.0.1:8000/ in your browser to access the application.


**Usage**

User Registration: Navigate to the registration page to create a new account.

Create Group: After logging in, create a new group by providing a name and description.

Add Expense: Within a group, add expenses by specifying the amount, category, and participants.

View Balances: Check the balance page to see how much each member owes or is owed.

Settle Debts: Use the settlement suggestions to clear balances among members.



**Contributing**

Contributions are welcome! To contribute:

Fork the repository.

Create a new branch (git checkout -b feature-name).

Make your changes.

Commit your changes (git commit -am 'Add new feature').

Push to the branch (git push origin feature-name).

Create a new Pull Request.
