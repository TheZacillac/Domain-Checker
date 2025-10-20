"""
Simple update checker for domain checker
Can be used to check for updates without full updater functionality
"""

import asyncio
import json
from typing import Optional, Tuple
import aiohttp


class UpdateChecker:
    """Simple update checker that doesn't require git or file operations"""
    
    def __init__(self):
        self.repo_api_url = "https://api.github.com/repos/TheZacillac/domain-checker"
        self.current_version = self._get_current_version()
    
    def _get_current_version(self) -> str:
        """Get the current installed version"""
        try:
            from . import __version__
            return __version__
        except ImportError:
            return "unknown"
    
    async def check_for_updates(self) -> Tuple[bool, Optional[str], Optional[dict]]:
        """
        Check if there are updates available
        
        Returns:
            Tuple of (has_updates, latest_version, update_info)
        """
        try:
            import ssl
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            
            connector = aiohttp.TCPConnector(ssl=ssl_context)
            async with aiohttp.ClientSession(connector=connector) as session:
                # Try to get latest release first
                async with session.get(f"{self.repo_api_url}/releases/latest") as response:
                    if response.status == 200:
                        release_data = await response.json()
                        latest_version = release_data.get("tag_name", "").lstrip("v")
                        
                        update_info = {
                            "version": latest_version,
                            "release_notes": release_data.get("body", ""),
                            "published_at": release_data.get("published_at", ""),
                            "download_url": release_data.get("tarball_url", ""),
                            "html_url": release_data.get("html_url", "")
                        }
                        
                        has_updates = self._compare_versions(self.current_version, latest_version)
                        return has_updates, latest_version, update_info
                
                # Fallback: get latest commit from main branch
                async with session.get(f"{self.repo_api_url}/commits/main") as response:
                    if response.status == 200:
                        commit_data = await response.json()
                        latest_commit = commit_data.get("sha", "")[:8]
                        
                        update_info = {
                            "version": f"main-{latest_commit}",
                            "commit_message": commit_data.get("commit", {}).get("message", ""),
                            "commit_date": commit_data.get("commit", {}).get("author", {}).get("date", ""),
                            "commit_url": commit_data.get("html_url", "")
                        }
                        
                        # For main branch, assume there might be updates
                        has_updates = True
                        return has_updates, f"main-{latest_commit}", update_info
                        
        except Exception:
            # If we can't check, assume no updates
            pass
            
        return False, None, None
    
    def _compare_versions(self, current: str, latest: str) -> bool:
        """Compare version strings to determine if update is available"""
        if current == "unknown" or current == latest:
            return False
            
        try:
            # Simple version comparison (assumes semantic versioning)
            current_parts = [int(x) for x in current.split('.')]
            latest_parts = [int(x) for x in latest.split('.')]
            
            # Pad with zeros if needed
            max_len = max(len(current_parts), len(latest_parts))
            current_parts.extend([0] * (max_len - len(current_parts)))
            latest_parts.extend([0] * (max_len - len(latest_parts)))
            
            return latest_parts > current_parts
        except:
            # If version comparison fails, assume no update
            return False
    
    def get_update_message(self, has_updates: bool, latest_version: str, update_info: dict) -> str:
        """Get a formatted update message"""
        if not has_updates:
            return "✅ You're running the latest version!"
        
        message = f"🔄 Update available: {latest_version}\n"
        
        if update_info:
            if "release_notes" in update_info and update_info["release_notes"]:
                # Truncate release notes
                notes = update_info["release_notes"][:200]
                if len(update_info["release_notes"]) > 200:
                    notes += "..."
                message += f"📝 {notes}\n"
            
            if "commit_message" in update_info and update_info["commit_message"]:
                # Truncate commit message
                commit_msg = update_info["commit_message"][:100]
                if len(update_info["commit_message"]) > 100:
                    commit_msg += "..."
                message += f"💬 {commit_msg}\n"
            
            if "html_url" in update_info:
                message += f"🔗 {update_info['html_url']}\n"
        
        message += "\nRun 'domch update' to update automatically"
        return message


# Convenience function for quick update checks
async def quick_check() -> str:
    """Quick update check that returns a message"""
    checker = UpdateChecker()
    has_updates, latest_version, update_info = await checker.check_for_updates()
    return checker.get_update_message(has_updates, latest_version, update_info or {})
