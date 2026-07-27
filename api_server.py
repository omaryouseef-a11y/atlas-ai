from fastapi import FastAPI, HTTPException, BackgroundTasks
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

app = FastAPI(
    title="Atlas Kids Media API",
    description="Remote control interface for the Atlas AI content factory",
    version="2.0.0"
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
    return {
        "name": "Atlas Kids Media API",
        "version": "2.0.0",
        "status": "operational",
        "endpoints": [
            "/status",
            "/episodes",
            "/episodes/{id}",
            "/episodes/create",
            "/pipeline/trigger",
            "/pipeline/status/{episode_id}",
            "/publish",
            "/analytics/{episode_id}"
        ]
    }


@app.get("/status")
def get_status():
    """Get overall factory status."""
    episodes = cm.list_configs()
    return {
        "factory_status": "operational",
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


@app.post("/episodes/create")
def create_episode(request: EpisodeRequest):
    """Create a new episode configuration."""
    config_path = cm.create_episode_config(
        episode_id=request.episode_id,
        title=request.title,
        educational_goal=request.educational_goal,
        characters=request.characters,
        target_age=request.target_age,
        language=request.language,
        budget_limit=request.budget_limit,
        duration_seconds=request.duration_seconds,
        num_scenes=request.num_scenes,
        setting=request.setting
    )

    jm.create_episode(request.episode_id, request.title, request.budget_limit)
    notifier.notify(f'New episode created: {request.episode_id} - {request.title}', 'info')

    return {
        "success": True,
        "episode_id": request.episode_id,
        "config_path": config_path,
        "message": f"Episode '{request.title}' configured successfully."
    }


@app.get("/episodes")
def list_episodes():
    """List all episodes."""
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
    return {"episodes": episodes}


@app.get("/episodes/{episode_id}")
def get_episode(episode_id: str):
    """Get detailed info about a specific episode."""
    config = cm.load_config(episode_id)
    if not config:
        raise HTTPException(status_code=404, detail=f"Episode {episode_id} not found")

    plan = cm.get_production_plan(episode_id)
    stats = jm.get_episode_stats(episode_id)

    return {
        "config": config,
        "production_plan": plan,
        "stats": stats
    }


@app.post("/pipeline/trigger")
def trigger_pipeline(request: PipelineTrigger, background_tasks: BackgroundTasks):
    """Trigger the production pipeline for an episode."""
    config = cm.load_config(request.episode_id)
    if not config:
        raise HTTPException(status_code=404, detail=f"Episode {request.episode_id} not found")

    # Run in background so API returns immediately
    background_tasks.add_task(_run_pipeline_async, request.episode_id, request.phases)

    notifier.notify(f'Pipeline triggered for {request.episode_id}', 'info')

    return {
        "success": True,
        "episode_id": request.episode_id,
        "message": "Pipeline started in background. Check /pipeline/status for progress."
    }


def _run_pipeline_async(episode_id, phases):
    """Async pipeline runner for background tasks."""
    try:
        run_full_pipeline(episode_id)
        notifier.notify(f'Pipeline complete for {episode_id}', 'success')
    except Exception as e:
        notifier.notify(f'Pipeline failed for {episode_id}: {str(e)}', 'error')


@app.get("/pipeline/status/{episode_id}")
def get_pipeline_status(episode_id: str):
    """Get current pipeline status for an episode."""
    stats = jm.get_episode_stats(episode_id)
    if not stats['episode']:
        raise HTTPException(status_code=404, detail=f"Episode {episode_id} not found")

    return {
        "episode_id": episode_id,
        "status": stats['episode'][2] if stats['episode'] else "unknown",
        "phase": stats['episode'][3] if stats['episode'] else "unknown",
        "budget_spent": stats['episode'][5] if stats['episode'] else 0,
        "completed_jobs": stats['completed_jobs'],
        "failed_jobs": stats['failed_jobs'],
        "total_job_cost": stats['total_job_cost']
    }


@app.post("/publish")
def publish_episode(request: PublishRequest):
    """Publish a completed episode to YouTube."""
    from publisher.youtube_publisher import YouTubePublisher
    from metadata_engine import MetadataEngine

    final_video = f'episodes/{request.episode_id}/final/final_episode.mp4'
    if not os.path.exists(final_video):
        raise HTTPException(status_code=400, detail=f"Final video not found for {request.episode_id}")

    meta_engine = MetadataEngine()
    meta_path = f'episodes/{request.episode_id}/final/youtube_metadata.md'

    if os.path.exists(meta_path):
        with open(meta_path, 'r', encoding='utf-8') as f:
            metadata = meta_engine.parse_metadata(f.read())
    else:
        metadata = {
            'title': f'Atlas Kids Media - {request.episode_id}',
            'description': 'Educational content for children.',
            'tags': ['kids', 'education', 'arabic'],
            'category': 'Education'
        }

    publisher = YouTubePublisher()
    result = publisher.upload_video(
        video_path=final_video,
        title=metadata.get('title', request.episode_id),
        description=metadata.get('description', ''),
        tags=metadata.get('tags', []),
        category_id='27',
        privacy_status=request.privacy_status,
        thumbnail_path=f'episodes/{request.episode_id}/final/thumbnail.png'
    )

    if request.schedule_at:
        publisher.schedule_video(result['id'], request.schedule_at)

    notifier.notify(f'Episode {request.episode_id} published to YouTube', 'success')

    return {
        "success": True,
        "video_id": result.get('id'),
        "privacy_status": request.privacy_status,
        "scheduled_at": request.schedule_at
    }


@app.get("/analytics/{episode_id}")
def get_analytics(episode_id: str):
    """Get analytics for an episode."""
    from analytics_engine import AnalyticsEngine

    # Check if we have a video ID stored
    # For now, return simulated data
    engine = AnalyticsEngine()
    report = engine.generate_performance_report([f'{episode_id}_video_id'])

    return {
        "episode_id": episode_id,
        "analytics": report
    }


@app.post("/safety/check/{episode_id}")
def safety_check(episode_id: str):
    """Run safety review on an episode."""
    from safety_engine import SafetyEngine

    engine = SafetyEngine()
    script_path = f'episodes/{episode_id}/script/story_v2.md'

    if not os.path.exists(script_path):
        raise HTTPException(status_code=404, detail="Script not found")

    result = engine.review_script(script_path)
    engine.save_report(episode_id, result)

    return {
        "episode_id": episode_id,
        "approved": result['approved'],
        "report_path": f'reports/safety/{episode_id}_safety_report.md'
    }


# --- Run Server ---
if __name__ == '__main__':
    import uvicorn
    print('Starting Atlas API Server...')
    print('Docs available at: http://localhost:8000/docs')
    uvicorn.run(app, host='0.0.0.0', port=8000)
