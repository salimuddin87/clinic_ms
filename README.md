## Clinic Management System
I built a complete, object-oriented, multi-file Clinic Management System that uses Python 3.13 + FastAPI + SQLAlchemy (SQLite for demo) + Redis for caching & session storage, and implements OAuth2 (password grant) + JWT + RBAC. The design uses OOP for service layers (each module is a class), keeps caching & session management centralized, supports pagination (top 10), and uses Python logging for info/warn/error.

You can copy the files into a `clinic-oop/` folder and run it. I kept the demo pragmatic (SQLite + synchronous SQLAlchemy) so you can run it locally. Replace DB and secret values for production.

```ignorelang
clinic-oop/
├─ app/
│  ├─ __init__.py
│  ├─ main.py
│  ├─ database.py
│  ├─ models.py
│  ├─ schemas.py
│  ├─ cache.py
│  ├─ auth.py
│  ├─ logger_config.py
│  ├─ services/
│  │   ├─ __init__.py
│  │   ├─ base_service.py
│  │   ├─ patient_service.py
│  │   ├─ appointment_service.py
│  │   ├─ medicine_service.py
│  │   └─ user_service.py
│  └─ routers/
│      ├─ __init__.py
│      ├─ patients.py
│      ├─ appointments.py
│      ├─ medicines.py
│      ├─ users.py
│      └─ reports.py
├─ requirements.txt
└─ README.md
```

### How this OOP design works (short)
* Each service is a class (e.g., PatientService) encapsulating DB operations and business logic (OOP).
* cache.py provides a Cache class to get/set JSON strings in Redis for sessions, patient pages, and medicine searches.
* auth.py handles OAuth2 password flow, JWT generation/verification, password hashing (passlib), and RBAC helper require_roles.
* Routers depend on service class instances (created in main.py) — keeps controllers thin.
* Pagination: endpoints accept page param; default page size is 10; pages >1 use offset logic.
* Logging: logger_config.py exposes get_logger(); services & routers log info/warn/error.
* Automated reminders: included as a background task stub demonstrating scheduling with FastAPI BackgroundTasks; you can plug in an SMS/email provider.
* Session storage: JWT token + Redis session entry (optional).

### Start Redis (Optional, recommended for caching/sessions)
```
docker run -p 6379:6379 -d redis:7
```

### Run the app
```ignorelang
uvicorn app.main:app --reload --port 8000
# docs: http://127.0.0.1:8000/docs
```

### Run tests
```ignorelang
pytest -q
```

### Quick Usage examples (Curl)
```bash
# create a user (doctor)
curl -X POST "http://127.0.0.1:8000/users/create" -H "Content-Type: application/json" \
 -d '{"username":"dr_joe","full_name":"Dr Joe","role":"doctor","password":"secret"}'
```

```bash
# get the access_token from response
curl -X POST "http://127.0.0.1:8000/users/token" -d "username=dr_joe&password=secret"
```

```bash
# use the access_token to create a patient
TOKEN=<access_token>
curl -X POST "http://127.0.0.1:8000/patients" \
 -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
 -d '{"first_name":"Asha","last_name":"K","phone":"999888777"}'
```

```bash
# search medicines (pagination supported)
curl -H "Authorization: Bearer $TOKEN" "http://127.0.0.1:8000/medicines?q=para&page=1"
```

### Notes & next steps
* This implementation uses synchronous SQLAlchemy with SQLite for demo. For production, switch to PostgreSQL + Alembic + connection pooling.
* The OOP design is visible in services (each Service class encapsulates operations). You can further encapsulate caching/notification inside services.
* OAuth2 here is password flow with JWT. You may add refresh tokens and token revocation logic (via Redis).
* Automated reminders: I provided a background task stub; for real scheduled reminders use Celery/Redis or APScheduler.
* Tests: I didn't include pytest files this time — if you want, I can add a test folder with pytest fixtures that override the DB session and provide isolated in-memory DB per test.
* Security: Put CLINIC_SECRET in environment variables and enforce HTTPS in production.







