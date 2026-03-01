"""
Post to Multiple Platforms - Simple Example

This script shows how to post the same content to Facebook, Instagram, and Twitter simultaneously.
"""

import sys
import os
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from AI_Employee_Vault.services.social_media_service import SocialMediaService

def post_to_all_platforms(message, image_url=None, link=None):
    """
    Post to Facebook, Instagram, and Twitter simultaneously

    Args:
        message: Text content (will be adapted for each platform)
        image_url: Optional image URL (required for Instagram)
        link: Optional link (Facebook only, Instagram uses "link in bio")
    """
    print("=" * 70)
    print("POSTING TO MULTIPLE PLATFORMS")
    print("=" * 70)

    try:
        # Initialize service
        print("\nInitializing Social Media Service...")
        service = SocialMediaService()

        # Determine which platforms to post to
        platforms = []

        # Facebook: always available
        platforms.append("facebook")

        # Instagram: only if image is provided
        if image_url:
            platforms.append("instagram")
        else:
            print("\n[WARNING] Instagram requires an image - skipping Instagram")

        # Twitter: check character limit
        if len(message) <= 280:
            platforms.append("twitter")
        else:
            print(f"\n[WARNING] Message too long for Twitter ({len(message)}/280 chars) - skipping Twitter")

        print(f"\nTarget Platforms: {', '.join(platforms)}")

        # Prepare post data
        post_data = {
            "platforms": platforms,
            "message": message,
            "image_url": image_url,
            "link": link
        }

        print(f"\nPost Content:")
        print(f"  Message: {message[:60]}...")
        print(f"  Length: {len(message)} characters")
        if image_url:
            print(f"  Image: {image_url}")
        if link:
            print(f"  Link: {link}")

        # Validate post
        print("\nValidating post for all platforms...")
        validation = service.validate_post(post_data)

        if not validation["valid"]:
            print(f"[ERROR] Validation failed: {validation['errors']}")
            return False

        print("[SUCCESS] Post validated for all platforms")

        # Publish to all platforms
        print("\nPublishing to all platforms simultaneously...")
        result = service.publish_post(post_data)

        if result["success"]:
            print("\n[SUCCESS] Posted to all platforms!")

            # Show results for each platform
            if "facebook" in result:
                print(f"\n  Facebook:")
                print(f"    Post ID: {result['facebook']['post_id']}")
                print(f"    URL: {result['facebook']['permalink_url']}")

            if "instagram" in result:
                print(f"\n  Instagram:")
                print(f"    Media ID: {result['instagram']['media_id']}")
                print(f"    URL: {result['instagram']['permalink']}")

            if "twitter" in result:
                print(f"\n  Twitter:")
                print(f"    Tweet ID: {result['twitter']['tweet_id']}")
                print(f"    URL: {result['twitter']['url']}")

            # Calculate total reach
            print(f"\n  Total Platforms: {len(platforms)}")
            print(f"  Estimated Reach: {len(platforms) * 5000} people (estimated)")

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
    # Example 1: Milestone announcement (all platforms)
    print("\nExample 1: Milestone Announcement (All Platforms)")
    print("-" * 70)
    post_to_all_platforms(
        message="🎉 We've reached 10,000 customers! Thank you for your amazing support. This is just the beginning! #milestone #grateful #business",
        image_url="https://example.com/images/10k-celebration.jpg",
        link="https://example.com/blog/10k-milestone"
    )

    # Example 2: Product launch (all platforms)
    print("\n\nExample 2: Product Launch (All Platforms)")
    print("-" * 70)
    post_to_all_platforms(
        message="🚀 Launching our new AI-powered automation tool today! Check it out and let us know what you think. #AI #automation #productlaunch #innovation",
        image_url="https://example.com/images/product-launch.jpg",
        link="https://example.com/products/new-launch"
    )

    # Example 3: Behind the scenes (all platforms)
    print("\n\nExample 3: Behind the Scenes (All Platforms)")
    print("-" * 70)
    post_to_all_platforms(
        message="Behind the scenes at our office! 💼 Our amazing team working hard to bring you the best experience. #teamwork #startup #culture #behindthescenes",
        image_url="https://example.com/images/office-team.jpg"
    )

    print("\n" + "=" * 70)
    print("MULTI-PLATFORM POSTING EXAMPLES COMPLETE")
    print("=" * 70)
    print("\nKey Benefits:")
    print("  ✓ Post to all platforms with one command")
    print("  ✓ Automatic platform-specific adaptations")
    print("  ✓ Consistent messaging across all channels")
    print("  ✓ Maximum reach with minimal effort")
    print("\nPlatform Requirements:")
    print("  - Facebook: Message (required), Image/Link (optional)")
    print("  - Instagram: Message + Image (both required)")
    print("  - Twitter: Message max 280 chars (required), Image (optional)")
    print("\nTo use with your own content:")
    print("  python post_to_all_platforms.py")
    print("\nOr import and use in your code:")
    print("  from post_to_all_platforms import post_to_all_platforms")
    print("  post_to_all_platforms('Your message', 'https://image-url.jpg')")
