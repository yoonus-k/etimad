"""
Cache Manager Module
Handles caching for document processing and API calls to optimize performance
"""

import os
import json
import hashlib
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Optional, Any
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CacheManager:
    """Manages caching for tender analysis to avoid redundant processing"""
    
    def __init__(self, cache_dir: str = "data/cache"):
        """
        Initialize cache manager
        
        Args:
            cache_dir: Directory to store cache files
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Cache subdirectories
        self.documents_cache = self.cache_dir / "documents"
        self.search_cache = self.cache_dir / "search"
        self.analysis_cache = self.cache_dir / "analysis"
        
        # Create subdirectories
        self.documents_cache.mkdir(exist_ok=True)
        self.search_cache.mkdir(exist_ok=True)
        self.analysis_cache.mkdir(exist_ok=True)
        
        # Cache expiry times
        self.document_cache_days = 30  # Document text cache expires after 30 days
        self.search_cache_days = 7     # Search results cache expires after 7 days
        self.analysis_cache_days = 90  # Analysis results cache expires after 90 days
        
        logger.info(f"✅ Cache Manager initialized at {self.cache_dir}")
    
    def _get_file_hash(self, file_path: Path) -> str:
        """
        Get MD5 hash of a file
        
        Args:
            file_path: Path to file
            
        Returns:
            MD5 hash string
        """
        hash_md5 = hashlib.md5()
        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception as e:
            logger.error(f"Failed to hash file {file_path}: {e}")
            return ""
    
    def _get_folder_hash(self, folder_path: Path) -> str:
        """
        Get combined hash of all files in a folder
        
        Args:
            folder_path: Path to folder
            
        Returns:
            Combined hash string
        """
        hashes = []
        try:
            for file_path in sorted(folder_path.rglob("*")):
                if file_path.is_file():
                    file_hash = self._get_file_hash(file_path)
                    if file_hash:
                        hashes.append(f"{file_path.name}:{file_hash}")
            
            combined = "|".join(hashes)
            return hashlib.md5(combined.encode()).hexdigest()
        except Exception as e:
            logger.error(f"Failed to hash folder {folder_path}: {e}")
            return ""
    
    def _is_cache_valid(self, cache_file: Path, max_age_days: int) -> bool:
        """
        Check if cache file is still valid
        
        Args:
            cache_file: Path to cache file
            max_age_days: Maximum age in days
            
        Returns:
            True if cache is valid, False otherwise
        """
        if not cache_file.exists():
            return False
        
        try:
            # Check file age
            file_age = datetime.now() - datetime.fromtimestamp(cache_file.stat().st_mtime)
            if file_age > timedelta(days=max_age_days):
                logger.info(f"Cache expired: {cache_file.name} (age: {file_age.days} days)")
                return False
            
            return True
        except Exception as e:
            logger.error(f"Failed to check cache validity: {e}")
            return False
    
    def get_document_cache(self, folder_path: Path) -> Optional[Dict]:
        """
        Get cached document extraction results
        
        Args:
            folder_path: Path to tender folder
            
        Returns:
            Cached document data or None if not found/invalid
        """
        folder_hash = self._get_folder_hash(folder_path)
        if not folder_hash:
            return None
        
        cache_file = self.documents_cache / f"{folder_hash}.json"
        
        if not self._is_cache_valid(cache_file, self.document_cache_days):
            return None
        
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            logger.info(f"✅ Document cache HIT for {folder_path.name}")
            return data
        except Exception as e:
            logger.error(f"Failed to read document cache: {e}")
            return None
    
    def set_document_cache(self, folder_path: Path, document_data: Dict) -> bool:
        """
        Cache document extraction results
        
        Args:
            folder_path: Path to tender folder
            document_data: Extracted document data to cache
            
        Returns:
            True if successful, False otherwise
        """
        folder_hash = self._get_folder_hash(folder_path)
        if not folder_hash:
            return False
        
        cache_file = self.documents_cache / f"{folder_hash}.json"
        
        try:
            # Add metadata
            document_data['_cache_metadata'] = {
                'folder_path': str(folder_path),
                'folder_hash': folder_hash,
                'cached_at': datetime.now().isoformat(),
                'expires_at': (datetime.now() + timedelta(days=self.document_cache_days)).isoformat()
            }
            
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(document_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"✅ Document cache SAVED for {folder_path.name}")
            return True
        except Exception as e:
            logger.error(f"Failed to save document cache: {e}")
            return False
    
    def get_search_cache(self, query: str) -> Optional[Dict]:
        """
        Get cached search results
        
        Args:
            query: Search query
            
        Returns:
            Cached search results or None if not found/invalid
        """
        query_hash = hashlib.md5(query.encode()).hexdigest()
        cache_file = self.search_cache / f"{query_hash}.json"
        
        if not self._is_cache_valid(cache_file, self.search_cache_days):
            return None
        
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            logger.info(f"✅ Search cache HIT for query: {query[:50]}...")
            return data
        except Exception as e:
            logger.error(f"Failed to read search cache: {e}")
            return None
    
    def set_search_cache(self, query: str, search_results: Dict) -> bool:
        """
        Cache search results
        
        Args:
            query: Search query
            search_results: Search results to cache
            
        Returns:
            True if successful, False otherwise
        """
        query_hash = hashlib.md5(query.encode()).hexdigest()
        cache_file = self.search_cache / f"{query_hash}.json"
        
        try:
            # Add metadata
            search_results['_cache_metadata'] = {
                'query': query,
                'query_hash': query_hash,
                'cached_at': datetime.now().isoformat(),
                'expires_at': (datetime.now() + timedelta(days=self.search_cache_days)).isoformat()
            }
            
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(search_results, f, ensure_ascii=False, indent=2)
            
            logger.info(f"✅ Search cache SAVED for query: {query[:50]}...")
            return True
        except Exception as e:
            logger.error(f"Failed to save search cache: {e}")
            return False
    
    def get_analysis_cache(self, tender_id: str) -> Optional[Dict]:
        """
        Get cached analysis results
        
        Args:
            tender_id: Tender ID
            
        Returns:
            Cached analysis or None if not found/invalid
        """
        cache_file = self.analysis_cache / f"{tender_id}.json"
        
        if not self._is_cache_valid(cache_file, self.analysis_cache_days):
            return None
        
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            logger.info(f"✅ Analysis cache HIT for tender {tender_id}")
            return data
        except Exception as e:
            logger.error(f"Failed to read analysis cache: {e}")
            return None
    
    def set_analysis_cache(self, tender_id: str, analysis_data: Dict) -> bool:
        """
        Cache analysis results
        
        Args:
            tender_id: Tender ID
            analysis_data: Analysis results to cache
            
        Returns:
            True if successful, False otherwise
        """
        cache_file = self.analysis_cache / f"{tender_id}.json"
        
        try:
            # Add metadata
            analysis_data['_cache_metadata'] = {
                'tender_id': tender_id,
                'cached_at': datetime.now().isoformat(),
                'expires_at': (datetime.now() + timedelta(days=self.analysis_cache_days)).isoformat()
            }
            
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(analysis_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"✅ Analysis cache SAVED for tender {tender_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to save analysis cache: {e}")
            return False
    
    def clear_cache(self, cache_type: str = "all") -> bool:
        """
        Clear cache files
        
        Args:
            cache_type: Type of cache to clear ('documents', 'search', 'analysis', 'all')
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if cache_type in ["documents", "all"]:
                for file in self.documents_cache.glob("*.json"):
                    file.unlink()
                logger.info("✅ Documents cache cleared")
            
            if cache_type in ["search", "all"]:
                for file in self.search_cache.glob("*.json"):
                    file.unlink()
                logger.info("✅ Search cache cleared")
            
            if cache_type in ["analysis", "all"]:
                for file in self.analysis_cache.glob("*.json"):
                    file.unlink()
                logger.info("✅ Analysis cache cleared")
            
            return True
        except Exception as e:
            logger.error(f"Failed to clear cache: {e}")
            return False
    
    def get_cache_stats(self) -> Dict:
        """
        Get cache statistics
        
        Returns:
            Dictionary with cache stats
        """
        try:
            doc_count = len(list(self.documents_cache.glob("*.json")))
            search_count = len(list(self.search_cache.glob("*.json")))
            analysis_count = len(list(self.analysis_cache.glob("*.json")))
            
            # Calculate total size
            total_size = 0
            for cache_dir in [self.documents_cache, self.search_cache, self.analysis_cache]:
                for file in cache_dir.glob("*.json"):
                    total_size += file.stat().st_size
            
            return {
                'documents_cached': doc_count,
                'searches_cached': search_count,
                'analyses_cached': analysis_count,
                'total_cache_size_mb': round(total_size / (1024 * 1024), 2),
                'cache_directory': str(self.cache_dir)
            }
        except Exception as e:
            logger.error(f"Failed to get cache stats: {e}")
            return {}


if __name__ == "__main__":
    # Test cache manager
    print("=" * 60)
    print("Cache Manager Test")
    print("=" * 60)
    
    cache = CacheManager()
    
    # Test document caching
    print("\n📁 Testing document cache...")
    test_folder = Path("downloads/test_tender")
    test_data = {
        'text': 'Sample tender text',
        'files': ['file1.pdf', 'file2.xlsx']
    }
    
    cache.set_document_cache(test_folder, test_data)
    cached = cache.get_document_cache(test_folder)
    
    if cached:
        print("✅ Document cache working!")
        print(f"Cached data: {cached}")
    
    # Test search caching
    print("\n🔍 Testing search cache...")
    test_query = "software licenses saudi arabia"
    test_results = {
        'results': ['result1', 'result2'],
        'count': 2
    }
    
    cache.set_search_cache(test_query, test_results)
    cached_search = cache.get_search_cache(test_query)
    
    if cached_search:
        print("✅ Search cache working!")
        print(f"Cached results: {cached_search}")
    
    # Get stats
    print("\n📊 Cache Statistics:")
    stats = cache.get_cache_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
