import os
from monetization.generator import ColoringBookGenerator
from monetization.publisher import GumroadPublisher

class DigitalStore:
    def __init__(self):
        self.generator = ColoringBookGenerator()
        self.publisher = GumroadPublisher()

    def process_new_video(self, character_prompts, video_id, title):
        print(f"[{video_id}] Generating digital products for: {title}")
        
        # 1. Generate PDF coloring book
        pdf_path = self.generator.generate_coloring_book(character_prompts, title)
        
        # 2. Publish to store
        product_url = self.publisher.publish_product(
            name=f"{title} - Coloring Book",
            description="Fun coloring pages featuring your favorite Atlas Kids characters!",
            price=3.99,
            file_path=pdf_path
        )
        
        print(f"[{video_id}] Success! Product live at: {product_url}")
        return product_url

if __name__ == "__main__":
    store = DigitalStore()
    # Test run
    store.process_new_video(
        character_prompts=["Super Khufu exploring the pyramids"],
        video_id="ep_001",
        title="Super Khufu Picnic Journey"
    )
