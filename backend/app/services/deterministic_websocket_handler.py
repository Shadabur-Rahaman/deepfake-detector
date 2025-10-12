# backend/app/services/deterministic_websocket_handler.py - Deterministic WebSocket Handler for Production-Grade Streaming

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
from datetime import datetime

from .deterministic_ensemble_detector import DeterministicEnsembleDetector, EnsembleResult
from .deterministic_config import get_deterministic_config
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
    last_result: Optional[EnsembleResult] = None
    frame_counter: int = 0

class DeterministicWebSocketManager:
    """Deterministic WebSocket manager with production-grade streaming"""
    
    def __init__(self):
        self.active_connections: Dict[str, ClientInfo] = {}
        self.ensemble_detector = DeterministicEnsembleDetector()
        self.config = get_deterministic_config()
        self.heartbeat_interval = 30.0  # seconds
        self.cleanup_interval = 60.0  # seconds
        self.max_inactive_time = 300.0  # 5 minutes
        
        # Start background tasks
        self.heartbeat_task = None
        self.cleanup_task = None
        self._start_background_tasks()
        
        # Initialize ensemble detector (will be called when first client connects)
        self._detector_initialized = False
    
    async def _initialize_detector(self):
        """Initialize the ensemble detector"""
        try:
            await self.ensemble_detector.initialize_models()
            logger.info("[OK] Deterministic ensemble detector initialized")
        except Exception as e:
            logger.error(f"[ERROR] Failed to initialize ensemble detector: {e}")
    
    def _start_background_tasks(self):
        """Start background maintenance tasks (will be started when first client connects)"""
        try:
            # Background tasks will be started when first client connects
            self.heartbeat_task = None
            self.cleanup_task = None
            self._background_tasks_started = False
            
            logger.info("[OK] Deterministic background tasks ready to start")
            
        except Exception as e:
            logger.error(f"[ERROR] Failed to setup background tasks: {e}")
    
    async def connect(self, websocket: WebSocket, client_id: str = None) -> str:
        """Accept a new WebSocket connection"""
        try:
            await websocket.accept()
            
            if client_id is None:
                import uuid
                client_id = f"client_{str(uuid.uuid4())[:8]}"
            
            # Create client info
            client_info = ClientInfo(
                websocket=websocket,
                client_id=client_id,
                state=ConnectionState.CONNECTED,
                connected_at=time.time(),
                frames_processed=0,
                last_activity=time.time(),
                frame_counter=0
            )
            
            self.active_connections[client_id] = client_info
            
            # Send connection confirmation with deterministic info
            await self._send_message(client_id, {
                "type": "connection_ready",
                "message": "Deterministic AI Server Ready - Production-grade ensemble detection",
                "status": "connected",
                "client_id": client_id,
                "features": {
                    "deterministic_mode": True,
                    "ensemble_detection": True,
                    "temporal_smoothing": True,
                    "per_model_outputs": True,
                    "preprocessing_hash": True
                },
                "config": {
                    "seed": self.config.seed,
                    "models_available": list(self.ensemble_detector.models.keys()),
                    "model_weights": self.config.get_model_weights(),
                    "thresholds": self.config.get_thresholds()
                }
            })
            
            log_websocket_event(logger, "client_connected", client_id=client_id)
            return client_id
            
        except Exception as e:
            logger.error(f"[ERROR] Failed to connect client: {e}")
            raise
    
    async def disconnect(self, client_id: str, reason: str = "Client disconnected"):
        """Disconnect a client and cleanup resources"""
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
                    logger.debug(f"WebSocket for client {client_id} already disconnected")
            except Exception as close_error:
                logger.debug(f"Error closing WebSocket for client {client_id}: {close_error}")
            
            # Remove from active connections
            del self.active_connections[client_id]
            
            log_websocket_event(logger, "client_disconnected", client_id=client_id, reason=reason)
            
        except Exception as e:
            logger.error(f"[ERROR] Failed to disconnect client {client_id}: {e}")
            # Force remove from active connections
            if client_id in self.active_connections:
                del self.active_connections[client_id]
    
    async def start_detection(self, client_id: str) -> bool:
        """Start detection for a specific client"""
        try:
            if client_id not in self.active_connections:
                await self._send_error(client_id, "Client not found")
                return False
            
            client_info = self.active_connections[client_id]
            
            if client_info.state != ConnectionState.CONNECTED:
                await self._send_error(client_id, f"Cannot start detection in state: {client_info.state}")
                return False
            
            client_info.state = ConnectionState.PROCESSING
            client_info.frame_counter = 0
            
            await self._send_message(client_id, {
                "type": "detection_started",
                "message": "Deterministic ensemble detection started",
                "status": "processing",
                "config": {
                    "deterministic_mode": True,
                    "models_available": list(self.ensemble_detector.models.keys()),
                    "model_weights": self.config.get_model_weights(),
                    "thresholds": self.config.get_thresholds()
                }
            })
            
            logger.info(f"[START] Deterministic detection started for client {client_id}")
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
            
            # Wait a moment for any ongoing processing
            await asyncio.sleep(0.1)
            
            client_info.state = ConnectionState.CONNECTED
            
            await self._send_message(client_id, {
                "type": "detection_stopped",
                "message": "Deterministic detection stopped",
                "status": "connected",
                "frames_processed": client_info.frames_processed,
                "stats": self.ensemble_detector.get_stats()
            })
            
            logger.info(f"[SHUTDOWN] Deterministic detection stopped for client {client_id}")
            return True
            
        except Exception as e:
            logger.error(f"[ERROR] Failed to stop detection for client {client_id}: {e}")
            await self._send_error(client_id, f"Failed to stop detection: {str(e)}")
            return False
    
    async def process_frame(self, client_id: str, frame_data: str) -> bool:
        """Process a frame for deterministic ensemble detection"""
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
            
            # Process frame with deterministic ensemble
            try:
                logger.info(f"[LOADING] Processing frame {client_info.frame_counter} for client {client_id}")
                
                # Detect faces deterministically
                from .deterministic_face_detector import detect_faces_deterministic
                faces, coordinates = detect_faces_deterministic(frame)
                
                if not faces:
                    # No faces detected, send result
                    await self._send_detection_result(client_id, {
                        "frame_id": client_info.frame_counter,
                        "timestamp": time.time(),
                        "prediction": "No Faces Detected",
                        "confidence": 0.0,
                        "faces_detected": 0,
                        "preproc_hash": "no_faces",
                        "models": {},
                        "fusion_raw": 0.5,
                        "fusion_smoothed": 0.5,
                        "decision": "no_faces",
                        "processing_time": 0.0
                    })
                    client_info.frames_processed += 1
                    client_info.last_activity = time.time()
                    return True
                
                # Run ensemble detection
                result = await self.ensemble_detector.detect_ensemble(faces, client_info.frame_counter)
                
                # Store last result
                client_info.last_result = result
                
                # Send comprehensive result
                await self._send_detection_result(client_id, self._format_ensemble_result(result))
                
                client_info.frames_processed += 1
                client_info.frame_counter += 1
                client_info.last_activity = time.time()
                
                logger.info(f"[OK] Processed frame {result.frame_id} for client {client_id}: {result.final_prediction} ({result.final_confidence:.1f}%)")
                
                return True
                
            except Exception as e:
                logger.error(f"[ERROR] Frame processing failed for client {client_id}: {e}")
                await self._send_error(client_id, f"Frame processing failed: {str(e)}")
                return False
            
        except Exception as e:
            logger.error(f"[ERROR] Failed to process frame for client {client_id}: {e}")
            return False
    
    def _format_ensemble_result(self, result: EnsembleResult) -> Dict[str, Any]:
        """Format ensemble result for WebSocket transmission"""
        try:
            # Convert timestamp to ISO format
            timestamp_dt = datetime.fromtimestamp(result.timestamp)
            timestamp_iso = timestamp_dt.isoformat() + "Z"
            
            # Format model results
            model_outputs = {}
            for model_name, model_result in result.model_results.items():
                model_outputs[model_name] = {
                    "prediction": model_result.prediction,
                    "confidence": model_result.confidence,
                    "raw_output": model_result.raw_output,
                    "processing_time": model_result.processing_time,
                    "success": model_result.success
                }
            
            return {
                "type": "detection_result",
                "frame_id": result.frame_id,
                "timestamp": result.timestamp,
                "timestamp_iso": timestamp_iso,
                "prediction": result.final_prediction,
                "confidence": result.final_confidence,
                "faces_detected": len(result.model_results),
                "preproc_hash": result.preproc_hash,
                "models": model_outputs,
                "fusion_raw": result.fusion_raw,
                "fusion_smoothed": result.fusion_smoothed,
                "decision": result.decision,
                "temporal_smoothed": result.temporal_smoothed,
                "processing_time": round(result.processing_time, 1) if isinstance(result.processing_time, (int, float)) else result.processing_time,
                "deterministic_mode": True
            }
            
        except Exception as e:
            logger.error(f"[ERROR] Failed to format ensemble result: {e}")
            return {
                "type": "detection_result",
                "frame_id": result.frame_id,
                "prediction": "Formatting Error",
                "confidence": 0.0,
                "error": str(e)
            }
    
    async def handle_message(self, client_id: str, message: Dict[str, Any]) -> bool:
        """Handle incoming WebSocket message"""
        try:
            if client_id not in self.active_connections:
                return False
            
            client_info = self.active_connections[client_id]
            client_info.last_activity = time.time()
            
            message_type = message.get("type", "unknown")
            
            if message_type == "start_detection":
                return await self.start_detection(client_id)
            
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
                stats = self.ensemble_detector.get_stats()
                await self._send_message(client_id, {
                    "type": "stats",
                    "stats": stats
                })
                return True
            
            elif message_type == "get_config":
                config_info = self.config.get_deterministic_info()
                await self._send_message(client_id, {
                    "type": "config",
                    "config": config_info
                })
                return True
            
            elif message_type == "get_last_result":
                if client_info.last_result:
                    await self._send_detection_result(client_id, self._format_ensemble_result(client_info.last_result))
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
            try:
                if client_id in self.active_connections:
                    client_info = self.active_connections[client_id]
                    if client_info.websocket.client_state == WebSocketState.CONNECTED:
                        await self._send_error(client_id, f"Message handling failed: {str(e)}")
            except Exception as send_error:
                logger.debug(f"Could not send error to client {client_id}: {send_error}")
            return False
    
    async def _send_message(self, client_id: str, message: Dict[str, Any]):
        """Send a message to a specific client"""
        try:
            if client_id not in self.active_connections:
                logger.debug(f"Client {client_id} not in active connections, skipping message")
                return
            
            client_info = self.active_connections[client_id]
            
            # Check if WebSocket is still connected
            if client_info.websocket.client_state != WebSocketState.CONNECTED:
                logger.debug(f"WebSocket for client {client_id} is not connected, skipping message")
                await self.disconnect(client_id, "WebSocket disconnected")
                return
            
            # Add timestamp
            message["timestamp"] = time.time()
            
            # Try to send the message
            try:
                await client_info.websocket.send_text(json.dumps(message))
            except Exception as send_error:
                if "WebSocket is not connected" in str(send_error) or "Need to call" in str(send_error):
                    logger.debug(f"WebSocket for client {client_id} disconnected during send")
                    await self.disconnect(client_id, "WebSocket disconnected during send")
                else:
                    raise send_error
            
        except Exception as e:
            logger.debug(f"Failed to send message to client {client_id}: {e}")
            try:
                await self.disconnect(client_id, "Send failed")
            except:
                pass
    
    async def _send_detection_result(self, client_id: str, result: Dict[str, Any]):
        """Send detection result to client"""
        try:
            await self._send_message(client_id, result)
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
                            "detector_stats": self.ensemble_detector.get_stats()
                        })
                    except:
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
            "detector_stats": self.ensemble_detector.get_stats(),
            "clients": {
                client_id: {
                    "state": client_info.state.value,
                    "connected_at": client_info.connected_at,
                    "frames_processed": client_info.frames_processed,
                    "last_activity": client_info.last_activity,
                    "last_result": client_info.last_result.final_prediction if client_info.last_result else None
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
            
            logger.info("[SHUTDOWN] Deterministic WebSocket manager shutdown complete")
            
        except Exception as e:
            logger.error(f"[ERROR] Shutdown failed: {e}")

# Global deterministic WebSocket manager instance
deterministic_websocket_manager = DeterministicWebSocketManager()
