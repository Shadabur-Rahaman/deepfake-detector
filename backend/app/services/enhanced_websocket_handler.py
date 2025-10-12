# backend/app/services/enhanced_websocket_handler.py - Fixed Real-time WebSocket Handler

import asyncio
import json
import base64
import logging
import time
import cv2
import numpy as np
from typing import Dict, Any, Optional, Set
from fastapi import WebSocket, WebSocketDisconnect
from fastapi.websockets import WebSocketState
from dataclasses import dataclass
from enum import Enum

from .enhanced_async_detector import EnhancedAsyncDeepfakeDetector, DetectionConfig, DetectionResult, DetectionState
from .logging_config import get_logger, log_websocket_event, log_detection_event

logger = get_logger(__name__)

class ConnectionState(Enum):
    CONNECTING = "connecting"
    CONNECTED = "connected"
    PROCESSING = "processing"
    STOPPING = "stopping"
    DISCONNECTED = "disconnected"
    ERROR = "error"

@dataclass
class ClientInfo:
    """Information about a connected client"""
    websocket: WebSocket
    client_id: str
    state: ConnectionState
    connected_at: float
    frames_processed: int
    last_activity: float
    config: DetectionConfig
    last_result: Optional[DetectionResult] = None

class EnhancedWebSocketManager:
    """Enhanced WebSocket manager with proper real-time processing and temporal smoothing"""
    
    def __init__(self):
        self.active_connections: Dict[str, ClientInfo] = {}
        self.detector = EnhancedAsyncDeepfakeDetector()
        self.heartbeat_interval = 30.0  # seconds
        self.cleanup_interval = 60.0  # seconds
        self.max_inactive_time = 300.0  # 5 minutes
        
        # Start background tasks
        self.heartbeat_task = None
        self.cleanup_task = None
        self._start_background_tasks()
    
    def _start_background_tasks(self):
        """Start background maintenance tasks (will be started when first client connects)"""
        try:
            # Background tasks will be started when first client connects
            self.heartbeat_task = None
            self.cleanup_task = None
            self._background_tasks_started = False
            
            logger.info("[OK] Enhanced background tasks ready to start")
            
        except Exception as e:
            logger.error(f"[ERROR] Failed to setup background tasks: {e}")
    
    async def connect(self, websocket: WebSocket, client_id: str = None) -> str:
        """Accept a new WebSocket connection"""
        try:
            await websocket.accept()
            
            if client_id is None:
                import uuid
                client_id = f"client_{str(uuid.uuid4())[:8]}"
            
            # Create client info with enhanced config
            client_info = ClientInfo(
                websocket=websocket,
                client_id=client_id,
                state=ConnectionState.CONNECTED,
                connected_at=time.time(),
                frames_processed=0,
                last_activity=time.time(),
                config=DetectionConfig(
                    confidence_threshold=0.7,  # Higher threshold to reduce false positives
                    temporal_smoothing_window=5,
                    min_confidence_for_fake=0.8,
                    enable_temporal_smoothing=True,
                    batch_size=6,  # Add batch_size for consistency
                    enable_batching=True
                )
            )
            
            self.active_connections[client_id] = client_info
            
            # Send connection confirmation
            await self._send_message(client_id, {
                "type": "connection_ready",
                "message": "Enhanced AI Server Ready - Real-time detection with temporal smoothing",
                "status": "connected",
                "client_id": client_id,
                "features": {
                    "temporal_smoothing": True,
                    "false_positive_reduction": True,
                    "real_time_processing": True
                }
            })
            
            log_websocket_event(logger, "client_connected", client_id=client_id)
            return client_id
            
        except Exception as e:
            logger.error(f"[ERROR] Failed to connect client: {e}")
            raise
    
    async def disconnect(self, client_id: str, reason: str = "Client disconnected"):
        """Disconnect a client and cleanup resources with proper WebSocket state handling"""
        try:
            if client_id not in self.active_connections:
                logger.debug(f"Client {client_id} not in active connections, skipping disconnect")
                return
            
            client_info = self.active_connections[client_id]
            
            # Stop detection if running
            if client_info.state == ConnectionState.PROCESSING:
                await self.stop_detection(client_id)
            
            # Close WebSocket only if it's still connected
            try:
                if client_info.websocket.client_state == WebSocketState.CONNECTED:
                    await client_info.websocket.close(code=1000, reason=reason)
                else:
                    logger.debug(f"WebSocket for client {client_id} already disconnected (state: {client_info.websocket.client_state})")
            except Exception as close_error:
                logger.debug(f"Error closing WebSocket for client {client_id}: {close_error}")
            
            # Remove from active connections
            del self.active_connections[client_id]
            
            # Reset detector state to IDLE if no more active connections
            if not self.active_connections:
                self.detector.state = DetectionState.IDLE
                logger.info("[LOADING] Detector state reset to IDLE - ready for new clients")
            
            log_websocket_event(logger, "client_disconnected", client_id=client_id, reason=reason)
            
        except Exception as e:
            logger.error(f"[ERROR] Failed to disconnect client {client_id}: {e}")
            # Force remove from active connections even if there's an error
            if client_id in self.active_connections:
                del self.active_connections[client_id]
    
    async def start_detection(self, client_id: str, config: DetectionConfig = None) -> bool:
        """Start detection for a specific client"""
        try:
            if client_id not in self.active_connections:
                await self._send_error(client_id, "Client not found")
                return False
            
            client_info = self.active_connections[client_id]
            
            if client_info.state != ConnectionState.CONNECTED:
                await self._send_error(client_id, f"Cannot start detection in state: {client_info.state}")
                return False
            
            # Check detector state and reset if needed
            if self.detector.state == DetectionState.STOPPED:
                logger.info(f"[LOADING] Resetting detector state from STOPPED to IDLE for client {client_id}")
                self.detector.state = DetectionState.IDLE
            
            # Update config if provided
            if config:
                client_info.config = config
            
            # Start the enhanced async detector
            if not await self.detector.start_detection():
                error_msg = f"Failed to start enhanced detector (detector state: {self.detector.state})"
                logger.warning(f"Cannot initialize detector in state: {self.detector.state}")
                await self._send_error(client_id, error_msg)
                return False
            
            client_info.state = ConnectionState.PROCESSING
            
            await self._send_message(client_id, {
                "type": "detection_started",
                "message": "Enhanced real-time detection started successfully",
                "status": "processing",
                "config": {
                    "max_faces_per_frame": client_info.config.max_faces_per_frame,
                    "confidence_threshold": client_info.config.confidence_threshold,
                    "temporal_smoothing": client_info.config.enable_temporal_smoothing,
                    "min_fake_confidence": client_info.config.min_confidence_for_fake
                }
            })
            
            logger.info(f"[START] Enhanced detection started for client {client_id}")
            return True
            
        except Exception as e:
            logger.error(f"[ERROR] Failed to start detection for client {client_id}: {e}")
            await self._send_error(client_id, f"Failed to start detection: {str(e)}")
            return False
    
    async def stop_detection(self, client_id: str) -> bool:
        """Stop detection for a specific client"""
        try:
            if client_id not in self.active_connections:
                return False
            
            client_info = self.active_connections[client_id]
            
            if client_info.state != ConnectionState.PROCESSING:
                return True
            
            client_info.state = ConnectionState.STOPPING
            
            # Stop the enhanced async detector
            await self.detector.stop_detection()
            
            # Reset detector state to IDLE so it can be started again by new clients
            self.detector.state = DetectionState.IDLE
            
            client_info.state = ConnectionState.CONNECTED
            
            await self._send_message(client_id, {
                "type": "detection_stopped",
                "message": "Enhanced detection stopped successfully",
                "status": "connected",
                "frames_processed": client_info.frames_processed,
                "false_positives_corrected": self.detector.stats.get('false_positives_corrected', 0)
            })
            
            logger.info(f"[SHUTDOWN] Enhanced detection stopped for client {client_id}")
            return True
            
        except Exception as e:
            logger.error(f"[ERROR] Failed to stop detection for client {client_id}: {e}")
            await self._send_error(client_id, f"Failed to stop detection: {str(e)}")
            return False
    
    async def process_frame(self, client_id: str, frame_data: str) -> bool:
        """Process a frame for a specific client with continuous real-time processing"""
        try:
            if client_id not in self.active_connections:
                logger.warning(f"Client {client_id} not found in active connections")
                return False
            
            client_info = self.active_connections[client_id]
            
            if client_info.state != ConnectionState.PROCESSING:
                logger.warning(f"Detection not active for client {client_id}, state: {client_info.state}")
                await self._send_error(client_id, "Detection not active")
                return False
            
            # Decode frame
            try:
                frame_bytes = base64.b64decode(frame_data)
                nparr = np.frombuffer(frame_bytes, np.uint8)
                frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                
                if frame is None:
                    logger.warning(f"Invalid frame data for client {client_id}")
                    await self._send_error(client_id, "Invalid frame data")
                    return False
                
            except Exception as e:
                logger.error(f"Frame decoding failed for client {client_id}: {e}")
                await self._send_error(client_id, f"Frame decoding failed: {str(e)}")
                return False
            
            # Process frame with enhanced detector
            try:
                logger.info(f"[LOADING] Processing frame for client {client_id}")
                result = await self.detector.process_frame(frame)
                
                if result:
                    # Store last result for client
                    client_info.last_result = result
                    
                    # Send result to client
                    await self._send_detection_result(client_id, result)
                    client_info.frames_processed += 1
                    client_info.last_activity = time.time()
                    
                    # Log processing success for debugging
                    logger.info(f"[OK] Processed frame {result.frame_id} for client {client_id}: {result.prediction} ({result.confidence:.1f}%)")
                else:
                    logger.debug(f"Detector returned None for client {client_id} (likely frame skipped)")
                
                return True
                
            except Exception as e:
                logger.error(f"[ERROR] Frame processing failed for client {client_id}: {e}")
                await self._send_error(client_id, f"Frame processing failed: {str(e)}")
                return False
            
        except Exception as e:
            logger.error(f"[ERROR] Failed to process frame for client {client_id}: {e}")
            return False
    
    async def handle_message(self, client_id: str, message: Dict[str, Any]) -> bool:
        """Handle incoming WebSocket message"""
        try:
            if client_id not in self.active_connections:
                return False
            
            client_info = self.active_connections[client_id]
            client_info.last_activity = time.time()
            
            message_type = message.get("type", "unknown")
            
            if message_type == "start_detection":
                config_data = message.get("config", {})
                config = DetectionConfig(**config_data)
                return await self.start_detection(client_id, config)
            
            elif message_type == "stop_detection" or message_type == "stop":
                return await self.stop_detection(client_id)
            
            elif message_type == "frame":
                frame_data = message.get("frame", "")
                return await self.process_frame(client_id, frame_data)
            
            elif message_type == "ping":
                await self._send_message(client_id, {
                    "type": "pong",
                    "timestamp": time.time()
                })
                return True
            
            elif message_type == "get_stats":
                stats = self.detector.get_stats()
                await self._send_message(client_id, {
                    "type": "stats",
                    "stats": stats
                })
                return True
            
            elif message_type == "get_last_result":
                if client_info.last_result:
                    await self._send_detection_result(client_id, client_info.last_result)
                else:
                    await self._send_message(client_id, {
                        "type": "no_result",
                        "message": "No detection result available"
                    })
                return True
            
            else:
                await self._send_error(client_id, f"Unknown message type: {message_type}")
                return False
            
        except Exception as e:
            logger.error(f"[ERROR] Failed to handle message for client {client_id}: {e}")
            # Only send error if client is still connected
            try:
                if client_id in self.active_connections:
                    client_info = self.active_connections[client_id]
                    if client_info.websocket.client_state == WebSocketState.CONNECTED:
                        await self._send_error(client_id, f"Message handling failed: {str(e)}")
            except Exception as send_error:
                logger.debug(f"Could not send error to client {client_id}: {send_error}")
            return False
    
    async def _send_message(self, client_id: str, message: Dict[str, Any]):
        """Send a message to a specific client with proper WebSocket state checking"""
        try:
            if client_id not in self.active_connections:
                logger.debug(f"Client {client_id} not in active connections, skipping message")
                return
            
            client_info = self.active_connections[client_id]
            
            # Check if WebSocket is still connected
            if client_info.websocket.client_state != WebSocketState.CONNECTED:
                logger.debug(f"WebSocket for client {client_id} is not connected (state: {client_info.websocket.client_state}), skipping message")
                # Mark client for cleanup
                await self.disconnect(client_id, "WebSocket disconnected")
                return
            
            # Add timestamp
            message["timestamp"] = time.time()
            
            # Try to send the message
            try:
                await client_info.websocket.send_text(json.dumps(message))
            except Exception as send_error:
                # If sending fails, it means the WebSocket is disconnected
                if "WebSocket is not connected" in str(send_error) or "Need to call" in str(send_error):
                    logger.debug(f"WebSocket for client {client_id} disconnected during send")
                    await self.disconnect(client_id, "WebSocket disconnected during send")
                else:
                    raise send_error
            
        except Exception as e:
            # Only log as debug to avoid spam
            logger.debug(f"Failed to send message to client {client_id}: {e}")
            # Mark client for cleanup
            try:
                await self.disconnect(client_id, "Send failed")
            except:
                pass  # Ignore cleanup errors
    
    async def _send_detection_result(self, client_id: str, result: DetectionResult):
        """Send enhanced detection result to client"""
        try:
            # Convert timestamp to user-friendly format
            from datetime import datetime
            timestamp_dt = datetime.fromtimestamp(result.timestamp)
            formatted_time = timestamp_dt.strftime("%H:%M:%S")
            elapsed_time = result.timestamp - self.active_connections[client_id].connected_at
            
            # Convert result to dict with enhanced information
            result_dict = {
                "type": "detection_result",
                "frame_id": result.frame_id,
                "prediction": result.prediction,
                "confidence": result.confidence,
                "raw_confidence": result.raw_confidence,
                "faces_detected": result.faces_detected,
                "processing_time": round(result.processing_time, 1) if isinstance(result.processing_time, (int, float)) else result.processing_time,
                "timestamp": result.timestamp,
                "formatted_time": formatted_time,
                "elapsed_time": round(elapsed_time, 2),
                "temporal_smoothed": result.temporal_smoothed,
                "enhanced_features": {
                    "false_positive_reduction": True,
                    "temporal_smoothing": result.temporal_smoothed,
                    "confidence_threshold": self.detector.config.confidence_threshold
                }
            }
            
            # Add face results if available
            if result.face_results:
                result_dict["face_results"] = result.face_results
            
            # Add error if present
            if result.error:
                result_dict["error"] = result.error
            
            await self._send_message(client_id, result_dict)
            
        except Exception as e:
            logger.error(f"[ERROR] Failed to send detection result to client {client_id}: {e}")
    
    async def _send_error(self, client_id: str, error_message: str):
        """Send error message to client"""
        try:
            await self._send_message(client_id, {
                "type": "error",
                "message": error_message,
                "status": "error"
            })
        except Exception as e:
            # Don't log error sending errors to avoid spam
            logger.debug(f"Could not send error to client {client_id}: {e}")
    
    async def _heartbeat_loop(self):
        """Send periodic heartbeats to all connected clients"""
        try:
            while True:
                await asyncio.sleep(self.heartbeat_interval)
                
                # Send heartbeat to all connected clients
                for client_id in list(self.active_connections.keys()):
                    try:
                        await self._send_message(client_id, {
                            "type": "heartbeat",
                            "status": "connected",
                            "server_time": time.time(),
                            "detector_stats": self.detector.get_stats()
                        })
                    except:
                        # Client disconnected, will be cleaned up
                        pass
                
        except asyncio.CancelledError:
            logger.info("Heartbeat loop cancelled")
        except Exception as e:
            logger.error(f"[ERROR] Heartbeat loop failed: {e}")
    
    async def _cleanup_loop(self):
        """Cleanup inactive connections"""
        try:
            while True:
                await asyncio.sleep(self.cleanup_interval)
                
                current_time = time.time()
                inactive_clients = []
                
                # Find inactive clients
                for client_id, client_info in self.active_connections.items():
                    if current_time - client_info.last_activity > self.max_inactive_time:
                        inactive_clients.append(client_id)
                
                # Disconnect inactive clients
                for client_id in inactive_clients:
                    await self.disconnect(client_id, "Inactive timeout")
                
                if inactive_clients:
                    logger.info(f"🧹 Cleaned up {len(inactive_clients)} inactive clients")
                
        except asyncio.CancelledError:
            logger.info("Cleanup loop cancelled")
        except Exception as e:
            logger.error(f"[ERROR] Cleanup loop failed: {e}")
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get WebSocket manager statistics"""
        return {
            "active_connections": len(self.active_connections),
            "detector_stats": self.detector.get_stats(),
            "clients": {
                client_id: {
                    "state": client_info.state.value,
                    "connected_at": client_info.connected_at,
                    "frames_processed": client_info.frames_processed,
                    "last_activity": client_info.last_activity,
                    "last_result": client_info.last_result.prediction if client_info.last_result else None
                }
                for client_id, client_info in self.active_connections.items()
            }
        }
    
    async def shutdown(self):
        """Shutdown the WebSocket manager"""
        try:
            # Cancel background tasks
            if self.heartbeat_task:
                self.heartbeat_task.cancel()
            if self.cleanup_task:
                self.cleanup_task.cancel()
            
            # Disconnect all clients
            for client_id in list(self.active_connections.keys()):
                await self.disconnect(client_id, "Server shutdown")
            
            # Cleanup detector
            await self.detector.cleanup()
            
            logger.info("[SHUTDOWN] Enhanced WebSocket manager shutdown complete")
            
        except Exception as e:
            logger.error(f"[ERROR] Shutdown failed: {e}")

# Global enhanced WebSocket manager instance
enhanced_websocket_manager = EnhancedWebSocketManager()
