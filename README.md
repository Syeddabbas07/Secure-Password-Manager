# Secure Password Manager

## Introduction

Secure Password Manager is a full-stack web application that allows users to securely store and manage their passwords through a modern web interface.

The application uses JWT authentication, BCrypt password hashing, and AES-GCM encryption to protect sensitive information. Each user has an isolated vault, ensuring that stored credentials can only be accessed by their owner.

This project was built to gain practical experience with backend development, secure software engineering, database design, REST APIs, and frontend development using FastAPI and JavaScript.

---

## Features

The application includes:

- User registration
- Secure login
- JWT authentication
- Password hashing with BCrypt
- AES-GCM password encryption
- Password vault
- Create, update and delete credentials
- Search stored passwords
- Password generator
- Account management
- Responsive frontend
- Automated backend testing

---

## Technologies

### Backend

- Python 3.11
- FastAPI
- SQLAlchemy
- SQLite

### Frontend

- HTML
- CSS
- JavaScript

### Security

- JWT
- BCrypt
- AES-GCM
- Cryptography
- Pydantic

### Testing

- Pytest
- FastAPI TestClient

---

## Project Structure

```text
secure-password-manager/
│
├── app/
│   ├── routers/
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   ├── security.py
│   ├── encryption.py
│   ├── dependencies.py
│   ├── password_generator.py
│   ├── config.py
│   ├── main.py
│   └── tests/
│
├── frontend/
│   ├── index.html
│   ├── dashboard.html
│   └── static/
│
├── requirements.txt
├── README.md
└── .env.example
```

---

## Security

User passwords are never stored in plaintext.

Account passwords are hashed using BCrypt before being stored in the database.

Passwords saved inside the vault are encrypted using AES-GCM with a unique nonce for every credential before being written to the database.

Authentication is handled using JWT access tokens, while authorization ensures users can only access their own vault entries.

---

## Testing

The project includes automated tests covering:

- User registration
- Login
- JWT authentication
- Protected endpoints
- Vault CRUD operations
- Search
- Password encryption
- Password generation
- User authorization

Run the test suite with:

```bash
python -m pytest -v
```

---

## Installation

Clone the repository.

```bash
git clone https://github.com/Syeddabbas07/Secure-Password-Manager.git
```

Move into the project directory.

```bash
cd Secure-Password-Manager
```

Create a virtual environment.

```bash
python -m venv .venv
```

Activate the virtual environment.

Windows

```bash
.venv\Scripts\activate
```

Linux/macOS

```bash
source .venv/bin/activate
```

Install the required packages.

```bash
pip install -r requirements.txt
```

---

## Configuration

Create a `.env` file in the project root.

Example:

```env
SECRET_KEY=your-secret-key
ENCRYPTION_KEY=your-base64-encryption-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

---

## Running the Application

Start the FastAPI development server.

```bash
uvicorn app.main:app --reload
```

Open the application:

```
http://127.0.0.1:8000/
```

Interactive API documentation:

```
http://127.0.0.1:8000/docs
```

Alternative API documentation:

```
http://127.0.0.1:8000/redoc
```

---

## API Endpoints

### Authentication

```
POST   /register
POST   /login
GET    /me
PATCH  /account/password
DELETE /account
```

### Vault

```
POST   /vault
GET    /vault
GET    /vault/{id}
PATCH  /vault/{id}
DELETE /vault/{id}
```

### Password Generator

```
POST   /generate-password
```

---

## Design

The application follows a layered architecture.

```text
Browser
      │
      ▼
HTML / CSS / JavaScript
      │
      ▼
FastAPI
      │
      ▼
Authentication & Authorization
      │
      ▼
SQLAlchemy ORM
      │
      ▼
SQLite Database
```

The frontend communicates with the backend using authenticated REST API requests. Sensitive passwords are encrypted before storage and decrypted only for authenticated users who own the corresponding vault entry.

---

## Future Improvements

Possible future enhancements include:

- Docker support
- PostgreSQL support
- Two-factor authentication
- Refresh tokens
- Audit logging
- Password import and export
- Cloud deployment

---

## License

This project was developed for educational and portfolio purposes.
