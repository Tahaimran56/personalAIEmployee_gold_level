/**
 * Instagram MCP Server for Gold Tier AI Employee
 *
 * This MCP server provides HTTP endpoints for Instagram Graph API integration.
 * Instagram uses Facebook's Graph API with a two-step publishing process.
 *
 * Endpoints:
 * - GET /health - Health check
 * - POST /media - Create media container (step 1)
 * - POST /media/publish - Publish media container (step 2)
 * - GET /media/:media_id - Get media details
 * - GET /media/:media_id/insights - Get media engagement metrics
 * - DELETE /media/:media_id - Delete media
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
  'INSTAGRAM_BUSINESS_ACCOUNT_ID',
  'MCP_API_KEY'
]);

if (!configValidation.valid) {
  logger.error('Configuration validation failed', { missing: configValidation.missing });
  process.exit(1);
}

// Initialize Express app
const app = express();
const PORT = process.env.INSTAGRAM_MCP_PORT || 3102;

// Instagram Graph API configuration
const INSTAGRAM_API_VERSION = 'v19.0';
const INSTAGRAM_BASE_URL = `https://graph.facebook.com/${INSTAGRAM_API_VERSION}`;
const PAGE_ACCESS_TOKEN = process.env.FACEBOOK_PAGE_ACCESS_TOKEN;
const INSTAGRAM_ACCOUNT_ID = process.env.INSTAGRAM_BUSINESS_ACCOUNT_ID;

// Middleware
app.use(express.json());
app.use(logRequest);
app.use(performanceMonitoring);

// ============================================
// Health Check Endpoint
// ============================================

app.get('/health', createHealthCheckHandler('instagram-mcp', async () => {
  try {
    if (!PAGE_ACCESS_TOKEN || !INSTAGRAM_ACCOUNT_ID) {
      return {
        connected: false,
        error: 'Instagram credentials not configured'
      };
    }

    // Test API connection
    const response = await axios.get(`${INSTAGRAM_BASE_URL}/${INSTAGRAM_ACCOUNT_ID}`, {
      params: {
        access_token: PAGE_ACCESS_TOKEN,
        fields: 'id,username'
      }
    });

    return {
      connected: true,
      token_valid: true,
      account_id: response.data.id,
      username: response.data.username
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
// Media Container Creation Endpoint (Step 1)
// ============================================

/**
 * POST /media - Create media container
 */
app.post('/media', authenticateApiKey, asyncHandler(async (req, res) => {
  const { image_url, caption, location_id, user_tags } = req.body;

  // Validate required fields
  if (!image_url || !caption) {
    return res.status(400).json(
      buildErrorResponse('MISSING_FIELDS', 'image_url and caption are required')
    );
  }

  // Validate caption length
  if (caption.length > 2200) {
    return res.status(400).json(
      buildErrorResponse('CAPTION_TOO_LONG', 'Caption exceeds 2,200 characters')
    );
  }

  // Validate image URL
  if (!image_url.startsWith('http://') && !image_url.startsWith('https://')) {
    return res.status(400).json(
      buildErrorResponse('INVALID_IMAGE_URL', 'Image URL must start with http:// or https://')
    );
  }

  try {
    // Create media container
    const containerData = {
      image_url,
      caption,
      access_token: PAGE_ACCESS_TOKEN
    };

    if (location_id) {
      containerData.location_id = location_id;
    }

    if (user_tags && user_tags.length > 0) {
      containerData.user_tags = JSON.stringify(user_tags);
    }

    const response = await axios.post(
      `${INSTAGRAM_BASE_URL}/${INSTAGRAM_ACCOUNT_ID}/media`,
      null,
      { params: containerData }
    );

    logger.info('Instagram media container created', { container_id: response.data.id });

    // Check container status
    const statusResponse = await axios.get(`${INSTAGRAM_BASE_URL}/${response.data.id}`, {
      params: {
        access_token: PAGE_ACCESS_TOKEN,
        fields: 'id,status,status_code'
      }
    });

    res.status(201).json({
      container_id: statusResponse.data.id,
      status: statusResponse.data.status,
      status_code: statusResponse.data.status_code
    });

  } catch (error) {
    logger.error('Failed to create Instagram media container', { error: error.message });

    const rateLimitError = handleRateLimitError(error, 'instagram');
    if (rateLimitError) {
      return res.status(429).json(rateLimitError);
    }

    if (error.response && error.response.status === 401) {
      return res.status(401).json(
        buildErrorResponse('INVALID_TOKEN', 'Instagram access token is invalid or expired')
      );
    }

    if (error.code === 'ECONNREFUSED' || error.code === 'ETIMEDOUT') {
      return res.status(503).json(
        buildErrorResponse('INSTAGRAM_UNAVAILABLE', 'Instagram API is unavailable. Post has been queued for retry.')
      );
    }

    res.status(500).json(
      buildErrorResponse('CONTAINER_CREATION_FAILED', error.response?.data?.error?.message || error.message)
    );
  }
}));

// ============================================
// Media Publishing Endpoint (Step 2)
// ============================================

/**
 * POST /media/publish - Publish media container
 */
app.post('/media/publish', authenticateApiKey, asyncHandler(async (req, res) => {
  const { container_id } = req.body;

  if (!container_id) {
    return res.status(400).json(
      buildErrorResponse('MISSING_FIELDS', 'container_id is required')
    );
  }

  try {
    // Check if container is ready
    const statusResponse = await axios.get(`${INSTAGRAM_BASE_URL}/${container_id}`, {
      params: {
        access_token: PAGE_ACCESS_TOKEN,
        fields: 'status,status_code'
      }
    });

    if (statusResponse.data.status !== 'FINISHED') {
      return res.status(400).json(
        buildErrorResponse('CONTAINER_NOT_READY', `Container status is ${statusResponse.data.status}. Wait for FINISHED status before publishing.`)
      );
    }

    // Publish media
    const response = await axios.post(
      `${INSTAGRAM_BASE_URL}/${INSTAGRAM_ACCOUNT_ID}/media_publish`,
      null,
      {
        params: {
          creation_id: container_id,
          access_token: PAGE_ACCESS_TOKEN
        }
      }
    );

    logger.info('Instagram media published', { media_id: response.data.id });

    // Get media details
    const mediaDetails = await axios.get(`${INSTAGRAM_BASE_URL}/${response.data.id}`, {
      params: {
        access_token: PAGE_ACCESS_TOKEN,
        fields: 'id,media_type,caption,permalink,timestamp'
      }
    });

    res.status(201).json({
      media_id: mediaDetails.data.id,
      permalink: mediaDetails.data.permalink
    });

  } catch (error) {
    logger.error('Failed to publish Instagram media', { container_id, error: error.message });

    if (error.response && error.response.status === 404) {
      return res.status(404).json(
        buildErrorResponse('CONTAINER_NOT_FOUND', 'Media container not found')
      );
    }

    res.status(500).json(
      buildErrorResponse('MEDIA_PUBLISH_FAILED', error.response?.data?.error?.message || error.message)
    );
  }
}));

// ============================================
// Media Retrieval Endpoint
// ============================================

/**
 * GET /media/:media_id - Get media details
 */
app.get('/media/:media_id', authenticateApiKey, asyncHandler(async (req, res) => {
  const { media_id } = req.params;

  try {
    const response = await axios.get(`${INSTAGRAM_BASE_URL}/${media_id}`, {
      params: {
        access_token: PAGE_ACCESS_TOKEN,
        fields: 'id,media_type,caption,permalink,timestamp,thumbnail_url'
      }
    });

    res.json(response.data);

  } catch (error) {
    logger.error('Failed to get Instagram media', { media_id, error: error.message });

    if (error.response && error.response.status === 404) {
      return res.status(404).json(
        buildErrorResponse('MEDIA_NOT_FOUND', 'Media not found')
      );
    }

    res.status(500).json(
      buildErrorResponse('MEDIA_RETRIEVAL_FAILED', error.message)
    );
  }
}));

// ============================================
// Media Insights Endpoint
// ============================================

/**
 * GET /media/:media_id/insights - Get media engagement metrics
 */
app.get('/media/:media_id/insights', authenticateApiKey, asyncHandler(async (req, res) => {
  const { media_id } = req.params;

  try {
    // Get media insights
    const response = await axios.get(`${INSTAGRAM_BASE_URL}/${media_id}/insights`, {
      params: {
        access_token: PAGE_ACCESS_TOKEN,
        metric: 'engagement,impressions,reach,saved,likes,comments'
      }
    });

    const insights = {};
    response.data.data.forEach(metric => {
      insights[metric.name] = metric.values[0].value;
    });

    const engagement = insights.engagement || 0;
    const reach = insights.reach || 0;
    const engagement_rate = reach > 0 ? (engagement / reach * 100) : 0;

    res.json({
      media_id,
      likes: insights.likes || 0,
      comments: insights.comments || 0,
      saves: insights.saved || 0,
      reach: reach,
      impressions: insights.impressions || 0,
      engagement: engagement,
      engagement_rate: parseFloat(engagement_rate.toFixed(2)),
      retrieved_at: new Date().toISOString()
    });

  } catch (error) {
    logger.error('Failed to get Instagram media insights', { media_id, error: error.message });

    if (error.response && error.response.status === 404) {
      return res.status(404).json(
        buildErrorResponse('MEDIA_NOT_FOUND', 'Media not found')
      );
    }

    res.status(500).json(
      buildErrorResponse('INSIGHTS_RETRIEVAL_FAILED', error.message)
    );
  }
}));

// ============================================
// Media Deletion Endpoint
// ============================================

/**
 * DELETE /media/:media_id - Delete media
 */
app.delete('/media/:media_id', authenticateApiKey, asyncHandler(async (req, res) => {
  const { media_id } = req.params;

  try {
    await axios.delete(`${INSTAGRAM_BASE_URL}/${media_id}`, {
      params: {
        access_token: PAGE_ACCESS_TOKEN
      }
    });

    logger.info('Instagram media deleted', { media_id });

    res.status(204).send();

  } catch (error) {
    logger.error('Failed to delete Instagram media', { media_id, error: error.message });

    if (error.response && error.response.status === 404) {
      return res.status(404).json(
        buildErrorResponse('MEDIA_NOT_FOUND', 'Media not found')
      );
    }

    res.status(500).json(
      buildErrorResponse('MEDIA_DELETION_FAILED', error.message)
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
  logger.info(`Instagram MCP Server listening on port ${PORT}`, { service: 'instagram-mcp' });
  console.log(`✓ Instagram MCP Server running on http://localhost:${PORT}`);
  console.log(`✓ Health check: http://localhost:${PORT}/health`);
  console.log(`✓ Metrics: http://localhost:${PORT}/metrics`);
});

// Setup graceful shutdown
setupGracefulShutdown(server, async () => {
  logger.info('Instagram MCP Server cleanup complete');
});

module.exports = app;
