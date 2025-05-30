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
from datetime import datetime

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
            
            if not session_id:
                return JSONResponse(
                    {"error": "Missing session_id parameter"}, 
                    status_code=400
                )

            # Auto-create session if it doesn't exist (for testing)
            if session_id not in self.client_sessions:
                self.client_sessions[session_id] = {
                    "created_at": datetime.now(),
                    "last_active": datetime.now(),
                    "queue": asyncio.Queue(),
                }
            else:
                # Update last active time
                self.client_sessions[session_id]["last_active"] = datetime.now()
            
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

    async def call_tool(self, tool_name, arguments, request):
        """Call a tool and return the result."""
        logger.info(
            f"Calling tool: {tool_name}, Arguments: {json.dumps(arguments, ensure_ascii=False)}"
        )

        # Get recent query content, used to handle random_string parameter
        recent_query = self._extract_recent_query(request)

        # Handle tool name mapping - our tools use mcp_ prefix
        tool_mapping = {
            "zap_health_check": "mcp_zap_health_check",
            "zap_spider_scan": "mcp_zap_spider_scan",
            "zap_active_scan": "mcp_zap_active_scan",
            "zap_spider_status": "mcp_zap_spider_status",
            "zap_active_scan_status": "mcp_zap_active_scan_status",
            "zap_get_alerts": "mcp_zap_get_alerts",
            "zap_generate_html_report": "mcp_zap_generate_html_report",
            "zap_generate_json_report": "mcp_zap_generate_json_report",
            "zap_clear_session": "mcp_zap_clear_session",
            "zap_scan_summary": "mcp_zap_scan_summary",
        }

        # Map tool name to internal function name
        mapped_tool_name = tool_mapping.get(tool_name, tool_name)
        logger.debug(f"Tool mapping: {tool_name} -> {mapped_tool_name}")

        # Process common input parameter conversions
        processed_args = self._process_tool_arguments(
            mapped_tool_name, arguments, recent_query
        )
        logger.debug(f"Processed arguments: {processed_args}")

        try:
            # First try to import tool functions from our tools module
            try:
                from .tools import zap_tools

                # Get the corresponding tool function
                tool_function = getattr(zap_tools, mapped_tool_name, None)

                if tool_function:
                    logger.debug(
                        f"Found tool function in zap_tools: {mapped_tool_name}"
                    )
                    # Call the tool function directly
                    if callable(tool_function):
                        result = await tool_function(**processed_args)
                        logger.info(
                            f"Tool {tool_name} executed successfully via direct function call"
                        )
                        return result
                    else:
                        raise ValueError(
                            f"Tool function is not callable: {mapped_tool_name}"
                        )

            except (AttributeError, ImportError) as e:
                logger.debug(
                    f"Could not import tool function {mapped_tool_name}: {str(e)}"
                )

            # Fallback: Use MCP server's registered tools
            logger.debug(f"Falling back to MCP server tools for: {tool_name}")

            # Get the list of registered tools from the MCP server
            tools = await self.mcp_server.list_tools()

            # Find the tool by name
            tool_instance = None
            for tool in tools:
                if (
                    getattr(tool, "name", None) == tool_name
                    or getattr(tool, "name", None) == mapped_tool_name
                ):
                    tool_instance = tool
                    break

            if not tool_instance:
                raise ValueError(f"Tool '{tool_name}' not found in registered tools")

            # Handle different tool execution patterns (following Apache Doris pattern)
            logger.debug(f"Tool instance type: {type(tool_instance)}")
            logger.debug(f"Tool instance attributes: {dir(tool_instance)}")

            try:
                if callable(tool_instance):
                    logger.debug("Tool instance is callable, calling directly")
                    result = await tool_instance(**processed_args)
                elif hasattr(tool_instance, "run"):
                    logger.debug("Tool instance has run method, calling run method")
                    result = await tool_instance.run(**processed_args)
                elif hasattr(tool_instance, "execute"):
                    logger.debug(
                        "Tool instance has execute method, calling execute method"
                    )
                    result = await tool_instance.execute(**processed_args)
                elif hasattr(tool_instance, "call"):
                    logger.debug("Tool instance has call method, calling call method")
                    result = await tool_instance.call(**processed_args)
                elif hasattr(tool_instance, "__call__"):
                    logger.debug(
                        "Tool instance has __call__ method, calling __call__ method"
                    )
                    result = await tool_instance.__call__(**processed_args)
                elif hasattr(tool_instance, "func"):
                    # Try to get the actual function from the tool
                    func = tool_instance.func
                    if callable(func):
                        logger.debug("Tool instance has func attribute, calling func")
                        result = await func(**processed_args)
                    else:
                        raise ValueError(f"Tool.func is not callable for {tool_name}")
                else:
                    raise ValueError(
                        f"Tool '{tool_name}' is not callable and has no recognized execution method. "
                        f"Available attributes: {dir(tool_instance)}"
                    )

            except RuntimeError as re:
                # Handle the case where the MCP tool wrapper raises RuntimeError
                # This means we should use the direct function call instead
                if "should be called via SSE server parameter processing" in str(re):
                    logger.info(
                        f"MCP tool wrapper for {tool_name} deferred to direct function call"
                    )
                    # Import and call the actual tool function directly
                    from .tools import zap_tools

                    tool_function = getattr(zap_tools, mapped_tool_name, None)
                    if tool_function and callable(tool_function):
                        result = await tool_function(**processed_args)
                        logger.info(
                            f"Tool {tool_name} executed successfully via fallback direct function call"
                        )
                        return result
                    else:
                        raise ValueError(
                            f"Could not find fallback function {mapped_tool_name}"
                        )
                else:
                    raise re

            logger.info(f"Tool {tool_name} executed successfully via MCP server")
            return result

        except Exception as e:
            logger.error(f"Error in call_tool for {tool_name}: {str(e)}", exc_info=True)
            raise ValueError(f"Tool execution failed: {str(e)}")

    def _extract_recent_query(self, request):
        """
        Extract the most recent user query from the request

        Args:
            request: Request object

        Returns:
            Optional[str]: The most recent user query, or None if not found
        """
        try:
            # Try to extract message history from request body
            body = None
            body_bytes = getattr(request, "_body", None)
            if body_bytes:
                try:
                    body = json.loads(body_bytes)
                except:
                    pass

            if not body:
                body = getattr(request, "_json", {})

            # Find the most recent user message from message history
            messages = body.get("params", {}).get("messages", [])
            if messages:
                # Iterate messages in reverse to find the most recent user message
                for msg in reversed(messages):
                    if msg.get("role") == "user":
                        return msg.get("content", "")

            # If not found in message history, try extracting from the original message
            message = body.get("params", {}).get("message", {})
            if message and message.get("role") == "user":
                return message.get("content", "")

            return None
        except Exception as e:
            logger.error(f"Error extracting recent query: {str(e)}")
            return None

    def _process_tool_arguments(self, tool_name, arguments, recent_query):
        """
        Process tool parameters, supporting special handling logic for ZAP tools

        Args:
            tool_name: Tool name (MCP internal name, e.g., mcp_zap_...)
            arguments: Original parameters
            recent_query: Recent query content

        Returns:
            Processed parameter dictionary
        """
        # Copy parameters to avoid modifying the original object
        processed_args = dict(arguments)
        logger.debug(
            f"Processing arguments for {tool_name}: original={arguments}, recent_query='{recent_query}'"
        )

        # Handle potential random_string parameter as fallback
        if "random_string" in processed_args and tool_name.startswith("mcp_zap_"):
            random_string = processed_args.pop("random_string", "")
            logger.debug(
                f"Processing random_string parameter for tool {tool_name}: '{random_string}'"
            )

            # 1. For tools requiring URL parameter
            if tool_name in [
                "mcp_zap_spider_scan",
                "mcp_zap_active_scan",
                "mcp_zap_scan_summary",
            ]:
                if not processed_args.get("url"):
                    url_fallback = random_string or recent_query
                    if url_fallback:
                        # Try to extract URL from the string
                        import re

                        # Look for URLs in the string
                        url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
                        url_matches = re.findall(url_pattern, url_fallback)
                        if url_matches:
                            url_fallback = url_matches[0]
                            logger.debug(f"Found URL pattern match: {url_fallback}")
                        elif url_fallback and not url_fallback.startswith(
                            ("http://", "https://")
                        ):
                            # If it looks like a domain, add https://
                            if "." in url_fallback and " " not in url_fallback:
                                url_fallback = f"https://{url_fallback}"
                                logger.debug(
                                    f"Added https:// to domain: {url_fallback}"
                                )

                        if url_fallback:
                            logger.info(
                                f"Using random_string/recent_query as URL for {tool_name}: {url_fallback}"
                            )
                            processed_args["url"] = url_fallback
                        else:
                            logger.warning(
                                f"{tool_name} missing url parameter, and random_string/recent_query is empty or URL cannot be extracted"
                            )
                    else:
                        logger.warning(
                            f"{tool_name} missing url parameter, and both random_string and recent_query are empty"
                        )

            # 2. For tools requiring scan_id parameter
            elif tool_name in ["mcp_zap_spider_status", "mcp_zap_active_scan_status"]:
                if not processed_args.get("scan_id"):
                    scan_id_fallback = random_string
                    if scan_id_fallback:
                        # Extract scan ID (usually a number or simple string)
                        import re

                        scan_id_match = re.search(r"\b(\d+)\b", scan_id_fallback)
                        if scan_id_match:
                            scan_id_fallback = scan_id_match.group(1)
                            logger.debug(
                                f"Extracted scan ID from string: {scan_id_fallback}"
                            )

                        logger.info(
                            f"Using random_string as scan_id for {tool_name}: {scan_id_fallback}"
                        )
                        processed_args["scan_id"] = scan_id_fallback
                    else:
                        logger.warning(
                            f"{tool_name} missing scan_id parameter, and random_string is empty"
                        )

            # 3. For tools requiring risk_level parameter
            elif tool_name == "mcp_zap_get_alerts":
                if not processed_args.get("risk_level") and random_string:
                    # Check if random_string contains a valid risk level
                    risk_levels = ["High", "Medium", "Low", "Informational"]
                    for level in risk_levels:
                        if level.lower() in random_string.lower():
                            logger.info(
                                f"Using random_string as risk_level for {tool_name}: {level}"
                            )
                            processed_args["risk_level"] = level
                            break

        elif "random_string" in processed_args:
            # Remove random_string for non-ZAP tools
            processed_args.pop("random_string", "")
            logger.debug(
                f"Removed random_string parameter for non-ZAP tool: {tool_name}"
            )

        logger.debug(f"Final processed arguments for {tool_name}: {processed_args}")
        return processed_args
