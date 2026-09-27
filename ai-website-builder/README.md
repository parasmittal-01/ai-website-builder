# 🧠 AI Website Builder

**AI Website Builder** is a full-stack project built using **FastAPI** and **OpenAI API**, allowing users to generate complete multi-page websites (HTML, CSS, JS) automatically from text descriptions.
It also includes user authentication (signup/login), task management, and automatic project zipping and previewing.

---

## 🖼️ Screenshots

### 🔹 Main Pages

| Main Project Genarator Page |
| --------------------------- |
| ![Home](images/main.png)      |

### 🔹 Genarated Pages

| Home                   | About                    | Login                    | Signup                     |
| ---------------------- | ------------------------ | ------------------------ | -------------------------- |
| ![Home](images/home.png) | ![About](images/about.png) | ![Login](images/login.png) | ![Signup](images/signup.png) |

### 🔹 Game Page

| Tasks Page             |
| ---------------------- |
| ![Game](images/game.png) |

---


## ▶️ Demo Video

[![Watch the demo](https://img.youtube.com/vi/-OBv_LPE2B0/0.jpg)](https://youtu.be/-OBv_LPE2B0)

> 🎥 *Click the thumbnail above to watch the full walkthrough on YouTube.*

---



## 🚀 Features

- 🔥 Generate full multi-page websites using AI (OpenAI GPT models)
- 📁 Automatic project folder creation with unique IDs
- 🧾 Each project includes:
  - `index.html`
  - `login.html`
  - `signup.html`
  - `about.html`
  - `tasks.html`
- ⚡ Built-in base `<base>` tag injection for relative link handling
- 📦 Automatic ZIP download for each generated project
- 👤 User and task endpoints backed by PostgreSQL
- 📝 Task management for logged-in users
- 🌍 Frontend served via local folder preview
- 🔒 Secure JSON parsing for generated output

---

## 🧰 Tech Stack

**Backend:**

- FastAPI
- SQLAlchemy
- PostgreSQL (SQLAlchemy + pg8000)
- OpenAI API
- Python 3.10+

**Frontend:**

- React UI for entering descriptions and viewing generated projects
- Generated websites use HTML, CSS, and JavaScript; TailwindCSS is available by CDN

---

## 📦 Installation & Setup

### 1. Install PostgreSQL

Install PostgreSQL 16 or later and start its Windows service. In pgAdmin, connect to the server, open the Query Tool, and create the app database:

```sql
CREATE DATABASE ai_website_builder;
```

### 2. Configure the application

From the project root, copy the example environment file and edit `.env` with your PostgreSQL username/password and a newly generated OpenAI API key:

```powershell
Copy-Item .env.example .env
```

Do not commit `.env`. If your PostgreSQL password contains URL-special characters, URL-encode them in `DATABASE_URL`.

### 3. Install and run the backend

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
uvicorn app:app --reload --app-dir backend
```

The API starts at `http://127.0.0.1:8000`. Keep this terminal running.

### 4. Install and run the frontend

In a second PowerShell terminal:

```powershell
Set-Location frontend
npm install
npm start
```

Open `http://localhost:3000`. Describe a site, generate it, then use the preview or ZIP download controls.

---

## 🧠 API Endpoints

| Endpoint                                        | Method | Description                        |
| ----------------------------------------------- | ------ | ---------------------------------- |
| `/generate/`                                  | POST   | Generate a new AI website project  |
| `/download/{project_id}.zip`                  | GET    | Download the generated project ZIP |
| `/api/signup`                                 | POST   | Create a new user                  |
| `/api/login`                                  | POST   | Login user                         |
| `/api/tasks/{username}`                       | GET    | Fetch user tasks                   |
| `/api/tasks`                                  | POST   | Add new task                       |
| `/api/tasks/{task_id}`                        | DELETE | Delete a task                      |
| `/generated_projects/{project_id}/{file_path}` | GET    | Serve generated HTML/CSS/JS and nested assets |

---

## 🧩 Example: Generate a Project

Send a request:

```bash
curl -X POST http://127.0.0.1:8000/generate/ \
  -H "Content-Type: application/json" \
  -d '{"description": "a portfolio website with about, login, and contact pages"}'
```

Response:

```json
{
  "project_id": "a1b2c3d4-e",
  "message": "Project generated successfully"
}
```

The React UI opens the preview automatically. It is also available at:

```
http://127.0.0.1:8000/generated_projects/a1b2c3d4-e/index.html
```

---

## 🗂 Project Structure

```
AI-WEBSITE-BUILDER/
├── backend/ # FastAPI backend and generated project files
├── frontend/ # React frontend (UI, components, pages)
├── images/ # App screenshots and assets
├── old-versions/ # Previous archived versions (zip files)
├── .env.example # Local configuration template
├── requirements.txt # Python dependencies
└── README.md # Project documentation
```

---

## ⚙️ Environment Variables

```
DATABASE_URL=postgresql+pg8000://postgres:your_password@localhost:5432/ai_website_builder
OPENAI_API_KEY=your-openai-api-key
```

The backend creates the `users` and `tasks` tables automatically after connecting. The old `backend/data.db` SQLite file is not used or migrated; it currently contains no rows.

---

## 📦 Packaging & Version Control

Initialize git:

```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/Subrata0Ghosh/ai-website-builder.git
git push -u origin main
```

---

## 🧪 Troubleshooting

| Issue                         | Possible Fix                                                                  |
| ----------------------------- | ----------------------------------------------------------------------------- |
| Backend cannot start | Check that PostgreSQL is running, the database exists, and `DATABASE_URL` in `.env` is correct |
| Website generation fails | Check that `OPENAI_API_KEY` is set and the key has API access |
| JSON parsing error            | The AI output may contain markdown or invalid escape characters               |
| Links not working             | Ensure `<base>`tag injection logic is present                               |
| `.zip`file missing          | Check `generated_projects/`folder permissions                               |

---

## 💡 Future Enhancements

* Add frontend React interface
* Integrate preview in a live iframe
* Support for exporting to GitHub Pages
* Optional themes (dark/light)
* Database-based project history

---

## 🪄 License

This project is released under the  **MIT License** .

You can freely use, modify, and distribute this software.
