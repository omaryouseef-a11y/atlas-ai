import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from atlas_core.orchestrator import AtlasOrchestrator
from atlas_core.job_manager import AtlasJobManager
from editor_engine import EditorEngine
from thumbnail_engine import ThumbnailEngine
from metadata_engine import MetadataEngine
from publisher.youtube_publisher import YouTubePublisher
from monetization.store import DigitalStore

def run_full_pipeline(episode_id):
    """
    Atlas Full Factory Pipeline
    Runs the complete end-to-end production for an episode:
    1. Script (assumes pre-generated)
    2. Voice (assumes pre-generated)
    3. Motion Prompts (assumes pre-generated)
    4. Video Generation (via Orchestrator + Video Engine)
    5. Video Editing (Editor Engine)
    6. Thumbnail Generation
    7. Metadata Generation
    8. Publishing (YouTube)
    """
    print(f'\n{"="*60}')
    print(f'  ATLAS FULL FACTORY PIPELINE')
    print(f'  Episode: {episode_id}')
    print(f'{"="*60}\n')

    jm = AtlasJobManager()
    orc = AtlasOrchestrator()

    # Register Episode
    jm.create_episode(episode_id, 'The Great Forest Picnic Journey - V2', budget_limit=20.0)
    jm.update_phase(episode_id, 'video_generation')

    # Phase 4: Video Generation
    print('\n--- PHASE 4: VIDEO GENERATION ---')
    prompts_file = f'episodes/{episode_id}/video_v2/animation_prompts_v2.md'
    if os.path.exists(prompts_file):
        results = orc.generate_all_clips(episode_id, prompts_file)
        successful = [r for r in results if r]
        print(f'Video generation complete: {len(successful)}/{len(results)} clips generated.')
    else:
        print('Prompts not found. Run Motion Engine first.')
        return

    # Phase 5: Video Editing
    print('\n--- PHASE 5: VIDEO EDITING ---')
    jm.update_phase(episode_id, 'editing')
    editor = EditorEngine(episode_id)
    video_dir = f'episodes/{episode_id}/video_v2'
    audio_dir = f'episodes/{episode_id}/voice_v2'
    final_video = editor.assemble_episode(video_dir, audio_dir)

    if not final_video:
        print('Video editing failed. Stopping pipeline.')
        jm.update_status(episode_id, 'QA_failed')
        return

    # Phase 6: Thumbnail
    print('\n--- PHASE 6: THUMBNAIL GENERATION ---')
    thumb_engine = ThumbnailEngine()
    thumb_prompt = thumb_engine.generate_thumbnail_prompt(
        episode_title='The Great Forest Picnic Journey',
        characters=['Sokkar', 'Felix', 'Bonnie', 'Barnaby', 'Tweety', 'Bambi', 'Torti', 'Ricky', 'Henry', 'Freddy'],
        educational_topic='Counting from 1 to 10'
    )
    thumb_engine.save_thumbnail_prompt(episode_id, thumb_prompt)
    print('Thumbnail prompt saved.')

    # Phase 7: Metadata
    print('\n--- PHASE 7: METADATA GENERATION ---')
    meta_engine = MetadataEngine()
    metadata = meta_engine.generate_metadata(
        episode_title='The Great Forest Picnic Journey - V2',
        episode_description='10 animal friends go on a picnic and learn to count from 1 to 10 in Arabic.',
        characters=['Sokkar', 'Felix', 'Bonnie', 'Barnaby', 'Tweety', 'Bambi', 'Torti', 'Ricky', 'Henry', 'Freddy'],
        educational_goal='Counting from 1 to 10 in Arabic'
    )
    meta_engine.save_metadata(episode_id, metadata)
    print('Metadata saved.')

    # Phase 8: Publishing
    print('\n--- PHASE 8: PUBLISHING ---')
    jm.update_phase(episode_id, 'publishing')
    publisher = YouTubePublisher()
    meta_data = meta_engine.parse_metadata(metadata)

    upload_result = publisher.upload_video(
        video_path=final_video,
        title=meta_data.get('title', f'Atlas Kids Media - {episode_id}'),
        description=meta_data.get('description', 'Educational content for children.'),
        tags=meta_data.get('tags', ['kids', 'education', 'arabic']),
        category_id='27',  # Education
        privacy_status='private',
        thumbnail_path=f'episodes/{episode_id}/final/thumbnail.png'
    )

    if upload_result:
        jm.update_status(episode_id, 'published')
        print(f'\n Episode {episode_id} published successfully!')
        print(f'  Video ID: {upload_result.get("id", "N/A")}')
    else:
        jm.update_status(episode_id, 'ready_for_approval')
        print(f'\n Episode {episode_id} is ready for manual review and publishing.')

    # Phase 9: Digital Store Generation (Monetization)
    print('\n--- PHASE 9: DIGITAL STORE GENERATION ---')
    jm.update_phase(episode_id, 'digital_store')
    store = DigitalStore()
    product_url = store.process_new_video(
        character_prompts=meta_data.get('characters', ['Sokkar', 'Felix', 'Bonnie', 'Barnaby', 'Tweety', 'Bambi', 'Torti', 'Ricky', 'Henry', 'Freddy']),
        video_id=episode_id,
        title=meta_data.get('title', f'Atlas Kids Media - {episode_id}')
    )

    # Final Report
    print(f'\n{"="*60}')
    print('  PIPELINE COMPLETE')
    print(f'{"="*60}')
    stats = jm.get_episode_stats(episode_id)
    print(f'  Total Jobs: {stats["completed_jobs"]}')
    print(f'  Failed Jobs: {stats["failed_jobs"]}')
    print(f'  Total Cost: ${stats["total_job_cost"]:.2f}')
    print(f'  Final Video: {final_video}')
    print(f'{"="*60}\n')


if __name__ == '__main__':
    run_full_pipeline('ep_001_picnic_journey')
