"""
LinkedIn Service - LinkedIn Business Posts
Handles LinkedIn post drafting, approval workflow, and publishing via LinkedIn API
"""

import os
import json
import re
import requests
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Optional, List
from dotenv import load_dotenv, set_key
import logging


class LinkedInService:
    """
    LinkedIn service for composing and publishing posts with approval workflow.

    Features:
    - Draft post composition
    - Post content validation (3000 char limit, hashtags)
    - Approval workflow integration
    - LinkedIn Share API integration
    - OAuth2 token management (60-day expiry)
    - Engagement metrics fetching
    - Post logging
    - Error handling
    """

    # LinkedIn API endpoints
    SHARE_API_URL = 'https://api.linkedin.com/v2/ugcPosts'
    PROFILE_URL = 'https://api.linkedin.com/v2/userinfo'
    ANALYTICS_URL = 'https://api.linkedin.com/v2/organizationalEntityShareStatistics'

    # Content limits
    MAX_POST_LENGTH = 3000
    MAX_HASHTAGS = 30

    def __init__(self, vault_path: str):
        """
        Initialize LinkedIn Service.

        Args:
            vault_path: Path to Obsidian vault
        """
        self.vault_path = Path(vault_path)
        self.pending_approval = self.vault_path / 'Pending_Approval'
        self.approved = self.vault_path / 'Approved'
        self.logs = self.vault_path / 'Logs'

        # Ensure directories exist
        self.pending_approval.mkdir(parents=True, exist_ok=True)
        self.approved.mkdir(parents=True, exist_ok=True)
        self.logs.mkdir(parents=True, exist_ok=True)

        # Load configuration
        env_path = Path(__file__).parent.parent.parent / 'config' / '.env'
        load_dotenv(env_path)
        self.env_path = env_path

        self.access_token = os.getenv('LINKEDIN_ACCESS_TOKEN')
        self.person_id = os.getenv('LINKEDIN_PERSON_ID')

        if not self.access_token or not self.person_id:
            raise ValueError("LinkedIn credentials not found in config/.env. Run: python AI_Employee_Vault/setup/linkedin_auth.py")

        # Setup logging
        self.logger = self._setup_logger()

        self.logger.info("LinkedIn Service initialized")

    def _setup_logger(self) -> logging.Logger:
        """Set up logging for LinkedIn service."""
        logger = logging.getLogger('LinkedInService')
        logger.setLevel(logging.INFO)

        log_file = self.logs / 'linkedin_service.log'
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.INFO)

        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)

        logger.addHandler(file_handler)
        return logger

    def compose_draft_post(self, content: str, visibility: str = 'PUBLIC',
                          hashtags: List[str] = None) -> Dict:
        """
        Compose a draft LinkedIn post and create approval request.

        Args:
            content: Post content text
            visibility: Post visibility (PUBLIC, CONNECTIONS, LOGGED_IN)
            hashtags: List of hashtags to include

        Returns:
            Dict with draft_id and draft_file_path
        """
        self.logger.info("Composing draft LinkedIn post")

        # Validate content
        validation = self.validate_post_content(content, hashtags)
        if not validation['valid']:
            raise ValueError(f"Invalid post content: {validation['errors']}")

        # Add hashtags to content if provided
        if hashtags:
            content = content.strip() + '\n\n' + ' '.join(f'#{tag}' for tag in hashtags)

        # Generate draft ID
        draft_id = f"linkedin-draft-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"

        # Create draft file
        draft_file = self.pending_approval / f"{draft_id}.md"

        # Build frontmatter
        frontmatter = {
            'entity_type': 'draft_linkedin_post',
            'draft_id': draft_id,
            'visibility': visibility,
            'created_timestamp': datetime.utcnow().isoformat() + 'Z',
            'approval_status': 'pending',
            'published_status': 'not_published',
            'character_count': len(content)
        }

        if hashtags:
            frontmatter['hashtags'] = hashtags

        # Build body
        markdown_body = f"""
# Draft LinkedIn Post

**Visibility**: {visibility}
**Status**: ⏳ Pending Approval
**Character Count**: {len(content)} / {self.MAX_POST_LENGTH}

## Post Content

{content}

## Hashtags

"""

        if hashtags:
            for tag in hashtags:
                markdown_body += f"- #{tag}\n"
        else:
            markdown_body += "None\n"

        markdown_body += """
## Approval Actions
- ✅ **Approve**: Move this file to Approved/ folder
- ❌ **Reject**: Move this file to Done/ folder with rejection reason

**Note**: Post will be published automatically after approval.
"""

        # Write draft file
        self._create_markdown_file(draft_file, frontmatter, markdown_body)

        self.logger.info(f"Created draft LinkedIn post: {draft_file}")

        return {
            'draft_id': draft_id,
            'draft_file_path': str(draft_file),
            'approval_status': 'pending',
            'created_timestamp': frontmatter['created_timestamp'],
            'character_count': len(content)
        }

    def validate_post_content(self, content: str, hashtags: List[str] = None) -> Dict:
        """
        Validate LinkedIn post content.

        Args:
            content: Post content text
            hashtags: List of hashtags

        Returns:
            Dict with valid status and errors list
        """
        errors = []

        # Check content length
        if not content or not content.strip():
            errors.append("Post content cannot be empty")

        if len(content) > self.MAX_POST_LENGTH:
            errors.append(f"Post exceeds maximum length: {len(content)} / {self.MAX_POST_LENGTH} characters")

        # Check hashtags
        if hashtags:
            if len(hashtags) > self.MAX_HASHTAGS:
                errors.append(f"Too many hashtags: {len(hashtags)} / {self.MAX_HASHTAGS}")

            for tag in hashtags:
                # Validate hashtag format (alphanumeric, no spaces)
                if not re.match(r'^[a-zA-Z0-9_]+$', tag):
                    errors.append(f"Invalid hashtag format: #{tag} (use only letters, numbers, underscores)")

        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'character_count': len(content),
            'hashtag_count': len(hashtags) if hashtags else 0
        }

    def publish_post(self, draft_id: str) -> Dict:
        """
        Publish an approved draft post via LinkedIn API.

        Args:
            draft_id: Draft ID to publish

        Returns:
            Dict with success status, post_id, and published_timestamp
        """
        self.logger.info(f"Attempting to publish LinkedIn post: {draft_id}")

        # Find draft file in Approved folder
        draft_file = self.approved / f"{draft_id}.md"

        if not draft_file.exists():
            raise FileNotFoundError(f"Draft not found in Approved folder: {draft_id}")

        # Parse draft file
        draft_data = self._parse_draft_file(draft_file)

        # Verify approval status
        if draft_data.get('approval_status') != 'approved':
            raise ValueError(f"Draft not approved: {draft_id}")

        # Check token expiry
        self._check_token_expiry()

        # Publish via LinkedIn API
        try:
            response = self._publish_via_linkedin_api(draft_data)

            if response.get('id'):
                post_id = response['id']
                published_timestamp = datetime.utcnow().isoformat() + 'Z'

                # Log published post
                self._log_published_post(draft_data, post_id, published_timestamp)

                # Move draft to Done
                done_folder = self.vault_path / 'Done'
                done_folder.mkdir(parents=True, exist_ok=True)
                draft_file.rename(done_folder / draft_file.name)

                self.logger.info(f"Post published successfully: {post_id}")

                return {
                    'success': True,
                    'post_id': post_id,
                    'published_timestamp': published_timestamp,
                    'log_file_path': str(self.logs / f"linkedin-post-{draft_id}.md")
                }
            else:
                error = response.get('message', 'Unknown error')
                self.logger.error(f"Failed to publish post: {error}")
                return {
                    'success': False,
                    'error': error
                }

        except requests.exceptions.RequestException as e:
            self.logger.error(f"LinkedIn API error: {e}")
            self._handle_api_error(e)
            raise
        except Exception as e:
            self.logger.error(f"Error publishing post: {e}")
            raise

    def _publish_via_linkedin_api(self, draft_data: Dict) -> Dict:
        """
        Publish post via LinkedIn Share API.

        Args:
            draft_data: Draft post data

        Returns:
            Response from LinkedIn API
        """
        # Extract content from draft
        content = draft_data.get('content', '')

        # Build API request payload
        payload = {
            "author": f"urn:li:person:{self.person_id}",
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {
                        "text": content
                    },
                    "shareMediaCategory": "NONE"
                }
            },
            "visibility": {
                "com.linkedin.ugc.MemberNetworkVisibility": draft_data.get('visibility', 'PUBLIC')
            }
        }

        # Send request to LinkedIn API
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json',
            'X-Restli-Protocol-Version': '2.0.0'
        }

        response = requests.post(
            self.SHARE_API_URL,
            json=payload,
            headers=headers,
            timeout=30
        )

        response.raise_for_status()
        return response.json()

    def get_engagement_metrics(self, post_id: str) -> Dict:
        """
        Fetch engagement metrics for a published post.

        Args:
            post_id: LinkedIn post ID

        Returns:
            Dict with likes, comments, shares, impressions
        """
        self.logger.info(f"Fetching engagement metrics for post: {post_id}")

        try:
            # Check token expiry
            self._check_token_expiry()

            # Fetch analytics from LinkedIn API
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'X-Restli-Protocol-Version': '2.0.0'
            }

            # Note: LinkedIn analytics API requires specific permissions
            # This is a simplified implementation
            params = {
                'q': 'organizationalEntity',
                'organizationalEntity': f"urn:li:person:{self.person_id}",
                'shares': post_id
            }

            response = requests.get(
                self.ANALYTICS_URL,
                headers=headers,
                params=params,
                timeout=30
            )

            if response.status_code == 200:
                data = response.json()
                # Extract metrics from response
                metrics = {
                    'likes': data.get('likeCount', 0),
                    'comments': data.get('commentCount', 0),
                    'shares': data.get('shareCount', 0),
                    'impressions': data.get('impressionCount', 0),
                    'fetched_timestamp': datetime.utcnow().isoformat() + 'Z'
                }

                self.logger.info(f"Metrics fetched: {metrics}")
                return metrics
            else:
                self.logger.warning(f"Could not fetch metrics: {response.status_code}")
                return {
                    'error': f"API returned {response.status_code}",
                    'fetched_timestamp': datetime.utcnow().isoformat() + 'Z'
                }

        except Exception as e:
            self.logger.error(f"Error fetching metrics: {e}")
            return {
                'error': str(e),
                'fetched_timestamp': datetime.utcnow().isoformat() + 'Z'
            }

    def _check_token_expiry(self):
        """
        Check if LinkedIn access token is expired or expiring soon.
        LinkedIn tokens expire after 60 days.
        """
        # Check if token file exists with timestamp
        token_file = Path(__file__).parent.parent.parent / 'token_linkedin.json'

        if token_file.exists():
            try:
                with open(token_file, 'r') as f:
                    token_data = json.load(f)

                created_timestamp = datetime.fromisoformat(token_data.get('created_timestamp', '').replace('Z', ''))
                expiry_date = created_timestamp + timedelta(days=60)

                days_until_expiry = (expiry_date - datetime.utcnow()).days

                if days_until_expiry <= 0:
                    self.logger.error("LinkedIn access token has expired")
                    raise ValueError("LinkedIn access token expired. Run: python AI_Employee_Vault/setup/linkedin_auth.py")
                elif days_until_expiry <= 7:
                    self.logger.warning(f"LinkedIn access token expires in {days_until_expiry} days. Consider refreshing.")

            except Exception as e:
                self.logger.warning(f"Could not check token expiry: {e}")
        else:
            self.logger.warning("Token file not found. Cannot verify expiry.")

    def _handle_api_error(self, error: requests.exceptions.RequestException):
        """
        Handle LinkedIn API errors.

        Args:
            error: Request exception
        """
        if hasattr(error, 'response') and error.response is not None:
            status_code = error.response.status_code

            if status_code == 401:
                self.logger.error("Authentication failed. Token may be expired. Run: python AI_Employee_Vault/setup/linkedin_auth.py")
                raise ValueError("LinkedIn authentication failed. Please refresh access token.")
            elif status_code == 403:
                self.logger.error("Permission denied. Check LinkedIn app permissions.")
                raise ValueError("LinkedIn API permission denied. Check app settings.")
            elif status_code == 429:
                self.logger.error("Rate limit exceeded. Please wait and try again.")
                raise ValueError("LinkedIn API rate limit exceeded. Please wait before retrying.")
            elif status_code == 422:
                self.logger.error("Invalid post content. Check content format and length.")
                raise ValueError("LinkedIn rejected post content. Check validation rules.")
            else:
                self.logger.error(f"LinkedIn API error: {status_code}")
                raise ValueError(f"LinkedIn API error: {status_code}")
        else:
            self.logger.error(f"Network error: {error}")
            raise ValueError(f"Network error: {error}")

    def _parse_draft_file(self, file_path: Path) -> Dict:
        """
        Parse draft LinkedIn post file.

        Args:
            file_path: Path to draft file

        Returns:
            Dict with draft data
        """
        content = file_path.read_text(encoding='utf-8')

        # Extract frontmatter
        draft_data = {}
        if content.startswith('---'):
            parts = content.split('---', 2)
            if len(parts) >= 3:
                frontmatter_text = parts[1]
                body_text = parts[2].strip()

                # Parse YAML frontmatter (simple parsing)
                for line in frontmatter_text.strip().split('\n'):
                    if ':' in line:
                        key, value = line.split(':', 1)
                        draft_data[key.strip()] = value.strip()

                # Extract post content from markdown
                # Look for "## Post Content" section
                if '## Post Content' in body_text:
                    content_parts = body_text.split('## Post Content', 1)[1]
                    content_parts = content_parts.split('##', 1)[0].strip()
                    draft_data['content'] = content_parts

        return draft_data

    def _log_published_post(self, draft_data: Dict, post_id: str, published_timestamp: str):
        """
        Log published post to Logs folder.

        Args:
            draft_data: Draft post data
            post_id: LinkedIn post ID
            published_timestamp: When post was published
        """
        log_file = self.logs / f"linkedin-post-{draft_data['draft_id']}.md"

        frontmatter = {
            'entity_type': 'published_linkedin_post',
            'draft_id': draft_data['draft_id'],
            'post_id': post_id,
            'visibility': draft_data.get('visibility', 'PUBLIC'),
            'published_timestamp': published_timestamp,
            'approved_by': 'user',
            'approval_timestamp': draft_data.get('approval_timestamp', published_timestamp)
        }

        body = f"""
# Published LinkedIn Post

**Post ID**: {post_id}
**Published**: {published_timestamp}
**Visibility**: {draft_data.get('visibility', 'PUBLIC')}
**Status**: ✅ Published Successfully

## Post Content
{draft_data.get('content', '[Content not available]')}

## Publishing Details
- Published via: LinkedIn Share API
- Authentication: OAuth2
- Status: Successful

## Engagement Metrics
To fetch metrics, run:
```python
from AI_Employee_Vault.services.linkedin_service import LinkedInService
service = LinkedInService('AI_Employee_Vault')
metrics = service.get_engagement_metrics('{post_id}')
```
"""

        self._create_markdown_file(log_file, frontmatter, body)

    def _create_markdown_file(self, file_path: Path, frontmatter: Dict, body: str):
        """
        Create a Markdown file with YAML frontmatter.

        Args:
            file_path: Path where file should be created
            frontmatter: Dictionary of frontmatter data
            body: Markdown body content
        """
        # Convert frontmatter to YAML
        yaml_lines = ['---']
        for key, value in frontmatter.items():
            if isinstance(value, list):
                yaml_lines.append(f'{key}:')
                for item in value:
                    yaml_lines.append(f'  - {item}')
            else:
                yaml_lines.append(f'{key}: {value}')
        yaml_lines.append('---')
        yaml_lines.append('')

        # Combine frontmatter and body
        content = '\n'.join(yaml_lines) + body

        # Write file
        file_path.write_text(content, encoding='utf-8')


# Example usage
if __name__ == '__main__':
    import sys

    # Get vault path
    if len(sys.argv) > 1:
        vault_path = sys.argv[1]
    else:
        vault_path = Path(__file__).parent.parent

    # Create service
    service = LinkedInService(str(vault_path))

    # Example: Compose draft post
    draft = service.compose_draft_post(
        content="Excited to share our latest AI automation project! 🚀\n\nWe've built a personal AI assistant that helps manage emails, tasks, and social media posts with human-in-the-loop approval.\n\nKey features:\n- Gmail monitoring\n- Email drafting\n- Multi-step task planning\n- LinkedIn integration\n\nBuilt with Python, Claude API, and lots of ☕",
        visibility='PUBLIC',
        hashtags=['AI', 'Automation', 'Python', 'ProductivityTools']
    )

    print(f"Draft created: {draft['draft_file_path']}")
    print("Move to Approved/ folder to publish")
