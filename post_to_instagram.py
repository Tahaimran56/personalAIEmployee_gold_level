"""
Post to Instagram - Simple Example

This script shows how to post to your Instagram Business Account using the AI Employee system.
Note: Instagram requires an image for all posts.
"""

import sys
import os
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from AI_Employee_Vault.services.social_media_service import SocialMediaService

def post_to_instagram(caption, image_url):
    """
    Post to Instagram Business Account

    Args:
        caption: Text caption for the post (with hashtags)
        image_url: URL of the image to post (REQUIRED for Instagram)
    """
    print("=" * 70)
    print("POSTING TO INSTAGRAM")
    print("=" * 70)

    try:
        # Initialize service
        print("\nInitializing Social Media Service...")
        service = SocialMediaService()

        # Prepare post data
        post_data = {
            "platforms": ["instagram"],
            "message": caption,
            "image_url": image_url
        }

        print(f"\nPost Content:")
        print(f"  Caption: {caption[:60]}...")
        print(f"  Image: {image_url}")

        # Validate post
        print("\nValidating post...")
        validation = service.validate_post(post_data)

        if not validation["valid"]:
            print(f"[ERROR] Validation failed: {validation['errors']}")
            return False

        print("[SUCCESS] Post validated")

        # Publish post (two-step process for Instagram)
        print("\nPublishing to Instagram...")
        print("  Step 1: Creating media container...")
        print("  Step 2: Publishing media...")

        result = service.publish_post(post_data)

        if result["success"]:
            print("\n[SUCCESS] Posted to Instagram!")
            print(f"  Media ID: {result['instagram']['media_id']}")
            print(f"  URL: {result['instagram']['permalink']}")
            print(f"  Posted at: {result['instagram']['published_at']}")
            print("\nNote: Engagement metrics available after 24 hours")
            return True
        else:
            print(f"\n[ERROR] Failed to post: {result.get('error', 'Unknown error')}")
            return False

    except Exception as e:
        print(f"\n[ERROR] Exception occurred: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    # Example 1: Product launch post
    print("\nExample 1: Product Launch Post")
    print("-" * 70)
    post_to_instagram(
        caption="Launching our new product today! 🚀 Check it out at the link in bio. #newproduct #launch #innovation #business #startup",
        image_url="https://example.com/images/product-launch.jpg"
    )

    # Example 2: Milestone celebration
    print("\n\nExample 2: Milestone Celebration")
    print("-" * 70)
    post_to_instagram(
        caption="We've reached 10,000 customers! 🎉 Thank you for your amazing support. This is just the beginning! #milestone #grateful #thankyou #business #growth",
        image_url="https://example.com/images/10k-celebration.jpg"
    )

    # Example 3: Behind the scenes
    print("\n\nExample 3: Behind the Scenes")
    print("-" * 70)
    post_to_instagram(
        caption="Behind the scenes at our office today! 💼 Our amazing team working hard to bring you the best experience. #teamwork #office #behindthescenes #startup #culture",
        image_url="https://example.com/images/office-team.jpg"
    )

    print("\n" + "=" * 70)
    print("INSTAGRAM POSTING EXAMPLES COMPLETE")
    print("=" * 70)
    print("\nIMPORTANT: Instagram requires:")
    print("  - Image URL (required for all posts)")
    print("  - Instagram Business Account (not personal account)")
    print("  - Account linked to Facebook Page")
    print("\nTo use with your own content:")
    print("  python post_to_instagram.py")
    print("\nOr import and use in your code:")
    print("  from post_to_instagram import post_to_instagram")
    print("  post_to_instagram('Your caption here', 'https://your-image-url.jpg')")
