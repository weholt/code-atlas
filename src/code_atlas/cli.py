"""CLI interface for CodeAtlas."""

import json
import subprocess
import sys
from pathlib import Path

import typer

from code_atlas.agent_adapter import AgentAdapter
from code_atlas.query import CodeIndex
from code_atlas.rules import RuleEngine
from code_atlas.scanner import scan_directory
from code_atlas.scoring import ScoringEngine

# Optional rich for progress display
try:
    from rich.progress import BarColumn, Progress, SpinnerColumn, TaskProgressColumn, TextColumn

    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

app = typer.Typer(help="CodeAtlas - Agent-oriented Python codebase analyzer")


@app.command()
def scan(
    path: str = typer.Argument(..., help="Path to scan"),
    output: str = typer.Option("code_index.json", help="Output file path"),
    incremental: bool = typer.Option(False, "--incremental", help="Use incremental caching (skip unchanged files)"),
    deep: bool = typer.Option(False, "--deep", help="Enable deep analysis (call graphs, type coverage)"),
    verbose: bool = typer.Option(False, "--verbose", help="Show detailed progress information"),
) -> None:
    """Scan a Python codebase and generate structure index."""
    root_path = Path(path).resolve()
    output_path = Path(output).resolve()

    typer.echo(f"Scanning {root_path}...")
    if incremental:
        typer.echo("Incremental mode: skipping unchanged files")
    if deep:
        typer.echo("Deep analysis: including call graphs and type coverage")

    # Set up progress display
    if verbose and RICH_AVAILABLE:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
        ) as progress:
            task = progress.add_task("Scanning files...", total=100)

            def progress_callback(file_path: str, current: int, total: int) -> None:
                progress.update(task, completed=current, total=total, description=f"Scanning: {file_path}")

            scan_directory(
                root_path, output_path, incremental=incremental, deep=deep, progress_callback=progress_callback
            )
    elif verbose:
        # Fallback to basic echo if rich not available
        def progress_callback(file_path: str, current: int, total: int) -> None:
            typer.echo(f"[{current}/{total}] {file_path}")

        scan_directory(root_path, output_path, incremental=incremental, deep=deep, progress_callback=progress_callback)
    else:
        # No progress display
        scan_directory(root_path, output_path, incremental=incremental, deep=deep)

    typer.echo(f"Index written to {output_path}")


@app.command()
def rank(
    rules: str = typer.Option("rules.yaml", help="Rules configuration file"),
    top: int = typer.Option(20, help="Number of top results to show"),
    index_file: str = typer.Option("code_index.json", help="Code index file"),
    output: str = typer.Option("refactor_rank.json", help="Output file"),
) -> None:
    """Rank files by refactor priority."""
    # Load code index
    ci = CodeIndex(index_file)

    # Create scoring engine
    se = ScoringEngine(rules)

    # Rank files
    rankings = se.rank(ci.data)

    # Write top N to output file
    top_rankings = rankings[:top]
    Path(output).write_text(json.dumps(top_rankings, indent=2), encoding="utf-8")

    typer.echo(f"\nTop {len(top_rankings)} refactor priorities:")
    for i, item in enumerate(top_rankings, 1):
        typer.echo(
            f"{i}. {item['file']} - Score: {item['score']:.3f} "
            f"(complexity: {item['complexity']:.1f}, LOC: {item['loc']})"
        )

    typer.echo(f"\nFull rankings written to {output}")


@app.command()
def check(
    rules: str = typer.Option("rules.yaml", help="Rules configuration file"),
    index_file: str = typer.Option("code_index.json", help="Code index file"),
    output: str = typer.Option("violations.json", help="Output file"),
) -> None:
    """Check code against quality rules."""
    # Load code index
    ci = CodeIndex(index_file)

    # Create rule engine
    re = RuleEngine(rules)

    # Evaluate all files
    all_violations = []
    for file_data in ci.data.get("files", []):
        violations = re.evaluate(file_data)
        all_violations.extend(violations)

    # Write to output file
    Path(output).write_text(json.dumps(all_violations, indent=2), encoding="utf-8")

    typer.echo(f"\nFound {len(all_violations)} rule violations")

    if all_violations:
        typer.echo("\nSample violations:")
        for violation in all_violations[:5]:
            typer.echo(f"  [{violation['id']}] {violation['file']}: {violation['message']}")

    typer.echo(f"\nAll violations written to {output}")


@app.command()
def agent(
    index_file: str = typer.Option("code_index.json", help="Code index file"),
    rules: str = typer.Option("rules.yaml", help="Rules configuration file"),
    summary: bool = typer.Option(False, "--summary", help="Show codebase summary"),
    symbol: str = typer.Option(None, help="Find symbol location"),
    top: int = typer.Option(0, help="Show top N refactor priorities"),
    complex_threshold: int = typer.Option(0, help="Find functions above complexity threshold"),
    hotspots: int = typer.Option(0, help="Find dependency hotspots (min edges)"),
    poor_docs: float = typer.Option(0.0, help="Find files below comment ratio threshold"),
) -> None:
    """Query codebase for agent integration (outputs JSON)."""
    # Initialize adapter
    adapter = AgentAdapter(Path.cwd(), index_file, rules)

    result = {}

    # Handle different query modes
    if summary:
        result = adapter.summarize_state()
    elif symbol:
        result = adapter.get_symbol_location(symbol) or {"error": f"Symbol '{symbol}' not found"}
    elif top > 0:
        result = {"refactor_priorities": adapter.get_top_refactors(limit=top)}
    elif complex_threshold > 0:
        result = {"complex_functions": adapter.get_complex_functions(threshold=complex_threshold)}
    elif hotspots > 0:
        result = {"dependency_hotspots": adapter.get_dependency_hotspots(min_edges=hotspots)}
    elif poor_docs > 0:
        result = {"poor_documentation": adapter.get_untyped_or_poor_docs(min_comment_ratio=poor_docs)}
    else:
        # Default: return summary + violations
        result = {
            "summary": adapter.summarize_state(),
            "violations": adapter.get_rule_violations(),
        }

    # Output JSON for subprocess consumption
    typer.echo(json.dumps(result, indent=2))


@app.command()
def watch(
    path: str = typer.Argument(".", help="Path to watch"),
    output: str = typer.Option("code_index.json", help="Output file path"),
    debounce: float = typer.Option(2.0, help="Debounce delay in seconds"),
    daemon: bool = typer.Option(False, "--daemon", help="Run in background as daemon"),
    pid_file: str = typer.Option(".code_atlas_watch.pid", help="PID file for daemon mode"),
    incremental: bool = typer.Option(True, "--incremental/--no-incremental", help="Use incremental caching"),
    deep: bool = typer.Option(False, "--deep", help="Enable deep analysis"),
    _daemon_child: bool = typer.Option(False, "--_daemon-child", hidden=True, help="Internal: daemon child process"),
) -> None:
    """Watch directory for Python file changes and update index."""
    import os
    import sys
    import time

    from watchdog.events import FileSystemEventHandler
    from watchdog.observers import Observer

    root_path = Path(path).resolve()
    output_path = Path(output).resolve()
    pid_path = Path(pid_file).resolve()

    # Handle daemon mode - spawn subprocess and exit
    if daemon:
        # Check if already running
        if pid_path.exists():
            try:
                existing_pid = int(pid_path.read_text().strip())
                # Check if process exists (Windows-compatible)
                try:
                    import psutil

                    if psutil.pid_exists(existing_pid):
                        typer.echo(f"Watch daemon already running (PID: {existing_pid})")
                        typer.echo(f"PID file: {pid_path}")
                        raise typer.Exit(1)
                except ImportError:
                    # Fallback without psutil - just check PID file age
                    if time.time() - pid_path.stat().st_mtime < 3600:  # Less than 1 hour old
                        typer.echo(f"Watch daemon may already be running (PID: {existing_pid})")
                        typer.echo(f"Delete {pid_path} if daemon is not running")
                        raise typer.Exit(1) from None
            except (ValueError, OSError):
                pass  # Invalid/stale PID file, continue

        # Spawn a detached background process
        log_path = output_path.parent / f"{output_path.stem}_watch.log"
        
        # Build command to run watch without --daemon flag
        cmd = [
            sys.executable,
            "-m",
            "code_atlas.cli",
            "watch",
            str(path),
            "--output",
            str(output),
            "--debounce",
            str(debounce),
            "--pid-file",
            str(pid_file),
        ]
        if incremental:
            cmd.append("--incremental")
        else:
            cmd.append("--no-incremental")
        if deep:
            cmd.append("--deep")
        
        # Add internal flag to indicate we're in daemon subprocess
        cmd.append("--_daemon-child")
        
        # Spawn detached process
        if sys.platform == "win32":
            # Windows: use CREATE_NEW_PROCESS_GROUP and DETACHED_PROCESS
            import subprocess
            DETACHED_PROCESS = 0x00000008
            CREATE_NEW_PROCESS_GROUP = 0x00000200
            
            with open(log_path, "a", encoding="utf-8") as log_file:
                proc = subprocess.Popen(
                    cmd,
                    stdout=log_file,
                    stderr=log_file,
                    stdin=subprocess.DEVNULL,
                    creationflags=DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP,
                    close_fds=True,
                )
            
            # Write PID file
            pid_path.write_text(str(proc.pid))
            
            typer.echo(f"✅ Watch daemon started (PID: {proc.pid})")
            typer.echo(f"   PID file: {pid_path}")
            typer.echo(f"   Logs: {log_path}")
            typer.echo(f"\nUse 'uv run code-atlas watch-status' to check status")
            typer.echo(f"Use 'uv run code-atlas stop-watch' to stop")
            return
        else:
            # Unix: double fork to daemonize
            try:
                pid = os.fork()
                if pid > 0:
                    # Parent process - exit
                    typer.echo(f"✅ Watch daemon starting...")
                    typer.echo(f"   PID file: {pid_path}")
                    typer.echo(f"   Logs: {log_path}")
                    typer.echo(f"\nUse 'uv run code-atlas watch-status' to check status")
                    typer.echo(f"Use 'uv run code-atlas stop-watch' to stop")
                    sys.exit(0)
            except OSError as e:
                typer.echo(f"Fork failed: {e}")
                raise typer.Exit(1) from e
            
            # First child
            os.setsid()
            
            try:
                pid = os.fork()
                if pid > 0:
                    sys.exit(0)  # Exit first child
            except OSError as e:
                sys.exit(1)
            
            # Second child - this is the daemon
            os.chdir("/")
            os.umask(0)
            
            # Redirect standard file descriptors
            with open(log_path, "a", encoding="utf-8") as log_file:
                os.dup2(log_file.fileno(), sys.stdout.fileno())
                os.dup2(log_file.fileno(), sys.stderr.fileno())
            
            sys.stdin.close()
            
            # Write PID file
            pid_path.write_text(str(os.getpid()))
            
            print(f"\n{'=' * 80}")
            print(f"Watch daemon started at {time.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"PID: {os.getpid()}")
            print(f"Watching: {root_path}")
            print(f"Output: {output_path}")
            print(f"Debounce: {debounce}s")
            print(f"{'=' * 80}\n")
            
            # Continue to watch loop below (don't return)
    
    # If we're the daemon child process, set up logging
    if _daemon_child:
        log_path = output_path.parent / f"{output_path.stem}_watch.log"
        
        # Write PID file
        pid_path.write_text(str(os.getpid()))
        
        # Redirect output to log file
        log_file = open(log_path, "a", encoding="utf-8")
        sys.stdout = log_file
        sys.stderr = log_file
        
        print(f"\n{'=' * 80}")
        print(f"Watch daemon started at {time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"PID: {os.getpid()}")
        print(f"Watching: {root_path}")
        print(f"Output: {output_path}")
        print(f"Debounce: {debounce}s")
        print(f"{'=' * 80}\n")

    # Track pending rescans
    last_scan_time = 0.0
    pending_rescan = False

    class PythonFileHandler(FileSystemEventHandler):
        """Handle Python file change events."""

        def on_modified(self, event: object) -> None:
            """Handle file modification."""
            nonlocal pending_rescan
            if not event.is_directory and event.src_path.endswith(".py"):  # type: ignore
                typer.echo(f"Detected change: {event.src_path}")  # type: ignore
                pending_rescan = True

        def on_created(self, event: object) -> None:
            """Handle file creation."""
            nonlocal pending_rescan
            if not event.is_directory and event.src_path.endswith(".py"):  # type: ignore
                typer.echo(f"Detected new file: {event.src_path}")  # type: ignore
                pending_rescan = True

        def on_deleted(self, event: object) -> None:
            """Handle file deletion."""
            nonlocal pending_rescan
            if not event.is_directory and event.src_path.endswith(".py"):  # type: ignore
                typer.echo(f"Detected deletion: {event.src_path}")  # type: ignore
                pending_rescan = True

    # Initial scan
    if not daemon:
        typer.echo(f"Performing initial scan of {root_path}...")
        if incremental:
            typer.echo("Incremental mode: enabled")
        if deep:
            typer.echo("Deep analysis: enabled")

    scan_directory(root_path, output_path, incremental=incremental, deep=deep)

    if not daemon:
        typer.echo(f"Index written to {output_path}")
    last_scan_time = time.time()

    # Setup watchdog observer
    event_handler = PythonFileHandler()
    observer = Observer()
    observer.schedule(event_handler, str(root_path), recursive=True)
    observer.start()

    typer.echo(f"\nWatching {root_path} for changes (Ctrl+C to stop)...")
    typer.echo(f"Debounce delay: {debounce}s\n")

    try:
        while True:
            time.sleep(0.5)

            # Check if rescan needed and debounce period passed
            if pending_rescan and (time.time() - last_scan_time >= debounce):
                if daemon:
                    print(f"\nRescanning codebase at {time.strftime('%H:%M:%S')}...")
                else:
                    typer.echo("\nRescanning codebase...")

                scan_directory(root_path, output_path, incremental=incremental, deep=deep)

                if daemon:
                    print(f"Index updated at {output_path}")
                else:
                    typer.echo(f"Index updated at {output_path}")

                pending_rescan = False
                last_scan_time = time.time()

    except KeyboardInterrupt:
        if _daemon_child:
            print("\n\nReceived shutdown signal...")
        else:
            typer.echo("\n\nStopping watch mode...")
        observer.stop()

    observer.join()

    # Cleanup in daemon mode
    if _daemon_child:
        print(f"Watch daemon stopped at {time.strftime('%Y-%m-%d %H:%M:%S')}")
        if pid_path.exists():
            pid_path.unlink()
            print(f"Removed PID file: {pid_path}")
    else:
        typer.echo("Watch mode stopped.")


@app.command()
def watch_status(
    pid_file: str = typer.Option(".code_atlas_watch.pid", help="PID file for daemon"),
    output: str = typer.Option("code_index.json", help="Output file path"),
    log_lines: int = typer.Option(20, help="Number of recent log lines to show"),
) -> None:
    """Check watch daemon status and show recent activity."""
    import os
    import time

    pid_path = Path(pid_file).resolve()
    output_path = Path(output).resolve()
    log_path = output_path.parent / f"{output_path.stem}_watch.log"

    # Check PID file
    if not pid_path.exists():
        typer.echo("❌ Watch daemon is NOT running")
        typer.echo(f"   PID file not found: {pid_path}")
        if log_path.exists():
            typer.echo(f"\n📄 Last log activity: {log_path}")
            typer.echo(f"   Modified: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(log_path.stat().st_mtime))}")
        raise typer.Exit(1)

    # Read PID
    try:
        pid = int(pid_path.read_text().strip())
    except (ValueError, OSError) as e:
        typer.echo(f"❌ Invalid PID file: {e}")
        raise typer.Exit(1) from None

    # Check if process is actually running
    is_running = False
    try:
        import psutil

        if psutil.pid_exists(pid):
            proc = psutil.Process(pid)
            is_running = True
            typer.echo(f"✅ Watch daemon is RUNNING")
            typer.echo(f"   PID: {pid}")
            typer.echo(f"   Status: {proc.status()}")
            typer.echo(f"   CPU: {proc.cpu_percent(interval=0.1):.1f}%")
            typer.echo(f"   Memory: {proc.memory_info().rss / 1024 / 1024:.1f} MB")
            typer.echo(f"   Started: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(proc.create_time()))}")
    except ImportError:
        # Fallback without psutil
        try:
            os.kill(pid, 0)  # Check if process exists (Unix)
            is_running = True
            typer.echo(f"✅ Watch daemon appears to be running")
            typer.echo(f"   PID: {pid}")
        except (OSError, AttributeError):
            # On Windows without psutil, check PID file age
            file_age = time.time() - pid_path.stat().st_mtime
            if file_age < 300:  # Less than 5 minutes old
                is_running = True
                typer.echo(f"⚠️  Watch daemon status unknown (install psutil for accurate status)")
                typer.echo(f"   PID: {pid}")
                typer.echo(f"   PID file age: {file_age:.0f}s")

    if not is_running:
        typer.echo(f"❌ Watch daemon NOT running (stale PID file)")
        typer.echo(f"   PID {pid} not found")
        typer.echo(f"   Run 'uv run code-atlas stop-watch' to cleanup")
        raise typer.Exit(1)

    # Show file info
    typer.echo(f"\n📁 Files:")
    typer.echo(f"   PID file: {pid_path}")
    typer.echo(f"   Log file: {log_path}")
    if output_path.exists():
        typer.echo(f"   Index: {output_path}")
        typer.echo(
            f"   Index updated: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(output_path.stat().st_mtime))}"
        )

    # Show recent log lines
    if log_path.exists() and log_lines > 0:
        typer.echo(f"\n📋 Recent log activity (last {log_lines} lines):")
        typer.echo("   " + "─" * 60)
        try:
            lines = log_path.read_text(encoding="utf-8").splitlines()
            for line in lines[-log_lines:]:
                typer.echo(f"   {line}")
        except OSError as e:
            typer.echo(f"   Error reading log: {e}")


@app.command()
def stop_watch(
    pid_file: str = typer.Option(".code_atlas_watch.pid", help="PID file for daemon"),
) -> None:
    """Stop the watch daemon."""
    import os
    import signal

    pid_path = Path(pid_file).resolve()

    if not pid_path.exists():
        typer.echo("No watch daemon running (PID file not found)")
        typer.echo(f"Expected: {pid_path}")
        raise typer.Exit(1)

    try:
        pid = int(pid_path.read_text().strip())
        typer.echo(f"Stopping watch daemon (PID: {pid})...")

        # Send SIGTERM (or CTRL_BREAK_EVENT on Windows)
        try:
            if sys.platform == "win32":
                # On Windows, use taskkill
                subprocess.run(["taskkill", "/PID", str(pid), "/F"], capture_output=True, check=False)  # noqa: S603, S607
            else:
                os.kill(pid, signal.SIGTERM)

            # Wait a moment and check if PID file was cleaned up
            import time

            time.sleep(1)

            if pid_path.exists():
                # Force remove if daemon didn't cleanup
                pid_path.unlink()

            typer.echo("Watch daemon stopped successfully")

        except ProcessLookupError:
            typer.echo(f"Process {pid} not found (daemon may have already stopped)")
            pid_path.unlink()

    except (ValueError, OSError) as e:
        typer.echo(f"Error stopping daemon: {e}")
        raise typer.Exit(1) from e


if __name__ == "__main__":
    app()
