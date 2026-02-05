/**
 * Shared Utilities for Gold Tier MCP Servers
 *
 * This module provides common functionality for all MCP servers:
 * - Logging
 * - Error handling
 * - Authentication middleware
 * - Health check utilities
 * - Rate limit handling
 */

const winston = require('winston');
require('dotenv').config();

// ============================================
// Logger Configuration
// ============================================

const logger = winston.createLogger({
  level: process.env.LOG_LEVEL || 'info',
  format: winston.format.combine(
    winston.format.timestamp({ format: 'YYYY-MM-DD HH:mm:ss' }),
    winston.format.errors({ stack: true }),
    winston.format.splat(),
    winston.format.json()
  ),
  defaultMeta: { service: 'mcp-server' },
  transports: [
    // Write all logs to console
    new winston.transports.Console({
      format: winston.format.combine(
        winston.format.colorize(),
        winston.format.printf(({ timestamp, level, message, service, ...meta }) => {
          return `${timestamp} [${service}] ${level}: ${message} ${Object.keys(meta).length ? JSON.stringify(meta) : ''}`;
        })
      )
    }),
    // Write all logs with level 'error' and below to error.log
    new winston.transports.File({
      filename: '../../Audit_Logs/mcp-error.log',
      level: 'error',
      maxsize: 5242880, // 5MB
      maxFiles: 5
    }),
    // Write all logs to combined.log
    new winston.transports.File({
      filename: '../../Audit_Logs/mcp-combined.log',
      maxsize: 5242880, // 5MB
      maxFiles: 5
    })
  ]
});

// ============================================
// Error Response Builder
// ============================================

/**
 * Build standardized error response
 * @param {string} error - Error code
 * @param {string} message - Human-readable error message
 * @param {object} details - Additional error details
 * @returns {object} Standardized error response
 */
function buildErrorResponse(error, message, details = {}) {
  return {
    error,
    message,
    details,
    timestamp: new Date().toISOString()
  };
}

// ============================================
// Authentication Middleware
// ============================================

/**
 * Middleware to verify API key authentication
 * Checks X-API-Key header against MCP_API_KEY environment variable
 */
function authenticateApiKey(req, res, next) {
  const apiKey = req.headers['x-api-key'];
  const expectedApiKey = process.env.MCP_API_KEY;

  // Skip authentication in development if no API key is set
  if (!expectedApiKey && process.env.NODE_ENV === 'development') {
    logger.warn('API key authentication disabled in development mode');
    return next();
  }

  if (!apiKey) {
    logger.warn('Missing API key in request', { path: req.path, ip: req.ip });
    return res.status(401).json(
      buildErrorResponse('MISSING_API_KEY', 'API key is required in X-API-Key header')
    );
  }

  if (apiKey !== expectedApiKey) {
    logger.warn('Invalid API key attempt', { path: req.path, ip: req.ip });
    return res.status(401).json(
      buildErrorResponse('INVALID_API_KEY', 'Invalid API key provided')
    );
  }

  next();
}

// ============================================
// Health Check Utilities
// ============================================

/**
 * Build health check response
 * @param {string} serviceName - Name of the service
 * @param {boolean} isHealthy - Whether the service is healthy
 * @param {object} additionalInfo - Additional health information
 * @returns {object} Health check response
 */
function buildHealthResponse(serviceName, isHealthy, additionalInfo = {}) {
  return {
    service: serviceName,
    status: isHealthy ? 'healthy' : 'unhealthy',
    timestamp: new Date().toISOString(),
    ...additionalInfo
  };
}

/**
 * Generic health check endpoint handler
 * @param {string} serviceName - Name of the service
 * @param {function} checkFunction - Async function that returns health status
 */
function createHealthCheckHandler(serviceName, checkFunction) {
  return async (req, res) => {
    try {
      const healthInfo = await checkFunction();
      const isHealthy = healthInfo.connected !== false;

      logger.info(`Health check for ${serviceName}`, { status: isHealthy ? 'healthy' : 'unhealthy' });

      const statusCode = isHealthy ? 200 : 503;
      res.status(statusCode).json(
        buildHealthResponse(serviceName, isHealthy, healthInfo)
      );
    } catch (error) {
      logger.error(`Health check failed for ${serviceName}`, { error: error.message });
      res.status(503).json(
        buildHealthResponse(serviceName, false, { error: error.message })
      );
    }
  };
}

// ============================================
// Rate Limit Handling
// ============================================

/**
 * Build rate limit error response
 * @param {number} retryAfter - Seconds to wait before retrying
 * @param {object} rateLimitInfo - Rate limit details
 * @returns {object} Rate limit error response
 */
function buildRateLimitError(retryAfter, rateLimitInfo = {}) {
  return {
    error: 'RATE_LIMIT_EXCEEDED',
    message: 'Rate limit exceeded. Please try again later.',
    retry_after: retryAfter,
    rate_limit: rateLimitInfo,
    timestamp: new Date().toISOString()
  };
}

/**
 * Handle rate limit errors from external APIs
 * @param {Error} error - Error from external API
 * @param {string} platform - Platform name (facebook, instagram, twitter)
 * @returns {object} Formatted rate limit error or null if not a rate limit error
 */
function handleRateLimitError(error, platform) {
  // Check if error is a rate limit error
  if (error.response && error.response.status === 429) {
    const retryAfter = error.response.headers['retry-after'] || 3600;

    logger.warn(`Rate limit exceeded for ${platform}`, {
      retryAfter,
      platform
    });

    return buildRateLimitError(parseInt(retryAfter), {
      limit: error.response.headers['x-rate-limit-limit'],
      remaining: error.response.headers['x-rate-limit-remaining'],
      reset_at: error.response.headers['x-rate-limit-reset']
    });
  }

  return null;
}

// ============================================
// Request Logging Middleware
// ============================================

/**
 * Middleware to log all incoming requests
 */
function logRequest(req, res, next) {
  const startTime = Date.now();

  // Log request
  logger.info('Incoming request', {
    method: req.method,
    path: req.path,
    ip: req.ip,
    userAgent: req.get('user-agent')
  });

  // Log response when finished
  res.on('finish', () => {
    const duration = Date.now() - startTime;
    logger.info('Request completed', {
      method: req.method,
      path: req.path,
      statusCode: res.statusCode,
      duration: `${duration}ms`
    });
  });

  next();
}

// ============================================
// Error Handler Middleware
// ============================================

/**
 * Global error handler middleware
 * Should be added as the last middleware in Express app
 */
function errorHandler(err, req, res, next) {
  logger.error('Unhandled error', {
    error: err.message,
    stack: err.stack,
    path: req.path,
    method: req.method
  });

  // Don't leak error details in production
  const message = process.env.NODE_ENV === 'production'
    ? 'Internal server error'
    : err.message;

  res.status(err.statusCode || 500).json(
    buildErrorResponse(
      err.code || 'INTERNAL_ERROR',
      message,
      process.env.NODE_ENV === 'production' ? {} : { stack: err.stack }
    )
  );
}

// ============================================
// Async Handler Wrapper
// ============================================

/**
 * Wrap async route handlers to catch errors
 * @param {function} fn - Async route handler function
 * @returns {function} Wrapped handler
 */
function asyncHandler(fn) {
  return (req, res, next) => {
    Promise.resolve(fn(req, res, next)).catch(next);
  };
}

// ============================================
// Exports
// ============================================

module.exports = {
  logger,
  buildErrorResponse,
  authenticateApiKey,
  buildHealthResponse,
  createHealthCheckHandler,
  buildRateLimitError,
  handleRateLimitError,
  logRequest,
  errorHandler,
  asyncHandler
};
