"""
MCP (Model Context Protocol) Module

This module provides MCP server infrastructure for tool registration and invocation.
It exposes backend capabilities as MCP-compatible tools for frontend integration.
"""

from backend.app.modules.mcp.router import router

__all__ = ["router"]
