# RootsLink

**A Continuous Global Talent Retention Network and Research Observatory**

RootsLink connects underserved students with mentors, scholarships, and locally-grounded opportunity pathways — so global ambition doesn't require permanent departure.

---

## MVP Architecture

```
rootslink/
├── backend/
│   ├── main.py                    # FastAPI app entry point
│   ├── config.py                  # Algorithm weights + settings
│   ├── database.py                # SQLAlchemy + SQLite setup
│   ├── models/                    # DB models: User, Mentor, Opportunity, Interaction
│   ├── schemas/                   # Pydantic v2 schemas
│   ├── routers/                   # API routes: users, mentors, opportunities, matching
│   ├── algorithms/
│   │   ├── opportunity_fit.py     # Algorithm 1: OpportunityFit
│   │   ├── mentor_match.py        # Algorithm 2: MentorMatch
│   │   ├── brain_drain_risk.py    # Algorithm 3: BrainDrainRisk
│   │   └── retention_priority.py  # Algorithm 4: RetentionPriority
│   └── services/
│       └── matching_service.py    # Full recommendation pipeline
├── frontend/
│   ├── index.html                 # Homepage + impact stats
│   ├── register-student.html      # Student registration form
│   ├── register-mentor.html       # Mentor registration form
│   ├── opportunities.html         # Browseable opportunity database
│   ├── dashboard.html             # Personalised match dashboard
│   └── styles.css                 # Global CSS
└── data/
    └── seed.py                    # Sample mentors, opportunities, test user
```

---

## The 4 Algorithms

| Algorithm | Formula | Purpose |
|---|---|---|
| **OpportunityFit** | `w1·S + w2·I + w3·E + w4·L + w5·A + w6·B + w7·T` | How well an opportunity matches a user |
| **MentorMatch** | `a1·F + a2·G + a3·R + a4·Lang + a5·C + a6·Q + a7·X` | How well a mentor fits a user |
| **BrainDrainRisk** | `b1·P + b2·M + b3·F + b4·D + b5·H + b6·C + b7·O − b8·V` | Structural risk of losing a user to brain drain |
| **RetentionPriority** | `c1·G + c2·R + c3·K + c4·N + c5·C + c6·L + c7·Y` | Prioritise opportunities that keep users locally connected |

**Final Recommendation Score:**
```
FinalScore = α·OpportunityFit + γ·RetentionPriority
```

All weights are configurable in `backend/config.py` or via `.env`.

---

## Quick Start

### 1. Backend

```bash
cd rootslink
python -m venv venv && source venv/bin/activate
pip install -r backend/requirements.txt

# Seed the database
python -m data.seed

# Run the API
uvicorn backend.main:app --reload
```

API available at: `http://localhost:8000`  
Interactive docs: `http://localhost:8000/docs`

### 2. Frontend

Open `frontend/index.html` in a browser (no build step needed for MVP).

---

## API Endpoints

| Method | Path | Description |
|---|---|---|
| `GET` | `/health` | Health check |
| `GET` | `/info` | Version + algorithm list |
| `POST` | `/users/` | Register student |
| `GET` | `/users/{id}` | Get student profile |
| `POST` | `/mentors/` | Register mentor |
| `GET` | `/mentors/` | List mentors |
| `POST` | `/opportunities/` | Add opportunity |
| `GET` | `/opportunities/` | Browse opportunities |
| `GET` | `/match/{user_id}` | **Full recommendation pipeline** |
| `POST` | `/match/interaction` | Log interaction (feedback loop) |
| `GET` | `/match/stats/overview` | Platform impact stats |

---

## MVP vs Future

### MVP (this repo)
- Rule-based filtering
- Weighted scoring
- Keyword/tag matching
- SQLite database
- Vanilla HTML/CSS/JS frontend

### Future Versions
- Graph-based recommendation (Neo4j)
- NLP for opportunity parsing
- Adaptive user embeddings
- Survival analysis for dropout/retention prediction
- Causal inference on intervention effectiveness
- PostgreSQL + React frontend
- Authentication + user sessions

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.11+, FastAPI, SQLAlchemy |
| Database | SQLite (MVP) → PostgreSQL |
| Schemas | Pydantic v2 |
| Logging | Loguru |
| Frontend | HTML/CSS/JS (MVP) → React |

---

## Project Lead

**Dayeon Kang** — MICA International School, Seongnam, Korea  
dayeon603@gmail.com

---

## License

MIT
