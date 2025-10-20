#!/usr/bin/env python3
"""
Standalone Domain Checker Updater
Can be run independently to update the domain checker installation
"""

import asyncio
import sys
from pathlib import Path

# Add the domain_checker module to the path
sys.path.insert(0, str(Path(__file__).parent))

from domain_checker.updater import DomainCheckerUpdater


async def main():
    """Main updater function"""
    updater = DomainCheckerUpdater()
    
    print("Domain Checker Updater")
    print("=" * 50)
    
    # Check for updates
    has_updates, latest_version, update_info = await updater.check_for_updates()
    
    if has_updates:
        print(f"Update available: {latest_version}")
        if update_info:
            if "release_notes" in update_info:
                print(f"Release Notes: {update_info['release_notes'][:200]}...")
            if "commit_message" in update_info:
                print(f"Latest Commit: {update_info['commit_message'][:100]}...")
        
        response = input("\nDo you want to update now? (y/N): ").strip().lower()
        if response in ['y', 'yes']:
            success = await updater.update_installation()
            if success:
                print("✅ Update completed successfully!")
            else:
                print("❌ Update failed!")
        else:
            print("Update cancelled.")
    else:
        print("✅ You're running the latest version!")


if __name__ == "__main__":
    asyncio.run(main())
