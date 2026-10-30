import asyncio
import httpx
import time
import argparse

API_URL = "http://127.0.0.1:8000/api/health"

async def fetch(client, i):
    start_time = time.time()
    try:
        response = await client.get(API_URL)
        latency = time.time() - start_time
        return response.status_code, latency
    except Exception as e:
        return 0, time.time() - start_time

async def run_load_test(concurrent_users=50, total_requests=200):
    print(f"Starting Load Test: {total_requests} requests with {concurrent_users} concurrent users.")
    
    limits = httpx.Limits(max_connections=concurrent_users)
    async with httpx.AsyncClient(limits=limits) as client:
        start_time = time.time()
        
        tasks = []
        for i in range(total_requests):
            tasks.append(fetch(client, i))
            
        results = await asyncio.gather(*tasks)
        
        total_time = time.time() - start_time
        
        successes = sum(1 for status, _ in results if status == 200)
        failures = total_requests - successes
        latencies = [lat for _, lat in results]
        avg_latency = sum(latencies) / len(latencies) if latencies else 0
        
        print("\n--- Load Test Results ---")
        print(f"Total Time: {total_time:.2f}s")
        print(f"Total Requests: {total_requests}")
        print(f"Successes: {successes}")
        print(f"Failures: {failures}")
        print(f"Avg Latency: {avg_latency:.4f}s")
        print(f"Requests per second: {total_requests / total_time:.2f}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--concurrent", type=int, default=50)
    parser.add_argument("-n", "--requests", type=int, default=200)
    args = parser.parse_args()
    
    asyncio.run(run_load_test(args.concurrent, args.requests))
