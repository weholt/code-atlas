#!/usr/bin/env python3
"""Build script for CodeAtlas."""

import argparse
import shutil
import subprocess
import sys
import time
from pathlib import Path


class BuildRunner:
    """Handles the build process for CodeAtlas."""

    def __init__(self, verbose: bool = False, fix: bool = False):
        self.verbose = verbose
        self.fix = fix
        self.project_root = Path(__file__).parent.parent
        self.failed_steps: list[str] = []

    def run_command(
        self,
        cmd: list[str],
        description: str,
        check: bool = True,
        capture_output: bool = True,
    ) -> tuple[bool, str, str]:
        """Run a command and return success status and output."""
        if self.verbose:
            print(f"Running: {' '.join(cmd)}")

        try:
            result = subprocess.run(
                cmd,
                capture_output=capture_output,
                text=True,
                cwd=self.project_root,
                check=check,
                encoding="utf-8",
                errors="replace",
            )
            return True, result.stdout, result.stderr
        except subprocess.CalledProcessError as e:
            return False, e.stdout or "", e.stderr or ""
        except FileNotFoundError:
            return False, "", f"Command not found: {cmd[0]}"

    def print_step(self, step: str) -> None:
        """Print a build step header."""
        print(f"\n{'=' * 60}")
        print(f"[TOOL] {step}")
        print(f"{'=' * 60}")

    def print_result(self, success: bool, step: str, output: str = "", error: str = "") -> None:
        """Print the result of a build step."""
        if success:
            print(f"[OK] {step} - PASSED")
        else:
            print(f"[FAIL] {step} - FAILED")
            self.failed_steps.append(step)
            if error:
                print(f"Error: {error}")
            if output:
                print(f"Output: {output}")

    def check_dependencies(self) -> bool:
        """Check if all required tools are available."""
        self.print_step("Checking Dependencies")

        tools = [
            ("uv", ["uv", "--version"]),
            ("ruff", ["uv", "run", "ruff", "--version"]),
            ("mypy", ["uv", "run", "mypy", "--version"]),
            ("pytest", ["uv", "run", "pytest", "--version"]),
        ]

        all_available = True
        for tool_name, cmd in tools:
            success, output, _error = self.run_command(cmd, f"Check {tool_name}")
            if success:
                version = output.strip().split("\n")[0] if output else "unknown"
                print(f"[OK] {tool_name}: {version}")
            else:
                print(f"[FAIL] {tool_name}: Not available")
                all_available = False

        return all_available

    def sync_dependencies(self) -> bool:
        """Sync project dependencies."""
        self.print_step("Syncing Dependencies")
        success, output, error = self.run_command(["uv", "sync", "--all-extras"], "Sync dependencies")
        self.print_result(success, "Dependency Sync", output, error)
        return success

    def format_code(self) -> bool:
        """Format code with ruff."""
        self.print_step("Code Formatting")

        src_path = self.project_root / "src" / "code_atlas"
        if not src_path.exists():
            print(f"[WARN] Source directory not found at {src_path}")
            return False

        cmd = ["uv", "run", "ruff", "format"]
        if self.fix:
            cmd.extend(["--exclude", "tests", "--exclude", "scripts", str(src_path)])
        else:
            cmd.extend(["--check", "--exclude", "tests", "--exclude", "scripts", str(src_path)])

        success_format, output_format, error_format = self.run_command(cmd, "ruff format")
        
        check_cmd = ["uv", "run", "ruff", "check"]
        if self.fix:
            check_cmd.append("--fix")
        check_cmd.extend(["--exclude", "tests", "--exclude", "scripts", str(src_path)])
        
        success_check, output_check, error_check = self.run_command(check_cmd, "ruff check")

        self.print_result(success_format, "ruff format", output_format, error_format)
        self.print_result(success_check, "ruff check", output_check, error_check)

        return success_format and success_check

    def lint_code(self) -> bool:
        """Lint code with ruff."""
        self.print_step("Code Linting")

        src_path = self.project_root / "src" / "code_atlas"
        if not src_path.exists():
            print(f"[WARN] Source directory not found at {src_path}")
            return False

        cmd = ["uv", "run", "ruff", "check"]
        if self.fix:
            cmd.append("--fix")
        cmd.extend(["--exclude", "tests", "--exclude", "scripts", str(src_path)])

        success, output, error = self.run_command(cmd, "ruff linting")
        self.print_result(success, "ruff", output, error)
        return success

    def type_check(self) -> bool:
        """Type check with mypy."""
        self.print_step("Type Checking")

        src_path = self.project_root / "src" / "code_atlas"
        if not src_path.exists():
            print(f"[WARN] Source directory not found at {src_path}")
            return False

        success, output, error = self.run_command(
            ["uv", "run", "mypy", str(src_path)], 
            f"mypy {src_path}"
        )

        self.print_result(success, f"mypy {src_path}", output, error)
        return success

    def run_unit_tests(self) -> bool:
        """Run unit tests with coverage."""
        self.print_step("Unit Tests")

        coverage_files = [".coverage", "htmlcov", "coverage.xml"]
        for file_name in coverage_files:
            path = self.project_root / file_name
            if path.exists():
                if path.is_dir():
                    shutil.rmtree(path)
                else:
                    path.unlink()

        tests_dir = self.project_root / "tests"
        src_path = self.project_root / "src" / "code_atlas"

        if not tests_dir.exists():
            print(f"[WARN] Test directory not found at {tests_dir}")
            return False

        if not src_path.exists():
            print(f"[WARN] Source directory not found at {src_path}")
            return False

        cmd = [
            "uv",
            "run",
            "pytest",
            str(tests_dir),
            f"--cov={src_path}",
            "--cov-report=term",
            "--cov-report=html",
            "--cov-report=xml",
            "--durations=20",
            "-vv" if self.verbose else "-v",
        ]

        if self.verbose:
            cmd[cmd.index("--durations=20")] = "--durations=50"

        success, output, error = self.run_command(
            cmd,
            "pytest with coverage",
            capture_output=False,
        )

        self.print_result(success, "Unit Tests with Coverage", "", "")

        if success:
            coverage_xml = self.project_root / "coverage.xml"
            if coverage_xml.exists():
                import xml.etree.ElementTree as ET
                try:
                    tree = ET.parse(coverage_xml)
                    root = tree.getroot()
                    coverage_elem = root.find(".//coverage")
                    if coverage_elem is not None:
                        line_rate = float(coverage_elem.get("line-rate", "0"))
                        coverage_pct = int(line_rate * 100)
                        print(f"Code Coverage: {coverage_pct}%")
                        if coverage_pct < 70:
                            print("WARNING: Coverage below 70% threshold!")
                            return False
                except Exception as e:
                    print(f"Warning: Could not parse coverage.xml: {e}")
            else:
                print("Warning: coverage.xml not found")

        return success

    def step_security(self) -> bool:
        """Run security checks."""
        self.print_step("Security Checks")

        src_path = self.project_root / "src" / "code_atlas"
        if not src_path.exists():
            print(f"[WARN] Source directory not found at {src_path}")
            return False

        success, output, error = self.run_command(
            ["uv", "run", "ruff", "check", "--exclude", "tests", "--exclude", "scripts", str(src_path), "--select", "S"], 
            "Security linting"
        )

        self.print_result(success, "Security Check", output, error)
        return success

    def generate_reports(self) -> bool:
        """Generate build reports."""
        self.print_step("Generating Reports")

        coverage_html = self.project_root / "htmlcov"
        if coverage_html.exists():
            print("[OK] Coverage HTML report: htmlcov/index.html")

        coverage_xml = self.project_root / "coverage.xml"
        if coverage_xml.exists():
            print("[OK] Coverage XML report: coverage.xml")

        return True

    def clean_artifacts(self) -> bool:
        """Clean build artifacts."""
        self.print_step("Cleaning Artifacts")

        artifacts = [
            "__pycache__",
            ".pytest_cache",
            ".mypy_cache",
            ".ruff_cache",
            "*.egg-info",
            ".coverage",
        ]

        for pattern in artifacts:
            if pattern.startswith("*"):
                for path in self.project_root.glob(pattern):
                    if path.is_dir():
                        shutil.rmtree(path)
                    else:
                        path.unlink()
            else:
                path = self.project_root / pattern
                if path.exists():
                    if path.is_dir():
                        shutil.rmtree(path)
                    else:
                        path.unlink()

        print("[OK] Cleaned build artifacts")
        return True

    def run_full_build(self) -> bool:
        """Run the complete build pipeline."""
        print("CodeAtlas - Comprehensive Build Pipeline")
        print(f"{'=' * 80}")

        start_time = time.time()

        steps = [
            ("Check Dependencies", self.check_dependencies),
            ("Sync Dependencies", self.sync_dependencies),
            ("Format Code", self.format_code),
            ("Lint Code", self.lint_code),
            ("Type Check", self.type_check),
            ("Security Check", self.step_security),
            ("Unit Tests", self.run_unit_tests),
            ("Generate Reports", self.generate_reports),
        ]

        success_count = 0
        total_steps = len(steps)

        for step_name, step_func in steps:
            try:
                if step_func():
                    success_count += 1
            except Exception as e:
                print(f"[FAIL] {step_name} failed with exception: {e}")
                self.failed_steps.append(step_name)

        end_time = time.time()
        duration = end_time - start_time

        print(f"\n{'=' * 80}")
        print("[STAT] Build Summary")
        print(f"{'=' * 80}")
        print(f"[OK] Successful steps: {success_count}/{total_steps}")
        print(f"[TIME]  Build duration: {duration:.2f} seconds")

        if self.failed_steps:
            print(f"[FAIL] Failed steps: {', '.join(self.failed_steps)}")

        if success_count == total_steps:
            print("\n[SUCCESS] BUILD SUCCESSFUL - All quality checks passed!")
            print("[PKG] Ready for deployment")
            return True
        elif success_count >= total_steps - 1:
            print(f"\n[WARN]  BUILD MOSTLY SUCCESSFUL - {total_steps - success_count} minor issues")
            print("[TOOL] Consider addressing failed steps before deployment")
            return True
        else:
            print(f"\n[FAIL] BUILD FAILED - {total_steps - success_count} critical issues")
            print("[FIX]  Please fix the failed steps before proceeding")
            return False


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Comprehensive build script for CodeAtlas")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose output")
    parser.add_argument("--fix", action="store_true", help="Auto-fix formatting and linting issues")
    parser.add_argument("--clean", action="store_true", help="Clean build artifacts and exit")

    args = parser.parse_args()

    builder = BuildRunner(verbose=args.verbose, fix=args.fix)

    if args.clean:
        builder.clean_artifacts()
        return 0

    success = builder.run_full_build()
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
