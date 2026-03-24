#!/usr/bin/env python3
"""
Advanced Rate Limiter for Human-Like Browsing
Implements intelligent throttling to avoid detection and respect rate limits
"""

import time
import random
import threading
from collections import deque
from typing import Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


@dataclass
class RateLimitConfig:
    """Configuration for rate limiting"""
    # Request timing
    min_delay_between_requests: float = 2.0  # seconds
    max_delay_between_requests: float = 5.0  # seconds
    min_delay_between_subreddits: float = 10.0  # seconds
    max_delay_between_subreddits: float = 20.0  # seconds

    # Human-like reading time
    min_reading_time: float = 1.0  # seconds
    max_reading_time: float = 3.0  # seconds

    # Rate limits
    max_requests_per_minute: int = 30
    max_requests_per_hour: int = 500

    # Backoff settings
    initial_backoff: float = 5.0  # seconds
    max_backoff: float = 300.0  # 5 minutes
    backoff_multiplier: float = 2.0
    max_retries: int = 5

    # Jitter (randomness)
    jitter_factor: float = 0.3  # 30% randomness


@dataclass
class RateLimitState:
    """Current state of rate limiting"""
    request_times: deque = field(default_factory=lambda: deque(maxlen=100))
    current_backoff: float = 0.0
    consecutive_errors: int = 0
    last_request_time: float = 0.0
    total_requests: int = 0
    total_errors: int = 0
    is_throttled: bool = False
    throttle_until: float = 0.0


class RateLimiter:
    """
    Advanced rate limiter with human-like behavior.

    Features:
    - Configurable delays between requests
    - Exponential backoff on errors
    - Request tracking per minute/hour
    - Human-like jitter (randomness)
    - Thread-safe operations
    """

    def __init__(self, config: Optional[RateLimitConfig] = None):
        self.config = config or RateLimitConfig()
        self.state = RateLimitState()
        self._lock = threading.Lock()
        self._last_subreddit_time = 0.0

    def _add_jitter(self, value: float) -> float:
        """Add random jitter to a value"""
        jitter = value * self.config.jitter_factor
        return value + random.uniform(-jitter, jitter)

    def _get_random_delay(self, min_val: float, max_val: float) -> float:
        """Get a random delay between min and max"""
        delay = random.uniform(min_val, max_val)
        return self._add_jitter(delay)

    def get_request_delay(self) -> float:
        """Calculate delay before next request"""
        with self._lock:
            now = time.time()

            # Check if we're throttled
            if self.state.is_throttled and now < self.state.throttle_until:
                remaining = self.state.throttle_until - now
                logger.warning(f"Throttled for {remaining:.1f} more seconds")
                return remaining

            # Clear throttle if expired
            if self.state.is_throttled and now >= self.state.throttle_until:
                self.state.is_throttled = False

            # Check rate limits
            minute_ago = now - 60
            hour_ago = now - 3600

            # Count recent requests
            requests_last_minute = sum(1 for t in self.state.request_times if t > minute_ago)
            requests_last_hour = sum(1 for t in self.state.request_times if t > hour_ago)

            # Calculate base delay
            base_delay = self._get_random_delay(
                self.config.min_delay_between_requests,
                self.config.max_delay_between_requests
            )

            # Increase delay if approaching rate limit
            if requests_last_minute >= self.config.max_requests_per_minute * 0.8:
                # Near minute limit - slow down significantly
                base_delay = max(base_delay, 10.0)
                logger.info(f"Approaching minute limit ({requests_last_minute} requests), slowing down")

            if requests_last_hour >= self.config.max_requests_per_hour * 0.9:
                # Near hour limit - major slowdown
                base_delay = max(base_delay, 30.0)
                logger.warning(f"Approaching hour limit ({requests_last_hour} requests), major slowdown")

            # Add backoff if there were recent errors
            if self.state.current_backoff > 0:
                base_delay = max(base_delay, self.state.current_backoff)

            # Account for time since last request
            time_since_last = now - self.state.last_request_time if self.state.last_request_time > 0 else float('inf')

            if time_since_last >= base_delay:
                return 0  # No need to wait

            return base_delay - time_since_last

    def get_subreddit_delay(self) -> float:
        """Calculate delay before switching to a new subreddit"""
        with self._lock:
            now = time.time()

            base_delay = self._get_random_delay(
                self.config.min_delay_between_subreddits,
                self.config.max_delay_between_subreddits
            )

            # Account for time since last subreddit switch
            time_since_last = now - self._last_subreddit_time if self._last_subreddit_time > 0 else float('inf')

            if time_since_last >= base_delay:
                return 0

            return base_delay - time_since_last

    def get_reading_delay(self) -> float:
        """Get a human-like reading delay"""
        return self._get_random_delay(
            self.config.min_reading_time,
            self.config.max_reading_time
        )

    def record_request(self):
        """Record that a request was made"""
        with self._lock:
            now = time.time()
            self.state.request_times.append(now)
            self.state.last_request_time = now
            self.state.total_requests += 1
            # Successful request - decay backoff
            if self.state.current_backoff > 0:
                self.state.current_backoff = max(0, self.state.current_backoff / 2)
            self.state.consecutive_errors = 0

    def record_subreddit_switch(self):
        """Record switching to a new subreddit"""
        with self._lock:
            self._last_subreddit_time = time.time()

    def record_error(self, status_code: Optional[int] = None) -> float:
        """
        Record an error and return the backoff time.

        Returns the number of seconds to wait before retrying.
        """
        with self._lock:
            self.state.total_errors += 1
            self.state.consecutive_errors += 1

            # Calculate backoff
            if self.state.current_backoff == 0:
                self.state.current_backoff = self.config.initial_backoff
            else:
                self.state.current_backoff = min(
                    self.state.current_backoff * self.config.backoff_multiplier,
                    self.config.max_backoff
                )

            # Special handling for specific status codes
            if status_code == 429:  # Too Many Requests
                logger.warning("Received 429 - Rate limited by Reddit")
                self.state.current_backoff = max(self.state.current_backoff, 60.0)
                self.state.is_throttled = True
                self.state.throttle_until = time.time() + self.state.current_backoff

            elif status_code == 503:  # Service Unavailable
                logger.warning("Received 503 - Reddit temporarily unavailable")
                self.state.current_backoff = max(self.state.current_backoff, 30.0)

            # Add jitter to backoff
            backoff_with_jitter = self._add_jitter(self.state.current_backoff)

            logger.info(f"Backoff: {backoff_with_jitter:.1f}s (consecutive errors: {self.state.consecutive_errors})")
            return backoff_with_jitter

    def should_retry(self) -> bool:
        """Check if we should retry after an error"""
        with self._lock:
            return self.state.consecutive_errors < self.config.max_retries

    def reset_backoff(self):
        """Reset backoff after successful operation"""
        with self._lock:
            self.state.current_backoff = 0
            self.state.consecutive_errors = 0

    def wait_for_request(self, callback: Optional[Callable[[], None]] = None):
        """
        Wait the appropriate time before making a request.

        Args:
            callback: Optional function to call while waiting (e.g., for progress updates)
        """
        delay = self.get_request_delay()
        if delay > 0:
            logger.debug(f"Waiting {delay:.1f}s before next request")
            if callback:
                # Call callback periodically during wait
                start = time.time()
                while time.time() - start < delay:
                    remaining = delay - (time.time() - start)
                    callback()
                    time.sleep(min(1.0, remaining))
            else:
                time.sleep(delay)

    def wait_for_subreddit(self, callback: Optional[Callable[[], None]] = None):
        """Wait the appropriate time before switching subreddits"""
        delay = self.get_subreddit_delay()
        if delay > 0:
            logger.info(f"Waiting {delay:.1f}s before next subreddit")
            if callback:
                start = time.time()
                while time.time() - start < delay:
                    remaining = delay - (time.time() - start)
                    callback()
                    time.sleep(min(1.0, remaining))
            else:
                time.sleep(delay)

    def simulate_reading(self):
        """Simulate human reading time"""
        delay = self.get_reading_delay()
        logger.debug(f"Simulating reading time: {delay:.1f}s")
        time.sleep(delay)

    def get_stats(self) -> dict:
        """Get current rate limiter statistics"""
        with self._lock:
            now = time.time()
            minute_ago = now - 60
            hour_ago = now - 3600

            return {
                'total_requests': self.state.total_requests,
                'total_errors': self.state.total_errors,
                'requests_last_minute': sum(1 for t in self.state.request_times if t > minute_ago),
                'requests_last_hour': sum(1 for t in self.state.request_times if t > hour_ago),
                'current_backoff': self.state.current_backoff,
                'consecutive_errors': self.state.consecutive_errors,
                'is_throttled': self.state.is_throttled,
                'error_rate': self.state.total_errors / max(1, self.state.total_requests) * 100,
            }


class AdaptiveRateLimiter(RateLimiter):
    """
    Rate limiter that adapts based on response patterns.
    Automatically adjusts timing based on server responses.
    """

    def __init__(self, config: Optional[RateLimitConfig] = None):
        super().__init__(config)
        self._response_times = deque(maxlen=50)
        self._success_streak = 0

    def record_response_time(self, response_time: float):
        """Record server response time for adaptive behavior"""
        with self._lock:
            self._response_times.append(response_time)

    def record_success(self, response_time: float):
        """Record a successful request"""
        with self._lock:
            self._success_streak += 1
            self._response_times.append(response_time)

            # Gradually reduce delays after consistent success
            if self._success_streak >= 10:
                self.config.min_delay_between_requests = max(
                    1.5,
                    self.config.min_delay_between_requests * 0.95
                )

    def record_error(self, status_code: Optional[int] = None) -> float:
        """Record error and reset success streak"""
        with self._lock:
            self._success_streak = 0
            # Increase delays after errors
            self.config.min_delay_between_requests = min(
                10.0,
                self.config.min_delay_between_requests * 1.5
            )
        return super().record_error(status_code)

    def get_avg_response_time(self) -> float:
        """Get average server response time"""
        with self._lock:
            if not self._response_times:
                return 0.0
            return sum(self._response_times) / len(self._response_times)


# Convenience functions
_default_limiter: Optional[RateLimiter] = None


def get_limiter() -> RateLimiter:
    """Get the default rate limiter instance"""
    global _default_limiter
    if _default_limiter is None:
        _default_limiter = AdaptiveRateLimiter()
    return _default_limiter


def wait_before_request():
    """Convenience function to wait before making a request"""
    get_limiter().wait_for_request()


def wait_before_subreddit():
    """Convenience function to wait before switching subreddits"""
    get_limiter().wait_for_subreddit()


if __name__ == '__main__':
    # Test the rate limiter
    logging.basicConfig(level=logging.DEBUG)

    print("Testing Rate Limiter")
    print("=" * 60)

    limiter = AdaptiveRateLimiter()

    print("\n1. Testing request delays:")
    for i in range(5):
        delay = limiter.get_request_delay()
        print(f"   Request {i+1}: delay = {delay:.2f}s")
        limiter.record_request()

    print("\n2. Testing subreddit delays:")
    for i in range(3):
        delay = limiter.get_subreddit_delay()
        print(f"   Subreddit {i+1}: delay = {delay:.2f}s")
        limiter.record_subreddit_switch()

    print("\n3. Testing backoff on errors:")
    for i in range(3):
        backoff = limiter.record_error(500)
        print(f"   Error {i+1}: backoff = {backoff:.2f}s")

    print("\n4. Testing 429 handling:")
    backoff = limiter.record_error(429)
    print(f"   429 error: backoff = {backoff:.2f}s, throttled = {limiter.state.is_throttled}")

    print("\n5. Statistics:")
    stats = limiter.get_stats()
    for key, value in stats.items():
        print(f"   {key}: {value}")
