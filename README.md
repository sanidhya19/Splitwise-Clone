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

2. **Set up a virtual environment**:

```bash
python -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
```

3. **Install dependencies**:

```bash
pip install -r requirements.txt
```

4. **Apply migrations**:

```bash
python manage.py migrate
```

5. **Run the development server**:

```bash
python manage.py runserver
```

Visit http://127.0.0.1:8000/ in your browser to access the application.

---

## Usage

- **User Registration**: Navigate to the registration page to create a new account.

- **Create Group**: After logging in, create a new group by providing a name and description.

- **Add Expense**: Within a group, add expenses by specifying the amount, category, and participants.

- **View Balances**: Check the balance page to see how much each member owes or is owed.

- **Settle Debts**: Use the settlement suggestions to clear balances among members.

---

## Contributing

1. Contributions are welcome! To contribute:

2. Fork the repository.

3. Create a new branch
```bash
git checkout -b feature-name
```

4. Make your changes.

5. Commit your changes

```bash
git commit -am 'Add new feature'
```

6. Push to the branch

```bash  
git push origin feature-name
```

7. Create a new Pull Request.
