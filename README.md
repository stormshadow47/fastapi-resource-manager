# fastapi-resource-manager

A simple resource manager built using FastAPI and Streamlit frontend with SQLAlchemy for async database operations and JWT authentication for the endpoints.

## Features

- User registration & login (JWT-based)
- Add, view, update, and delete books
- Streamlit frontend with sidebar auth controls
- Protected backend API with bearer token auth
- Async-ready SQLAlchemy integration

## Setup Instructions

### 1. Clone the Repo

```bash
git clone https://github.com/stormshadow47/fastapi-resource-manager.git
cd fastapi-resource-manager
```

## 2.  Create venv
```
# macOS
python3 -m venv venv
source venv/bin/activate

# On Windows
python -m venv venv
venv\Scripts\activate or
venv\Scripts\activate.ps1
```

## 3. Install Dependencies
```
pip install -r requirements.txt
```

## 4. Run the Fastapi app
```
uvicorn app.main:app --reload
```

## 5. Run the streamlit frontend
```
cd frontend
streamlit run streamlit_app.py
```



