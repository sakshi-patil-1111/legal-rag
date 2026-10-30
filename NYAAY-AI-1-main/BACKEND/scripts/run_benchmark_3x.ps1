$env:OMP_NUM_THREADS="4"
$env:TORCH_NUM_THREADS="4"
for ($i = 1; $i -le 3; $i++) {
    Write-Host "Running Benchmark Iteration $i..."
    python -u scripts/deterministic_benchmark.py
    Write-Host "--------------------------------"
}
