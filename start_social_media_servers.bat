@echo off
REM Start all social media MCP servers on Windows
REM Run this script to start all servers at once

echo Starting Social Media MCP Servers...
echo.

cd AI_Employee_Vault\mcp

REM Start Facebook MCP Server
echo Starting Facebook MCP Server on port 3101...
start "Facebook MCP" cmd /k "node facebook-server.js"
timeout /t 2 /nobreak >nul

REM Start Instagram MCP Server
echo Starting Instagram MCP Server on port 3102...
start "Instagram MCP" cmd /k "node instagram-server.js"
timeout /t 2 /nobreak >nul

REM Start Twitter MCP Server
echo Starting Twitter MCP Server on port 3103...
start "Twitter MCP" cmd /k "node twitter-server.js"
timeout /t 2 /nobreak >nul

echo.
echo All MCP servers started!
echo Facebook MCP: http://localhost:3101
echo Instagram MCP: http://localhost:3102
echo Twitter MCP: http://localhost:3103
echo.
echo Close the individual command windows to stop each server
echo.
pause
