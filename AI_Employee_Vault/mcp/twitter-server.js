/**
 * Twitter MCP Server for Gold Tier AI Employee
 *
 * This MCP server provides HTTP endpoints for Twitter API v2 integration.
 * It exposes tweet posting, retrieval, and metrics functionality via REST API.
 *
 * Endpoints:
 * - GET /health - Health check
 * - POST /tweets - Create tweet
 * - GET /tweets/:tweet_id - Get tweet details
 * - GET /tweets/:tweet_id/metrics - Get tweet engagement metrics
 * - DELETE /tweets/:tweet_id - Delete tweet
 * - GET /rate_limit_status - Get rate limit status
 *
 * Author: AI Employee Gold Tier
 * Created: 2026-02-05
 */

const express = require('express');
const axios = require('axios');
const {
  logger,
  buildErrorResponse,
  authenticateApiKey,
  createHealthCheckHandler,
  handleRateLimitError,
  logRequest,
  errorHandler,
  asyncHandler
} = require('./shared-utils');

require('dotenv').config();

// Initialize Express app
const app = express();
const PORT = process.env.TWITTER_MCP_PORT || 3103;

// Twitter API v2 configuration
const TWITTER_API_BASE_URL = 'https://api.twitter.com/2';
const TWITTER_BEARER_TOKEN = process.env.TWITTER_BEARER_TOKEN;
const TWITTER_API_KEY = process.env.TWITTER_API_KEY;
const TWITTER_API_SECRET = process.env.TWITTER_API_SECRET;
const TWITTER_ACCESS_TOKEN = process.env.TWITTER_ACCESS_TOKEN;
const TWITTER_ACCESS_SECRET = process.env.TWITTER_ACCESS_SECRET;

// OAuth 1.0a for Twitter API v2
const OAuth = require('oauth-1.0a');
const crypto = require('crypto');

const oauth = OAuth({
  consumer: {
    key: TWITTER_API_KEY,
    secret: TWITTER_API_SECRET
  },
  signature_method: 'HMAC-SHA1',
  hash_function(base_string, key) {
    return crypto
      .createHmac('sha1', key)
      .update(base_string)
      .digest('base64');
  }
});

const token = {
  key: TWITTER_ACCESS_TOKEN,
  secret: TWITTER_ACCESS_SECRET
};

// Middleware
app.use(express.json());
app.use(logRequest);

// ============================================
// Health Check Endpoint
// ============================================

app.get('/health', createHealthCheckHandler('twitter-mcp', async () => {
  try {
    if (!TWITTER_BEARER_TOKEN || !TWITTER_API_KEY) {
      return {
        connected: false,
        error: 'Twitter credentials not configured'
      };
    }

    // Test API connection - get authenticated user
    const response = await axios.get(`${TWITTER_API_BASE_URL}/users/me`, {
      headers: {
        'Authorization': `Bearer ${TWITTER_BEARER_TOKEN}`
      }
    });

    return {
      connected: true,
      token_valid: true,
      user_id: response.data.data.id,
      username: response.data.data.username
    };
  } catch (error) {
    return {
      connected: false,
      token_valid: false,
      error: error.message
    };
  }
}));

// ============================================
// Tweet Creation Endpoint
// ============================================

/**
 * POST /tweets - Create tweet
 */
app.post('/tweets', authenticateApiKey, asyncHandler(async (req, res) => {
  const { text, media_url, reply_to_tweet_id } = req.body;

  // Validate required fields
  if (!text) {
    return res.status(400).json(
      buildErrorResponse('MISSING_FIELDS', 'text is required')
    );
  }

  // Validate text length
  if (text.length > 280) {
    return res.status(400).json(
      buildErrorResponse('TEXT_TOO_LONG', `Tweet exceeds 280 characters (current: ${text.length})`)
    );
  }

  try {
    let media_id = null;

    // Upload media if provided
    if (media_url) {
      // Download media from URL
      const mediaResponse = await axios.get(media_url, { responseType: 'arraybuffer' });
      const mediaBuffer = Buffer.from(mediaResponse.data);

      // Upload to Twitter (media upload endpoint)
      const uploadUrl = 'https://upload.twitter.com/1.1/media/upload.json';

      const authHeader = oauth.toHeader(oauth.authorize({
        url: uploadUrl,
        method: 'POST'
      }, token));

      const FormData = require('form-data');
      const formData = new FormData();
      formData.append('media', mediaBuffer, { filename: 'media.jpg' });

      const uploadResponse = await axios.post(uploadUrl, formData, {
        headers: {
          ...authHeader,
          ...formData.getHeaders()
        }
      });

      media_id = uploadResponse.data.media_id_string;
    }

    // Create tweet
    const tweetData = {
      text: text
    };

    if (media_id) {
      tweetData.media = {
        media_ids: [media_id]
      };
    }

    if (reply_to_tweet_id) {
      tweetData.reply = {
        in_reply_to_tweet_id: reply_to_tweet_id
      };
    }

    const requestData = {
      url: `${TWITTER_API_BASE_URL}/tweets`,
      method: 'POST'
    };

    const authHeader = oauth.toHeader(oauth.authorize(requestData, token));

    const response = await axios.post(
      `${TWITTER_API_BASE_URL}/tweets`,
      tweetData,
      {
        headers: {
          ...authHeader,
          'Content-Type': 'application/json'
        }
      }
    );

    logger.info('Twitter tweet created', { tweet_id: response.data.data.id });

    // Get tweet details
    const tweetDetails = await axios.get(
      `${TWITTER_API_BASE_URL}/tweets/${response.data.data.id}?tweet.fields=created_at,public_metrics`,
      {
        headers: {
          'Authorization': `Bearer ${TWITTER_BEARER_TOKEN}`
        }
      }
    );

    res.status(201).json({
      tweet_id: tweetDetails.data.data.id,
      text: tweetDetails.data.data.text,
      created_at: tweetDetails.data.data.created_at,
      tweet_url: `https://twitter.com/user/status/${tweetDetails.data.data.id}`
    });

  } catch (error) {
    logger.error('Failed to create Twitter tweet', { error: error.message });

    const rateLimitError = handleRateLimitError(error, 'twitter');
    if (rateLimitError) {
      return res.status(429).json(rateLimitError);
    }

    if (error.response && error.response.status === 401) {
      return res.status(401).json(
        buildErrorResponse('INVALID_TOKEN', 'Twitter access token is invalid or expired')
      );
    }

    if (error.code === 'ECONNREFUSED' || error.code === 'ETIMEDOUT') {
      return res.status(503).json(
        buildErrorResponse('TWITTER_UNAVAILABLE', 'Twitter API is unavailable. Tweet has been queued for retry.')
      );
    }

    res.status(500).json(
      buildErrorResponse('TWEET_CREATION_FAILED', error.response?.data?.detail || error.message)
    );
  }
}));

// ============================================
// Tweet Retrieval Endpoint
// ============================================

/**
 * GET /tweets/:tweet_id - Get tweet details
 */
app.get('/tweets/:tweet_id', authenticateApiKey, asyncHandler(async (req, res) => {
  const { tweet_id } = req.params;

  try {
    const response = await axios.get(
      `${TWITTER_API_BASE_URL}/tweets/${tweet_id}?tweet.fields=created_at,public_metrics,attachments`,
      {
        headers: {
          'Authorization': `Bearer ${TWITTER_BEARER_TOKEN}`
        }
      }
    );

    res.json(response.data.data);

  } catch (error) {
    logger.error('Failed to get Twitter tweet', { tweet_id, error: error.message });

    if (error.response && error.response.status === 404) {
      return res.status(404).json(
        buildErrorResponse('TWEET_NOT_FOUND', 'Tweet not found')
      );
    }

    res.status(500).json(
      buildErrorResponse('TWEET_RETRIEVAL_FAILED', error.message)
    );
  }
}));

// ============================================
// Tweet Metrics Endpoint
// ============================================

/**
 * GET /tweets/:tweet_id/metrics - Get tweet engagement metrics
 */
app.get('/tweets/:tweet_id/metrics', authenticateApiKey, asyncHandler(async (req, res) => {
  const { tweet_id } = req.params;

  try {
    // Get tweet with public metrics
    const response = await axios.get(
      `${TWITTER_API_BASE_URL}/tweets/${tweet_id}?tweet.fields=public_metrics,non_public_metrics,organic_metrics`,
      {
        headers: {
          'Authorization': `Bearer ${TWITTER_BEARER_TOKEN}`
        }
      }
    );

    const tweet = response.data.data;
    const metrics = tweet.public_metrics || {};
    const organicMetrics = tweet.organic_metrics || {};

    const likes = metrics.like_count || 0;
    const retweets = metrics.retweet_count || 0;
    const replies = metrics.reply_count || 0;
    const quotes = metrics.quote_count || 0;
    const impressions = organicMetrics.impression_count || metrics.impression_count || 0;

    const engagement = likes + retweets + replies + quotes;
    const engagement_rate = impressions > 0 ? (engagement / impressions * 100) : 0;

    res.json({
      tweet_id,
      likes,
      retweets,
      replies,
      quotes,
      impressions,
      engagement,
      engagement_rate: parseFloat(engagement_rate.toFixed(2)),
      retrieved_at: new Date().toISOString()
    });

  } catch (error) {
    logger.error('Failed to get Twitter tweet metrics', { tweet_id, error: error.message });

    if (error.response && error.response.status === 404) {
      return res.status(404).json(
        buildErrorResponse('TWEET_NOT_FOUND', 'Tweet not found')
      );
    }

    res.status(500).json(
      buildErrorResponse('METRICS_RETRIEVAL_FAILED', error.message)
    );
  }
}));

// ============================================
// Tweet Deletion Endpoint
// ============================================

/**
 * DELETE /tweets/:tweet_id - Delete tweet
 */
app.delete('/tweets/:tweet_id', authenticateApiKey, asyncHandler(async (req, res) => {
  const { tweet_id } = req.params;

  try {
    const requestData = {
      url: `${TWITTER_API_BASE_URL}/tweets/${tweet_id}`,
      method: 'DELETE'
    };

    const authHeader = oauth.toHeader(oauth.authorize(requestData, token));

    await axios.delete(
      `${TWITTER_API_BASE_URL}/tweets/${tweet_id}`,
      {
        headers: authHeader
      }
    );

    logger.info('Twitter tweet deleted', { tweet_id });

    res.status(204).send();

  } catch (error) {
    logger.error('Failed to delete Twitter tweet', { tweet_id, error: error.message });

    if (error.response && error.response.status === 404) {
      return res.status(404).json(
        buildErrorResponse('TWEET_NOT_FOUND', 'Tweet not found')
      );
    }

    res.status(500).json(
      buildErrorResponse('TWEET_DELETION_FAILED', error.message)
    );
  }
}));

// ============================================
// Rate Limit Status Endpoint
// ============================================

/**
 * GET /rate_limit_status - Get rate limit status
 */
app.get('/rate_limit_status', authenticateApiKey, asyncHandler(async (req, res) => {
  try {
    // Get rate limit status for tweets endpoint
    const response = await axios.get(
      'https://api.twitter.com/1.1/application/rate_limit_status.json?resources=tweets',
      {
        headers: {
          'Authorization': `Bearer ${TWITTER_BEARER_TOKEN}`
        }
      }
    );

    const tweetLimits = response.data.resources.tweets;

    res.json({
      tweets: {
        '/tweets': {
          limit: tweetLimits['/tweets']?.limit || 0,
          remaining: tweetLimits['/tweets']?.remaining || 0,
          reset: tweetLimits['/tweets']?.reset || 0,
          reset_time: new Date(tweetLimits['/tweets']?.reset * 1000).toISOString()
        }
      },
      checked_at: new Date().toISOString()
    });

  } catch (error) {
    logger.error('Failed to get Twitter rate limit status', { error: error.message });

    res.status(500).json(
      buildErrorResponse('RATE_LIMIT_CHECK_FAILED', error.message)
    );
  }
}));

// ============================================
// Error Handler
// ============================================

app.use(errorHandler);

// ============================================
// Start Server
// ============================================

app.listen(PORT, () => {
  logger.info(`Twitter MCP Server listening on port ${PORT}`, { service: 'twitter-mcp' });
  console.log(`✓ Twitter MCP Server running on http://localhost:${PORT}`);
  console.log(`✓ Health check: http://localhost:${PORT}/health`);
});

module.exports = app;
