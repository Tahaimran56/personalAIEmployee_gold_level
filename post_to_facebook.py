"""
Post to Facebook - Simple Example

This script shows how to post to your Facebook Page using the AI Employee system.
"""

import sys
import os
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from AI_Employee_Vault.services.social_media_service import SocialMediaService

def post_to_facebook(message, link=None, image_url=None):
    """
    Post to Facebook Page

    Args:
        message: Text content of the post
        link: Optional URL to include
        image_url: Optional image URL
    """
    print("=" * 70)
    print("POSTING TO FACEBOOK")
    print("=" * 70)

    try:
        # Initialize service
        print("\nInitializing Social Media Service...")
        service = SocialMediaService()

        # Prepare post data
        post_data = {
            "platforms": ["facebook"],
            "message": message,
            "link": link,
            "image_url": image_url
        }

        print(f"\nPost Content:")
        print(f"  Message: {message[:60]}...")
        if link:
            print(f"  Link: {link}")
        if image_url:
            print(f"  Image: {image_url}")

        # Validate post
        print("\nValidating post...")
        validation = service.validate_post(post_data)

        if not validation["valid"]:
            print(f"[ERROR] Validation failed: {validation['errors']}")
            return False

        print("[SUCCESS] Post validated")

        # Publish post
        print("\nPublishing to Facebook...")
        result = service.publish_post(post_data)

        if result["success"]:
            print("\n[SUCCESS] Posted to Facebook!")
            print(f"  Post ID: {result['facebook']['post_id']}")
            print(f"  URL: {result['facebook']['permalink_url']}")
            print(f"  Posted at: {result['facebook']['created_time']}")
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
    # Example 1: Simple text post
    print("\nExample 1: Simple Text Post")
    print("-" * 70)
    post_to_facebook(
        message="Excited to share our latest milestone! We've reached 10,000 customers. Thank you for your amazing support! 🎉 #milestone #grateful #business"
    )

    # Example 2: Post with link
    print("\n\nExample 2: Post with Link")
    print("-" * 70)
    post_to_facebook(
        message="Check out our latest blog post about AI automation in business. Link in the post! #AI #automation #business",
        link="https://example.com/blog/ai-automation"
    )

    # Example 3: Post with image
    print("\n\nExample 3: Post with Image")
    print("-" * 70)
    post_to_facebook(
        message="Launching our new product today! Check it out at the link below. #newproduct #launch #innovation",
        link="https://example.com/products/new-launch",
        image_url="https://example.com/images/product-launch.jpg"
    )

    print("\n" + "=" * 70)
    print("FACEBOOK POSTING EXAMPLES COMPLETE")
    print("=" * 70)
    print("\nTo use with your own content:")
    print("  python post_to_facebook.py")
    print("\nOr import and use in your code:")
    print("  from post_to_facebook import post_to_facebook")
    print("  post_to_facebook('Your message here')")
