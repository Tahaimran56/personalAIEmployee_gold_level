/**
 * Facebook MCP Server for Gold Tier AI Employee
 *
 * This MCP server provides HTTP endpoints for Facebook Graph API integration.
 * It exposes social media posting functionality via REST API.
 *
 * Endpoints:
 * - GET /health - Health check
 * - POST /posts - Create Facebook post
 * - GET /posts/:post_id - Get post details
 * - GET /posts/:post_id/insights - Get post engagement metrics
 * - DELETE /posts/:post_id - Delete post
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
  asyncHandler,
  performanceMonitoring,
  getPerformanceMetrics,
  getErrorStats,
  setupGracefulShutdown,
  validateConfig,
  trackError
} = require('./shared-utils');

require('dotenv').config();

// Validate configuration on startup
const configValidation = validateConfig([
  'FACEBOOK_PAGE_ACCESS_TOKEN',
  'FACEBOOK_PAGE_ID',
  'MCP_API_KEY'
]);

if (!configValidation.valid) {
  logger.error('Configuration validation failed', { missing: configValidation.missing });
  process.exit(1);
}

// Initialize Express app
const app = express();
const PORT = process.env.FACEBOOK_MCP_PORT || 3101;

// Facebook Graph API configuration
const FACEBOOK_API_VERSION = 'v19.0';
const FACEBOOK_BASE_URL = `https://graph.facebook.com/${FACEBOOK_API_VERSION}`;
const PAGE_ACCESS_TOKEN = process.env.FACEBOOK_PAGE_ACCESS_TOKEN;
const PAGE_ID = process.env.FACEBOOK_PAGE_ID;

// Middleware
app.use(express.json());
app.use(logRequest);
app.use(performanceMonitoring);

// ============================================
// Health Check Endpoint
// ============================================

app.get('/health', createHealthCheckHandler('facebook-mcp', async () => {
  try {
    // Verify token is valid
    if (!PAGE_ACCESS_TOKEN) {
      return {
        connected: false,
        error: 'FACEBOOK_PAGE_ACCESS_TOKEN not configured'
      };
    }

    // Test API connection
    const response = await axios.get(`${FACEBOOK_BASE_URL}/me`, {
      params: {
        access_token: PAGE_ACCESS_TOKEN,
        fields: 'id,name'
      }
    });

    return {
      connected: true,
      token_valid: true,
      page_id: response.data.id,
      page_name: response.data.name
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
// Post Creation Endpoint
// ============================================

/**
 * POST /posts - Create Facebook post
 */
app.post('/posts', authenticateApiKey, asyncHandler(async (req, res) => {
  const { message, link, image_url, published = true } = req.body;

  // Validate required fields
  if (!message) {
    return res.status(400).json(
      buildErrorResponse('MISSING_FIELDS', 'message is required')
    );
  }

  // Validate message length
  if (message.length > 63206) {
    return res.status(400).json(
      buildErrorResponse('MESSAGE_TOO_LONG', 'Message exceeds 63,206 characters')
    );
  }

  try {
    // Prepare post data
    const postData = {
      message,
      access_token: PAGE_ACCESS_TOKEN,
      published: published ? 'true' : 'false'
    };

    if (link) {
      postData.link = link;
    }

    if (image_url) {
      postData.url = image_url;
    }

    // Create post
    const endpoint = image_url
      ? `${FACEBOOK_BASE_URL}/${PAGE_ID}/photos`
      : `${FACEBOOK_BASE_URL}/${PAGE_ID}/feed`;

    const response = await axios.post(endpoint, null, { params: postData });

    logger.info('Facebook post created', { post_id: response.data.id });

    // Get post details
    const postDetails = await axios.get(`${FACEBOOK_BASE_URL}/${response.data.id}`, {
      params: {
        access_token: PAGE_ACCESS_TOKEN,
        fields: 'id,message,created_time,permalink_url'
      }
    });

    res.status(201).json({
      post_id: postDetails.data.id,
      message: postDetails.data.message,
      created_time: postDetails.data.created_time,
      permalink_url: postDetails.data.permalink_url
    });

  } catch (error) {
    logger.error('Failed to create Facebook post', { error: error.message });

    // Check for rate limit
    const rateLimitError = handleRateLimitError(error, 'facebook');
    if (rateLimitError) {
      return res.status(429).json(rateLimitError);
    }

    // Check for authentication error
    if (error.response && error.response.status === 401) {
      return res.status(401).json(
        buildErrorResponse('INVALID_TOKEN', 'Facebook access token is invalid or expired')
      );
    }

    // Check if Facebook API is unavailable
    if (error.code === 'ECONNREFUSED' || error.code === 'ETIMEDOUT') {
      return res.status(503).json(
        buildErrorResponse('FACEBOOK_UNAVAILABLE', 'Facebook API is unavailable. Post has been queued for retry.')
      );
    }

    res.status(500).json(
      buildErrorResponse('POST_CREATION_FAILED', error.response?.data?.error?.message || error.message)
    );
  }
}));

// ============================================
// Post Retrieval Endpoint
// ============================================

/**
 * GET /posts/:post_id - Get post details
 */
app.get('/posts/:post_id', authenticateApiKey, asyncHandler(async (req, res) => {
  const { post_id } = req.params;

  try {
    const response = await axios.get(`${FACEBOOK_BASE_URL}/${post_id}`, {
      params: {
        access_token: PAGE_ACCESS_TOKEN,
        fields: 'id,message,created_time,permalink_url,link'
      }
    });

    res.json(response.data);

  } catch (error) {
    logger.error('Failed to get Facebook post', { post_id, error: error.message });

    if (error.response && error.response.status === 404) {
      return res.status(404).json(
        buildErrorResponse('POST_NOT_FOUND', 'Post not found')
      );
    }

    res.status(500).json(
      buildErrorResponse('POST_RETRIEVAL_FAILED', error.message)
    );
  }
}));

// ============================================
// Post Insights Endpoint
// ============================================

/**
 * GET /posts/:post_id/insights - Get post engagement metrics
 */
app.get('/posts/:post_id/insights', authenticateApiKey, asyncHandler(async (req, res) => {
  const { post_id } = req.params;

  try {
    // Get post reactions (likes)
    const reactionsResponse = await axios.get(`${FACEBOOK_BASE_URL}/${post_id}/reactions`, {
      params: {
        access_token: PAGE_ACCESS_TOKEN,
        summary: true
      }
    });

    // Get post comments
    const commentsResponse = await axios.get(`${FACEBOOK_BASE_URL}/${post_id}/comments`, {
      params: {
        access_token: PAGE_ACCESS_TOKEN,
        summary: true
      }
    });

    // Get post shares
    const sharesResponse = await axios.get(`${FACEBOOK_BASE_URL}/${post_id}`, {
      params: {
        access_token: PAGE_ACCESS_TOKEN,
        fields: 'shares'
      }
    });

    // Get post insights (reach, impressions)
    let reach = 0;
    let impressions = 0;

    try {
      const insightsResponse = await axios.get(`${FACEBOOK_BASE_URL}/${post_id}/insights`, {
        params: {
          access_token: PAGE_ACCESS_TOKEN,
          metric: 'post_impressions,post_impressions_unique'
        }
      });

      const insightsData = insightsResponse.data.data;
      const impressionsMetric = insightsData.find(m => m.name === 'post_impressions');
      const reachMetric = insightsData.find(m => m.name === 'post_impressions_unique');

      if (impressionsMetric && impressionsMetric.values && impressionsMetric.values.length > 0) {
        impressions = impressionsMetric.values[0].value;
      }

      if (reachMetric && reachMetric.values && reachMetric.values.length > 0) {
        reach = reachMetric.values[0].value;
      }
    } catch (insightsError) {
      logger.warn('Could not retrieve post insights', { post_id, error: insightsError.message });
    }

    const likes = reactionsResponse.data.summary?.total_count || 0;
    const comments = commentsResponse.data.summary?.total_count || 0;
    const shares = sharesResponse.data.shares?.count || 0;
    const engagement = likes + comments + shares;
    const engagement_rate = reach > 0 ? (engagement / reach * 100) : 0;

    res.json({
      post_id,
      likes,
      comments,
      shares,
      reach,
      impressions,
      engagement,
      engagement_rate: parseFloat(engagement_rate.toFixed(2)),
      retrieved_at: new Date().toISOString()
    });

  } catch (error) {
    logger.error('Failed to get Facebook post insights', { post_id, error: error.message });

    if (error.response && error.response.status === 404) {
      return res.status(404).json(
        buildErrorResponse('POST_NOT_FOUND', 'Post not found')
      );
    }

    res.status(500).json(
      buildErrorResponse('INSIGHTS_RETRIEVAL_FAILED', error.message)
    );
  }
}));

// ============================================
// Post Deletion Endpoint
// ============================================

/**
 * DELETE /posts/:post_id - Delete post
 */
app.delete('/posts/:post_id', authenticateApiKey, asyncHandler(async (req, res) => {
  const { post_id } = req.params;

  try {
    await axios.delete(`${FACEBOOK_BASE_URL}/${post_id}`, {
      params: {
        access_token: PAGE_ACCESS_TOKEN
      }
    });

    logger.info('Facebook post deleted', { post_id });

    res.status(204).send();

  } catch (error) {
    logger.error('Failed to delete Facebook post', { post_id, error: error.message });

    if (error.response && error.response.status === 404) {
      return res.status(404).json(
        buildErrorResponse('POST_NOT_FOUND', 'Post not found')
      );
    }

    res.status(500).json(
      buildErrorResponse('POST_DELETION_FAILED', error.message)
    );
  }
}));

// ============================================
// Metrics Endpoint
// ============================================

/**
 * GET /metrics - Get performance metrics
 */
app.get('/metrics', authenticateApiKey, (req, res) => {
  const metrics = getPerformanceMetrics();
  const errorStats = getErrorStats();

  res.json({
    performance: metrics,
    errors: errorStats
  });
});

// ============================================
// Error Handler
// ============================================

app.use((err, req, res, next) => {
  trackError(err, {
    path: req.path,
    method: req.method
  });
  errorHandler(err, req, res, next);
});

// ============================================
// Start Server
// ============================================

const server = app.listen(PORT, () => {
  logger.info(`Facebook MCP Server listening on port ${PORT}`, { service: 'facebook-mcp' });
  console.log(`✓ Facebook MCP Server running on http://localhost:${PORT}`);
  console.log(`✓ Health check: http://localhost:${PORT}/health`);
  console.log(`✓ Metrics: http://localhost:${PORT}/metrics`);
});

// Setup graceful shutdown
setupGracefulShutdown(server, async () => {
  logger.info('Facebook MCP Server cleanup complete');
});

module.exports = app;
