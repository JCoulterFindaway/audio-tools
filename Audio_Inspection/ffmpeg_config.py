#!/usr/bin/env python3
"""
FFmpeg Version Manager

Manages multiple ffmpeg installations for audio corruption diagnosis.
Supports version-specific probing to identify version-dependent issues.
"""

import os
import re
import shutil
import subprocess
from pathlib import Path
from typing import Dict, List


class FFmpegVersionManager:
    """
    Manages multiple ffmpeg versions for comprehensive audio analysis.
    
    This is particularly useful for diagnosing corrupt audio files, as different
    ffmpeg versions may handle corruption differently or provide different
    diagnostic information.
    """
    
    # Default version for system compatibility
    DEFAULT_VERSION = "5.1.6"
    
    # Known ffmpeg version locations and Docker images
    VERSION_PATHS = {
        "5.1.6": "/usr/local/ffmpeg-versions/5.1.6/ffmpeg",
        "7.1.0": "/usr/local/ffmpeg-versions/7.1.0/ffmpeg", 
        "8.0.0": "/usr/local/ffmpeg-versions/8.0.0/ffmpeg",
        "system": "ffmpeg",  # System PATH version
        "homebrew": "/opt/homebrew/bin/ffmpeg",  # Common Homebrew location
    }
    
    # Docker-based versions (TRUE version isolation)
    DOCKER_VERSIONS = {
        "5.1.6": "ffmpeg:5.1.6",
        "7.1.0": "ffmpeg:7.1.0",
        "8.0.0": "ffmpeg:8.0.0",
    }
    
    def __init__(self, preferred_version: str = None, use_docker: bool = True):
        """
        Initialize the version manager.
        
        Args:
            preferred_version: Preferred ffmpeg version to use. 
                             Defaults to DEFAULT_VERSION if available.
            use_docker: Whether to prefer Docker-based versions for true isolation.
        """
        self.preferred_version = preferred_version or self.DEFAULT_VERSION
        self.use_docker = use_docker
        self._available_versions = None
        self._version_info_cache = {}
        self._docker_available = None
    
    def is_docker_available(self) -> bool:
        """
        Check if Docker is available and running.
        
        Returns:
            True if Docker is available, False otherwise
        """
        if self._docker_available is None:
            try:
                result = subprocess.run(
                    ["docker", "info"],
                    capture_output=True,
                    timeout=5
                )
                self._docker_available = result.returncode == 0
            except (subprocess.TimeoutExpired, FileNotFoundError):
                self._docker_available = False
        
        return self._docker_available
    
    def is_docker_image_available(self, version: str) -> bool:
        """
        Check if a Docker image for the specified version exists.
        
        Args:
            version: Version identifier
            
        Returns:
            True if Docker image exists, False otherwise
        """
        if not self.is_docker_available() or version not in self.DOCKER_VERSIONS:
            return False
        
        try:
            image_name = self.DOCKER_VERSIONS[version]
            result = subprocess.run(
                ["docker", "image", "inspect", image_name],
                capture_output=True,
                timeout=5
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False
    
    def get_binary_path(self, version: str = None) -> str:
        """
        Get the full path to a specific ffmpeg version or Docker command.
        
        Args:
            version: Version identifier. Uses preferred_version if None.
            
        Returns:
            Full path to the ffmpeg binary or Docker command
            
        Raises:
            FileNotFoundError: If the specified version is not available
        """
        version = version or self.preferred_version
        
        if version not in self.VERSION_PATHS:
            raise ValueError(f"Unknown ffmpeg version: {version}")
        
        # Prefer Docker version if available and enabled
        if self.use_docker and self.is_docker_image_available(version):
            return f"docker_ffmpeg_{version}"  # Special identifier for Docker execution
        
        binary_path = self.VERSION_PATHS[version]
        
        # Check if binary exists and is executable
        if version == "system":
            if not shutil.which(binary_path):
                raise FileNotFoundError(f"System ffmpeg not found in PATH")
        else:
            # Check both direct path and bin/ subdirectory (for source builds)
            possible_paths = [
                binary_path,
                str(Path(binary_path).parent / "bin" / "ffmpeg")
            ]
            
            found_path = None
            for path in possible_paths:
                if Path(path).exists() and os.access(path, os.X_OK):
                    found_path = path
                    break
            
            if not found_path:
                raise FileNotFoundError(f"FFmpeg {version} not found at {binary_path} or {possible_paths[1]}")
            
            # Update the binary path to the found location
            if found_path != binary_path:
                self.VERSION_PATHS[version] = found_path
                binary_path = found_path
        
        return binary_path
    
    def execute_ffmpeg_command(self, version: str, command_args: List[str], input_file: str) -> subprocess.CompletedProcess:
        """
        Execute an ffmpeg command using the specified version (Docker or native).
        
        Args:
            version: Version identifier
            command_args: FFmpeg command arguments (without the 'ffmpeg' part)
            input_file: Path to input audio file
            
        Returns:
            subprocess.CompletedProcess result
        """
        if self.use_docker and self.is_docker_image_available(version):
            # Use Docker execution for true version isolation
            docker_image = self.DOCKER_VERSIONS[version]
            
            # Mount the directory containing the input file
            input_path = Path(input_file).resolve()
            mount_dir = input_path.parent
            container_file = f"/audio/{input_path.name}"
            
            docker_cmd = [
                "docker", "run", "--rm",
                "-v", f"{mount_dir}:/audio",
                docker_image
            ] + [arg.replace(str(input_file), container_file) for arg in command_args]
            
            return subprocess.run(docker_cmd, capture_output=True, text=False)
        else:
            # Use native binary execution
            binary_path = self.get_binary_path(version)
            if binary_path.startswith("docker_ffmpeg_"):
                raise RuntimeError(f"Docker not available for version {version}")
            
            ffmpeg_cmd = [binary_path] + command_args
            return subprocess.run(ffmpeg_cmd, capture_output=True, text=False)
    
    def list_available_versions(self) -> List[str]:
        """
        Get list of available ffmpeg versions on this system.
        
        Returns:
            List of version identifiers that are actually available
        """
        if self._available_versions is None:
            available = []
            
            for version, path in self.VERSION_PATHS.items():
                try:
                    # Check Docker version first if enabled
                    if self.use_docker and self.is_docker_image_available(version):
                        available.append(version)
                        continue
                    
                    # Check native binary
                    self.get_binary_path(version)
                    available.append(version)
                except (FileNotFoundError, PermissionError):
                    continue
            
            self._available_versions = available
        
        return self._available_versions.copy()
    
    def get_version_info(self, version: str = None) -> Dict[str, str]:
        """
        Get detailed version information for a specific ffmpeg installation.
        
        Args:
            version: Version identifier. Uses preferred_version if None.
            
        Returns:
            Dictionary with version details (version, build_date, configuration, etc.)
        """
        version = version or self.preferred_version
        
        if version in self._version_info_cache:
            return self._version_info_cache[version].copy()
        
        try:
            binary_path = self.get_binary_path(version)
            
            # Run ffmpeg -version to get detailed info
            result = subprocess.run(
                [binary_path, "-version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode != 0:
                raise subprocess.CalledProcessError(result.returncode, binary_path)
            
            # Parse version output
            output_lines = result.stdout.strip().split('\n')
            version_line = output_lines[0] if output_lines else ""
            
            # Extract version number
            version_match = re.search(r'ffmpeg version (\S+)', version_line)
            actual_version = version_match.group(1) if version_match else "unknown"
            
            # Extract build date if available
            build_date = "unknown"
            for line in output_lines:
                if "built with" in line.lower() or "built on" in line.lower():
                    build_date = line.strip()
                    break
            
            # Get configuration (usually on line 2)
            configuration = ""
            if len(output_lines) > 1:
                config_line = output_lines[1]
                if config_line.strip().startswith("configuration:"):
                    configuration = config_line.strip()
            
            info = {
                "identifier": version,
                "version": actual_version,
                "binary_path": binary_path,
                "build_info": build_date,
                "configuration": configuration,
                "full_output": result.stdout
            }
            
            self._version_info_cache[version] = info
            return info.copy()
            
        except Exception as e:
            return {
                "identifier": version,
                "version": "error",
                "binary_path": self.VERSION_PATHS.get(version, "unknown"),
                "error": str(e),
                "available": False
            }
    
    def validate_installation(self) -> Dict[str, bool]:
        """
        Validate all configured ffmpeg installations.
        
        Returns:
            Dictionary mapping version identifiers to availability status
        """
        validation_results = {}
        
        for version in self.VERSION_PATHS.keys():
            try:
                self.get_binary_path(version)
                # Try to run a simple command to verify it works
                binary_path = self.get_binary_path(version)
                result = subprocess.run(
                    [binary_path, "-version"],
                    capture_output=True,
                    timeout=5
                )
                validation_results[version] = result.returncode == 0
            except Exception:
                validation_results[version] = False
        
        return validation_results
    
    def get_best_available_version(self) -> str:
        """
        Get the best available version, preferring the default but falling back.
        
        Returns:
            Version identifier for the best available version
            
        Raises:
            RuntimeError: If no ffmpeg versions are available
        """
        available = self.list_available_versions()
        
        if not available:
            raise RuntimeError("No ffmpeg versions are available on this system")
        
        # Prefer the default version if available
        if self.DEFAULT_VERSION in available:
            return self.DEFAULT_VERSION
        
        # Prefer the configured preferred version
        if self.preferred_version in available:
            return self.preferred_version
        
        # Fall back to any available version, preferring newer ones
        version_priority = ["8.0.0", "7.1.0", "5.1.6", "system", "homebrew"]
        for version in version_priority:
            if version in available:
                return version
        
        # Return the first available version as last resort
        return available[0]
    
    def print_status(self) -> None:
        """Print a formatted status report of all ffmpeg installations."""
        print("=" * 60)
        print("FFMPEG VERSION MANAGER STATUS")
        print("=" * 60)
        print(f"Preferred Version: {self.preferred_version}")
        print(f"Default Version: {self.DEFAULT_VERSION}")
        print()
        
        available_versions = self.list_available_versions()
        
        if not available_versions:
            print("❌ No ffmpeg versions are available!")
            print("\nPlease install ffmpeg using the provided installation guide.")
            return
        
        print(f"Available Versions: {len(available_versions)}")
        print("-" * 40)
        
        for version in self.VERSION_PATHS.keys():
            status = "✅" if version in available_versions else "❌"
            info = self.get_version_info(version)
            
            # Show if using Docker or native
            execution_type = ""
            if self.use_docker and self.is_docker_image_available(version):
                execution_type = " (Docker)"
            elif version in available_versions:
                execution_type = " (Native)"
            
            print(f"{status} {version:10} | {info.get('version', 'N/A'):15} | {info.get('binary_path', 'N/A')}{execution_type}")
            
            if version in available_versions and 'error' not in info:
                print(f"   └─ {info.get('build_info', 'No build info')}")
        
        print("-" * 40)
        
        try:
            best_version = self.get_best_available_version()
            print(f"🎯 Best Available: {best_version}")
        except RuntimeError as e:
            print(f"❌ Error: {e}")
        
        print("=" * 60)


class FFmpegConfig:
    """
    Configuration class for ffmpeg binary selection in audio probing.
    
    This class provides a clean interface for the audio probing classes
    to use different ffmpeg versions without tightly coupling to the
    version management logic.
    """
    
    def __init__(self, version: str = None, version_manager: FFmpegVersionManager = None):
        """
        Initialize ffmpeg configuration.
        
        Args:
            version: Specific version to use. If None, uses the best available.
            version_manager: Custom version manager. Creates default if None.
        """
        self.version_manager = version_manager or FFmpegVersionManager()
        
        if version is None:
            self.version = self.version_manager.get_best_available_version()
        else:
            self.version = version
        
        # Validate the version is available
        self.binary_path = self.version_manager.get_binary_path(self.version)
    
    @classmethod
    def for_version(cls, version: str) -> 'FFmpegConfig':
        """
        Create configuration for a specific ffmpeg version.
        
        Args:
            version: Version identifier
            
        Returns:
            FFmpegConfig instance configured for the specified version
        """
        return cls(version=version)
    
    @classmethod
    def default(cls) -> 'FFmpegConfig':
        """
        Create configuration using the default/best available version.
        
        Returns:
            FFmpegConfig instance with optimal version selection
        """
        return cls()
    
    def get_version_info(self) -> Dict[str, str]:
        """Get detailed information about the configured ffmpeg version."""
        return self.version_manager.get_version_info(self.version)
    
    def __str__(self) -> str:
        return f"FFmpegConfig(version={self.version}, path={self.binary_path})"
    
    def __repr__(self) -> str:
        return self.__str__()


# Convenience function for quick setup
def get_ffmpeg_binary(version: str = None) -> str:
    """
    Quick function to get ffmpeg binary path for a specific version.
    
    Args:
        version: Version identifier. Uses best available if None.
        
    Returns:
        Full path to ffmpeg binary
    """
    config = FFmpegConfig(version=version)
    return config.binary_path


if __name__ == "__main__":
    # Demo/test functionality
    manager = FFmpegVersionManager()
    manager.print_status()
    
    print("\nTesting configuration creation:")
    try:
        config = FFmpegConfig.default()
        print(f"Default config: {config}")
        
        info = config.get_version_info()
        print(f"Version info: {info.get('version', 'unknown')}")
    except Exception as e:
        print(f"Error creating config: {e}")
