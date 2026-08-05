# Atlas Kids Media - AI-Native Children's Content Factory v2.0

> An autonomous AI pipeline that produces, edits, and publishes safe, educational children's content for Arab kids (ages 3-7) — now with multi-language support, analytics, storyboarding, and a full REST API.

## The Vision

Atlas Kids Media is an AI-native company built to create high-quality children's educational videos with minimal human intervention. From scriptwriting to YouTube publishing, every step is orchestrated by AI agents.

**Founder:** Omar
**CEO Engine:** Ramo (رامو) — AI orchestrator built on CrewAI + Gemini

## The 10 Atlas Characters

| # | Character | Name (Arabic) | Trait |
|---|-----------|---------------|-------|
| 1 | Squirrel | Sokkar (سكر) | Active and bouncy |
| 2 | Fox | Felix (فليكس) | Smart and fast |
| 3 | Rabbit | Bonnie (بوني) | Gentle and light |
| 4 | Bear | Barnaby (بارني) | Kind with a warm voice |
| 5 | Bird | Tweety (تويتي) | Sweet voice |
| 6 | Deer | Bambi (بامبي) | Loves flowers |
| 7 | Turtle | Torti (تورتي) | Slow but wise |
| 8 | Raccoon | Ricky (ريكي) | Playful and clean |
| 9 | Hedgehog | Henry (هنري) | Small and cute |
| 10 | Frog | Freddy (فريدي) | Welcoming and friendly |

## The Factory Pipeline (v2.0)

```
Config → Storyboard → Script → Safety Review → Voice → Motion Prompts →
Video Generation → Editing → Subtitles → Thumbnail → Metadata →
Translation → Safety Review → Publish → Analytics → Improvement Loop
```

### Phase 0: Config Manager (`config_manager.py`)
- YAML-based episode configuration
- Non-technical users can define episodes without code
- Auto-generates production plans with cost estimates
- Output: `configs/{id}.yaml`

### Phase 1: Storyboard Engine (`storyboard_engine.py`)
- Generates shot-by-shot visual storyboards from scripts
- Specifies camera angles, composition, lighting, transitions
- Creates image generation prompts for reference art
- Output: `episodes/{id}/storyboard/storyboard.md`

### Phase 2: Script Engine (`script_engine_v2.py`)
- CrewAI agent writes scene-by-scene scripts
- Educational focus: counting, colors, teamwork, shapes
- Output: `episodes/{id}/script/story_v2.md`

### Phase 3: Safety Engine (`safety_engine.py`)
- Advanced content moderation beyond basic QA
- Checks: violence, fear, stereotypes, cultural sensitivity, COPPA
- AI-powered review with structured PASS/FAIL report
- Output: `reports/safety/{id}_safety_report.md`

### Phase 4: Voice Engine (`voice_engine_v2.py`)
- Extracts dialogue from script
- Generates Arabic TTS via Google TTS (gTTS)
- Output: `episodes/{id}/voice_v2/line_001_SOKKAR.mp3`

### Phase 5: Motion Engine (`motion_engine.py`)
- Generates detailed text-to-video prompts
- Enforces visual consistency (magical green forest, Pixar style)
- Output: `episodes/{id}/video_v2/animation_prompts_v2.md`

### Phase 6: Video Engine (`video_engine.py`)
- Integrates with Fal.ai Veo 3 API
- Generates actual video clips from prompts
- Cost tracking per clip (~$0.50 per 5s clip)
- Retry system with exponential backoff

### Phase 7: Editor Engine (`editor_engine.py`)
- Assembles clips with moviepy
- Adds voice audio, background music, transitions
- Adds Arabic numeral text overlays
- Creates intro title card
- Output: `episodes/{id}/final/final_episode.mp4`

### Phase 8: Subtitle Engine (`subtitle_engine.py`)
- Auto-generates SRT subtitle files from scripts
- Supports OpenAI Whisper for auto-transcription
- Can burn subtitles directly into video
- Output: `episodes/{id}/final/subtitles.srt`

### Phase 9: Thumbnail Engine (`thumbnail_engine.py`)
- Generates YouTube-optimized thumbnail prompts
- Can integrate with DALL-E / Stable Diffusion
- Output: `episodes/{id}/final/thumbnail.png`

### Phase 10: Metadata Engine (`metadata_engine.py`)
- Generates SEO-optimized titles, descriptions, tags
- Arabic + English for maximum reach
- Output: `episodes/{id}/final/youtube_metadata.md`

### Phase 11: Translation Engine (`translation_engine.py`)
- Translates scripts and metadata to English, French, Spanish
- Preserves character names and educational intent
- Creates parallel episode folders: `{id}_en/`, `{id}_fr/`
- Output: `episodes/{id}_en/script/story_en.md`

### Phase 12: YouTube Publisher (`publisher/youtube_publisher.py`)
- OAuth2 authentication with YouTube Data API v3
- Uploads video with metadata
- Sets "Made for Kids" flag (COPPA compliance)
- Uploads custom thumbnail
- Supports scheduling

### Phase 13: Analytics Engine (`analytics_engine.py`)
- Pulls YouTube performance data (views, likes, comments)
- Generates improvement recommendations
- Tracks engagement rates and trends
- Feeds insights back into content creation
- Output: `reports/performance_report.json`

## Core Infrastructure

### Atlas Core (`atlas_core/`)
- **Database** (`db_setup.py`): SQLite with episodes, jobs, assets, analytics tables
- **Job Manager** (`job_manager.py`): Prevents duplicate work, tracks budget, handles failures
- **QA Gate** (`qa_gate.py`): Enforces consistency rules, budget limits, deduplication
- **Orchestrator** (`orchestrator.py`): Routes approved prompts to video engine
- **Asset Vault** (`asset_vault.py`): Catalogs reusable characters, voices, backgrounds
- **Status Dashboard** (`status.py`): CLI view of all episodes and jobs
- **RAMO Brain** (`RAMO_BRAIN.md`): CEO Engine's memory and state

### Resilience & Monitoring
- **Retry System** (`retry_system.py`): Exponential backoff for all API calls
- **Notification Engine** (`retry_system.py`): Slack + Email alerts for pipeline events
- **Safety Engine** (`safety_engine.py`): Advanced content moderation

### API Server (`api_server.py`)
- FastAPI REST API for remote pipeline control
- **API Key Authentication** (`auth.py`) — see Authentication section below
- Role-based access control: Admin vs Read-Only
- Rate limiting: 60 requests/minute per IP
- Endpoints: create episode, trigger pipeline, check status, publish, analytics
- Background task processing
- Auto-generated docs at `/docs`

### Web Dashboard (`dashboard/index.html`)
- Fully interactive HTML dashboard
- Real-time episode status tracking
- Budget visualization with progress bars
- Recent jobs monitor
- One-click pipeline execution
- System log console
- Export reports to JSON

## Episodes

### Episode 001: The Great Forest Picnic Journey - V2
- **Status**: Script, Voice, Motion Prompts, Thumbnail complete. Full pipeline ready.
- **Educational Goal**: Counting from 1 to 10 in Arabic
- **Duration**: ~60 seconds
- **Scenes**: 11 (10 counting scenes + finale)
- **Thumbnail**: AI-generated and ready

### Episode 002: The Ocean Adventure
- **Status**: Concept approved, script engine ready
- **Educational Goal**: Colors in Arabic + Ocean conservation
- **Setting**: Magical underwater kingdom

### Episode 003: The Space Journey (Template)
- **Status**: Config template ready
- **Educational Goal**: Learning shapes in Arabic
- **Setting**: Colorful space station

## Quick Start

```bash
# 1. Clone and install
pip install -r requirements.txt

# 2. Set up environment
cp .env.example .env
# Edit .env with your API keys

# 3. Generate API authentication keys (run once)
python auth.py
# This creates ATLAS_API_KEY and ATLAS_READ_ONLY_KEY in your .env

# 4. Initialize database
python atlas_core/db_setup.py

# 5. Run full pipeline for Episode 001
python main_factory.py

# 6. Start API server
python api_server.py
# Visit http://localhost:8000/docs for interactive API docs

# 7. View dashboard
open dashboard/index.html
```

## 🔐 API Authentication

All API endpoints (except `/`) now require authentication via API keys.

### Generating Keys

```bash
# Generate new admin and read-only keys
python auth.py
```

This updates your `.env` file with:
```bash
ATLAS_API_KEY=atlas_admin_xxxxxxxxxxxxxxxx
ATLAS_READ_ONLY_KEY=atlas_read_xxxxxxxxxxxxxxxx
```

### Authentication Headers

Pass your key in **either** of these headers:

```bash
# Option 1: Bearer token (recommended)
Authorization: Bearer your-api-key

# Option 2: Direct header
X-API-Key: your-api-key
```

### Access Levels

| Role | Key Variable | Permissions |
|------|-------------|-------------|
| **Admin** | `ATLAS_API_KEY` | Create, trigger, publish, safety check |
| **Read-Only** | `ATLAS_READ_ONLY_KEY` | View status, episodes, analytics only |

### Protected Endpoints

| Endpoint | Required Role |
|----------|--------------|
| `GET /` | Public (no auth) |
| `GET /status` | Read or Admin |
| `GET /episodes` | Read or Admin |
| `GET /episodes/{id}` | Read or Admin |
| `GET /pipeline/status/{id}` | Read or Admin |
| `GET /analytics/{id}` | Read or Admin |
| `POST /episodes/create` | **Admin only** |
| `POST /pipeline/trigger` | **Admin only** |
| `POST /publish` | **Admin only** |
| `POST /safety/check/{id}` | **Admin only** |

### Example API Calls

```bash
# Set your key
export ATLAS_KEY="your-admin-api-key"

# Health check (no auth)
curl http://localhost:8000/

# Get status (read access)
curl -H "Authorization: Bearer $ATLAS_KEY" \
  http://localhost:8000/status

# Create episode (admin only)
curl -X POST http://localhost:8000/episodes/create \
  -H "Authorization: Bearer $ATLAS_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "episode_id": "ep_003_space_journey",
    "title": "The Space Journey",
    "educational_goal": "Learning shapes in Arabic",
    "characters": ["Sokkar", "Felix", "Bonnie", "Barnaby", "Tweety"],
    "budget_limit": 25.0
  }'

# Trigger pipeline (admin only)
curl -X POST http://localhost:8000/pipeline/trigger \
  -H "Authorization: Bearer $ATLAS_KEY" \
  -H "Content-Type: application/json" \
  -d '{"episode_id": "ep_003_space_journey"}'

# Check status (read access)
curl -H "Authorization: Bearer $ATLAS_KEY" \
  http://localhost:8000/pipeline/status/ep_003_space_journey
```

### Rate Limiting

- **Limit**: 60 requests per minute per IP address
- **Exceeded**: Returns `429 Too Many Requests` with retry-after info

### Security Features

- ✅ Constant-time key comparison (timing-attack resistant)
- ✅ SHA-256 key hashing
- ✅ Per-IP rate limiting
- ✅ Role-based access control
- ✅ Request logging with IP + role
- ✅ Auto-generated secure random keys

## API Keys Required

| Service | Key | Purpose |
|---------|-----|---------|
| Atlas API | `ATLAS_API_KEY` | API server authentication (admin) |
| Atlas API | `ATLAS_READ_ONLY_KEY` | API server authentication (read-only) |
| Google Gemini | `GEMINI_API_KEY` | All AI agents (Script, Motion, Thumbnail, Metadata, Safety, Translation, Storyboard) |
| Fal.ai | `FAL_API_KEY` | Video generation (Veo 3) |
| YouTube | `client_secrets.json` | Publishing + Analytics (OAuth2) |
| OpenAI | `OPENAI_API_KEY` | Optional: DALL-E thumbnails, Whisper subtitles |
| Slack | `SLACK_WEBHOOK_URL` | Optional: Pipeline notifications |
| SMTP | `SMTP_HOST`, `SMTP_USER`, `SMTP_PASS` | Optional: Email alerts |

## Cost Estimates (Per Episode)

| Item | Cost |
|------|------|
| Script (Gemini) | ~$0.01 |
| Storyboard (Gemini) | ~$0.01 |
| Safety Review (Gemini) | ~$0.01 |
| Voice (gTTS) | Free |
| Motion Prompts (Gemini) | ~$0.01 |
| Video Generation (10 clips x 5s) | ~$5.00 |
| Thumbnail (DALL-E) | ~$0.04 |
| Metadata (Gemini) | ~$0.01 |
| Translation (Gemini) | ~$0.02 per language |
| Subtitles (Whisper) | Free (local) |
| **Total per Episode (Arabic)** | **~$5.11** |
| **Total per Episode (Arabic + English + French)** | **~$5.15** |

## Roadmap

- [x] Phase 1: Script, Voice, Motion for Episode 001
- [x] Phase 2: Video Engine + Editor Engine
- [x] Phase 3: Thumbnail + Metadata + Publisher
- [x] Phase 4: Web Dashboard
- [x] Phase 5: Subtitle Engine (SRT + Whisper)
- [x] Phase 6: Translation Engine (Multi-language)
- [x] Phase 7: Analytics Engine (YouTube stats + recommendations)
- [x] Phase 8: Storyboard Engine (Pre-production visuals)
- [x] Phase 9: Safety Engine (Advanced moderation)
- [x] Phase 10: Config Manager (YAML-based episodes)
- [x] Phase 11: Retry System + Notifications (Slack/Email)
- [x] Phase 12: REST API Server (FastAPI)
- [x] Phase 12b: API Authentication + Rate Limiting
- [ ] Phase 13: Episode 002 production
- [ ] Phase 14: Batch production (multiple episodes in parallel)
- [ ] Phase 15: Automated A/B thumbnail testing
- [ ] Phase 16: Multi-channel publishing (Instagram, TikTok, Facebook)
- [ ] Phase 17: Comment moderation and auto-response
- [ ] Phase 18: Revenue tracking and monetization analytics

## Architecture Diagram

```
                    +------------------+
                    |   Config Manager |
                    |   (YAML configs) |
                    +--------+---------+
                             |
        +--------------------+--------------------+
        |                    |                    |
+-------v-------+   +--------v--------+   +-------v-------+
| Storyboard    |   | Safety Engine   |   | Translation |
| Engine        |   | (Content Review)|   | Engine      |
+-------+-------+   +--------+--------+   +-------+-------+
        |                    |                    |
        +--------------------+--------------------+
                             |
                    +--------v---------+
                    |   Script Engine  |
                    +--------+---------+
                             |
        +--------------------+--------------------+
        |                    |                    |
+-------v-------+   +--------v--------+   +-------v-------+
| Voice Engine  |   | Motion Engine   |   | Subtitle      |
| (gTTS Arabic) |   | (Video Prompts) |   | Engine        |
+-------+-------+   +--------+--------+   +-------+-------+
        |                    |                    |
        +--------------------+--------------------+
                             |
                    +--------v---------+
                    |  Video Engine    |
                    |  (Fal.ai Veo 3)  |
                    +--------+---------+
                             |
                    +--------v---------+
                    |  Editor Engine   |
                    |  (MoviePy)       |
                    +--------+---------+
                             |
        +--------------------+--------------------+
        |                    |                    |
+-------v-------+   +--------v--------+   +-------v-------+
| Thumbnail     |   | Metadata Engine |   | Analytics   |
| Engine        |   | (YouTube SEO)   |   | Engine      |
+-------+-------+   +--------+--------+   +-------+-------+
        |                    |                    |
        +--------------------+--------------------+
                             |
                    +--------v---------+
                    | YouTube Publisher|
                    | (OAuth2 Upload)  |
                    +--------+---------+
                             |
                    +--------v---------+
                    |  Notification    |
                    |  (Slack/Email)   |
                    +------------------+
```

## License

Proprietary - Atlas Kids Media. All rights reserved.

---

*Built with love by Omar and Ramo for the children of the Arab world.*
