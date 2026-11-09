from __future__ import annotations

import platform
import shutil
import subprocess
import threading
import time
from pathlib import Path
from typing import Any

import psutil


def _gpu_snapshot() -> list[dict[str, Any]]:
    executable = shutil.which("nvidia-smi")
    if not executable:
        return []
    try:
        result = subprocess.run([executable, "--query-gpu=name,memory.total", "--format=csv,noheader,nounits"],
                                capture_output=True, text=True, timeout=5, check=True)
        devices = []
        for line in result.stdout.splitlines():
            pieces = [part.strip() for part in line.split(",", 1)]
            if len(pieces) == 2:
                devices.append({"name": pieces[0], "vram_total_mb": int(float(pieces[1]))})
        return devices
    except (subprocess.SubprocessError, ValueError):
        return []


def environment_snapshot(root: Path, backend_name: str, model: str,
                          backend_details: dict[str, Any], prompt_version: str,
                          data_hash: str) -> dict[str, Any]:
    cpu_model = platform.processor() or "unknown"
    try:
        for line in Path("/proc/cpuinfo").read_text(encoding="utf-8", errors="ignore").splitlines():
            if line.lower().startswith("model name"):
                cpu_model = line.split(":", 1)[1].strip()
                break
    except OSError:
        pass
    git_commit: str | None = None
    try:
        result = subprocess.run(["git", "rev-parse", "HEAD"], cwd=root, text=True,
                                capture_output=True, timeout=2, check=True)
        git_commit = result.stdout.strip()
    except (subprocess.SubprocessError, FileNotFoundError):
        pass
    devices = _gpu_snapshot()
    total_ram = psutil.virtual_memory().total
    return {
        "model": model,
        "backend": backend_name,
        **backend_details,
        "operating_system": platform.platform(),
        "cpu_model": cpu_model,
        "logical_cpu_cores": psutil.cpu_count(logical=True),
        "physical_cpu_cores": psutil.cpu_count(logical=False),
        "total_ram_bytes": total_ram,
        "total_ram_gib": round(total_ram / (1024 ** 3), 2),
        "gpu_devices": devices,
        "gpu_available": bool(devices),
        "gpu_note": None if devices else ("No NVIDIA GPU detected by nvidia-smi; GPU utilization and VRAM sampling are unavailable."),
        "python_version": platform.python_version(),
        "git_commit": git_commit,
        "prompt_version": prompt_version,
        "dataset_hash": data_hash,
    }


def _ollama_process() -> psutil.Process | None:
    for process in psutil.process_iter(["name", "cmdline"]):
        try:
            name = (process.info.get("name") or "").lower()
            command = " ".join(process.info.get("cmdline") or []).lower()
            if "ollama" in name and "serve" in command:
                return process
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return None


def _ollama_runner() -> psutil.Process | None:
    for process in psutil.process_iter(["name", "cmdline"]):
        try:
            command = " ".join(process.info.get("cmdline") or []).lower()
            if "llama-server" in command:
                return process
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return None


class ResourceSampler:
    """Samples host, Ollama server, and NVIDIA metrics once per interval."""

    def __init__(self, interval_seconds: float = 1.0):
        self.interval = interval_seconds
        self.samples: list[dict[str, Any]] = []
        self.errors: set[str] = set()
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None
        self._server = _ollama_process()
        self._runner: psutil.Process | None = None
        self._client = psutil.Process()

    def start(self) -> None:
        psutil.cpu_percent(interval=None)
        if self._server is not None:
            try:
                self._server.cpu_percent(interval=None)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                self._server = None
        try:
            self._client.cpu_percent(interval=None)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
        self._take_sample()
        self._thread = threading.Thread(target=self._run, name="resource-sampler", daemon=True)
        self._thread.start()

    def stop(self) -> dict[str, Any]:
        self._stop.set()
        if self._thread:
            self._thread.join(timeout=max(3.0, self.interval + 1))
        self._take_sample()
        ram_values = [s["ram_used_bytes"] for s in self.samples if s.get("ram_used_bytes") is not None]
        gpu_values = [s["gpu_vram_used_mb"] for s in self.samples if s.get("gpu_vram_used_mb") is not None]
        cpu_values = [s["system_cpu_percent"] for s in self.samples if s.get("system_cpu_percent") is not None]
        server_rss = [s["ollama_server_rss_bytes"] for s in self.samples if s.get("ollama_server_rss_bytes") is not None]
        server_cpu = [s["ollama_server_cpu_percent"] for s in self.samples if s.get("ollama_server_cpu_percent") is not None]
        runner_rss = [s["ollama_model_runner_rss_bytes"] for s in self.samples if s.get("ollama_model_runner_rss_bytes") is not None]
        client_cpu = [s["benchmark_process_cpu_percent"] for s in self.samples if s.get("benchmark_process_cpu_percent") is not None]
        gpu_util = [s["gpu_utilization_percent"] for s in self.samples if s.get("gpu_utilization_percent") is not None]
        return {
            "sample_interval_seconds": self.interval,
            "sample_count": len(self.samples),
            "mean_system_cpu_percent": round(sum(cpu_values) / len(cpu_values), 2) if cpu_values else None,
            "peak_system_cpu_percent": round(max(cpu_values), 2) if cpu_values else None,
            "mean_ram_used_bytes": round(sum(ram_values) / len(ram_values)) if ram_values else None,
            "peak_ram_used_bytes": max(ram_values) if ram_values else None,
            "mean_ollama_server_cpu_percent": round(sum(server_cpu) / len(server_cpu), 2) if server_cpu else None,
            "peak_ollama_server_rss_bytes": max(server_rss) if server_rss else None,
            "peak_ollama_model_runner_rss_bytes": max(runner_rss) if runner_rss else None,
            "peak_ollama_process_tree_rss_bytes": max((s["ollama_process_tree_rss_bytes"] for s in self.samples if s.get("ollama_process_tree_rss_bytes") is not None), default=None),
            "mean_benchmark_process_cpu_percent": round(sum(client_cpu) / len(client_cpu), 2) if client_cpu else None,
            "mean_gpu_utilization_percent": round(sum(gpu_util) / len(gpu_util), 2) if gpu_util else None,
            "peak_gpu_utilization_percent": max(gpu_util) if gpu_util else None,
            "peak_gpu_vram_used_mb": max(gpu_values) if gpu_values else None,
            "degradation_notes": sorted(self.errors) + ([] if gpu_values else ["NVIDIA utilization/VRAM samples unavailable."]),
            "samples": self.samples,
        }

    def _run(self) -> None:
        while not self._stop.wait(self.interval):
            self._take_sample()

    def _take_sample(self) -> None:
        sample: dict[str, Any] = {"timestamp": time.time(), "system_cpu_percent": None,
                                  "ram_used_bytes": None, "ollama_server_rss_bytes": None,
                                  "ollama_server_cpu_percent": None, "ollama_model_runner_rss_bytes": None,
                                  "ollama_process_tree_rss_bytes": None, "benchmark_process_cpu_percent": None,
                                  "gpu_utilization_percent": None,
                                  "gpu_vram_used_mb": None}
        try:
            sample["system_cpu_percent"] = psutil.cpu_percent(interval=None)
            sample["ram_used_bytes"] = psutil.virtual_memory().used
        except (psutil.Error, OSError) as exc:
            self.errors.add(f"Host resource sample failed: {exc}")
        try:
            sample["benchmark_process_cpu_percent"] = self._client.cpu_percent(interval=None)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            self.errors.add("Benchmark process CPU sample unavailable.")
        if self._runner is None or not self._runner.is_running():
            self._runner = _ollama_runner()
        if self._server is not None:
            try:
                sample["ollama_server_rss_bytes"] = self._server.memory_info().rss
                sample["ollama_server_cpu_percent"] = self._server.cpu_percent(interval=None)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                self.errors.add("Ollama server process RSS/CPU unavailable or process exited.")
                self._server = None
        if self._runner is not None:
            try:
                sample["ollama_model_runner_rss_bytes"] = self._runner.memory_info().rss
                server_rss = sample.get("ollama_server_rss_bytes") or 0
                sample["ollama_process_tree_rss_bytes"] = server_rss + sample["ollama_model_runner_rss_bytes"]
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                self._runner = None
        if shutil.which("nvidia-smi"):
            try:
                result = subprocess.run(["nvidia-smi", "--query-gpu=utilization.gpu,memory.used", "--format=csv,noheader,nounits"],
                                        capture_output=True, text=True, timeout=3, check=True)
                pairs = []
                for line in result.stdout.splitlines():
                    bits = [part.strip() for part in line.split(",")]
                    if len(bits) >= 2:
                        pairs.append((float(bits[0]), float(bits[1])))
                if pairs:
                    sample["gpu_utilization_percent"] = max(pair[0] for pair in pairs)
                    sample["gpu_vram_used_mb"] = sum(pair[1] for pair in pairs)
            except (subprocess.SubprocessError, ValueError, OSError) as exc:
                self.errors.add(f"nvidia-smi sampling failed: {exc}")
        else:
            self.errors.add("nvidia-smi not installed; GPU metrics unavailable.")
        self.samples.append(sample)
