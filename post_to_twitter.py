"""
Post to Twitter - Simple Example

This script shows how to post tweets using the AI Employee system.
"""

import sys
import os
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from AI_Employee_Vault.services.social_media_service import SocialMediaService

def post_to_twitter(text, image_url=None):
    """
    Post to Twitter

    Args:
        text: Tweet text (max 280 characters)
        image_url: Optional image URL
    """
    print("=" * 70)
    print("POSTING TO TWITTER")
    print("=" * 70)

    try:
        # Initialize service
        print("\nInitializing Social Media Service...")
        service = SocialMediaService()

        # Prepare post data
        post_data = {
            "platforms": ["twitter"],
            "message": text,
            "image_url": image_url
        }

        print(f"\nTweet Content:")
        print(f"  Text: {text}")
        print(f"  Length: {len(text)}/280 characters")
        if image_url:
            print(f"  Image: {image_url}")

        # Validate post
        print("\nValidating tweet...")
        validation = service.validate_post(post_data)

        if not validation["valid"]:
            print(f"[ERROR] Validation failed: {validation['errors']}")
            return False

        print("[SUCCESS] Tweet validated")

        # Check rate limit before posting
        print("\nChecking rate limit...")
        # Rate limit check would happen here in real implementation

        # Publish tweet
        print("\nPublishing to Twitter...")
        result = service.publish_post(post_data)

        if result["success"]:
            print("\n[SUCCESS] Posted to Twitter!")
            print(f"  Tweet ID: {result['twitter']['tweet_id']}")
            print(f"  URL: {result['twitter']['url']}")
            print(f"  Posted at: {result['twitter']['created_at']}")
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
    # Example 1: Simple announcement
    print("\nExample 1: Simple Announcement")
    print("-" * 70)
    post_to_twitter(
        text="Excited to share our latest milestone! We've reached 10,000 customers. Thank you for your amazing support! 🎉 #milestone #grateful"
    )

    # Example 2: Product launch
    print("\n\nExample 2: Product Launch")
    print("-" * 70)
    post_to_twitter(
        text="🚀 Launching our new AI-powered automation tool today! Check it out and let us know what you think. #AI #automation #productlaunch"
    )

    # Example 3: Tweet with image
    print("\n\nExample 3: Tweet with Image")
    print("-" * 70)
    post_to_twitter(
        text="Behind the scenes at our office! Our amazing team working hard to bring you the best experience. 💼 #teamwork #startup",
        image_url="https://example.com/images/office-team.jpg"
    )

    # Example 4: Thread starter (short tweet)
    print("\n\nExample 4: Thread Starter")
    print("-" * 70)
    post_to_twitter(
        text="🧵 Thread: 5 lessons we learned building our AI Employee system (1/5)"
    )

    print("\n" + "=" * 70)
    print("TWITTER POSTING EXAMPLES COMPLETE")
    print("=" * 70)
    print("\nIMPORTANT: Twitter limits:")
    print("  - 280 characters per tweet")
    print("  - 50 tweets per 15 minutes (rate limit)")
    print("  - Requires Elevated API access for posting")
    print("\nTo use with your own content:")
    print("  python post_to_twitter.py")
    print("\nOr import and use in your code:")
    print("  from post_to_twitter import post_to_twitter")
    print("  post_to_twitter('Your tweet here')")
