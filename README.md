# 🔐 Secure Password Manager

A secure web-based password manager built with **FastAPI**, **SQLAlchemy**, and **SQLite**. The application allows users to securely store, manage, and retrieve passwords using modern authentication and encryption techniques.

This project was built to strengthen backend development skills while following secure software engineering principles and cybersecurity best practices.

---

# 👨‍💻 Author

**Syed Abbas Shah**

GitHub: https://github.com/Syeddabbas07

---

# 🚀 Features

### Authentication

- User Registration
- Secure Login
- JWT Authentication
- Protected API Endpoints
- Password Change
- Secure Account Deletion

### Password Security

- BCrypt Password Hashing
- AES-GCM Password Encryption
- Secure Key Management using Environment Variables
- Unique Nonce for Every Stored Password

### Vault

- Create Password Entries
- View Stored Passwords
- Update Existing Passwords
- Delete Password Entries
- Search Vault
- User Isolation (Users can only access their own data)

### Password Generator

- Cryptographically Secure Password Generation
- Configurable Password Length
- Optional Uppercase
- Optional Lowercase
- Optional Numbers
- Optional Symbols

### Security

- JWT Access Tokens
- Protected Routes
- Authentication Middleware
- Authorization Checks
- Input Validation using Pydantic
- Secure Database Transactions

### Testing

- Automated API Testing
- Authentication Tests
- Vault Security Tests
- Cross-User Authorization Tests
- Password Encryption Tests

---

# 🛠 Tech Stack

### Backend

- Python 3.11
- FastAPI
- SQLAlchemy ORM
- SQLite

### Authentication

- JWT (python-jose)
- Passlib
- BCrypt

### Encryption

- AES-GCM
- Cryptography Library

### Validation

- Pydantic

### Testing

- Pytest
- FastAPI TestClient

### Version Control

- Git
- GitHub

---

# 📂 Project Structure

```text
secure-password-manager/
│
├── app/
│   ├── routers/
│   │   ├── auth.py
│   │   ├── vault.py
│   │   └── generator.py
│   │
│   ├── config.py
│   ├── database.py
│   ├── dependencies.py
│   ├── encryption.py
│   ├── main.py
│   ├── models.py
│   ├── password_generator.py
│   ├── schemas.py
│   └── security.py
│
├── tests/
│   ├── test_auth.py
│   ├── test_generator.py
│   └── test_vault.py
│
├── requirements.txt
├── README.md
├── .gitignore
└── .env
```

---

# 🔒 Security Features

This project was designed with security in mind.

## Password Hashing

User passwords are **never stored in plaintext**.

Passwords are hashed using **BCrypt** before being stored in the database.

---

## Vault Encryption

Stored passwords are encrypted using:

- AES-GCM
- Unique Nonce
- Authentication Tag
- Base64 Encoding

Each stored password is encrypted before being written to the database.

---

## Authentication

Authentication is implemented using:

- JWT Access Tokens
- Bearer Authentication
- Protected Endpoints

Only authenticated users can access password data.

---

## Authorization

Every vault operation verifies ownership before allowing access.

Users cannot:

- Read another user's passwords
- Update another user's passwords
- Delete another user's passwords

---

# 🧪 Automated Testing

The project includes automated backend testing using **Pytest**.

Current tests cover:

- User Registration
- Duplicate Registration
- Login
- Invalid Login
- JWT Authentication
- Protected Routes
- Password Encryption
- Vault CRUD
- Search
- Cross User Isolation
- Password Generator
- Account Security

Run all tests:

```bash
python -m pytest -v
```

---

# ⚙ Installation

Clone the repository

```bash
git clone https://github.com/Syeddabbas07/Secure-Password-Manager.git
```

Navigate into the project

```bash
cd Secure-Password-Manager
```

Create a virtual environment

```bash
python -m venv .venv
```

Activate the virtual environment

Windows

```bash
.venv\Scripts\activate
```

Install dependencies

```bash
pip install -r requirements.txt
```

---

# 🔑 Environment Variables

Create a `.env` file in the project root.

Example:

```env
SECRET_KEY=your-secret-key
ENCRYPTION_KEY=your-base64-encryption-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

---

# ▶ Running the Application

Start the FastAPI server

```bash
uvicorn app.main:app --reload
```

API Documentation

```
http://127.0.0.1:8000/docs
```

Alternative Documentation

```
http://127.0.0.1:8000/redoc
```

---

# 📖 API Overview

## Authentication

```
POST /register
POST /login
GET  /me
PATCH /account/password
DELETE /account
```

## Vault

```
POST   /vault
GET    /vault
GET    /vault/{id}
PATCH  /vault/{id}
DELETE /vault/{id}
```

## Password Generator

```
POST /generate-password
```

---

# 🎯 Learning Objectives

This project was developed to gain practical experience with:

- Backend API Development
- FastAPI
- SQLAlchemy ORM
- REST API Design
- Authentication
- Authorization
- Cryptography
- Secure Software Development
- API Testing
- Software Architecture

---

# 🚧 Future Improvements

Planned enhancements include:

- Responsive Frontend
- Docker Support
- PostgreSQL Support
- Refresh Tokens
- Password Strength Meter
- Two-Factor Authentication (2FA)
- Password History
- Audit Logs
- Deployment to Cloud

---

# 📸 Screenshots

*(Add screenshots of your application here once the frontend is complete.)*

---

# 📄 License

This project is intended for educational and portfolio purposes.

---

# ⭐ Acknowledgements

This project was built as part of my backend development and cybersecurity learning journey, focusing on secure software engineering practices, authentication, encryption, and practical API development.
