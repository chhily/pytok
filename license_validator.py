import requests
import json
from typing import Optional, Tuple
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LicenseValidator:
    def __init__(self, supabase_url: str, anon_key: str):
        self.supabase_url = supabase_url
        self.endpoint = f"{supabase_url}/functions/v1/validate_license"
        self.anon_key = anon_key
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {anon_key}",
            "User-Agent": "LicenseValidator/1.0"
        }

    def validate_license_key(self, license_key: str, timeout: int = 10) -> Tuple[bool, Optional[str]]:
        """
        Validate a license key against the Supabase edge function.
        
        Args:
            license_key: The license key to validate
            timeout: Request timeout in seconds
            
        Returns:
            Tuple of (is_valid, error_reason)
        """
        if not license_key or not license_key.strip():
            return False, "Empty license key provided"

        payload = {"key": license_key.strip()}

        try:
            logger.info(f"Validating license key: {license_key[:8]}...")
            
            response = requests.post(
                self.endpoint,
                json=payload,
                headers=self.headers,
                timeout=timeout
            )

            # Log response details for debugging
            logger.info(f"Response status: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    result = response.json()
                    is_valid = result.get("valid", False)
                    logger.info(f"License validation result: {'Valid' if is_valid else 'Invalid'}")
                    return is_valid, None
                except json.JSONDecodeError:
                    logger.error("Failed to parse response JSON")
                    return False, "Invalid response format"
                    
            else:
                # Handle error responses
                try:
                    error_data = response.json()
                    reason = error_data.get("reason", f"HTTP {response.status_code}")
                except json.JSONDecodeError:
                    reason = f"HTTP {response.status_code}: {response.text[:100]}"
                
                logger.warning(f"License validation failed: {reason}")
                return False, reason

        except requests.exceptions.Timeout:
            logger.error("Request timeout")
            return False, "Request timeout"
        except requests.exceptions.ConnectionError:
            logger.error("Connection error")
            return False, "Connection error"
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error: {e}")
            return False, f"Request error: {str(e)}"
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return False, f"Unexpected error: {str(e)}"