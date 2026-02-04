/**
 * MCP Email Server
 * Handles email sending via SMTP with OAuth2 authentication
 */

const express = require('express');
const nodemailer = require('nodemailer');
const cors = require('cors');
const path = require('path');
require('dotenv').config({ path: path.join(__dirname, '../../config/.env') });

const app = express();
const PORT = process.env.MCP_EMAIL_SERVER_PORT || 3000;

// Middleware
app.use(cors());
app.use(express.json());

// Logging middleware
app.use((req, res, next) => {
    console.log(`${new Date().toISOString()} - ${req.method} ${req.path}`);
    next();
});

// Create transporter with OAuth2
let transporter = null;

function createTransporter() {
    const config = {
        service: 'gmail',
        auth: {
            type: 'OAuth2',
            user: process.env.GMAIL_USER,
            clientId: process.env.GMAIL_CLIENT_ID,
            clientSecret: process.env.GMAIL_CLIENT_SECRET,
            refreshToken: process.env.GMAIL_REFRESH_TOKEN
        }
    };

    console.log('Creating email transporter with OAuth2...');
    transporter = nodemailer.createTransporter(config);

    // Verify transporter
    transporter.verify((error, success) => {
        if (error) {
            console.error('Transporter verification failed:', error);
        } else {
            console.log('✓ Email transporter ready');
        }
    });

    return transporter;
}

// Initialize transporter
createTransporter();

// Health check endpoint
app.get('/health', (req, res) => {
    res.json({
        status: 'ok',
        service: 'MCP Email Server',
        version: '1.0.0',
        timestamp: new Date().toISOString()
    });
});

// Send email endpoint
app.post('/send-email', async (req, res) => {
    try {
        const { to, subject, body, format = 'plain', attachments = [] } = req.body;

        // Validate required fields
        if (!to || !subject || !body) {
            return res.status(400).json({
                success: false,
                error: 'Missing required fields: to, subject, body'
            });
        }

        console.log(`Sending email to: ${to}`);
        console.log(`Subject: ${subject}`);

        // Prepare email options
        const mailOptions = {
            from: process.env.GMAIL_USER,
            to: to,
            subject: subject
        };

        // Set body based on format
        if (format === 'html') {
            mailOptions.html = body;
        } else {
            mailOptions.text = body;
        }

        // Add attachments if provided
        if (attachments && attachments.length > 0) {
            mailOptions.attachments = attachments.map(att => ({
                filename: att.filename,
                path: att.path
            }));
        }

        // Send email with retry logic
        let lastError = null;
        for (let attempt = 0; attempt < 3; attempt++) {
            try {
                const info = await transporter.sendMail(mailOptions);

                console.log('✓ Email sent successfully');
                console.log('Message ID:', info.messageId);

                return res.json({
                    success: true,
                    message_id: info.messageId,
                    timestamp: new Date().toISOString()
                });
            } catch (error) {
                lastError = error;
                console.error(`Attempt ${attempt + 1} failed:`, error.message);

                // Check if error is retryable
                if (error.code === 'ECONNECTION' || error.code === 'ETIMEDOUT') {
                    // Wait before retry (exponential backoff)
                    const delay = Math.pow(2, attempt) * 1000;
                    console.log(`Retrying in ${delay}ms...`);
                    await new Promise(resolve => setTimeout(resolve, delay));
                } else {
                    // Non-retryable error
                    break;
                }
            }
        }

        // All retries failed
        throw lastError;

    } catch (error) {
        console.error('Error sending email:', error);

        // Determine error type
        let errorMessage = error.message;
        let statusCode = 500;

        if (error.code === 'EAUTH') {
            errorMessage = 'Authentication failed. Check OAuth2 credentials.';
            statusCode = 401;
        } else if (error.code === 'EENVELOPE') {
            errorMessage = 'Invalid email address.';
            statusCode = 400;
        } else if (error.code === 'EMESSAGE') {
            errorMessage = 'Invalid email content.';
            statusCode = 400;
        }

        res.status(statusCode).json({
            success: false,
            error: errorMessage,
            code: error.code
        });
    }
});

// Refresh transporter endpoint (for token refresh)
app.post('/refresh-transporter', (req, res) => {
    try {
        createTransporter();
        res.json({
            success: true,
            message: 'Transporter refreshed'
        });
    } catch (error) {
        res.status(500).json({
            success: false,
            error: error.message
        });
    }
});

// Error handling middleware
app.use((err, req, res, next) => {
    console.error('Unhandled error:', err);
    res.status(500).json({
        success: false,
        error: 'Internal server error'
    });
});

// Start server
app.listen(PORT, () => {
    console.log('='.repeat(60));
    console.log('MCP Email Server');
    console.log('='.repeat(60));
    console.log(`Server running on http://localhost:${PORT}`);
    console.log(`Health check: http://localhost:${PORT}/health`);
    console.log('');
    console.log('Endpoints:');
    console.log('  POST /send-email - Send an email');
    console.log('  POST /refresh-transporter - Refresh OAuth2 transporter');
    console.log('  GET  /health - Health check');
    console.log('='.repeat(60));
});

// Graceful shutdown
process.on('SIGTERM', () => {
    console.log('SIGTERM received, shutting down gracefully...');
    process.exit(0);
});

process.on('SIGINT', () => {
    console.log('\nSIGINT received, shutting down gracefully...');
    process.exit(0);
});
