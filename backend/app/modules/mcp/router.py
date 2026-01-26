"""
MCP Module Router

FastAPI endpoints for MCP server operations.
"""

import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from .schema import (
    CreateSessionRequest,
    ListToolsResponse,
    SessionResponse,
    ToolInvocationRequest,
    ToolInvocationResult,
)
from .service import MCPServer
from backend.app.modules.mcp.tools import register_all_tools
from backend.app.shared.database import get_db

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/mcp", tags=["mcp"])

# Global MCP server instance (will be initialized in main.py)
_mcp_server: Optional[MCPServer] = None
_tools_registered = False


def get_mcp_server(db: Session = Depends(get_db)) -> MCPServer:
    """Get MCP server instance"""
    global _mcp_server, _tools_registered
    if _mcp_server is None:
        _mcp_server = MCPServer(db)
        
    # Register tools on first access
    if not _tools_registered:
        register_all_tools(_mcp_server)
        _tools_registered = True
        logger.info("MCP tools registered successfully")
        
    return _mcp_server


def get_current_user_optional(request: Request):
    """Get current user from request state if available"""
    return getattr(request.state, "user", None)


@router.get("/tools", response_model=ListToolsResponse)
async def list_tools(
    mcp_server: MCPServer = Depends(get_mcp_server),
):
    """
    List all available MCP tools.

    Returns:
        ListToolsResponse: List of available tools with their schemas
    """
    tools = mcp_server.list_tools()
    return ListToolsResponse(tools=tools, total=len(tools))


@router.post("/invoke", response_model=ToolInvocationResult)
async def invoke_tool(
    request: ToolInvocationRequest,
    mcp_server: MCPServer = Depends(get_mcp_server),
    current_user=Depends(get_current_user_optional),
):
    """
    Invoke an MCP tool.

    Args:
        request: Tool invocation request with tool name and arguments

    Returns:
        ToolInvocationResult: Result of tool invocation

    Raises:
        HTTPException: If tool requires auth and user not authenticated
    """
    # Check authentication if tool requires it
    tool = mcp_server.tool_registry.get_tool(request.tool_name)
    if tool and tool["definition"].requires_auth and not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required for this tool",
        )

    result = await mcp_server.invoke_tool(
        session_id=request.session_id,
        tool_name=request.tool_name,
        arguments=request.arguments,
    )

    return result


@router.post("/sessions", response_model=SessionResponse, status_code=status.HTTP_201_CREATED)
async def create_session(
    request: CreateSessionRequest,
    mcp_server: MCPServer = Depends(get_mcp_server),
    current_user=Depends(get_current_user_optional),
):
    """
    Create a new MCP session for multi-turn interactions.

    Args:
        request: Session creation request with initial context

    Returns:
        SessionResponse: Created session information
    """
    user_id = current_user.id if current_user else None
    session = mcp_server.create_session(user_id=user_id, context=request.context)
    return session


@router.get("/sessions/{session_id}", response_model=SessionResponse)
async def get_session(
    session_id: str,
    mcp_server: MCPServer = Depends(get_mcp_server),
):
    """
    Get MCP session by ID.

    Args:
        session_id: Session ID

    Returns:
        SessionResponse: Session information

    Raises:
        HTTPException: If session not found
    """
    session = mcp_server.get_session(session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session not found: {session_id}",
        )
    return session


@router.delete("/sessions/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def close_session(
    session_id: str,
    mcp_server: MCPServer = Depends(get_mcp_server),
):
    """
    Close an MCP session.

    Args:
        session_id: Session ID

    Raises:
        HTTPException: If session not found
    """
    success = mcp_server.close_session(session_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session not found: {session_id}",
        )
