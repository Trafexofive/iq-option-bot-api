#!/usr/bin/env python3
"""
Benchmarking script for IQ Option Bot API performance testing.
"""

import asyncio
import time
import statistics
from typing import List, Dict, Any
import httpx
import json


class APIBenchmark:
    def __init__(self, base_url: str = "http://localhost:8000/api/v1"):
        self.base_url = base_url
        self.results: List[Dict[str, Any]] = []
    
    async def benchmark_endpoint(self, 
                                endpoint: str, 
                                method: str = "GET", 
                                data: Dict = None, 
                                iterations: int = 10) -> Dict[str, Any]:
        """Benchmark a specific API endpoint"""
        
        print(f"\n🔧 Benchmarking {method} {endpoint} ({iterations} iterations)")
        
        latencies = []
        errors = 0
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            for i in range(iterations):
                start_time = time.time()
                
                try:
                    if method == "GET":
                        response = await client.get(f"{self.base_url}{endpoint}")
                    elif method == "POST":
                        response = await client.post(f"{self.base_url}{endpoint}", json=data)
                    
                    end_time = time.time()
                    latency = (end_time - start_time) * 1000  # Convert to milliseconds
                    
                    if response.status_code == 200:
                        latencies.append(latency)
                    else:
                        errors += 1
                        print(f"  ❌ Request {i+1}: HTTP {response.status_code}")
                        
                except Exception as e:
                    errors += 1
                    print(f"  ❌ Request {i+1}: {str(e)}")
                    
                # Small delay between requests
                await asyncio.sleep(0.1)
        
        if latencies:
            result = {
                "endpoint": endpoint,
                "method": method,
                "iterations": iterations,
                "successful_requests": len(latencies),
                "errors": errors,
                "avg_latency_ms": statistics.mean(latencies),
                "min_latency_ms": min(latencies),
                "max_latency_ms": max(latencies),
                "median_latency_ms": statistics.median(latencies),
                "p95_latency_ms": self._percentile(latencies, 95),
                "p99_latency_ms": self._percentile(latencies, 99)
            }
        else:
            result = {
                "endpoint": endpoint,
                "method": method,
                "iterations": iterations,
                "successful_requests": 0,
                "errors": errors,
                "status": "ALL_FAILED"
            }
        
        self.results.append(result)
        return result
    
    def _percentile(self, data: List[float], percentile: int) -> float:
        """Calculate percentile"""
        if not data:
            return 0
        sorted_data = sorted(data)
        index = (percentile / 100) * len(sorted_data)
        if index.is_integer():
            return sorted_data[int(index) - 1]
        else:
            lower = sorted_data[int(index)]
            upper = sorted_data[int(index) + 1]
            return (lower + upper) / 2
    
    def print_results(self):
        """Print benchmark results"""
        print("\n" + "="*80)
        print("🏁 BENCHMARK RESULTS")
        print("="*80)
        
        for result in self.results:
            if result.get("status") == "ALL_FAILED":
                print(f"\n❌ {result['method']} {result['endpoint']}: ALL REQUESTS FAILED")
                continue
                
            print(f"\n✅ {result['method']} {result['endpoint']}:")
            print(f"   Success Rate: {result['successful_requests']}/{result['iterations']} "
                  f"({result['successful_requests']/result['iterations']*100:.1f}%)")
            print(f"   Average Latency: {result['avg_latency_ms']:.2f}ms")
            print(f"   Min/Max Latency: {result['min_latency_ms']:.2f}ms / {result['max_latency_ms']:.2f}ms")
            print(f"   P95/P99 Latency: {result['p95_latency_ms']:.2f}ms / {result['p99_latency_ms']:.2f}ms")
            
            if result['errors'] > 0:
                print(f"   ⚠️  Errors: {result['errors']}")
    
    def save_results(self, filename: str = "benchmark_results.json"):
        """Save results to JSON file"""
        with open(filename, 'w') as f:
            json.dump(self.results, f, indent=2)
        print(f"\n💾 Results saved to {filename}")


async def main():
    """Run comprehensive API benchmarks"""
    
    print("🚀 IQ Option Bot API Performance Benchmark")
    print("=" * 50)
    
    benchmark = APIBenchmark()
    
    # Test endpoints
    test_cases = [
        # Health checks (fast)
        ("/health", "GET", None, 20),
        
        # Market data (moderate)
        ("/market/data?asset=EURUSD", "GET", None, 15),
        
        # Trading operations (slower)
        ("/trading/balance", "GET", None, 10),
        ("/trading/history", "GET", None, 10),
        
        # LLM completion (slowest)
        ("/llm/completion", "POST", {
            "messages": [{"role": "user", "content": "What is 1+1?"}],
            "temperature": 0.1
        }, 5),
    ]
    
    # Run benchmarks
    for endpoint, method, data, iterations in test_cases:
        await benchmark.benchmark_endpoint(endpoint, method, data, iterations)
    
    # Test concurrent requests
    print(f"\n🔀 Testing concurrent requests...")
    start_time = time.time()
    
    tasks = []
    for i in range(5):  # 5 concurrent requests
        task = benchmark.benchmark_endpoint("/health", "GET", None, 1)
        tasks.append(task)
    
    await asyncio.gather(*tasks)
    
    concurrent_time = time.time() - start_time
    print(f"   ⏱️  5 concurrent requests took {concurrent_time:.2f}s")
    
    # Print and save results
    benchmark.print_results()
    benchmark.save_results("data/benchmark_results.json")
    
    print(f"\n🎯 Benchmark completed!")
    print(f"   Total API tests: {len(benchmark.results)}")
    print(f"   Check data/benchmark_results.json for detailed results")


if __name__ == "__main__":
    asyncio.run(main())