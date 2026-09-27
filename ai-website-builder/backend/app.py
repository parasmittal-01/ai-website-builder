import json
import mimetypes
import os
import re
import uuid
import zipfile
from pathlib import Path
from google import genai

from dotenv import load_dotenv
from fastapi import FastAPI, Form, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from sqlalchemy import Column, Integer, String, Text, create_engine
from sqlalchemy.engine import make_url
from sqlalchemy.orm import declarative_base, sessionmaker

PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is missing. Configure it in the project-root .env file.")

database_url = make_url(DATABASE_URL)
if database_url.drivername in {"postgresql", "postgresql+psycopg", "postgresql+psycopg2"}:
    database_url = database_url.set(drivername="postgresql+pg8000")

engine = create_engine(database_url, pool_pre_ping=True)
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True)
    password = Column(String)

class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String)
    content = Column(Text)

Base.metadata.create_all(bind=engine)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)



# Initialize app
app = FastAPI()

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Directory for generated projects
GENERATED_DIR = Path(__file__).resolve().parent / "generated_projects"
GENERATED_DIR.mkdir(parents=True, exist_ok=True)

@app.post("/generate/")
async def generate_project(request: Request):
    """Generate a project folder with index.html + preview"""
    try:
        data = await request.json()
        description = data.get("description", "")
        if not isinstance(description, str):
            description = ""
        description = description.strip()

        if not description:
            return JSONResponse({"error": "Missing project description"}, status_code=400)

        api_key = os.getenv("GEMINI_API_KEY") or os.getenv("API_KEY")
        if not api_key:
            return JSONResponse({"error": "GEMINI_API_KEY is missing from the project-root .env file."}, status_code=503)
        client = genai.Client(api_key=api_key)

        # Create unique folder
        project_id = str(uuid.uuid4())[:10]
        project_folder = GENERATED_DIR / project_id
        project_folder.mkdir(parents=True, exist_ok=True)
        
        print(f"Generated pages for {project_id}:")
        for f in project_folder.iterdir():
            print(" -", f.name)
        
        
       
               # ---- AI Generation (JSON output enforced) ----
        system_prompt = """
        You are an expert full-stack web developer and a code-generation assistant.

        Your job: produce a multi-page website as a JSON object only. STRICT RULES:
        1) Output MUST be valid JSON and nothing else (no markdown, no explanation text).
        2) The top-level JSON must be an object with a key "files" that is an array of objects.
           Each file object must have: "path" (string, e.g. "index.html" or "assets/style.css")
           and "content" (string) containing the full file contents (HTML/CSS/JS).
        3) Include at least the following files (complete HTML with <!DOCTYPE html>):
           "index.html", "login.html", "signup.html", "about.html", "tasks.html".
        4) Use TailwindCSS from CDN where appropriate.
        5) Use relative links inside HTML (e.g., <a href="login.html">).
        6) Do NOT include any keys other than "files" at top-level.
        7) Keep JSON compact (but valid). If content contains characters that require escaping, ensure JSON remains valid.
        """

        user_prompt = f"""
        Build a project based on this description: {json.dumps(description)}

        Return a JSON object that matches the rules above. Example shape:
        {{
          "files": [
            {{ "path": "index.html", "content": "<!DOCTYPE html>... entire html ..." }},
            {{ "path": "login.html", "content": "<!DOCTYPE html>... entire html ..." }},
            ...
          ]
        }}
        """

        # Request JSON from Gemini so generated files can be parsed reliably.
        response = client.models.generate_content(
            model="gemma-4-26b-a4b-it",
            contents=f"{system_prompt}\n\n{user_prompt}",
            config={"response_mime_type": "application/json"},
        )

        raw = (response.text or "").strip()
        if not raw:
            raise RuntimeError("The model returned an empty response.")

        # ---- Robust JSON extraction & parsing ----
        def extract_json(s: str):
            """
            Try to parse JSON directly. If it fails, attempt to find the largest JSON object substring.
            Returns parsed object or raises ValueError.
            """
            try:
                return json.loads(s)
            except Exception:
                # attempt to locate a {...} block with balanced braces (simple heuristic)
                # find the first '{' and last '}' and try to load progressively
                first = s.find("{")
                last = s.rfind("}")
                if first == -1 or last == -1 or last <= first:
                    raise ValueError("No JSON object found in model output.")
                candidate = s[first:last+1]
                # attempt incremental trimming of trailing invalid chars
                while candidate:
                    try:
                        return json.loads(candidate)
                    except Exception:
                        # chop off a small tail and try again
                        candidate = candidate[:-1]
                raise ValueError("Failed to extract valid JSON from model output.")

        try:
            parsed = extract_json(raw)
        except ValueError as e:
            # helpful debug info in logs and return an error to client
            print("MODEL OUTPUT (preview):", raw[:1000])
            raise RuntimeError("Failed to parse JSON from model output: " + str(e))

        # Validate structure
        if not isinstance(parsed, dict) or "files" not in parsed or not isinstance(parsed["files"], list):
            print("Parsed JSON doesn't contain expected 'files' array. Preview:", str(parsed)[:1000])
            raise RuntimeError("Model output JSON must contain a 'files' array.")

        # Write files to project folder
        for fileobj in parsed["files"]:
            if not isinstance(fileobj, dict):
                continue
            rel_path = fileobj.get("path")
            content = fileobj.get("content")
            if not isinstance(rel_path, str) or not isinstance(content, str):
                continue
            rel_path = rel_path.strip().replace("\\", "/")
            if not rel_path:
                continue
            target = (project_folder / rel_path).resolve()
            try:
                target.relative_to(project_folder.resolve())
            except ValueError:
                continue
            target.parent.mkdir(parents=True, exist_ok=True)
            # Inject base tag into HTML files so relative links work in iframe/preview
            if target.suffix.lower() == ".html":
                # ensure the document has <head>
                base_tag = f'<base href="/generated_projects/{project_id}/" />'
                if "<head" in content.lower():
                    # replace first occurrence of <head.*?> with <head> + base_tag after tag
                    content = re.sub(r"(?i)(<head[^>]*>)", r"\1" + base_tag, content, count=1)
                else:
                    # prepend head with base
                    content = f"<head>{base_tag}</head>\n" + content
            target.write_text(content, encoding="utf-8")

        # Ensure index.html exists (fallback to first HTML file if not provided)
        if not (project_folder / "index.html").exists():
            # find first .html in folder
            for p in sorted(project_folder.rglob("*.html")):
                (project_folder / "index.html").write_text(p.read_text(), encoding="utf-8")
                break

       
       
    
       

        # Save index.html
        # html_file = project_folder / "index_preview.html"
        # html_file.write_text(html_code, encoding="utf-8")
        index_path = project_folder / "index.html"
        preview_path = project_folder / "index_preview.html"
        if index_path.exists():
            preview_path.write_text(index_path.read_text(), encoding="utf-8")

        # Zip project folder
        zip_path = GENERATED_DIR / f"{project_id}.zip"
        with zipfile.ZipFile(zip_path, "w") as zipf:
            for file in project_folder.rglob("*"):
                zipf.write(file, file.relative_to(GENERATED_DIR))

        return JSONResponse({
            "project_id": project_id,
            "message": "Project generated successfully"
        })

    except Exception as e:
        status_code = getattr(e, "code", 500)
        if not isinstance(status_code, int) or not 400 <= status_code <= 599:
            status_code = 500
        return JSONResponse({"error": str(e)}, status_code=status_code)
    
@app.post("/api/signup")
async def signup(username: str = Form(...), password: str = Form(...)):
    with SessionLocal() as db:
        if db.query(User).filter(User.username == username).first():
            return {"success": False, "message": "Username already exists"}
        new_user = User(username=username, password=password)
        db.add(new_user)
        db.commit()
    return {"success": True, "message": "Signup successful!"}


@app.post("/api/login")
async def login(username: str = Form(...), password: str = Form(...)):
    with SessionLocal() as db:
        user = db.query(User).filter(User.username == username, User.password == password).first()
    if user:
        return {"success": True, "message": "Login successful!"}
    else:
        return {"success": False, "message": "Invalid credentials"}


@app.get("/api/tasks/{username}")
async def get_tasks(username: str):
    with SessionLocal() as db:
        tasks = db.query(Task).filter(Task.username == username).all()
        return [{"id": task.id, "content": task.content} for task in tasks]


@app.post("/api/tasks")
async def add_task(username: str = Form(...), content: str = Form(...)):
    with SessionLocal() as db:
        task = Task(username=username, content=content)
        db.add(task)
        db.commit()
    return {"success": True, "message": "Task added"}


@app.delete("/api/tasks/{task_id}")
async def delete_task(task_id: int):
    with SessionLocal() as db:
        task = db.query(Task).filter(Task.id == task_id).first()
        if task:
            db.delete(task)
            db.commit()
    return {"success": True, "message": "Task deleted"}


@app.get("/download/{project_id}.zip")
async def download_zip(project_id: str):
    if not re.fullmatch(r"[0-9a-f]{8}-[0-9a-f]", project_id):
        return JSONResponse({"error": "File not found"}, status_code=404)
    zip_path = GENERATED_DIR / f"{project_id}.zip"
    if not zip_path.exists():
        return JSONResponse({"error": "File not found"}, status_code=404)
    return FileResponse(zip_path, media_type="application/zip", filename=f"{project_id}.zip")


@app.get("/generated_projects/{project_id}/{file_path:path}")
async def get_generated_file(project_id: str, file_path: str):
    """Serve any generated HTML or static asset from a project folder."""
    if not re.fullmatch(r"[0-9a-f]{8}-[0-9a-f]", project_id):
        return JSONResponse({"error": "File not found"}, status_code=404)
    project_folder = (GENERATED_DIR / project_id).resolve()
    target = (project_folder / file_path).resolve()
    try:
        target.relative_to(project_folder)
    except ValueError:
        return JSONResponse({"error": "File not found"}, status_code=404)
    if not target.is_file():
        return JSONResponse({"error": "File not found"}, status_code=404)
    media_type = mimetypes.guess_type(target.name)[0] or "application/octet-stream"
    return FileResponse(target, media_type=media_type)

