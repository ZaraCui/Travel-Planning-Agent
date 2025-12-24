"""
Itinerary Storage Service
Allows users to save and retrieve itineraries without authentication
Uses Redis for temporary storage and optional database for persistence
"""
import json
import uuid
from datetime import datetime, timedelta
from typing import Optional, Dict, List
import hashlib


class ItineraryStorage:
    """Manage itinerary storage and retrieval"""
    
    def __init__(self, cache_client=None, db_client=None):
        """
        Initialize storage
        
        Args:
            cache_client: Redis cache client for temporary storage
            db_client: Database client for persistent storage (optional)
        """
        self.cache = cache_client
        self.db = db_client
    
    def generate_share_id(self, itinerary_data: dict) -> str:
        """Generate unique share ID for itinerary"""
        # Create hash from content for deduplication
        content_hash = hashlib.md5(
            json.dumps(itinerary_data, sort_keys=True).encode()
        ).hexdigest()[:8]
        
        # Add random component for uniqueness
        random_component = uuid.uuid4().hex[:8]
        
        return f"{content_hash}-{random_component}"
    
    def save_itinerary(
        self, 
        itinerary_data: dict, 
        ttl_days: int = 30,
        persistent: bool = False
    ) -> Dict:
        """
        Save itinerary
        
        Args:
            itinerary_data: Itinerary data to save
            ttl_days: Days until expiration (for cache)
            persistent: Save to database for permanent storage
        
        Returns:
            {
                "share_id": "abc123def",
                "share_url": "https://app.com/share/abc123def",
                "expires_at": "2025-01-24T10:00:00Z" (if not persistent)
            }
        """
        # Generate share ID
        share_id = self.generate_share_id(itinerary_data)
        
        # Add metadata
        saved_data = {
            "itinerary": itinerary_data,
            "created_at": datetime.utcnow().isoformat(),
            "version": "1.0"
        }
        
        # Save to cache (temporary)
        if self.cache and self.cache.enabled:
            cache_key = f"itinerary:{share_id}"
            ttl_seconds = ttl_days * 24 * 3600
            self.cache.set(cache_key, saved_data, ttl=ttl_seconds)
        
        # Save to database (permanent)
        if persistent and self.db:
            # TODO: Implement database storage
            pass
        
        # Generate response
        expires_at = datetime.utcnow() + timedelta(days=ttl_days)
        
        result = {
            "share_id": share_id,
            "share_url": f"/share/{share_id}",
            "created_at": saved_data["created_at"]
        }
        
        if not persistent:
            result["expires_at"] = expires_at.isoformat()
            result["expires_in_days"] = ttl_days
        
        return result
    
    def load_itinerary(self, share_id: str) -> Optional[Dict]:
        """
        Load itinerary by share ID
        
        Args:
            share_id: Unique share identifier
        
        Returns:
            Itinerary data or None if not found
        """
        # Try cache first
        if self.cache and self.cache.enabled:
            cache_key = f"itinerary:{share_id}"
            cached = self.cache.get(cache_key)
            if cached:
                return cached
        
        # Try database
        if self.db:
            # TODO: Implement database retrieval
            pass
        
        return None
    
    def list_recent_itineraries(self, limit: int = 10) -> List[Dict]:
        """
        List recent itineraries (for admin/stats)
        
        Args:
            limit: Maximum number to return
        
        Returns:
            List of itinerary metadata
        """
        # This would require database support
        # For now, return empty list
        return []
    
    def delete_itinerary(self, share_id: str) -> bool:
        """
        Delete itinerary
        
        Args:
            share_id: Unique share identifier
        
        Returns:
            True if deleted, False otherwise
        """
        deleted = False
        
        # Delete from cache
        if self.cache and self.cache.enabled:
            cache_key = f"itinerary:{share_id}"
            deleted = self.cache.delete(cache_key)
        
        # Delete from database
        if self.db:
            # TODO: Implement database deletion
            pass
        
        return deleted


# Flask route handlers to add to app.py

"""
Add these routes to app.py:

from agent.itinerary_storage import ItineraryStorage
from agent.cache import cache

# Initialize storage
storage = ItineraryStorage(cache_client=cache)


@app.route('/api/itinerary/save', methods=['POST'])
def save_itinerary():
    '''
    Save an itinerary
    
    Request body:
    {
        "itinerary": {...},  # Full itinerary data
        "ttl_days": 30,      # Optional, default 30
        "persistent": false  # Optional, save permanently
    }
    '''
    try:
        data = request.json
        if not data or 'itinerary' not in data:
            return error_response("Missing itinerary data", 400)
        
        itinerary_data = data['itinerary']
        ttl_days = data.get('ttl_days', 30)
        persistent = data.get('persistent', False)
        
        result = storage.save_itinerary(
            itinerary_data,
            ttl_days=ttl_days,
            persistent=persistent
        )
        
        return success_response(result, "Itinerary saved successfully")
    
    except Exception as e:
        return error_response(str(e), 500, "Failed to save itinerary")


@app.route('/api/itinerary/<share_id>', methods=['GET'])
def load_itinerary(share_id):
    '''
    Load a saved itinerary
    '''
    try:
        itinerary = storage.load_itinerary(share_id)
        
        if not itinerary:
            return error_response(
                f"Itinerary not found or expired: {share_id}",
                404,
                "Not found"
            )
        
        return success_response(itinerary, "Itinerary loaded successfully")
    
    except Exception as e:
        return error_response(str(e), 500, "Failed to load itinerary")


@app.route('/api/itinerary/<share_id>', methods=['DELETE'])
def delete_itinerary(share_id):
    '''
    Delete a saved itinerary
    '''
    try:
        deleted = storage.delete_itinerary(share_id)
        
        if deleted:
            return success_response(
                {"share_id": share_id},
                "Itinerary deleted successfully"
            )
        else:
            return error_response(
                f"Itinerary not found: {share_id}",
                404,
                "Not found"
            )
    
    except Exception as e:
        return error_response(str(e), 500, "Failed to delete itinerary")


# Share page route
@app.route('/share/<share_id>')
def share_itinerary_page(share_id):
    '''
    Render shared itinerary page
    '''
    return render_template('share.html', share_id=share_id)
"""
