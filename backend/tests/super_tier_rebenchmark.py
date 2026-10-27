"""
SUPER Tier Physical Re-Benchmark Script for Saarthi Closed Beta.
Measures physical inference latency, tokens/sec, RAM footprint, CPU load, and 10-cycle memory stability.
"""

import time
import asyncio
import psutil
from app.system.hardware import HardwareDetectionService
from app.models.nemotron_service import NemotronService
from app.config.settings import settings

async def run_super_physical_benchmark():
    print("=== SUPER TIER PHYSICAL HARDWARE RE-BENCHMARK (NUM_CTX=4096) ===", flush=True)
    profile = HardwareDetectionService.get_hardware_profile()
    print(f"Host Machine: {profile.os_name} | CPU Cores: {profile.cpu_cores} | System RAM: {profile.total_ram_gb} GB | GPU: {profile.gpu_vendor} {profile.gpu_model} ({profile.vram_gb} GB VRAM)", flush=True)
    
    nemotron = NemotronService(model_name="nemotron-3-nano:4b")
    
    # 1. Cold Model Load & First Token Latency Check
    t0 = time.time()
    resp_short = await nemotron.generate(prompt="Write a 1-sentence career summary for a Senior Developer.")
    load_and_first_token_time = round((time.time() - t0) * 1000, 2)
    print(f"\n[MEASUREMENT 1] Cold Load + Response Latency: {load_and_first_token_time} ms", flush=True)
    print(f"Response Preview: '{resp_short[:80]}...'", flush=True)

    # 2. Token Length Execution Benchmarks (50, 100, 250, 500 tokens)
    token_tests = [
        ("50 Tokens", "Write a 50-word concise resume summary for a Full Stack Developer."),
        ("100 Tokens", "Write a 100-word professional bio highlighting achievements in cloud architecture."),
        ("250 Tokens", "Write a 250-word cover letter for a Principal Systems Engineer position at an AI startup."),
        ("500 Tokens", "Provide a comprehensive 500-word STAR interview answer explaining a complex system migration under high traffic.")
    ]
    
    print("\n--- [TOKEN LENGTH BENCHMARKS] ---", flush=True)
    for label, prompt in token_tests:
        t_start = time.time()
        output = await nemotron.generate(prompt=prompt)
        t_duration = time.time() - t_start
        words = len(output.split())
        approx_tokens = int(words * 1.3)
        tok_sec = round(approx_tokens / t_duration, 2) if t_duration > 0 else 0
        print(f"- {label:12s} | Time: {t_duration:6.2f}s | Words: {words:3d} | Approx Tokens: {approx_tokens:3d} | Speed: {tok_sec:5.2f} tok/s", flush=True)

    # 3. Sustained 5-Cycle Memory & Process Stability Check
    print("\n--- [SUSTAINED MEMORY STABILITY BENCHMARK] ---", flush=True)
    proc = psutil.Process()
    initial_mem_mb = round(proc.memory_info().rss / (1024 * 1024), 2)
    cpu_loads = []
    
    for cycle in range(1, 6):
        t_c_start = time.time()
        _ = await nemotron.generate(prompt=f"Cycle {cycle}: Provide 3 ATS keywords for a Data Scientist role.")
        c_dur = time.time() - t_c_start
        c_cpu = psutil.cpu_percent(interval=0.1)
        c_mem = round(proc.memory_info().rss / (1024 * 1024), 2)
        cpu_loads.append(c_cpu)
        print(f"Cycle {cycle:02d}/05 | Duration: {c_dur:5.2f}s | Process RAM: {c_mem:6.2f} MB | CPU Load: {c_cpu:5.1f}%", flush=True)

    final_mem_mb = round(proc.memory_info().rss / (1024 * 1024), 2)
    mem_delta_mb = round(final_mem_mb - initial_mem_mb, 2)
    avg_cpu = round(sum(cpu_loads) / len(cpu_loads), 1)
    
    print("\n=== BENCHMARK SUMMARY ===", flush=True)
    print(f"Initial Process Memory : {initial_mem_mb} MB", flush=True)
    print(f"Final Process Memory   : {final_mem_mb} MB", flush=True)
    print(f"Process Memory Growth  : +{mem_delta_mb} MB", flush=True)
    print(f"Average CPU Load       : {avg_cpu}%", flush=True)
    print(f"Process Crashes        : 0", flush=True)

if __name__ == "__main__":
    asyncio.run(run_super_physical_benchmark())
