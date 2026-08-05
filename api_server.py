from fastapi import FastAPI, HTTPException, BackgroundTasks, Request, Depends
from fastapi.security import HTTPBearer
from pydantic import BaseModel
from typing import Optional, List
import os
import sys

# Add parent to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from main_factory import run_full_pipeline
from atlas_core.status import print_dashboard
from atlas_core.job_manager import AtlasJobManager
from config_manager import ConfigManager
from retry_system import NotificationEngine
from auth import require_admin, require_read, require_auth, setup_env_file, AuthLogger

app = FastAPI(
    title="Atlas Kids Media API",
    description="""
    Remote control interface for the Atlas AI content factory.

    ## Authentication
    All endpoints (except `/`) require an API key.

    ### Headers
    - `Authorization: Bearer <your-api-key>`
    - OR `X-API-Key: <your-api-key>`

    ### Roles
    - **Admin** (`ATLAS_API_KEY`): Full access — create, trigger, publish, delete
    - **Read-Only** (`ATLAS_READ_ONLY_KEY`): View-only — status, episodes, analytics

    ### Rate Limiting
    60 requests per minute per IP address.

    To generate keys, run: `python auth.py`
    """,
    version="2.0.1",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Initialize components
jm = AtlasJobManager()
cm = ConfigManager()
notifier = NotificationEngine()


# --- Request Models ---

class EpisodeRequest(BaseModel):
    episode_id: str
    title: str
    educational_goal: str
    characters: List[str]
    target_age: str = "3-7"
    language: str = "arabic"
    budget_limit: float = 20.0
    duration_seconds: int = 60
    num_scenes: int = 10
    setting: str = "magical green forest"

class PipelineTrigger(BaseModel):
    episode_id: str
    phases: Optional[List[str]] = None  # If None, run all phases

class PublishRequest(BaseModel):
    episode_id: str
    privacy_status: str = "private"  # private, unlisted, public
    schedule_at: Optional[str] = None  # ISO 8601 datetime


# --- Endpoints ---

@app.get("/")
def root():
    """Public health check — no auth required."""
    return {
        "name": "Atlas Kids Media API",
        "version": "2.0.1",
        "status": "operational",
        "auth_required": True,
        "docs": "/docs",
        "endpoints": {
            "public": ["/"],
            "read": ["/status", "/episodes", "/episodes/{id}", "/pipeline/status/{id}", "/analytics/{id}"],
            "admin": ["/episodes/create", "/pipeline/trigger", "/publish", "/safety/check/{id}"]
        }
    }


@app.get("/status", dependencies=[Depends(require_read)])
def get_status(request: Request, user: dict = Depends(require_read)):
    """Get overall factory status. (Read access required)"""
    episodes = cm.list_configs()
    AuthLogger.log(request, user, "/status")
    return {
        "factory_status": "operational",
        "authenticated_as": user["role"],
        "total_episodes_configured": len(episodes),
        "episodes": episodes,
        "engines": {
            "script": "ready",
            "voice": "ready",
            "motion": "ready",
            "video": "ready",
            "editor": "ready",
            "thumbnail": "ready",
            "metadata": "ready",
            "publisher": "ready",
            "subtitle": "ready",
            "translation": "ready",
            "analytics": "ready",
            "safety": "ready",
            "storyboard": "ready"
        }
    }


@app.post("/episodes/create", dependencies=[Depends(require_admin)])
def create_episode(
    request: Request,
    episode_request: EpisodeRequest,
    user: dict = Depends(require_admin)
):
    """Create a new episode configuration. (Admin only)"""
    config_path = cm.create_episode_config(
        episode_id=episode_request.episode_id,
        title=episode_request.title,
        educational_goal=episode_request.educational_goal,
        characters=episode_request.characters,
        target_age=episode_request.target_age,
        language=episode_request.language,
        budget_limit=episode_request.budget_limit,
        duration_seconds=episode_request.duration_seconds,
        num_scenes=episode_request.num_scenes,
        setting=episode_request.setting
    )

    jm.create_episode(episode_request.episode_id, episode_request.title, episode_request.budget_limit)
    notifier.notify(f'New episode created: {episode_request.episode_id} - {episode_request.title}', 'info')
    AuthLogger.log(request, user, f"/episodes/create {episode_request.episode_id}")

    return {
        "success": True,
        "episode_id": episode_request.episode_id,
        "config_path": config_path,
        "created_by": user["role"],
        "message": f"Episode '{episode_request.title}' configured successfully."
    }


@app.get("/episodes", dependencies=[Depends(require_read)])
def list_episodes(request: Request, user: dict = Depends(require_read)):
    """List all episodes. (Read access required)"""
    configs = cm.list_configs()
    episodes = []
    for ep_id in configs:
        config = cm.load_config(ep_id)
        plan = cm.get_production_plan(ep_id)
        episodes.append({
            "id": ep_id,
            "title": config['episode']['title'] if config else "Unknown",
            "status": config['episode']['status'] if config else "unknown",
            "estimated_cost": plan['total_estimated_cost'] if plan else 0
        })
    AuthLogger.log(request, user, "/episodes")
    return {"episodes": episodes}


@app.get("/episodes/{episode_id}", dependencies=[Depends(require_read)])
def get_episode(episode_id: str, request: Request, user: dict = Depends(require_read)):
    """Get detailed info about a specific episode. (Read access required)"""
    config = cm.load_config(episode_id)
    if not config:
        raise HTTPException(status_code=404, detail=f"Episode {episode_id} not found")

    plan = cm.get_production_plan(episode_id)
    stats = jm.get_episode_stats(episode_id)
    AuthLogger.log(request, user, f"/episodes/{episode_id}")

    return {
        "config": config,
        "production_plan": plan,
        "stats": stats
    }


@app.post("/pipeline/trigger", dependencies=[Depends(require_admin)])
def trigger_pipeline(
    request: Request,
    pipeline_request: PipelineTrigger,
    background_tasks: BackgroundTasks,
    user: dict = Depends(require_admin)
):
    """Trigger the production pipeline for an episode. (Admin only)"""
    config = cm.load_config(pipeline_request.episode_id)
    if not config:
        raise HTTPException(status_code=404, detail=f"Episode {pipeline_request.episode_id} not found")

    # Run in background so API returns immediately
    background_tasks.add_task(_run_pipeline_async, pipeline_request.episode_id, pipeline_request.phases)

    notifier.notify(f'Pipeline triggered for {pipeline_request.episode_id}', 'info')
    AuthLogger.log(request, user, f"/pipeline/trigger {pipeline_request.episode_id}")

    return {
        "success": True,
        "episode_id": pipeline_request.episode_id,
        "triggered_by": user["role"],
        "message": "Pipeline started in background. Check /pipeline/status for progress."
    }


def _run_pipeline_async(episode_id, phases):
    """Async pipeline runner for background tasks."""
    try:
        run_full_pipeline(episode_id)
        notifier.notify(f'Pipeline complete for {episode_id}', 'success')
    except Exception as e:
        notifier.notify(f'Pipeline failed for {episode_id}: {str(e)}', 'error')


@app.get("/pipeline/status/{episode_id}", dependencies=[Depends(require_read)])
def get_pipeline_status(episode_id: str, request: Request, user: dict = Depends(require_read)):
    """Get current pipeline status for an episode. (Read access required)"""
    stats = jm.get_episode_stats(episode_id)
    if not stats['episode']:
        raise HTTPException(status_code=404, detail=f"Episode {episode_id} not found")

    AuthLogger.log(request, user, f"/pipeline/status/{episode_id}")
    return {
        "episode_id": episode_id,
        "status": stats['episode'][2] if stats['episode'] else "unknown",
        "phase": stats['episode'][3] if stats['episode'] else "unknown",
        "budget_spent": stats['episode'][5] if stats['episode'] else 0,
        "completed_jobs": stats['completed_jobs'],
        "failed_jobs": stats['failed_jobs'],
        "total_job_cost": stats['total_job_cost"]
    }


@app.post("/publish", dependencies=[Depends(require_admin)])
def publish_episode(
    request: Request,
    publish_request: PublishRequest,
    user: dict = Depends(require_admin)
):
    """Publish a completed episode to YouTube. (Admin only)"""
    from publisher.youtube_publisher import YouTubePublisher
    from metadata_engine import MetadataEngine

    final_video = f'episodes/{publish_request.episode_id}/final/final_episode.mp4'
    if not os.path.exists(final_video):
        raise HTTPException(status_code=400, detail=f"Final video not found for {publish_request.episode_id}")

    meta_engine = MetadataEngine()
    meta_path = f'episodes/{publish_request.episode_id}/final/youtube_metadata.md'

    if os.path.exists(meta_path):
        with open(meta_path, 'r', encoding='utf-8') as f:
            metadata = meta_engine.parse_metadata(f.read())
    else:
        metadata = {
            'title': f'Atlas Kids Media - {publish_request.episode_id}',
            'description': 'Educational content for children.',
            'tags': ['kids', 'education', 'arabic'],
            'category': 'Education'
        }

    publisher = YouTubePublisher()
    result = publisher.upload_video(
        video_path=final_video,
        title=metadata.get('title', publish_request.episode_id),
        description=metadata.get('description', ''),
        tags=metadata.get('tags', []),
        category_id='27',
        privacy_status=publish_request.privacy_status,
        thumbnail_path=f'episodes/{publish_request.episode_id}/final/thumbnail.png'
    )

    if publish_request.schedule_at:
        publisher.schedule_video(result['id'], publish_request.schedule_at)

    notifier.notify(f'Episode {publish_request.episode_id} published to YouTube', 'success')
    AuthLogger.log(request, user, f"/publish {publish_request.episode_id}")

    return {
        "success": True,
        "video_id": result.get('id'),
        "published_by": user["role"],
        "privacy_status": publish_request.privacy_status,
        "scheduled_at": publish_request.schedule_at
    }


@app.get("/analytics/{episode_id}", dependencies=[Depends(require_read)])
def get_analytics(episode_id: str, request: Request, user: dict = Depends(require_read)):
    """Get analytics for an episode. (Read access required)"""
    from analytics_engine import AnalyticsEngine

    engine = AnalyticsEngine()
    report = engine.generate_performance_report([f'{episode_id}_video_id'])
    AuthLogger.log(request, user, f"/analytics/{episode_id}")

    return {
        "episode_id": episode_id,
        "analytics": report
    }


@app.post("/safety/check/{episode_id}", dependencies=[Depends(require_admin)])
def safety_check(episode_id: str, request: Request, user: dict = Depends(require_admin)):
    """Run safety review on an episode. (Admin only)"""
    from safety_engine import SafetyEngine

    engine = SafetyEngine()
    script_path = f'episodes/{episode_id}/script/story_v2.md'

    if not os.path.exists(script_path):
        raise HTTPException(status_code=404, detail="Script not found")

    result = engine.review_script(script_path)
    engine.save_report(episode_id, result)
    AuthLogger.log(request, user, f"/safety/check/{episode_id}")

    return {
        "episode_id": episode_id,
        "approved": result['approved'],
        "checked_by": user["role"],
        "report_path": f'reports/safety/{episode_id}_safety_report.md'
    }


# --- Run Server ---
if __name__ == '__main__':
    import uvicorn

    # Auto-generate API keys if not present
    setup_env_file()

    print('Starting Atlas API Server...')
    print('Docs available at: http://localhost:8000/docs')
    print('Authentication required for all endpoints except /')
    uvicorn.run(app, host='0.0.0.0', port=8000)
