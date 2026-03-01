#!/bin/bash
# Start all social media MCP servers
# Run this script to start all servers at once

echo "Starting Social Media MCP Servers..."

# Start Facebook MCP Server
echo "Starting Facebook MCP Server on port 3101..."
cd AI_Employee_Vault/mcp
node facebook-server.js &
FACEBOOK_PID=$!

# Start Instagram MCP Server
echo "Starting Instagram MCP Server on port 3102..."
node instagram-server.js &
INSTAGRAM_PID=$!

# Start Twitter MCP Server
echo "Starting Twitter MCP Server on port 3103..."
node twitter-server.js &
TWITTER_PID=$!

echo ""
echo "All MCP servers started!"
echo "Facebook MCP: http://localhost:3101 (PID: $FACEBOOK_PID)"
echo "Instagram MCP: http://localhost:3102 (PID: $INSTAGRAM_PID)"
echo "Twitter MCP: http://localhost:3103 (PID: $TWITTER_PID)"
echo ""
echo "Press Ctrl+C to stop all servers"

# Wait for Ctrl+C
trap "kill $FACEBOOK_PID $INSTAGRAM_PID $TWITTER_PID; exit" INT
wait
