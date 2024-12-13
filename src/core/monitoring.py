"""Monitoring module for trade manager service."""
from prometheus_client import Counter, Histogram, Info
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
import time

# Trade metrics
TRADE_REQUESTS = Counter(
    'trade_manager_trade_requests_total',
    'Total number of trade requests processed',
    ['status', 'strategy']
)

TRADE_EXECUTION_TIME = Histogram(
    'trade_manager_trade_execution_seconds',
    'Time spent executing trades',
    ['strategy']
)

# API metrics
HTTP_REQUEST_DURATION = Histogram(
    'trade_manager_http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint']
)

HTTP_REQUESTS_TOTAL = Counter(
    'trade_manager_http_requests_total',
    'Total number of HTTP requests',
    ['method', 'endpoint', 'status']
)

# System info
SYSTEM_INFO = Info('trade_manager_info', 'Trade manager service information')

class MetricsMiddleware(BaseHTTPMiddleware):
    """Middleware for collecting HTTP metrics."""
    
    async def dispatch(self, request: Request, call_next) -> Response:
        """Process the request and record metrics."""
        start_time = time.time()
        response = await call_next(request)
        duration = time.time() - start_time
        
        # Record metrics
        HTTP_REQUEST_DURATION.labels(
            method=request.method,
            endpoint=request.url.path
        ).observe(duration)
        
        HTTP_REQUESTS_TOTAL.labels(
            method=request.method,
            endpoint=request.url.path,
            status=response.status_code
        ).inc()
        
        return response

def track_trade_request(strategy: str, status: str):
    """Track a trade request."""
    TRADE_REQUESTS.labels(
        strategy=strategy,
        status=status
    ).inc()

def track_trade_execution(strategy: str):
    """Context manager to track trade execution time."""
    return TRADE_EXECUTION_TIME.labels(strategy=strategy).time()

def init_metrics(app_version: str):
    """Initialize system metrics."""
    SYSTEM_INFO.info({
        'version': app_version,
        'start_time': time.strftime('%Y-%m-%d %H:%M:%S')
    })
