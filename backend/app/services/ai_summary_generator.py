"""
AI Summary Generator Service
=============================
Generates intelligent, contextual summaries using AI models (OpenAI, Claude, Gemini)
for deepfake detection results.
"""

import os
import json
import logging
from typing import Dict, Optional, Any
import asyncio

logger = logging.getLogger(__name__)

class AISummaryGeneratorService:
    """Service to generate AI-powered summaries for detection results"""
    
    def __init__(self):
        self.openai_key = os.getenv('OPENAI_API_KEY')
        self.claude_key = os.getenv('CLAUDE_API_KEY')
        self.gemini_key = os.getenv('GEMINI_API_KEY')
        self.openai_enabled = os.getenv('ENABLE_OPENAI_API', 'true').lower() == 'true'
        self.claude_enabled = os.getenv('ENABLE_CLAUDE_API', 'true').lower() == 'true'
        self.gemini_enabled = os.getenv('ENABLE_GEMINI_API', 'true').lower() == 'true'
        
        self.available_apis = []
        if self.openai_key and self.openai_enabled:
            self.available_apis.append('openai')
        if self.claude_key and self.claude_enabled:
            self.available_apis.append('claude')
        if self.gemini_key and self.gemini_enabled:
            self.available_apis.append('gemini')
        
        logger.info(f"[AISummary] Available AI APIs: {self.available_apis}")
    
    async def generate_summary(
        self,
        detection_result: Dict[str, Any],
        mode: str = 'default'
    ) -> Optional[str]:
        """
        Generate AI-powered summary for detection results
        
        Args:
            detection_result: Complete detection result dictionary
            mode: Summary mode ('detailed', 'concise', 'default')
        
        Returns:
            AI-generated summary string or None if API unavailable
        """
        if not self.available_apis:
            logger.warning("[AISummary] No AI APIs available for summary generation")
            return None
        
        # Try APIs in order of preference
        for api_name in self.available_apis:
            try:
                if api_name == 'openai':
                    summary = await self._generate_with_openai(detection_result, mode)
                    if summary:
                        return summary
                elif api_name == 'claude':
                    summary = await self._generate_with_claude(detection_result, mode)
                    if summary:
                        return summary
                elif api_name == 'gemini':
                    summary = await self._generate_with_gemini(detection_result, mode)
                    if summary:
                        return summary
            except Exception as e:
                logger.warning(f"[AISummary] {api_name} API failed: {e}")
                continue
        
        return None
    
    async def _generate_with_openai(self, detection_result: Dict[str, Any], mode: str) -> Optional[str]:
        """Generate summary using OpenAI GPT-4"""
        try:
            import openai
            
            client = openai.OpenAI(api_key=self.openai_key)
            
            # Build comprehensive prompt
            prompt = self._build_prompt(detection_result, mode)
            
            response = await asyncio.to_thread(
                client.chat.completions.create,
                model="gpt-4o-mini",  # Use mini for cost efficiency
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert in deepfake detection and video forensics. Generate detailed, unique summaries based on detection analysis results. Focus on specific technical details, metrics, and evidence."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=1200  # Increased for 3-5 line comprehensive summaries with unique details
            )
            
            summary = response.choices[0].message.content.strip()
            logger.info(f"[AISummary] Generated summary via OpenAI ({len(summary)} chars)")
            return summary
            
        except ImportError:
            logger.warning("[AISummary] OpenAI library not installed")
            return None
        except Exception as e:
            logger.error(f"[AISummary] OpenAI API error: {e}")
            return None
    
    async def _generate_with_claude(self, detection_result: Dict[str, Any], mode: str) -> Optional[str]:
        """Generate summary using Claude API"""
        try:
            import anthropic
            
            client = anthropic.Anthropic(api_key=self.claude_key)
            
            prompt = self._build_prompt(detection_result, mode)
            
            response = await asyncio.to_thread(
                client.messages.create,
                model="claude-3-5-sonnet-20241022",
                max_tokens=1200,  # Increased for 3-5 line comprehensive summaries with unique details
                temperature=0.7,
                system="You are an expert in deepfake detection and video forensics. Generate detailed, unique summaries based on detection analysis results. Focus on specific technical details, metrics, and evidence.",
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            summary = response.content[0].text.strip()
            logger.info(f"[AISummary] Generated summary via Claude ({len(summary)} chars)")
            return summary
            
        except ImportError:
            logger.warning("[AISummary] Anthropic library not installed")
            return None
        except Exception as e:
            logger.error(f"[AISummary] Claude API error: {e}")
            return None
    
    async def _generate_with_gemini(self, detection_result: Dict[str, Any], mode: str) -> Optional[str]:
        """Generate summary using Gemini API"""
        try:
            import google.generativeai as genai
            
            genai.configure(api_key=self.gemini_key)
            model = genai.GenerativeModel('gemini-pro')
            
            prompt = self._build_prompt(detection_result, mode)
            
            response = await asyncio.to_thread(
                model.generate_content,
                prompt
            )
            
            summary = response.text.strip()
            logger.info(f"[AISummary] Generated summary via Gemini ({len(summary)} chars)")
            return summary
            
        except ImportError:
            logger.warning("[AISummary] Google Generative AI library not installed")
            return None
        except Exception as e:
            logger.error(f"[AISummary] Gemini API error: {e}")
            return None
    
    def _build_prompt(self, detection_result: Dict[str, Any], mode: str) -> str:
        """Build comprehensive prompt for AI summary generation"""
        
        # Extract key information
        prediction = detection_result.get('prediction', 'Unknown')
        confidence = detection_result.get('confidence', 0)
        faces_detected = detection_result.get('faces_detected', 0)
        processing_time = detection_result.get('processing_time', 0)
        
        model_info = detection_result.get('model_info', {})
        
        # ✅ CRITICAL: Detect mode from multiple possible sources
        detection_mode = (
            detection_result.get('detection_mode') or 
            detection_result.get('mode') or
            model_info.get('detection_mode') or
            'Standard'
        )
        
        # Normalize mode names
        detection_mode_upper = str(detection_mode).upper()
        if 'TRADITIONAL' in detection_mode_upper or detection_mode_upper == 'TRADITIONAL':
            detection_mode = 'Traditional'
        elif 'MODERN' in detection_mode_upper or 'MODERN AI' in detection_mode_upper:
            detection_mode = 'Modern AI'
        elif 'HYBRID' in detection_mode_upper or detection_mode_upper == 'HYBRID':
            detection_mode = 'Hybrid'
        
        # Extract scores
        temporal_consistency = detection_result.get('temporal_consistency')
        model_contributions = detection_result.get('model_contributions', {})
        frequency_score = model_contributions.get('frequency_score')
        temporal_score = model_contributions.get('temporal_score')
        spatial_score = model_contributions.get('spatial_score')
        ensemble_scores = detection_result.get('ensemble_scores', {})
        
        # Extract video characteristics
        video_duration = detection_result.get('video_duration')
        frame_count = detection_result.get('frame_count')
        face_quality = detection_result.get('face_quality_score')
        
        # Extract model details
        models_used = model_info.get('models_used', [])
        model_count = model_info.get('model_count', 1)
        analysis_method = detection_result.get('analysis_method', '')
        
        # Extract anomalies
        anomalies = detection_result.get('anomalies', [])
        ai_tool = detection_result.get('ai_tool_detected')
        
        # ✅ PRODUCTION-GRADE: Extract artifact scores and backend log details from multiple sources
        # Try ultra_ensemble_25 first (most comprehensive)
        ultra_result = detection_result.get('ultra_ensemble_25', {})
        if isinstance(ultra_result, dict):
            ultra_artifact_scores = ultra_result.get('artifact_scores', {}) or ultra_result.get('detailed_results', {}).get('artifact_scores', {})
            if isinstance(ultra_artifact_scores, dict):
                artifact_scores = ultra_artifact_scores
            elif ultra_result.get('artifact_score'):
                artifact_scores = {'overall_artifact_score': ultra_result.get('artifact_score')}
            else:
                artifact_scores = detection_result.get('artifact_scores', {}) or detection_result.get('model_contributions', {}).get('artifact_scores', {})
        else:
            artifact_scores = detection_result.get('artifact_scores', {}) or detection_result.get('model_contributions', {}).get('artifact_scores', {})
        
        if not isinstance(artifact_scores, dict):
            artifact_scores = {}
        
        overall_artifact_score = artifact_scores.get('overall_artifact_score', 0.0)
        if overall_artifact_score == 0.0:
            overall_artifact_score = detection_result.get('artifact_score', 0.0) or detection_result.get('overall_artifact_score', 0.0)
        
        # Extract specific artifact types (backend log categories)
        artifact_types = []
        if isinstance(artifact_scores, dict):
            artifact_types = [
                f"{k.replace('_', ' ').title()}" 
                for k, v in artifact_scores.items() 
                if isinstance(v, (int, float)) and v > 0.2 and k not in ['overall_artifact_score', 'artifact_score', 'anomaly_score']
            ]
            # Also check for detected_anomalies list
            detected_anomalies_list = artifact_scores.get('detected_anomalies', [])
            if isinstance(detected_anomalies_list, list):
                artifact_types.extend([a.replace('_', ' ').title() for a in detected_anomalies_list[:5]])
        
        # Extract face anomaly details from backend logs
        face_anomalies = []
        anomaly_score = 0.0
        if isinstance(artifact_scores, dict):
            face_anomaly_keys = ['lip_sync_issue', 'eye_inconsistency', 'eyebrow_misalignment', 
                               'facial_structure_distortion', 'face_swap_artifact']
            for key in face_anomaly_keys:
                if key in artifact_scores and artifact_scores[key] > 0.2:
                    face_anomalies.append(key.replace('_', ' ').title())
            anomaly_score = artifact_scores.get('anomaly_score', 0.0)
            
        # Also check ultra_ensemble detailed_results for anomalies
        if isinstance(ultra_result, dict):
            ultra_detailed = ultra_result.get('detailed_results', {})
            if isinstance(ultra_detailed, dict):
                ultra_anomalies = ultra_detailed.get('detected_anomalies', [])
                if isinstance(ultra_anomalies, list):
                    face_anomalies.extend([a.replace('_', ' ').title() for a in ultra_anomalies if a not in [f.lower().replace(' ', '_') for f in face_anomalies]])
                    if not anomaly_score:
                        anomaly_score = ultra_detailed.get('overall_anomaly_score', 0.0)
        
        # Remove duplicates from face_anomalies
        face_anomalies = list(dict.fromkeys(face_anomalies))  # Preserves order
        
        # Extract model contributions breakdown
        model_contributions_detail = detection_result.get('model_contributions_list', []) or detection_result.get('individual_results', {})
        top_contributing_models = []
        if isinstance(model_contributions_detail, dict):
            top_contributing_models = sorted(
                [(k, v) for k, v in model_contributions_detail.items() if isinstance(v, (int, float))],
                key=lambda x: x[1], reverse=True
            )[:3]
        
        # Extract hybrid/enhanced specific data
        model_categories = detection_result.get('model_categories', {})
        stage_results = detection_result.get('stage_results', [])
        hybrid_ensemble_score = detection_result.get('hybrid_ensemble_score')
        cross_validation_score = detection_result.get('cross_validation_score')
        
        # Determine if this is authentic or deepfake
        prediction_upper = prediction.upper()
        is_authentic = 'AUTHENTIC' in prediction_upper or 'REAL' in prediction_upper or 'GENUINE' in prediction_upper
        
        if is_authentic:
            prompt = f"""Generate a detailed, unique summary for an AUTHENTIC/REAL video detection analysis result.

DETECTION RESULTS:
- Prediction: {prediction}
- Confidence: {confidence}%
- Detection Mode: {detection_mode}
- Faces Analyzed: {faces_detected}
- Processing Time: {processing_time}s
"""
        
        if video_duration:
            prompt += f"- Video Duration: {video_duration}s\n"
        if frame_count:
            prompt += f"- Frames Analyzed: {frame_count}\n"
        if face_quality:
            prompt += f"- Face Quality Score: {face_quality * 100:.1f}%\n"
        
        prompt += "\nTECHNICAL METRICS:\n"
        
        if temporal_consistency is not None:
            prompt += f"- Temporal Consistency: {temporal_consistency * 100:.1f}%\n"
        if frequency_score is not None:
            prompt += f"- Frequency Analysis Score: {frequency_score * 100:.1f}%\n"
        if temporal_score is not None:
            prompt += f"- Temporal Score: {temporal_score * 100:.1f}%\n"
        if spatial_score is not None:
            prompt += f"- Spatial Score: {spatial_score * 100:.1f}%\n"
        
        prompt += f"\nMODELS USED:\n"
        prompt += f"- Model Count: {model_count}\n"
        if models_used:
            prompt += f"- Models: {', '.join(models_used[:5])}\n"
        if analysis_method:
            prompt += f"- Analysis Method: {analysis_method}\n"
        
        if model_categories:
            prompt += f"\nMODEL CATEGORIES:\n"
            if model_categories.get('traditional_models'):
                prompt += f"- Traditional Models: {model_categories['traditional_models']}\n"
            if model_categories.get('modern_ai_models'):
                prompt += f"- Modern AI Models: {model_categories['modern_ai_models']}\n"
            if model_categories.get('cloud_ai_models'):
                prompt += f"- Cloud AI Models: {model_categories['cloud_ai_models']}\n"
        
        if ensemble_scores:
            top_scores = sorted(ensemble_scores.items(), key=lambda x: x[1], reverse=True)[:3]
            prompt += f"\nTOP MODEL SCORES:\n"
            for model, score in top_scores:
                prompt += f"- {model}: {score * 100:.1f}%\n"
        
        if anomalies:
            prompt += f"\nDETECTED ANOMALIES: {', '.join(anomalies[:5])}\n"
        
        # ✅ PRODUCTION-GRADE: Add artifact scores and backend log insights
        if overall_artifact_score and overall_artifact_score > 0:
            prompt += f"\nARTIFACT DETECTION (Backend Logs):\n"
            prompt += f"- Overall Artifact Score: {overall_artifact_score * 100:.1f}%\n"
            if artifact_types:
                prompt += f"- Specific Artifacts Detected: {', '.join(artifact_types[:5])}\n"
            if face_anomalies:
                prompt += f"- Face Anomalies: {', '.join(face_anomalies[:4])}\n"
            if anomaly_score and anomaly_score > 0:
                prompt += f"- Overall Anomaly Score: {anomaly_score * 100:.1f}%\n"
        
        if ai_tool:
            prompt += f"\nAI TOOL DETECTED: {ai_tool}\n"
        
        if hybrid_ensemble_score:
            prompt += f"\nHybrid Ensemble Score: {hybrid_ensemble_score * 100:.1f}%\n"
        
        if cross_validation_score:
            prompt += f"\nCross-Validation Score: {cross_validation_score * 100:.1f}%\n"
        
        if top_contributing_models:
            prompt += f"\nTOP CONTRIBUTING MODELS:\n"
            for model_name, score in top_contributing_models:
                prompt += f"- {model_name}: {score * 100:.1f}% contribution\n"
        
        if stage_results:
            prompt += f"\nSTAGE RESULTS:\n"
            for i, stage in enumerate(stage_results[:3], 1):
                stage_name = stage.get('stage') or stage.get('model', 'Unknown')
                stage_conf = stage.get('confidence', 0)
                prompt += f"- Stage {i} ({stage_name}): {stage_conf * 100:.1f}%\n"
        
        # ✅ PRODUCTION-GRADE: Enhanced instructions for 3-5 line unique summaries with backend logs
        # Mode-specific summary styles
        mode_specific_guidance = ""
        if detection_mode == "Traditional":
            mode_specific_guidance = """
TRADITIONAL MODE SUMMARY STYLE:
- Line 1: "Traditional CNN-based detection analyzed [N] faces using [specific models like Custom Finetuned, ResNet]."
- Line 2: "Backend analysis revealed [specific artifacts/anomalies from logs] - [blending artifacts, boundary mismatches, color inconsistencies, etc.]."
- Line 3: "[Primary model name] classified this as [prediction] based on [specific evidence like spatial irregularities, temporal inconsistencies]."
- Line 4: "Ensemble confirmation: [mention ResNet or other supporting models] contributed [specific insights]."
- Line 5 (optional): "Processing completed in [time]s with [notable technical details from logs]."
"""
        elif detection_mode == "Modern AI":
            mode_specific_guidance = """
MODERN AI MODE SUMMARY STYLE:
- Line 1: "Multi-Service AI Ensemble deployed [N] advanced detection models (EfficientNet, YOLOv8, Vision Transformer, CLIP, etc.) across [N] detected faces."
- Line 2: "Neural texture analysis and frequency domain inspection revealed [specific artifacts/anomalies] - [mention actual backend log findings like frequency artifacts, neural texture irregularities]."
- Line 3: "Advanced model contributions: [top 2-3 models] detected [specific characteristics] with [model-specific scores or confidence levels]."
- Line 4: "Temporal consistency analysis showed [X%] frame-to-frame coherence, while spatial analysis identified [specific spatial artifacts or integrity levels]."
- Line 5 (optional): "Modern AI detection pipeline concluded [prediction] after comprehensive multi-model ensemble analysis in [processing time]s."
"""
        elif detection_mode == "Hybrid":
            mode_specific_guidance = """
HYBRID MODE SUMMARY STYLE:
- Line 1: "Production-Grade Multi-Model Ensemble orchestrated [N] models (Traditional CNNs, Modern Transformers, Ultra Ensemble 24) analyzing [N] faces."
- Line 2: "Backend logs from Ultra Ensemble detected [artifact score%] overall artifacts including [specific types: color_inconsistency, compression_artifacts, blurriness, lighting_inconsistencies]."
- Line 3: "Face anomaly detection identified [specific anomalies: lip_sync_issue, eye_inconsistency, eyebrow_misalignment, facial_structure_distortion, face_swap_artifact] with [anomaly score%] overall anomaly score."
- Line 4: "Key contributing models: [top 3 models from ensemble] scored [scores] influencing the final [prediction] classification."
- Line 5: "Hybrid ensemble decision: [prediction] confirmed through weighted consensus of [total_models] models with [artifact-adjusted or model consensus] validation."
- Line 6 (optional): "Comprehensive analysis completed in [processing_time]s, integrating Traditional, Modern AI, and Ultra Ensemble detection capabilities."
"""
        else:
            mode_specific_guidance = """
DEFAULT SUMMARY STYLE:
- Line 1: Detection mode and video characteristics
- Line 2: Backend log insights (artifacts, anomalies)
- Line 3: Technical evidence and model contributions
- Line 4-5: Unique characteristics and processing insights
"""
        
        # Add authentic-specific guidance if prediction is authentic
        if is_authentic:
            authentic_guidance = """
AUTHENTIC CONTENT SUMMARY REQUIREMENTS:
- Generate EXACTLY 3-5 detailed lines (sentences) - ABSOLUTE MINIMUM 3 lines
- Focus on POSITIVE authenticity indicators: low artifact scores, high temporal consistency, natural frequency patterns, genuine spatial integrity
- DO NOT include percentages or numerical scores in the summary - use descriptive language instead (e.g., "excellent temporal consistency" instead of "80.0% temporal consistency")
- Include SPECIFIC technical evidence that supports authenticity using descriptive terms:
  * Artifact scores: Use "minimal artifacts", "no significant manipulation", "artifact-free analysis" instead of percentages
  * Temporal consistency: Use descriptive levels like "excellent", "strong", "good" temporal consistency instead of percentages
  * Spatial score: Use "strong", "moderate", "fair" spatial integrity instead of percentages
  * Frequency analysis: Use "natural frequency patterns", "minimal frequency artifacts" instead of percentages
  * Model consensus across {model_count} models confirming authenticity
- Emphasize the COMPREHENSIVE nature of the analysis: all {model_count} models independently verified authenticity
- Mention specific quality metrics: face quality (use "high", "good", "excellent"), video duration, frame count, processing time
- Use language like "confirmed authentic", "verified genuine", "natural characteristics", "no manipulation detected", "consensus validation"
- Include model-specific contributions: Mention model names but avoid percentage breakdowns
- Make it as detailed and technical as deepfake summaries, but focusing on authenticity evidence
- Confidence levels: Use descriptive terms like "high confidence", "very high confidence" instead of percentages
"""
            mode_specific_guidance += authentic_guidance
        
        prompt += f"""

{mode_specific_guidance}

CRITICAL PRODUCTION REQUIREMENTS:
- Generate EXACTLY 3-5 lines (sentences) - ABSOLUTE MINIMUM 3 lines, maximum 5-6 for comprehensive details
- Each line MUST be a complete, detailed sentence with specific information
- Make each summary COMPLETELY UNIQUE and mode-specific - Traditional focuses on CNN artifacts, Modern AI emphasizes neural texture analysis, Hybrid highlights comprehensive ensemble
- NEVER repeat the same summary structure - vary sentence order, phrasing, and emphasis for each video
"""
        
        # Add authentic-specific requirements if prediction is authentic
        if is_authentic:
            prompt += """
IMPORTANT FOR AUTHENTIC CONTENT:
- DO NOT include percentages, numerical scores, or percentage signs (%) in the summary
- Focus on POSITIVE authenticity indicators using descriptive language: "minimal manipulation", "excellent temporal consistency", "natural frequency patterns", "strong spatial integrity"
- Use language like "confirmed authentic", "verified genuine", "natural characteristics", "no manipulation detected", "consensus validation", "independently verified"
- Emphasize comprehensive model consensus: all {model_count} models independently verified authenticity
- Include specific quality metrics using descriptive terms: "high quality", "excellent quality" for face quality; mention video duration, frame count, processing time
- Use descriptive confidence levels: "high confidence", "very high confidence", "strong confidence" instead of percentages
- Make summaries as detailed and technical as deepfake summaries, but emphasizing authenticity evidence without numerical percentages
"""
        
        # For authentic content, don't include percentages in the prompt context
        if is_authentic:
            prompt += f"""
- Include SPECIFIC backend log findings in EVERY summary using DESCRIPTIVE LANGUAGE (NO PERCENTAGES):
  * Artifact scores: Use descriptive terms like "minimal artifacts", "no significant manipulation" instead of {overall_artifact_score * 100:.1f}%
  * Face anomalies: {', '.join(face_anomalies[:3]) if face_anomalies else 'none detected'} (use descriptive terms, no percentages)
  * Model contributions: Mention model names {', '.join([m[0] for m in top_contributing_models[:3]]) if top_contributing_models else 'ensemble models'} but avoid percentage breakdowns
  * Temporal consistency: Use descriptive levels (excellent/strong/good/moderate) instead of {temporal_consistency * 100:.1f}% if available
  * Spatial score: Use descriptive levels (strong/moderate/fair) instead of {spatial_score * 100:.1f}% if available
  * Frequency score: Use descriptive terms (natural patterns, minimal artifacts) instead of {frequency_score * 100:.1f}% if available
"""
        else:
            prompt += f"""
- Include SPECIFIC backend log numbers and findings in EVERY summary:
  * Artifact scores: {overall_artifact_score * 100:.1f}% overall, specific types: {', '.join(artifact_types[:3]) if artifact_types else 'none'}
  * Face anomalies: {', '.join(face_anomalies[:3]) if face_anomalies else 'none'} (anomaly_score: {anomaly_score * 100:.1f}% if available)
  * Model contributions: {', '.join([f"{m[0]} ({m[1]*100:.1f}%)" for m in top_contributing_models[:3]]) if top_contributing_models else 'ensemble consensus'}
  * Temporal consistency: {temporal_consistency * 100:.1f}% if available
  * Spatial score: {spatial_score * 100:.1f}% if available
  * Frequency score: {frequency_score * 100:.1f}% if available
"""
        
        prompt += f"""
- Use PRODUCTION-GRADE language: technical but professional, specific metrics, backend log references
- Reference actual model names from backend: {', '.join(models_used[:5]) if models_used else 'ensemble models'}
- Avoid generic templates - each summary must be unique to THIS video's specific analysis
- If processing took {processing_time}s, mention it naturally in context
- Include specific detection characteristics that distinguish THIS analysis
- Vary sentence structure: start some summaries with model names, others with metrics, others with detection mode
- Ensure each line adds distinct value - no redundant information across lines"""
        
        if mode == 'detailed':
            prompt += "\n\nMODE: DETAILED - Use 4-5 lines with deeper technical depth, specific model contributions, and comprehensive backend log integration."
        elif mode == 'concise':
            prompt += "\n\nMODE: CONCISE - Use 3-4 lines focusing on most critical findings and key backend log insights."
        
        return prompt

# Singleton instance
_summary_generator = None

def get_summary_generator() -> AISummaryGeneratorService:
    """Get singleton instance of AI summary generator"""
    global _summary_generator
    if _summary_generator is None:
        _summary_generator = AISummaryGeneratorService()
    return _summary_generator

