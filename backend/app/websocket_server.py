"""
WebSocket Server for Real-time Admin Notifications
Handles real-time communication between users and admin dashboard
"""

import asyncio
import json
import logging
from typing import Dict, Set, Any
from fastapi import WebSocket, WebSocketDisconnect
from datetime import datetime
import jwt
import os

logger = logging.getLogger(__name__)

# Import enhanced logging functions
try:
    from .enhanced_logging import log_websocket_event
except ImportError:
    # Fallback if enhanced logging is not available
    def log_websocket_event(event_type: str, user_id: str = None, details: str = None):
        logger.info(f"WebSocket {event_type}: {user_id} - {details}")

class ConnectionManager:
    def __init__(self):
        # Store connections by user type
        self.admin_connections: Set[WebSocket] = set()
        self.user_connections: Dict[str, WebSocket] = {}  # userId -> WebSocket
        self.authenticated_users: Dict[str, Dict[str, Any]] = {}  # token -> user_info
        
    async def connect(self, websocket: WebSocket, user_type: str, user_id: str = None):
        # Note: websocket.accept() should be called before this method
        
        if user_type == 'admin':
            self.admin_connections.add(websocket)
            logger.info(f"Admin connected. Total admin connections: {len(self.admin_connections)}")
        else:
            if user_id:
                self.user_connections[user_id] = websocket
                logger.info(f"User {user_id} connected. Total user connections: {len(self.user_connections)}")
    
    def disconnect(self, websocket: WebSocket, user_type: str, user_id: str = None):
        if user_type == 'admin':
            self.admin_connections.discard(websocket)
            logger.info(f"Admin disconnected. Total admin connections: {len(self.admin_connections)}")
        else:
            if user_id and user_id in self.user_connections:
                del self.user_connections[user_id]
                logger.info(f"User {user_id} disconnected. Total user connections: {len(self.user_connections)}")
    
    async def send_to_admins(self, message: Dict[str, Any]):
        if not self.admin_connections:
            logger.warning("No admin connections available")
            return
            
        message_str = json.dumps(message)
        disconnected = set()
        
        for connection in self.admin_connections:
            try:
                await connection.send_text(message_str)
            except Exception as e:
                logger.error(f"Error sending to admin: {e}")
                disconnected.add(connection)
        
        # Remove disconnected connections
        for connection in disconnected:
            self.admin_connections.discard(connection)
    
    async def send_to_user(self, user_id: str, message: Dict[str, Any]):
        if user_id not in self.user_connections:
            logger.warning(f"No connection found for user {user_id}")
            return
            
        try:
            message_str = json.dumps(message)
            await self.user_connections[user_id].send_text(message_str)
        except Exception as e:
            logger.error(f"Error sending to user {user_id}: {e}")
            # Remove the connection if it's broken
            if user_id in self.user_connections:
                del self.user_connections[user_id]

# Global connection manager
manager = ConnectionManager()

class WebSocketServer:
    def __init__(self):
        self.jwt_secret = os.getenv("JWT_SECRET_KEY", "your-super-secret-key-change-in-production")
        self.jwt_algorithm = "HS256"
        self.user_requests: Dict[str, Dict[str, Any]] = {}  # Store user requests
    
    def verify_token(self, token: str) -> Dict[str, Any]:
        """Verify JWT token and return user info"""
        try:
            payload = jwt.decode(token, self.jwt_secret, algorithms=[self.jwt_algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            raise ValueError("Token has expired")
        except jwt.InvalidTokenError:
            raise ValueError("Invalid token")
    
    async def handle_admin_connection(self, websocket: WebSocket):
        """Handle admin WebSocket connection with enhanced logging"""
        user_type = 'admin'
        user_id = None
        
        try:
            # Accept the WebSocket connection first
            await websocket.accept()
            log_websocket_event("connect", "admin", "Admin WebSocket connection accepted")
            
            while True:
                data = await websocket.receive_text()
                message = json.loads(data)
                
                if message.get('type') == 'auth':
                    # Verify admin token
                    try:
                        log_websocket_event("auth_attempt", "admin", "Admin authentication attempt")
                        user_info = self.verify_token(message.get('token', ''))
                        if 'admin' not in user_info.get('roles', []):
                            log_websocket_event("auth_failed", "admin", "Admin access denied - insufficient privileges")
                            await websocket.close(code=1008, reason="Admin access required")
                            return
                        
                        manager.authenticated_users[message.get('token')] = user_info
                        await manager.connect(websocket, user_type, user_id)
                        
                        log_websocket_event("auth_success", "admin", "Admin authentication successful")
                        
                        # Send initial data
                        await websocket.send_text(json.dumps({
                            'type': 'auth_success',
                            'message': 'Admin authentication successful'
                        }))
                        
                    except Exception as e:
                        log_websocket_event("auth_failed", "admin", f"Admin authentication failed: {e}")
                        await websocket.close(code=1008, reason="Authentication failed")
                        return
                
                elif message.get('type') == 'approve_request':
                    # Handle request approval
                    request_id = message.get('requestId')
                    admin_notes = message.get('adminNotes', '')
                    
                    # Update request status
                    if request_id in self.user_requests:
                        self.user_requests[request_id]['status'] = 'approved'
                        self.user_requests[request_id]['adminNotes'] = admin_notes
                        self.user_requests[request_id]['updated_at'] = datetime.utcnow().isoformat()
                        
                        # Get user ID from the request
                        user_id = self.user_requests[request_id].get('userId')
                        
                        # Broadcast to all admins
                        await manager.send_to_admins({
                            'type': 'request_updated',
                            'requestId': request_id,
                            'status': 'approved',
                            'adminNotes': admin_notes,
                            'timestamp': datetime.utcnow().isoformat()
                        })
                        
                        # Notify the user if they're connected
                        if user_id:
                            await manager.send_to_user(user_id, {
                                'type': 'request_approved',
                                'requestId': request_id,
                                'message': 'Your request has been approved!'
                            })
                
                elif message.get('type') == 'reject_request':
                    # Handle request rejection
                    request_id = message.get('requestId')
                    admin_notes = message.get('adminNotes', '')
                    
                    # Update request status
                    if request_id in self.user_requests:
                        self.user_requests[request_id]['status'] = 'rejected'
                        self.user_requests[request_id]['adminNotes'] = admin_notes
                        self.user_requests[request_id]['updated_at'] = datetime.utcnow().isoformat()
                        
                        # Get user ID from the request
                        user_id = self.user_requests[request_id].get('userId')
                        
                        # Broadcast to all admins
                        await manager.send_to_admins({
                            'type': 'request_updated',
                            'requestId': request_id,
                            'status': 'rejected',
                            'adminNotes': admin_notes,
                            'timestamp': datetime.utcnow().isoformat()
                        })
                        
                        # Notify the user if they're connected
                        if user_id:
                            await manager.send_to_user(user_id, {
                                'type': 'request_rejected',
                                'requestId': request_id,
                                'message': 'Your request has been rejected.'
                            })
        
        except WebSocketDisconnect:
            logger.info("Admin WebSocket disconnected")
        except Exception as e:
            logger.error(f"Error in admin WebSocket: {e}")
        finally:
            manager.disconnect(websocket, user_type, user_id)
    
    async def handle_user_connection(self, websocket: WebSocket, user_id: str):
        """Handle user WebSocket connection"""
        user_type = 'user'
        
        try:
            # Accept the WebSocket connection first
            await websocket.accept()
            
            while True:
                data = await websocket.receive_text()
                message = json.loads(data)
                
                if message.get('type') == 'auth':
                    # Verify user token
                    try:
                        user_info = self.verify_token(message.get('token', ''))
                        if user_info.get('user_id') != user_id:
                            await websocket.close(code=1008, reason="User ID mismatch")
                            return
                        
                        manager.authenticated_users[message.get('token')] = user_info
                        await manager.connect(websocket, user_type, user_id)
                        
                        await websocket.send_text(json.dumps({
                            'type': 'auth_success',
                            'message': 'User authentication successful'
                        }))
                        
                    except Exception as e:
                        await websocket.close(code=1008, reason="Authentication failed")
                        return
        
        except WebSocketDisconnect:
            logger.info(f"User {user_id} WebSocket disconnected")
        except Exception as e:
            logger.error(f"Error in user WebSocket: {e}")
        finally:
            manager.disconnect(websocket, user_type, user_id)
    
    async def broadcast_user_request(self, request: Dict[str, Any]):
        """Broadcast new user request to all admin connections"""
        # Store the request
        self.user_requests[request['id']] = request
        
        await manager.send_to_admins({
            'type': 'new_request',
            'request': request
        })
    
    def get_user_requests(self) -> Dict[str, Any]:
        """Get all user requests"""
        return self.user_requests

# Global WebSocket server instance
websocket_server = WebSocketServer()
