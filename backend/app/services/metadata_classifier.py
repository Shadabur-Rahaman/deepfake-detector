# backend/app/services/metadata_classifier.py - Enhanced Metadata/Title Classifier

import re
import logging
from typing import List, Dict, Tuple, Optional, Set
from pathlib import Path
from collections import defaultdict
import time

# Import comprehensive keyword lists
from .ai_keywords import (
    ALL_HIGH_CONFIDENCE_KEYWORDS, 
    MEDIUM_CONFIDENCE_AI_KEYWORDS, 
    LOW_CONFIDENCE_AI_KEYWORDS,
    get_comprehensive_keywords,
    get_keyword_counts
)

logger = logging.getLogger(__name__)

class FastKeywordMatcher:
    """Fast keyword matching using multiple strategies for performance"""
    
    def __init__(self, keywords: List[str]):
        self.keywords = keywords
        self.keyword_set = set(keyword.lower() for keyword in keywords)
        self.keyword_trie = self._build_trie(keywords)
        self.word_boundary_patterns = self._compile_word_patterns(keywords)
        
    def _build_trie(self, keywords: List[str]) -> Dict:
        """Build a trie for fast prefix matching"""
        trie = {}
        for keyword in keywords:
            current = trie
            for char in keyword.lower():
                if char not in current:
                    current[char] = {}
                current = current[char]
            current['_end'] = True
        return trie
    
    def _compile_word_patterns(self, keywords: List[str]) -> List[re.Pattern]:
        """Compile regex patterns for word boundary matching"""
        patterns = []
        for keyword in keywords:
            # Escape special regex characters
            escaped_keyword = re.escape(keyword)
            # Create patterns for different matching strategies
            patterns.extend([
                re.compile(rf'\b{escaped_keyword}\b', re.IGNORECASE),  # Full word
                re.compile(rf'{escaped_keyword}', re.IGNORECASE),       # Partial match
            ])
        return patterns
    
    def find_matches(self, text: str) -> List[str]:
        """Find all keyword matches in text using multiple strategies"""
        if not text:
            return []
        
        text_lower = text.lower()
        matches = set()
        
        # Strategy 1: Set intersection (fastest for exact matches)
        words = re.findall(r'\b\w+\b', text_lower)
        for word in words:
            if word in self.keyword_set:
                matches.add(word)
        
        # Strategy 2: Substring matching for partial matches
        for keyword in self.keywords:
            if keyword.lower() in text_lower:
                matches.add(keyword)
        
        # Strategy 3: Regex patterns for complex matching
        for pattern in self.word_boundary_patterns:
            if pattern.search(text):
                # Extract the matched keyword
                match = pattern.search(text)
                if match:
                    matched_text = match.group().lower()
                    # Find the original keyword case
                    for keyword in self.keywords:
                        if keyword.lower() == matched_text:
                            matches.add(keyword)
                            break
        
        return list(matches)

class MetadataClassifier:
    """Enhanced metadata classifier for detecting AI/deepfake tool indicators"""
    
    def __init__(self):
        """Initialize the metadata classifier with comprehensive keyword lists"""
        
        # Load comprehensive keyword lists
        keyword_data = get_comprehensive_keywords()
        self.high_confidence_keywords = keyword_data['high_confidence']
        self.medium_confidence_keywords = keyword_data['medium_confidence']
        self.low_confidence_keywords = keyword_data['low_confidence']
        
        # Initialize fast matchers
        self.high_confidence_matcher = FastKeywordMatcher(self.high_confidence_keywords)
        self.medium_confidence_matcher = FastKeywordMatcher(self.medium_confidence_keywords)
        self.low_confidence_matcher = FastKeywordMatcher(self.low_confidence_keywords)
        
        # Performance tracking
        self.stats = {
            'total_classifications': 0,
            'total_processing_time': 0.0,
            'average_processing_time': 0.0,
            'keyword_counts': get_keyword_counts()
        }
        
        logger.info(f"[OK] MetadataClassifier initialized with {self.stats['keyword_counts']['total']} keywords")
        logger.info(f"   High confidence: {self.stats['keyword_counts']['high_confidence']}")
        logger.info(f"   Medium confidence: {self.stats['keyword_counts']['medium_confidence']}")
        logger.info(f"   Low confidence: {self.stats['keyword_counts']['low_confidence']}")
    
    def classify_metadata(self, 
                         title: str = "", 
                         filename: str = "", 
                         description: str = "",
                         uploader: str = "",
                         tags: List[str] = None) -> Tuple[float, List[str]]:
        """
        Classify metadata and return bias score and matched keywords
        
        Args:
            title: Video title
            filename: File name
            description: Video description
            uploader: Uploader name
            tags: List of tags
            
        Returns:
            Tuple of (bias_score, matched_keywords)
        """
        start_time = time.time()
        
        try:
            # Combine all text sources
            text_sources = {
                'title': title or '',
                'filename': filename or '',
                'description': description or '',
                'uploader': uploader or '',
                'tags': ' '.join(tags) if tags else ''
            }
            
            # Combine all text for analysis
            combined_text = ' '.join([v for v in text_sources.values() if v])
            
            if not combined_text.strip():
                return 0.0, []
            
            # Use fast matchers for each confidence level
            high_matches = self.high_confidence_matcher.find_matches(combined_text)
            medium_matches = self.medium_confidence_matcher.find_matches(combined_text)
            low_matches = self.low_confidence_matcher.find_matches(combined_text)
            
            # Calculate bias score
            bias_score = 0.0
            matched_keywords = []
            
            # High confidence matches (bias: +0.15 each, max +0.30)
            if high_matches:
                bias_score += min(len(high_matches) * 0.15, 0.30)
                matched_keywords.extend(high_matches)
            
            # Medium confidence matches (bias: +0.10 each, max +0.20)
            if medium_matches:
                bias_score += min(len(medium_matches) * 0.10, 0.20)
                matched_keywords.extend(medium_matches)
            
            # Low confidence matches (bias: +0.05 each, max +0.10)
            if low_matches:
                bias_score += min(len(low_matches) * 0.05, 0.10)
                matched_keywords.extend(low_matches)
            
            # Cap total bias at 0.30 to avoid over-biasing
            bias_score = min(bias_score, 0.30)
            
            # Remove duplicates while preserving order
            matched_keywords = list(dict.fromkeys(matched_keywords))
            
            # Update performance stats
            processing_time = time.time() - start_time
            self.stats['total_classifications'] += 1
            self.stats['total_processing_time'] += processing_time
            self.stats['average_processing_time'] = self.stats['total_processing_time'] / self.stats['total_classifications']
            
            logger.info(f"🔍 Metadata classification: bias={bias_score:.3f}, keywords={matched_keywords[:5]}{'...' if len(matched_keywords) > 5 else ''} ({processing_time*1000:.1f}ms)")
            
            return bias_score, matched_keywords
            
        except Exception as e:
            logger.error(f"[ERROR] Metadata classification failed: {e}")
            return 0.0, []
    
    def classify_youtube_metadata(self, metadata: Dict) -> Tuple[float, List[str]]:
        """
        Classify YouTube metadata specifically
        
        Args:
            metadata: YouTube metadata dictionary
            
        Returns:
            Tuple of (bias_score, matched_keywords)
        """
        try:
            title = metadata.get('title', '')
            description = metadata.get('description', '')
            uploader = metadata.get('uploader', '')
            
            # Extract tags if available
            tags = []
            if 'tags' in metadata and isinstance(metadata['tags'], list):
                tags = metadata['tags']
            
            return self.classify_metadata(
                title=title,
                filename="",  # YouTube doesn't have filename
                description=description,
                uploader=uploader,
                tags=tags
            )
            
        except Exception as e:
            logger.error(f"[ERROR] YouTube metadata classification failed: {e}")
            return 0.0, []
    
    def classify_uploaded_file(self, filename: str, user_description: str = "") -> Tuple[float, List[str]]:
        """
        Classify uploaded file metadata
        
        Args:
            filename: Uploaded file name
            user_description: Optional user-provided description
            
        Returns:
            Tuple of (bias_score, matched_keywords)
        """
        try:
            # Extract filename without extension for analysis
            filename_base = Path(filename).stem if filename else ""
            
            return self.classify_metadata(
                title="",  # No title for uploaded files
                filename=filename_base,
                description=user_description,
                uploader="",  # No uploader for uploaded files
                tags=[]
            )
            
        except Exception as e:
            logger.error(f"[ERROR] Uploaded file classification failed: {e}")
            return 0.0, []
    
    def get_keyword_categories(self) -> Dict[str, List[str]]:
        """Get all keyword categories for debugging/display"""
        return {
            'high_confidence': self.high_confidence_keywords,
            'medium_confidence': self.medium_confidence_keywords,
            'low_confidence': self.low_confidence_keywords
        }
    
    def get_performance_stats(self) -> Dict[str, any]:
        """Get performance statistics"""
        return {
            **self.stats,
            'keywords_per_second': self.stats['total_classifications'] / max(self.stats['total_processing_time'], 0.001),
            'memory_usage_mb': self._estimate_memory_usage()
        }
    
    def _estimate_memory_usage(self) -> float:
        """Estimate memory usage in MB"""
        import sys
        total_size = 0
        for keyword_list in [self.high_confidence_keywords, self.medium_confidence_keywords, self.low_confidence_keywords]:
            total_size += sys.getsizeof(keyword_list)
            for keyword in keyword_list:
                total_size += sys.getsizeof(keyword)
        return total_size / (1024 * 1024)  # Convert to MB
    
    def add_custom_keywords(self, 
                          high_keywords: List[str] = None,
                          medium_keywords: List[str] = None,
                          low_keywords: List[str] = None):
        """
        Add custom keywords to the classifier
        
        Args:
            high_keywords: High confidence keywords to add
            medium_keywords: Medium confidence keywords to add
            low_keywords: Low confidence keywords to add
        """
        try:
            if high_keywords:
                self.high_confidence_keywords.extend(high_keywords)
                # Reinitialize matcher with new keywords
                self.high_confidence_matcher = FastKeywordMatcher(self.high_confidence_keywords)
            
            if medium_keywords:
                self.medium_confidence_keywords.extend(medium_keywords)
                # Reinitialize matcher with new keywords
                self.medium_confidence_matcher = FastKeywordMatcher(self.medium_confidence_keywords)
            
            if low_keywords:
                self.low_confidence_keywords.extend(low_keywords)
                # Reinitialize matcher with new keywords
                self.low_confidence_matcher = FastKeywordMatcher(self.low_confidence_keywords)
            
            # Update keyword counts
            self.stats['keyword_counts'] = get_keyword_counts()
            
            logger.info(f"[OK] Added custom keywords: high={len(high_keywords or [])}, medium={len(medium_keywords or [])}, low={len(low_keywords or [])}")
            
        except Exception as e:
            logger.error(f"[ERROR] Failed to add custom keywords: {e}")
    
    def search_keywords(self, query: str, confidence_level: str = "all") -> List[str]:
        """
        Search for keywords matching a query
        
        Args:
            query: Search query
            confidence_level: "high", "medium", "low", or "all"
            
        Returns:
            List of matching keywords
        """
        query_lower = query.lower()
        matches = []
        
        if confidence_level in ["all", "high"]:
            matches.extend([kw for kw in self.high_confidence_keywords if query_lower in kw.lower()])
        
        if confidence_level in ["all", "medium"]:
            matches.extend([kw for kw in self.medium_confidence_keywords if query_lower in kw.lower()])
        
        if confidence_level in ["all", "low"]:
            matches.extend([kw for kw in self.low_confidence_keywords if query_lower in kw.lower()])
        
        return matches
    
    def benchmark_performance(self, test_texts: List[str], iterations: int = 100) -> Dict[str, float]:
        """
        Benchmark the classifier performance
        
        Args:
            test_texts: List of test texts to classify
            iterations: Number of iterations to run
            
        Returns:
            Performance metrics
        """
        import time
        
        start_time = time.time()
        
        for _ in range(iterations):
            for text in test_texts:
                self.classify_metadata(title=text)
        
        total_time = time.time() - start_time
        
        return {
            'total_time': total_time,
            'iterations': iterations,
            'texts_per_iteration': len(test_texts),
            'total_classifications': iterations * len(test_texts),
            'classifications_per_second': (iterations * len(test_texts)) / total_time,
            'average_time_per_classification': total_time / (iterations * len(test_texts))
        }

# Global classifier instance
metadata_classifier = MetadataClassifier()

def classify_metadata(title: str = "", filename: str = "", description: str = "", 
                    uploader: str = "", tags: List[str] = None) -> Tuple[float, List[str]]:
    """Convenience function for metadata classification"""
    return metadata_classifier.classify_metadata(title, filename, description, uploader, tags)

def classify_youtube_metadata(metadata: Dict) -> Tuple[float, List[str]]:
    """Convenience function for YouTube metadata classification"""
    return metadata_classifier.classify_youtube_metadata(metadata)

def classify_uploaded_file(filename: str, user_description: str = "") -> Tuple[float, List[str]]:
    """Convenience function for uploaded file classification"""
    return metadata_classifier.classify_uploaded_file(filename, user_description)
