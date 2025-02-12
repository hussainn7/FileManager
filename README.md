# File Exchange CMS

A content management system for file sharing with user management, file categorization, and token-based purchases.

## Features

- User authentication with email verification
- File upload and storage on Yandex.Disk
- Token-based payment system using YooKassa
- File categorization and search
- User roles (Admin, Moderator, User)
- Admin dashboard for user and content management

## Requirements

- Python 3.8+
- Flask and its extensions
- YooKassa API credentials
- Yandex.Disk API token
- SMTP server for email notifications

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd file-exchange-cms
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file with your configuration:
```
FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=your-super-secret-key
DATABASE_URL=sqlite:///cms.db

# YooKassa credentials
YOOKASSA_SHOP_ID=your-shop-id
YOOKASSA_SECRET_KEY=your-secret-key

# Yandex.Disk API
YADISK_TOKEN=your-yadisk-token

# Mail settings
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-email-password
```

5. Initialize the database:
```bash
flask db init
flask db migrate
flask db upgrade
```

6. Run the application:
```bash
flask run
```

## Usage

1. Register an account and verify your email
2. Upload files and set their prices in tokens
3. Purchase tokens using YooKassa
4. Browse and purchase files from other users
5. Admin users can manage categories and user roles

## API Endpoints

### Authentication
- POST /register - User registration
- POST /login - User login
- GET /logout - User logout
- POST /reset-password - Password reset request

### Files
- GET /browse - Browse all files
- POST /upload - Upload a new file
- GET /download/<file_id> - Download a file
- GET /my-files - View user's files

### Payments
- GET /balance - View token balance
- POST /deposit - Add tokens via YooKassa
- GET /payment/callback - Payment callback handler

### Admin
- GET /admin/dashboard - Admin dashboard
- GET /admin/users - User management
- POST /admin/categories - Category management

## License

This project is licensed under the MIT License - see the LICENSE file for details. 