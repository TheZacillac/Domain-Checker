"""
Domain Checker Updater
Checks for updates and updates the installation from the repository
"""

import asyncio
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import aiohttp
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.prompt import Confirm

console = Console()


class DomainCheckerUpdater:
    """Handles updating the domain checker from the repository"""
    
    def __init__(self):
        self.repo_url = "https://github.com/TheZacillac/domain-checker.git"
        self.current_version = self._get_current_version()
        self.temp_dir = None
        
    def _get_current_version(self) -> str:
        """Get the current installed version"""
        try:
            from . import __version__
            return __version__
        except ImportError:
            return "unknown"
    
    async def check_for_updates(self) -> Tuple[bool, Optional[str], Optional[Dict]]:
        """
        Check if there are updates available
        
        Returns:
            Tuple of (has_updates, latest_version, update_info)
        """
        try:
            # Get latest version from GitHub API
            import ssl
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            
            connector = aiohttp.TCPConnector(ssl=ssl_context)
            async with aiohttp.ClientSession(connector=connector) as session:
                # Try to get latest release
                async with session.get("https://api.github.com/repos/TheZacillac/domain-checker/releases/latest") as response:
                    if response.status == 200:
                        release_data = await response.json()
                        latest_version = release_data.get("tag_name", "").lstrip("v")
                        update_info = {
                            "version": latest_version,
                            "release_notes": release_data.get("body", ""),
                            "published_at": release_data.get("published_at", ""),
                            "download_url": release_data.get("tarball_url", "")
                        }
                        
                        has_updates = self._compare_versions(self.current_version, latest_version)
                        return has_updates, latest_version, update_info
                
                # Fallback: get latest commit from main branch
                async with session.get("https://api.github.com/repos/TheZacillac/domain-checker/commits/main") as response:
                    if response.status == 200:
                        commit_data = await response.json()
                        latest_commit = commit_data.get("sha", "")[:8]
                        update_info = {
                            "version": f"main-{latest_commit}",
                            "commit_message": commit_data.get("commit", {}).get("message", ""),
                            "commit_date": commit_data.get("commit", {}).get("author", {}).get("date", ""),
                            "commit_url": commit_data.get("html_url", "")
                        }
                        
                        # For main branch, we'll assume there might be updates
                        has_updates = True
                        return has_updates, f"main-{latest_commit}", update_info
                        
        except Exception as e:
            console.print(f"[red]Error checking for updates: {e}[/red]")
            
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
            # If version comparison fails, assume update is available
            return True
    
    async def get_repository_changes(self) -> List[Dict]:
        """Get list of changes from the repository"""
        try:
            # Clone repository to temp directory
            self.temp_dir = tempfile.mkdtemp(prefix="domain_checker_update_")
            
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                task = progress.add_task("Fetching repository...", total=None)
                
                # Clone the repository
                result = subprocess.run([
                    "git", "clone", "--depth", "1", 
                    self.repo_url, self.temp_dir
                ], capture_output=True, text=True)
                
                if result.returncode != 0:
                    console.print(f"[red]Failed to clone repository: {result.stderr}[/red]")
                    return []
                
                progress.update(task, description="Repository fetched successfully")
            
            # Get list of files in the repository
            repo_files = []
            for root, dirs, files in os.walk(self.temp_dir):
                # Skip .git directory
                dirs[:] = [d for d in dirs if d != '.git']
                
                for file in files:
                    file_path = os.path.join(root, file)
                    rel_path = os.path.relpath(file_path, self.temp_dir)
                    repo_files.append({
                        "path": rel_path,
                        "full_path": file_path,
                        "size": os.path.getsize(file_path)
                    })
            
            return repo_files
            
        except Exception as e:
            console.print(f"[red]Error getting repository changes: {e}[/red]")
            return []
    
    def _get_installation_path(self) -> Path:
        """Get the current installation path"""
        try:
            import domain_checker
            return Path(domain_checker.__file__).parent
        except ImportError:
            # Fallback: assume we're in the project directory
            return Path(__file__).parent
    
    async def update_installation(self, force: bool = False, auto_reinstall: bool = True) -> bool:
        """
        Update the installation from the repository
        
        Args:
            force: Force update even if no changes detected
            auto_reinstall: Automatically reinstall package if Python files are updated
            
        Returns:
            True if update was successful
        """
        try:
            # Check for updates
            has_updates, latest_version, update_info = await self.check_for_updates()
            
            if not has_updates and not force:
                console.print("[green]✅ You're already running the latest version![/green]")
                return True
            
            # Show update information
            if update_info:
                update_text = f"""
[bold blue]Update Available![/bold blue]

[bold]Current Version:[/bold] {self.current_version}
[bold]Latest Version:[/bold] {latest_version}

[bold]Update Information:[/bold]
"""
                if "release_notes" in update_info:
                    update_text += f"Release Notes: {update_info['release_notes'][:200]}...\n"
                if "commit_message" in update_info:
                    update_text += f"Latest Commit: {update_info['commit_message'][:100]}...\n"
                
                console.print(Panel(update_text, title="Update Available", border_style="yellow"))
            
            # Confirm update
            if not force and not Confirm.ask("Do you want to update now?"):
                console.print("[yellow]Update cancelled by user.[/yellow]")
                return False
            
            # Get repository changes
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                task = progress.add_task("Checking for changes...", total=None)
                repo_files = await self.get_repository_changes()
                progress.update(task, description="Changes checked")
            
            if not repo_files:
                console.print("[red]Failed to get repository files[/red]")
                return False
            
            # Get installation path
            install_path = self._get_installation_path()
            project_root = install_path.parent
            
            # Create backup
            backup_path = project_root / f"backup_{self.current_version}"
            if backup_path.exists():
                shutil.rmtree(backup_path)
            
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                task = progress.add_task("Creating backup...", total=None)
                shutil.copytree(project_root, backup_path, 
                              ignore=shutil.ignore_patterns('.git', '__pycache__', '*.pyc', 'backup_*'))
                progress.update(task, description="Backup created")
            
            # Update files
            updated_files = []
            skipped_files = []
            
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TaskProgressColumn(),
                console=console
            ) as progress:
                task = progress.add_task("Updating files...", total=len(repo_files))
                
                for file_info in repo_files:
                    rel_path = file_info["path"]
                    source_path = file_info["full_path"]
                    target_path = project_root / rel_path
                    
                    # Skip certain files
                    if any(skip in rel_path for skip in ['.git', '__pycache__', '.pyc', 'backup_']):
                        skipped_files.append(rel_path)
                        progress.advance(task)
                        continue
                    
                    # Create target directory if needed
                    target_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    # Copy file
                    try:
                        shutil.copy2(source_path, target_path)
                        updated_files.append(rel_path)
                    except Exception as e:
                        console.print(f"[yellow]Warning: Could not update {rel_path}: {e}[/yellow]")
                    
                    progress.advance(task)
            
            # Clean up temp directory
            if self.temp_dir and os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)
            
            # Show results
            result_text = f"""
[bold green]Update Complete![/bold green]

[bold]Files Updated:[/bold] {len(updated_files)}
[bold]Files Skipped:[/bold] {len(skipped_files)}
[bold]Backup Location:[/bold] {backup_path}

[bold]Updated Files:[/bold]
"""
            for file in updated_files[:10]:  # Show first 10 files
                result_text += f"  • {file}\n"
            
            if len(updated_files) > 10:
                result_text += f"  ... and {len(updated_files) - 10} more files\n"
            
            console.print(Panel(result_text, title="Update Results", border_style="green"))
            
            # Auto-reinstall if Python files were updated and auto_reinstall is enabled
            if auto_reinstall and any(f.endswith('.py') for f in updated_files):
                console.print("\n[yellow]⚠️  Python files were updated. Reinstalling package...[/yellow]")
                
                try:
                    with Progress(
                        SpinnerColumn(),
                        TextColumn("[progress.description]{task.description}"),
                        console=console
                    ) as progress:
                        task = progress.add_task("Reinstalling package...", total=None)
                        
                        # Run pip install -e . in the project directory
                        result = subprocess.run(
                            ["pip3", "install", "-e", "."],
                            cwd=project_root,
                            capture_output=True,
                            text=True,
                            timeout=60
                        )
                        
                        if result.returncode == 0:
                            progress.update(task, description="Package reinstalled successfully")
                            console.print("[green]✅ Package reinstalled successfully![/green]")
                        else:
                            progress.update(task, description="Reinstallation failed")
                            console.print(f"[red]❌ Reinstallation failed: {result.stderr}[/red]")
                            console.print("[yellow]You may need to manually run: pip3 install -e .[/yellow]")
                            
                except subprocess.TimeoutExpired:
                    console.print("[red]❌ Reinstallation timed out[/red]")
                    console.print("[yellow]You may need to manually run: pip3 install -e .[/yellow]")
                except Exception as e:
                    console.print(f"[red]❌ Reinstallation failed: {e}[/red]")
                    console.print("[yellow]You may need to manually run: pip3 install -e .[/yellow]")
            elif any(f.endswith('.py') for f in updated_files):
                # Python files were updated but auto_reinstall is disabled
                console.print("\n[yellow]⚠️  Python files were updated. You may need to reinstall the package:[/yellow]")
                console.print("[cyan]pip3 install -e .[/cyan]")
            
            return True
            
        except Exception as e:
            console.print(f"[red]Update failed: {e}[/red]")
            return False
    
    def rollback(self, version: str = None) -> bool:
        """
        Rollback to a previous version using backup
        
        Args:
            version: Version to rollback to (uses current version if None)
            
        Returns:
            True if rollback was successful
        """
        try:
            install_path = self._get_installation_path()
            project_root = install_path.parent
            
            if version is None:
                version = self.current_version
            
            backup_path = project_root / f"backup_{version}"
            
            if not backup_path.exists():
                console.print(f"[red]No backup found for version {version}[/red]")
                return False
            
            # Confirm rollback
            if not Confirm.ask(f"Rollback to version {version}? This will overwrite current files."):
                console.print("[yellow]Rollback cancelled by user.[/yellow]")
                return False
            
            # Restore from backup
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                task = progress.add_task("Rolling back...", total=None)
                
                # Remove current files (except backup directories)
                for item in project_root.iterdir():
                    if item.name.startswith('backup_'):
                        continue
                    if item.is_file():
                        item.unlink()
                    elif item.is_dir():
                        shutil.rmtree(item)
                
                # Copy from backup
                for item in backup_path.iterdir():
                    if item.is_file():
                        shutil.copy2(item, project_root / item.name)
                    elif item.is_dir():
                        shutil.copytree(item, project_root / item.name)
                
                progress.update(task, description="Rollback complete")
            
            console.print(f"[green]✅ Successfully rolled back to version {version}[/green]")
            return True
            
        except Exception as e:
            console.print(f"[red]Rollback failed: {e}[/red]")
            return False


async def main():
    """Main updater function"""
    updater = DomainCheckerUpdater()
    
    console.print("[bold blue]Domain Checker Updater[/bold blue]\n")
    
    # Check for updates
    has_updates, latest_version, update_info = await updater.check_for_updates()
    
    if has_updates:
        console.print(f"[yellow]Update available: {latest_version}[/yellow]")
        await updater.update_installation()
    else:
        console.print("[green]✅ You're running the latest version![/green]")


if __name__ == "__main__":
    asyncio.run(main())
