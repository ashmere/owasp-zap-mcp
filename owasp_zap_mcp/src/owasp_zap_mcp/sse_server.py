# -*- coding: utf-8 -*-

"""
OWASP ZAP MCP SSE Server Implementation

Based on the Apache Doris MCP server pattern for handling SSE connections
and MCP tool execution.
"""

import asyncio
import json
import logging
import time
import uuid
from typing import Any, Dict, Optional

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from sse_starlette.sse import EventSourceResponse

# Get logger
logger = logging.getLogger("owasp-zap-mcp-sse")


class ZAPMCPSseServer:
    """OWASP ZAP MCP SSE Server Implementation"""

    def __init__(self, mcp_server, app: FastAPI):
        """
        Initialize the OWASP ZAP MCP SSE server

        Args:
            mcp_server: FastMCP server instance
            app: FastAPI application instance
        """
        self.mcp_server = mcp_server
        self.app = app

        # Client session management
        self.client_sessions = {}

        # Set up SSE routes
        self.setup_sse_routes()

        # Register startup event for cleanup tasks
        @self.app.on_event("startup")
        async def startup_event():
            asyncio.create_task(self.cleanup_idle_sessions())

    def setup_sse_routes(self):
        """Set up SSE related routes"""

        @self.app.get("/health")
        async def health_check():
            """Health check endpoint"""
            try:
                return {
                    "status": "healthy",
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "server": "OWASP ZAP MCP Server",
                }
            except Exception as e:
                return {
                    "status": "error",
                    "error": str(e),
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                }

        @self.app.get("/status")
        async def status():
            """Get server status"""
            try:
                # Get tool list
                tools = await self.mcp_server.list_tools()
                tool_names = [
                    tool.name if hasattr(tool, "name") else str(tool) for tool in tools
                ]
                logger.info(
                    f"Getting tool list, currently registered tools: {tool_names}"
                )

                return {
                    "status": "running",
                    "name": self.mcp_server.name,
                    "mode": "mcp_sse",
                    "clients": len(self.client_sessions),
                    "tools": tool_names,
                }
            except Exception as e:
                logger.error(f"Error getting status: {str(e)}")
                return {"status": "error", "error": str(e)}

        @self.app.get("/sse")
        async def mcp_sse_init(request: Request):
            """SSE service entry point, establishes client connection"""
            # Generate session ID
            session_id = str(uuid.uuid4())
            logger.info(f"New SSE connection [Session ID: {session_id}] at /sse")

            # Create client session
            self.client_sessions[session_id] = {
                "client_id": request.headers.get(
                    "X-Client-ID", f"client_{str(uuid.uuid4())[:8]}"
                ),
                "created_at": time.time(),
                "last_active": time.time(),
                "queue": asyncio.Queue(),
            }

            # Put endpoint information into the queue
            endpoint_data = f"/mcp/messages?session_id={session_id}"
            await self.client_sessions[session_id]["queue"].put(
                {"event": "endpoint", "data": endpoint_data}
            )

            # Create event generator
            async def event_generator():
                try:
                    while True:
                        try:
                            message = await asyncio.wait_for(
                                self.client_sessions[session_id]["queue"].get(),
                                timeout=30,
                            )

                            # Check if it's a close command
                            if (
                                isinstance(message, dict)
                                and message.get("event") == "close"
                            ):
                                logger.info(
                                    f"Received close command [Session ID: {session_id}]"
                                )
                                break

                            # Return message
                            if isinstance(message, dict):
                                if "event" in message:
                                    event_type = message["event"]
                                    event_data = message["data"]
                                    yield {"event": event_type, "data": event_data}
                                else:
                                    yield {
                                        "event": "message",
                                        "data": json.dumps(message),
                                    }
                            elif isinstance(message, str):
                                yield {"event": "message", "data": message}
                            else:
                                yield {"event": "message", "data": json.dumps(message)}
                        except asyncio.TimeoutError:
                            # Send ping to keep connection alive
                            yield {"event": "ping", "data": "keepalive"}
                            continue
                except asyncio.CancelledError:
                    logger.info(f"SSE connection cancelled [Session ID: {session_id}]")
                except Exception as e:
                    logger.error(
                        f"SSE event generator error [Session ID: {session_id}]: {str(e)}"
                    )
                finally:
                    # Clean up session
                    if session_id in self.client_sessions:
                        logger.info(f"Cleaning up session [Session ID: {session_id}]")
                        del self.client_sessions[session_id]

            # Return SSE response
            return EventSourceResponse(
                event_generator(),
                headers={
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Credentials": "true",
                    "Access-Control-Allow-Methods": "*",
                    "Access-Control-Allow-Headers": "*",
                    "Access-Control-Expose-Headers": "*",
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                },
            )

        @self.app.options("/mcp/messages")
        async def mcp_messages_options(request: Request):
            """Handle preflight requests"""
            return JSONResponse(
                {},
                headers={
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Credentials": "true",
                    "Access-Control-Allow-Methods": "*",
                    "Access-Control-Allow-Headers": "*",
                    "Access-Control-Expose-Headers": "*",
                },
            )

        @self.app.post("/mcp/messages")
        async def mcp_messages_handler(request: Request):
            """Handle client message requests"""
            return await self.mcp_message(request)

        @self.app.post("/sse")
        async def mcp_sse_post(request: Request):
            """Handle POST requests to SSE endpoint - redirect to proper message handler"""
            # Extract session ID from query parameters or headers
            session_id = request.query_params.get("session_id")
            if not session_id:
                # If no session ID provided, return error
                return JSONResponse(
                    {"error": "Missing session_id parameter"},
                    status_code=400,
                    headers={
                        "Access-Control-Allow-Origin": "*",
                        "Access-Control-Allow-Credentials": "true",
                        "Access-Control-Allow-Methods": "*",
                        "Access-Control-Allow-Headers": "*",
                        "Access-Control-Expose-Headers": "*",
                    },
                )

            # Redirect to the proper message handler
            return await self.mcp_message(request)

        @self.app.options("/sse")
        async def mcp_sse_options(request: Request):
            """Handle preflight requests for SSE endpoint"""
            return JSONResponse(
                {},
                headers={
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Credentials": "true",
                    "Access-Control-Allow-Methods": "*",
                    "Access-Control-Allow-Headers": "*",
                    "Access-Control-Expose-Headers": "*",
                },
            )

    async def cleanup_idle_sessions(self):
        """Clean up idle client sessions"""
        while True:
            await asyncio.sleep(60)  # Check every minute
            current_time = time.time()

            # Find sessions idle for over 5 minutes
            idle_sessions = []
            for session_id, session in self.client_sessions.items():
                if current_time - session["last_active"] > 300:  # 5 minutes
                    idle_sessions.append(session_id)

            # Close and remove idle sessions
            for session_id in idle_sessions:
                try:
                    await self.client_sessions[session_id]["queue"].put(
                        {"event": "close"}
                    )
                    logger.info(f"Cleaned up idle session: {session_id}")
                except Exception as e:
                    logger.error(f"Error cleaning up session: {str(e)}")

    async def mcp_message(self, request: Request):
        """Handle MCP message requests"""
        try:
            # Get session ID from query parameters
            session_id = request.query_params.get("session_id")
            if not session_id or session_id not in self.client_sessions:
                return JSONResponse(
                    {"error": "Invalid session ID"},
                    status_code=400,
                    headers={
                        "Access-Control-Allow-Origin": "*",
                        "Access-Control-Allow-Credentials": "true",
                        "Access-Control-Allow-Methods": "*",
                        "Access-Control-Allow-Headers": "*",
                        "Access-Control-Expose-Headers": "*",
                    },
                )

            # Update last active time
            self.client_sessions[session_id]["last_active"] = time.time()

            # Parse request body
            body = await request.json()
            logger.info(f"Received MCP message [Session ID: {session_id}]: {body}")

            # Handle different message types
            message_id = body.get("id")
            method = body.get("method")
            params = body.get("params", {})

            response = None

            if method == "initialize":
                # Handle MCP initialization
                protocol_version = params.get("protocolVersion", "2024-11-05")
                client_capabilities = params.get("capabilities", {})
                client_info = params.get("clientInfo", {})

                logger.info(
                    f"MCP Initialize - Protocol: {protocol_version}, Client: {client_info}"
                )

                response = {
                    "jsonrpc": "2.0",
                    "id": message_id,
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "name": "owasp-zap-mcp",
                        "instructions": "This is an MCP server for OWASP ZAP security scanning",
                        "serverInfo": {"name": "owasp-zap-mcp", "version": "0.2.0"},
                        "capabilities": {
                            "tools": {
                                "supportsStreaming": False,
                                "supportsProgress": False,
                            },
                            "resources": {"supportsStreaming": False},
                            "prompts": {"supported": False},
                        },
                    },
                }
                await self.client_sessions[session_id]["queue"].put(response)
                return JSONResponse(
                    {"status": "success"},
                    headers={
                        "Access-Control-Allow-Origin": "*",
                        "Access-Control-Allow-Credentials": "true",
                        "Access-Control-Allow-Methods": "*",
                        "Access-Control-Allow-Headers": "*",
                        "Access-Control-Expose-Headers": "*",
                    },
                )

            elif method == "mcp/listOfferings":
                # List all available features
                logger.info(
                    f"Processing listOfferings command [Session ID: {session_id}]"
                )

                # Get tool list
                tools = await self.mcp_server.list_tools()
                tools_json = [
                    {
                        "name": getattr(tool, "name", str(tool)),
                        "description": getattr(
                            tool, "description", "No description available"
                        ),
                        "inputSchema": getattr(
                            tool,
                            "parameters",
                            {"type": "object", "properties": {}, "required": []},
                        ),
                    }
                    for tool in tools
                ]

                response = {
                    "jsonrpc": "2.0",
                    "id": message_id,
                    "result": {"tools": tools_json, "resources": [], "prompts": []},
                }
                await self.client_sessions[session_id]["queue"].put(response)
                return JSONResponse(
                    {"status": "success"},
                    headers={
                        "Access-Control-Allow-Origin": "*",
                        "Access-Control-Allow-Credentials": "true",
                        "Access-Control-Allow-Methods": "*",
                        "Access-Control-Allow-Headers": "*",
                        "Access-Control-Expose-Headers": "*",
                    },
                )

            elif method == "mcp/listTools" or method == "tools/list":
                # List all tools
                logger.info(f"Processing listTools command [Session ID: {session_id}]")
                tools = await self.mcp_server.list_tools()
                tools_json = [
                    {
                        "name": getattr(tool, "name", str(tool)),
                        "description": getattr(
                            tool, "description", "No description available"
                        ),
                        "inputSchema": getattr(
                            tool,
                            "parameters",
                            {"type": "object", "properties": {}, "required": []},
                        ),
                    }
                    for tool in tools
                ]
                response = {
                    "jsonrpc": "2.0",
                    "id": message_id,
                    "result": {"tools": tools_json},
                }
                await self.client_sessions[session_id]["queue"].put(response)
                return JSONResponse(
                    {"status": "success"},
                    headers={
                        "Access-Control-Allow-Origin": "*",
                        "Access-Control-Allow-Credentials": "true",
                        "Access-Control-Allow-Methods": "*",
                        "Access-Control-Allow-Headers": "*",
                        "Access-Control-Expose-Headers": "*",
                    },
                )

            elif method == "mcp/callTool" or method == "tools/call":
                # Call a tool
                tool_name = params.get("name")
                arguments = params.get("arguments", {})

                if not tool_name:
                    error_response = {
                        "jsonrpc": "2.0",
                        "id": message_id,
                        "error": {
                            "code": -32602,
                            "message": "Invalid params: tool name is required",
                        },
                    }
                    await self.client_sessions[session_id]["queue"].put(error_response)
                    return JSONResponse(
                        {"status": "error"},
                        headers={
                            "Access-Control-Allow-Origin": "*",
                            "Access-Control-Allow-Credentials": "true",
                            "Access-Control-Allow-Methods": "*",
                            "Access-Control-Allow-Headers": "*",
                            "Access-Control-Expose-Headers": "*",
                        },
                    )

                try:
                    # Execute the tool
                    result = await self.call_tool(tool_name, arguments, request)

                    # Format result properly for MCP
                    if (
                        isinstance(result, dict)
                        and "content" in result
                        and isinstance(result["content"], list)
                    ):
                        formatted_result = result
                    else:
                        # Format into standard MCP response format
                        formatted_result = {
                            "content": [
                                {
                                    "type": "text",
                                    "text": (
                                        result
                                        if isinstance(result, str)
                                        else json.dumps(result, ensure_ascii=False)
                                    ),
                                }
                            ]
                        }

                    response = {
                        "jsonrpc": "2.0",
                        "id": message_id,
                        "result": formatted_result,
                    }
                    await self.client_sessions[session_id]["queue"].put(response)
                    return JSONResponse(
                        {"status": "success"},
                        headers={
                            "Access-Control-Allow-Origin": "*",
                            "Access-Control-Allow-Credentials": "true",
                            "Access-Control-Allow-Methods": "*",
                            "Access-Control-Allow-Headers": "*",
                            "Access-Control-Expose-Headers": "*",
                        },
                    )
                except Exception as e:
                    logger.error(f"Error calling tool {tool_name}: {str(e)}")
                    error_response = {
                        "jsonrpc": "2.0",
                        "id": message_id,
                        "error": {
                            "code": -32000,
                            "message": f"Tool execution failed: {str(e)}",
                        },
                    }
                    await self.client_sessions[session_id]["queue"].put(error_response)
                    return JSONResponse(
                        {"status": "error"},
                        headers={
                            "Access-Control-Allow-Origin": "*",
                            "Access-Control-Allow-Credentials": "true",
                            "Access-Control-Allow-Methods": "*",
                            "Access-Control-Allow-Headers": "*",
                            "Access-Control-Expose-Headers": "*",
                        },
                    )

            else:
                # Unknown method
                logger.warning(f"Unknown method: {method}")
                error_response = {
                    "jsonrpc": "2.0",
                    "id": message_id,
                    "error": {"code": -32601, "message": f"Method not found: {method}"},
                }
                await self.client_sessions[session_id]["queue"].put(error_response)
                return JSONResponse(
                    {"status": "error"},
                    headers={
                        "Access-Control-Allow-Origin": "*",
                        "Access-Control-Allow-Credentials": "true",
                        "Access-Control-Allow-Methods": "*",
                        "Access-Control-Allow-Headers": "*",
                        "Access-Control-Expose-Headers": "*",
                    },
                )

            # Put response into queue (only if response is not None)
            if response:
                await self.client_sessions[session_id]["queue"].put(response)

            # Return received confirmation
            return JSONResponse(
                {"status": "received"},
                headers={
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Credentials": "true",
                    "Access-Control-Allow-Methods": "*",
                    "Access-Control-Allow-Headers": "*",
                    "Access-Control-Expose-Headers": "*",
                },
            )

        except Exception as e:
            logger.error(f"Error handling MCP message: {str(e)}")
            return JSONResponse(
                {"error": str(e)},
                status_code=500,
                headers={
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Credentials": "true",
                    "Access-Control-Allow-Methods": "*",
                    "Access-Control-Allow-Headers": "*",
                    "Access-Control-Expose-Headers": "*",
                },
            )

    async def call_tool(
        self, tool_name: str, arguments: Dict[str, Any], request: Request
    ) -> Any:
        """Call a tool by name with arguments"""
        try:
            logger.info(
                f"Calling tool: {tool_name}, Arguments: {json.dumps(arguments, ensure_ascii=False)}"
            )

            # Get the list of registered tools from the MCP server
            tools = await self.mcp_server.list_tools()

            # Find the tool by name
            tool_instance = None
            for tool in tools:
                if getattr(tool, "name", None) == tool_name:
                    tool_instance = tool
                    break

            if not tool_instance:
                raise ValueError(f"Tool '{tool_name}' not found")

            # Handle different tool execution patterns
            try:
                # Try different execution methods based on the tool type
                if hasattr(tool_instance, "run"):
                    logger.debug(f"Calling tool.run() for {tool_name}")
                    result = await tool_instance.run(**arguments)
                elif hasattr(tool_instance, "execute"):
                    logger.debug(f"Calling tool.execute() for {tool_name}")
                    result = await tool_instance.execute(**arguments)
                elif hasattr(tool_instance, "call"):
                    logger.debug(f"Calling tool.call() for {tool_name}")
                    result = await tool_instance.call(**arguments)
                elif callable(tool_instance):
                    logger.debug(f"Calling tool directly for {tool_name}")
                    result = await tool_instance(**arguments)
                elif hasattr(tool_instance, "__call__"):
                    logger.debug(f"Calling tool.__call__() for {tool_name}")
                    result = await tool_instance.__call__(**arguments)
                else:
                    # Try to get the actual function from the tool
                    if hasattr(tool_instance, "func"):
                        func = tool_instance.func
                        if callable(func):
                            logger.debug(f"Calling tool.func for {tool_name}")
                            result = await func(**arguments)
                        else:
                            raise ValueError(
                                f"Tool.func is not callable for {tool_name}"
                            )
                    else:
                        raise ValueError(
                            f"Tool '{tool_name}' is not callable and has no recognized execution method"
                        )

                logger.info(f"Tool {tool_name} executed successfully")
                return result

            except Exception as e:
                logger.error(
                    f"Error executing tool {tool_name}: {str(e)}", exc_info=True
                )
                raise ValueError(f"Tool execution failed: {str(e)}")

        except Exception as e:
            logger.error(f"Error in call_tool for {tool_name}: {str(e)}")
            raise
