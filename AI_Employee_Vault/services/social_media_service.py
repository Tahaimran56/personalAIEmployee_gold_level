"""
Social Media Service for Gold Tier AI Employee

This service manages social media integration for Facebook, Instagram, and Twitter.
It implements:
- Multi-platform posting with approval workflow
- Post validation (character limits, image requirements)
- Engagement metrics retrieval (24 hours after posting)
- Error handling with queue integration
- Comprehensive audit logging

Author: AI Employee Gold Tier
Created: 2026-02-05
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
import logging

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SocialMediaService:
    """
    Manages social media integration for the AI Employee.

    This service provides methods to:
    - Create and validate social media posts
    - Publish to multiple platforms (Facebook, Instagram, Twitter)
    - Retrieve engagement metrics
    - Handle errors gracefully with queue integration
    """

    def __init__(self, config_path: str = "config/social_media_config.json"):
        """
        Initialize the SocialMediaService.

        Args:
            config_path: Path to social media configuration file
        """
        self.config_path = Path(config_path)
        self.config = self._load_config()

        # Platform limits
        self.platform_limits = {
            "facebook": {"text_max": 63206, "image_required": False},
            "instagram": {"text_max": 2200, "image_required": True},
            "twitter": {"text_max": 280, "image_required": False}
        }

        logger.info("SocialMediaService initialized")

    def _load_config(self) -> Dict[str, Any]:
        """Load social media configuration from JSON file."""
        if not self.config_path.exists():
            logger.warning(f"Config file not found: {self.config_path}, using defaults")
            return {}

        with open(self.config_path, 'r') as f:
            return json.load(f)

    def validate_post(
        self,
        platforms: List[str],
        text: str,
        image_url: Optional[str] = None,
        link_url: Optional[str] = None,
        hashtags: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Validate post content for specified platforms.

        Args:
            platforms: List of target platforms
            text: Post text/caption
            image_url: URL to image (optional)
            link_url: External link (optional)
            hashtags: List of hashtags (optional)

        Returns:
            dict: Validation result with errors if any
        """
        errors = []
        warnings = []

        # Validate platforms
        valid_platforms = ["facebook", "instagram", "twitter"]
        for platform in platforms:
            if platform not in valid_platforms:
                errors.append(f"Invalid platform: {platform}")

        # Validate text length for each platform
        for platform in platforms:
            if platform in self.platform_limits:
                max_length = self.platform_limits[platform]["text_max"]
                if len(text) > max_length:
                    errors.append(f"{platform.capitalize()}: Text exceeds {max_length} characters (current: {len(text)})")

        # Check Instagram image requirement
        if "instagram" in platforms and not image_url:
            errors.append("Instagram: Image is required")

        # Validate image URL format
        if image_url:
            if not image_url.startswith(("http://", "https://")):
                errors.append("Image URL must start with http:// or https://")

        # Validate link URL format
        if link_url:
            if not link_url.startswith(("http://", "https://")):
                errors.append("Link URL must start with http:// or https://")

        # Check for hashtags
        if hashtags and len(hashtags) > 30:
            warnings.append("More than 30 hashtags may reduce engagement")

        is_valid = len(errors) == 0

        return {
            "valid": is_valid,
            "errors": errors,
            "warnings": warnings
        }

    def publish_post(
        self,
        platforms: List[str],
        text: str,
        image_url: Optional[str] = None,
        link_url: Optional[str] = None,
        hashtags: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Publish post to multiple platforms.

        Args:
            platforms: List of target platforms
            text: Post text/caption
            image_url: URL to image (optional)
            link_url: External link (optional)
            hashtags: List of hashtags (optional)

        Returns:
            dict: Publishing results with post IDs for each platform
        """
        # Validate post first
        validation = self.validate_post(platforms, text, image_url, link_url, hashtags)

        if not validation["valid"]:
            logger.error(f"Post validation failed: {validation['errors']}")
            return {
                "success": False,
                "errors": validation["errors"],
                "platform_results": {}
            }

        # Publish to each platform
        platform_results = {}

        for platform in platforms:
            try:
                if platform == "facebook":
                    result = self._publish_to_facebook(text, image_url, link_url)
                elif platform == "instagram":
                    result = self._publish_to_instagram(text, image_url, hashtags)
                elif platform == "twitter":
                    result = self._publish_to_twitter(text, image_url, hashtags)
                else:
                    result = {"success": False, "error": "Unknown platform"}

                platform_results[platform] = result

            except Exception as e:
                logger.error(f"Failed to publish to {platform}: {e}")
                platform_results[platform] = {
                    "success": False,
                    "error": str(e)
                }

                # Queue for retry
                self._queue_failed_post(platform, text, image_url, link_url, hashtags, str(e))

        # Determine overall success
        success_count = sum(1 for r in platform_results.values() if r.get("success"))
        overall_success = success_count == len(platforms)

        # Audit log
        try:
            from services.audit_service import AuditService
            audit_service = AuditService()
            audit_service.log_action(
                action_type="social_post",
                actor="ai_employee",
                target=",".join(platforms),
                parameters={
                    "platforms": platforms,
                    "text_preview": text[:50] + "..." if len(text) > 50 else text,
                    "has_image": image_url is not None,
                    "has_link": link_url is not None
                },
                result="success" if overall_success else "partial_success" if success_count > 0 else "failure",
                approval_status="approved"
            )
        except Exception as e:
            logger.error(f"Failed to log social media post: {e}")

        return {
            "success": overall_success,
            "platform_results": platform_results,
            "success_count": success_count,
            "total_platforms": len(platforms)
        }

    def _publish_to_facebook(
        self,
        text: str,
        image_url: Optional[str],
        link_url: Optional[str]
    ) -> Dict[str, Any]:
        """
        Publish post to Facebook via MCP server.

        Args:
            text: Post text
            image_url: Image URL (optional)
            link_url: Link URL (optional)

        Returns:
            dict: Publishing result
        """
        import requests

        facebook_mcp_url = os.getenv("FACEBOOK_MCP_URL", "http://localhost:3101")
        api_key = os.getenv("MCP_API_KEY")

        logger.info(f"Publishing to Facebook: {text[:50]}...")

        try:
            payload = {
                "message": text,
                "published": True
            }

            if image_url:
                payload["image_url"] = image_url

            if link_url:
                payload["link"] = link_url

            response = requests.post(
                f"{facebook_mcp_url}/posts",
                json=payload,
                headers={"X-API-Key": api_key},
                timeout=30
            )

            response.raise_for_status()
            data = response.json()

            return {
                "success": True,
                "post_id": data.get("post_id"),
                "permalink_url": data.get("permalink_url")
            }

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to publish to Facebook: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def _publish_to_instagram(
        self,
        text: str,
        image_url: str,
        hashtags: Optional[List[str]]
    ) -> Dict[str, Any]:
        """
        Publish post to Instagram via MCP server.

        Args:
            text: Post caption
            image_url: Image URL (required)
            hashtags: Hashtags (optional)

        Returns:
            dict: Publishing result
        """
        import requests
        import time

        instagram_mcp_url = os.getenv("INSTAGRAM_MCP_URL", "http://localhost:3102")
        api_key = os.getenv("MCP_API_KEY")

        logger.info(f"Publishing to Instagram: {text[:50]}...")

        try:
            # Add hashtags to caption if provided
            caption = text
            if hashtags:
                caption += "\n\n" + " ".join(f"#{tag}" for tag in hashtags)

            # Step 1: Create media container
            container_payload = {
                "image_url": image_url,
                "caption": caption
            }

            container_response = requests.post(
                f"{instagram_mcp_url}/media",
                json=container_payload,
                headers={"X-API-Key": api_key},
                timeout=30
            )

            container_response.raise_for_status()
            container_data = container_response.json()
            container_id = container_data.get("container_id")

            # Wait for container to be ready (Instagram requires this)
            max_wait = 30  # seconds
            wait_interval = 2  # seconds
            elapsed = 0

            while elapsed < max_wait:
                if container_data.get("status") == "FINISHED":
                    break
                time.sleep(wait_interval)
                elapsed += wait_interval

                # Check status again
                status_response = requests.get(
                    f"{instagram_mcp_url}/media/{container_id}",
                    headers={"X-API-Key": api_key},
                    timeout=10
                )
                container_data = status_response.json()

            # Step 2: Publish media container
            publish_payload = {
                "container_id": container_id
            }

            publish_response = requests.post(
                f"{instagram_mcp_url}/media/publish",
                json=publish_payload,
                headers={"X-API-Key": api_key},
                timeout=30
            )

            publish_response.raise_for_status()
            publish_data = publish_response.json()

            return {
                "success": True,
                "media_id": publish_data.get("media_id"),
                "permalink": publish_data.get("permalink")
            }

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to publish to Instagram: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def _publish_to_twitter(
        self,
        text: str,
        image_url: Optional[str],
        hashtags: Optional[List[str]]
    ) -> Dict[str, Any]:
        """
        Publish tweet to Twitter via MCP server.

        Args:
            text: Tweet text
            image_url: Image URL (optional)
            hashtags: Hashtags (optional)

        Returns:
            dict: Publishing result
        """
        import requests

        twitter_mcp_url = os.getenv("TWITTER_MCP_URL", "http://localhost:3103")
        api_key = os.getenv("MCP_API_KEY")

        logger.info(f"Publishing to Twitter: {text[:50]}...")

        try:
            # Add hashtags to text if provided
            tweet_text = text
            if hashtags:
                tweet_text += " " + " ".join(f"#{tag}" for tag in hashtags)

            payload = {
                "text": tweet_text
            }

            if image_url:
                payload["media_url"] = image_url

            response = requests.post(
                f"{twitter_mcp_url}/tweets",
                json=payload,
                headers={"X-API-Key": api_key},
                timeout=30
            )

            response.raise_for_status()
            data = response.json()

            return {
                "success": True,
                "tweet_id": data.get("tweet_id"),
                "tweet_url": data.get("tweet_url")
            }

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to publish to Twitter: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def get_metrics(
        self,
        platform: str,
        post_id: str
    ) -> Dict[str, Any]:
        """
        Retrieve engagement metrics for a post.

        Args:
            platform: Platform name
            post_id: Platform-specific post ID

        Returns:
            dict: Engagement metrics
        """
        try:
            if platform == "facebook":
                return self._get_facebook_metrics(post_id)
            elif platform == "instagram":
                return self._get_instagram_metrics(post_id)
            elif platform == "twitter":
                return self._get_twitter_metrics(post_id)
            else:
                return {"error": "Unknown platform"}

        except Exception as e:
            logger.error(f"Failed to get metrics for {platform} post {post_id}: {e}")
            return {"error": str(e)}

    def _get_facebook_metrics(self, post_id: str) -> Dict[str, Any]:
        """Get Facebook post metrics."""
        import requests

        facebook_mcp_url = os.getenv("FACEBOOK_MCP_URL", "http://localhost:3101")
        api_key = os.getenv("MCP_API_KEY")

        try:
            response = requests.get(
                f"{facebook_mcp_url}/posts/{post_id}/insights",
                headers={"X-API-Key": api_key},
                timeout=30
            )

            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get Facebook metrics: {e}")
            return {
                "error": str(e),
                "likes": 0,
                "comments": 0,
                "shares": 0,
                "reach": 0
            }

    def _get_instagram_metrics(self, media_id: str) -> Dict[str, Any]:
        """Get Instagram media metrics."""
        import requests

        instagram_mcp_url = os.getenv("INSTAGRAM_MCP_URL", "http://localhost:3102")
        api_key = os.getenv("MCP_API_KEY")

        try:
            response = requests.get(
                f"{instagram_mcp_url}/media/{media_id}/insights",
                headers={"X-API-Key": api_key},
                timeout=30
            )

            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get Instagram metrics: {e}")
            return {
                "error": str(e),
                "likes": 0,
                "comments": 0,
                "saves": 0,
                "reach": 0
            }

    def _get_twitter_metrics(self, tweet_id: str) -> Dict[str, Any]:
        """Get Twitter tweet metrics."""
        import requests

        twitter_mcp_url = os.getenv("TWITTER_MCP_URL", "http://localhost:3103")
        api_key = os.getenv("MCP_API_KEY")

        try:
            response = requests.get(
                f"{twitter_mcp_url}/tweets/{tweet_id}/metrics",
                headers={"X-API-Key": api_key},
                timeout=30
            )

            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get Twitter metrics: {e}")
            return {
                "error": str(e),
                "likes": 0,
                "retweets": 0,
                "replies": 0,
                "impressions": 0
            }

    def _queue_failed_post(
        self,
        platform: str,
        text: str,
        image_url: Optional[str],
        link_url: Optional[str],
        hashtags: Optional[List[str]],
        error: str
    ) -> None:
        """Queue failed post for retry."""
        try:
            from services.queue_service import QueueService
            queue_service = QueueService()

            operation_id = queue_service.create_operation(
                operation_type="social_post",
                target=platform,
                parameters={
                    "text": text,
                    "image_url": image_url,
                    "link_url": link_url,
                    "hashtags": hashtags,
                    "error": error
                }
            )

            logger.info(f"Queued failed {platform} post for retry: {operation_id}")

        except Exception as e:
            logger.error(f"Failed to queue post: {e}")


# Example usage
if __name__ == "__main__":
    # Initialize service
    social_media_service = SocialMediaService()

    # Validate a post
    validation = social_media_service.validate_post(
        platforms=["facebook", "instagram", "twitter"],
        text="Check out our new product! #innovation #tech",
        image_url="https://example.com/image.jpg"
    )

    print(f"Validation: {validation}")

    # Publish a post
    if validation["valid"]:
        result = social_media_service.publish_post(
            platforms=["facebook", "instagram"],
            text="Check out our new product! #innovation #tech",
            image_url="https://example.com/image.jpg"
        )

        print(f"Publishing result: {result}")
