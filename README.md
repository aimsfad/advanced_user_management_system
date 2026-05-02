# Advanced User Management System

A Python GUI project for managing users with MongoDB NoSQL database storage. The application separates the main CRUD tasks into clear tabs: Add, Display, Search, Update, and Delete.

## Features

- Add new users through a GUI form.
- Display all users in a structured table.
- Search users in a separated Search tab by choosing a specific field:
  - All Fields
  - First Name
  - Last Name
  - Birth Date
  - Birth Place
  - Phone Number
- Update selected users in a separated Update tab.
- Delete selected users with confirmation in a separated Delete tab.
- Validate inputs before saving:
  - No empty fields
  - Birth date format must be `YYYY-MM-DD`
  - Phone number must be unique
- Handle MongoDB connection and database errors with user-friendly messages.

## Technologies

- Python
- Streamlit
- MongoDB
- PyMongo
- Pandas
- Git / GitHub

## Project Structure

```text
advanced_user_management_system/
├── app.py
├── database.py
├── validation.py
├── requirements.txt
├── .env.example
├── .gitignore
├── student_info.txt
├── github_link.txt
└── screen_recording_checklist.md
```

## Installation

### 1. Clone the repository

```bash
git clone YOUR_GITHUB_REPOSITORY_LINK
cd advanced_user_management_system
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate it:

```bash
# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure MongoDB

Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

For local MongoDB, keep:

```env
MONGO_URI=mongodb://localhost:27017/
DB_NAME=user_management_db
COLLECTION_NAME=users
```

For MongoDB Atlas, replace `MONGO_URI` with your Atlas connection string.

### 5. Run the app

```bash
streamlit run app.py
```

The application opens in your browser.

## MongoDB Notes

The application stores users in the `users` collection. Each user document contains:

```json
{
  "first_name": "Ali",
  "last_name": "Benali",
  "birth_date": "2002-04-18",
  "birth_place": "Oum El Bouaghi",
  "phone_number": "+213555123456"
}
```

The app automatically creates a unique index on `phone_number`.

## Suggested Git Workflow

```bash
git init
git add .
git commit -m "Initial project structure"

git branch develop
git checkout develop

git checkout -b feature/database
git add database.py validation.py
git commit -m "Add MongoDB database integration and validation"

git checkout develop
git merge feature/database

git checkout -b feature/gui
git add app.py
git commit -m "Build Streamlit GUI for CRUD operations"

git checkout develop
git merge feature/gui

git checkout main
git merge develop
```

Then create a public GitHub repository and push:

```bash
git remote add origin YOUR_GITHUB_REPOSITORY_LINK
git push -u origin main
git push origin develop
```

## Submission Checklist

Upload the following files to Google Drive and share the folder with:

```text
salim.zerrougui@univ-oeb.dz
```

Required files:

1. `student_info.txt` containing the student's full name and major.
2. `github_link.txt` containing the public GitHub repository link.
3. Screen recording file `.MP4`, maximum 10 minutes.

After sharing the Google Drive folder, send an email to confirm the sharing.
