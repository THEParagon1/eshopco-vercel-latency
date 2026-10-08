from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import math
import statistics

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST"],
    allow_headers=["*"],
)

# Data from the supplied telemetry bundle.
TELEMETRY = [{'region': 'apac', 'service': 'support', 'latency_ms': 196.16, 'uptime_pct': 97.705, 'timestamp': 20250301}, {'region': 'apac', 'service': 'support', 'latency_ms': 143.23, 'uptime_pct': 97.457, 'timestamp': 20250302}, {'region': 'apac', 'service': 'recommendations', 'latency_ms': 228.07, 'uptime_pct': 98.71, 'timestamp': 20250303}, {'region': 'apac', 'service': 'recommendations', 'latency_ms': 105.73, 'uptime_pct': 98.49, 'timestamp': 20250304}, {'region': 'apac', 'service': 'recommendations', 'latency_ms': 227.56, 'uptime_pct': 98.058, 'timestamp': 20250305}, {'region': 'apac', 'service': 'payments', 'latency_ms': 226, 'uptime_pct': 97.412, 'timestamp': 20250306}, {'region': 'apac', 'service': 'payments', 'latency_ms': 116.84, 'uptime_pct': 97.851, 'timestamp': 20250307}, {'region': 'apac', 'service': 'analytics', 'latency_ms': 175.48, 'uptime_pct': 98.886, 'timestamp': 20250308}, {'region': 'apac', 'service': 'checkout', 'latency_ms': 233.18, 'uptime_pct': 98.209, 'timestamp': 20250309}, {'region': 'apac', 'service': 'recommendations', 'latency_ms': 219.57, 'uptime_pct': 98.881, 'timestamp': 20250310}, {'region': 'apac', 'service': 'catalog', 'latency_ms': 180.95, 'uptime_pct': 97.533, 'timestamp': 20250311}, {'region': 'apac', 'service': 'catalog', 'latency_ms': 123.92, 'uptime_pct': 99.24, 'timestamp': 20250312}, {'region': 'emea', 'service': 'analytics', 'latency_ms': 100.91, 'uptime_pct': 97.456, 'timestamp': 20250301}, {'region': 'emea', 'service': 'analytics', 'latency_ms': 151.68, 'uptime_pct': 98.54, 'timestamp': 20250302}, {'region': 'emea', 'service': 'recommendations', 'latency_ms': 168.1, 'uptime_pct': 98.828, 'timestamp': 20250303}, {'region': 'emea', 'service': 'catalog', 'latency_ms': 197.93, 'uptime_pct': 97.653, 'timestamp': 20250304}, {'region': 'emea', 'service': 'checkout', 'latency_ms': 154.5, 'uptime_pct': 97.777, 'timestamp': 20250305}, {'region': 'emea', 'service': 'catalog', 'latency_ms': 203.1, 'uptime_pct': 97.648, 'timestamp': 20250306}, {'region': 'emea', 'service': 'analytics', 'latency_ms': 227.78, 'uptime_pct': 97.983, 'timestamp': 20250307}, {'region': 'emea', 'service': 'recommendations', 'latency_ms': 184.73, 'uptime_pct': 98.98, 'timestamp': 20250308}, {'region': 'emea', 'service': 'recommendations', 'latency_ms': 200.95, 'uptime_pct': 97.537, 'timestamp': 20250309}, {'region': 'emea', 'service': 'catalog', 'latency_ms': 116.98, 'uptime_pct': 98.959, 'timestamp': 20250310}, {'region': 'emea', 'service': 'catalog', 'latency_ms': 110.07, 'uptime_pct': 99.138, 'timestamp': 20250311}, {'region': 'emea', 'service': 'catalog', 'latency_ms': 211.89, 'uptime_pct': 97.893, 'timestamp': 20250312}, {'region': 'amer', 'service': 'catalog', 'latency_ms': 188.45, 'uptime_pct': 97.872, 'timestamp': 20250301}, {'region': 'amer', 'service': 'recommendations', 'latency_ms': 219.59, 'uptime_pct': 97.579, 'timestamp': 20250302}, {'region': 'amer', 'service': 'recommendations', 'latency_ms': 173.92, 'uptime_pct': 97.537, 'timestamp': 20250303}, {'region': 'amer', 'service': 'checkout', 'latency_ms': 205.12, 'uptime_pct': 99.322, 'timestamp': 20250304}, {'region': 'amer', 'service': 'checkout', 'latency_ms': 147.81, 'uptime_pct': 99.062, 'timestamp': 20250305}, {'region': 'amer', 'service': 'support', 'latency_ms': 211.94, 'uptime_pct': 98.329, 'timestamp': 20250306}, {'region': 'amer', 'service': 'recommendations', 'latency_ms': 128.99, 'uptime_pct': 98.571, 'timestamp': 20250307}, {'region': 'amer', 'service': 'recommendations', 'latency_ms': 218.69, 'uptime_pct': 97.722, 'timestamp': 20250308}, {'region': 'amer', 'service': 'payments', 'latency_ms': 148.78, 'uptime_pct': 97.966, 'timestamp': 20250309}, {'region': 'amer', 'service': 'analytics', 'latency_ms': 175.83, 'uptime_pct': 97.852, 'timestamp': 20250310}, {'region': 'amer', 'service': 'recommendations', 'latency_ms': 118.25, 'uptime_pct': 98.486, 'timestamp': 20250311}, {'region': 'amer', 'service': 'support', 'latency_ms': 142.17, 'uptime_pct': 98.405, 'timestamp': 20250312}]


class RequestBody(BaseModel):
    regions: list[str] = Field(default_factory=list)
    threshold_ms: float = 180


def percentile(values: list[float], p: float = 95.0) -> float:
    if not values:
        raise ValueError("No telemetry records for region")

    values = sorted(values)
    if len(values) == 1:
        return float(values[0])

    rank = (len(values) - 1) * p / 100.0
    lo = math.floor(rank)
    hi = math.ceil(rank)

    if lo == hi:
        return float(values[lo])

    return values[lo] + (values[hi] - values[lo]) * (rank - lo)


@app.post("/")
def analyze(body: RequestBody):
    response = []

    for region in body.regions:
        rows = [r for r in TELEMETRY if r["region"] == region]

        if not rows:
            response.append({
                "region": region,
                "avg_latency": None,
                "p95_latency": None,
                "avg_uptime": None,
                "breaches": 0,
            })
            continue

        latencies = [float(r["latency_ms"]) for r in rows]
        uptimes = [float(r["uptime_pct"]) for r in rows]

        response.append({
            "region": region,
            "avg_latency": statistics.mean(latencies),
            "p95_latency": percentile(latencies, 95),
            "avg_uptime": statistics.mean(uptimes),
            "breaches": sum(latency > body.threshold_ms for latency in latencies),
        })

    return response
