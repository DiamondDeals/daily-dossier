#!/usr/bin/env python3
"""
Rotating User Agent Pool for Human-Like Browsing
Provides realistic browser fingerprints across multiple platforms
"""

import random
from typing import Dict, List, Tuple
from dataclasses import dataclass


@dataclass
class BrowserProfile:
    """Complete browser profile for realistic requests"""
    user_agent: str
    accept: str
    accept_language: str
    accept_encoding: str
    sec_ch_ua: str
    sec_ch_ua_mobile: str
    sec_ch_ua_platform: str
    sec_fetch_dest: str
    sec_fetch_mode: str
    sec_fetch_site: str
    sec_fetch_user: str
    upgrade_insecure_requests: str


class UserAgentRotator:
    """
    Manages a pool of realistic user agents and browser profiles.
    Rotates through them to appear as different users.
    """

    def __init__(self):
        self._setup_profiles()
        self._current_index = 0
        self._used_count = {}

    def _setup_profiles(self):
        """Setup comprehensive browser profiles"""

        # Chrome on Windows
        self.chrome_windows = [
            {
                'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'sec_ch_ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
                'sec_ch_ua_platform': '"Windows"',
            },
            {
                'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
                'sec_ch_ua': '"Not_A Brand";v="8", "Chromium";v="119", "Google Chrome";v="119"',
                'sec_ch_ua_platform': '"Windows"',
            },
            {
                'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
                'sec_ch_ua': '"Not_A Brand";v="8", "Chromium";v="121", "Google Chrome";v="121"',
                'sec_ch_ua_platform': '"Windows"',
            },
        ]

        # Chrome on Mac
        self.chrome_mac = [
            {
                'user_agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'sec_ch_ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
                'sec_ch_ua_platform': '"macOS"',
            },
            {
                'user_agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
                'sec_ch_ua': '"Not_A Brand";v="8", "Chromium";v="119", "Google Chrome";v="119"',
                'sec_ch_ua_platform': '"macOS"',
            },
        ]

        # Chrome on Linux
        self.chrome_linux = [
            {
                'user_agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'sec_ch_ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
                'sec_ch_ua_platform': '"Linux"',
            },
            {
                'user_agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
                'sec_ch_ua': '"Not_A Brand";v="8", "Chromium";v="119", "Google Chrome";v="119"',
                'sec_ch_ua_platform': '"Linux"',
            },
        ]

        # Firefox on Windows
        self.firefox_windows = [
            {
                'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
                'sec_ch_ua': None,  # Firefox doesn't send sec-ch-ua
                'sec_ch_ua_platform': None,
            },
            {
                'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0',
                'sec_ch_ua': None,
                'sec_ch_ua_platform': None,
            },
        ]

        # Firefox on Mac
        self.firefox_mac = [
            {
                'user_agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0',
                'sec_ch_ua': None,
                'sec_ch_ua_platform': None,
            },
            {
                'user_agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:120.0) Gecko/20100101 Firefox/120.0',
                'sec_ch_ua': None,
                'sec_ch_ua_platform': None,
            },
        ]

        # Firefox on Linux
        self.firefox_linux = [
            {
                'user_agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:121.0) Gecko/20100101 Firefox/121.0',
                'sec_ch_ua': None,
                'sec_ch_ua_platform': None,
            },
            {
                'user_agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:120.0) Gecko/20100101 Firefox/120.0',
                'sec_ch_ua': None,
                'sec_ch_ua_platform': None,
            },
        ]

        # Safari on Mac
        self.safari_mac = [
            {
                'user_agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15',
                'sec_ch_ua': None,
                'sec_ch_ua_platform': None,
            },
            {
                'user_agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
                'sec_ch_ua': None,
                'sec_ch_ua_platform': None,
            },
        ]

        # Edge on Windows
        self.edge_windows = [
            {
                'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0',
                'sec_ch_ua': '"Not_A Brand";v="8", "Chromium";v="120", "Microsoft Edge";v="120"',
                'sec_ch_ua_platform': '"Windows"',
            },
        ]

        # Combine all profiles with weights (Chrome is most common)
        self.all_profiles = []

        # Add with weights: Chrome 60%, Firefox 25%, Safari 10%, Edge 5%
        for _ in range(6):  # Chrome weight
            self.all_profiles.extend(self.chrome_windows)
            self.all_profiles.extend(self.chrome_mac)
            self.all_profiles.extend(self.chrome_linux)

        for _ in range(3):  # Firefox weight
            self.all_profiles.extend(self.firefox_windows)
            self.all_profiles.extend(self.firefox_mac)
            self.all_profiles.extend(self.firefox_linux)

        for _ in range(1):  # Safari weight
            self.all_profiles.extend(self.safari_mac)

        for _ in range(1):  # Edge weight
            self.all_profiles.extend(self.edge_windows)

        # Shuffle the pool
        random.shuffle(self.all_profiles)

        # Common accept headers
        self.accept_languages = [
            'en-US,en;q=0.9',
            'en-US,en;q=0.9,es;q=0.8',
            'en-GB,en;q=0.9,en-US;q=0.8',
            'en-US,en;q=0.8',
            'en-US,en;q=0.9,fr;q=0.8',
        ]

    def get_random_profile(self) -> Dict[str, str]:
        """Get a random browser profile with complete headers"""
        profile = random.choice(self.all_profiles)

        # Build complete headers
        headers = {
            'User-Agent': profile['user_agent'],
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': random.choice(self.accept_languages),
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0',
        }

        # Add Chrome-specific headers if applicable
        if profile.get('sec_ch_ua'):
            headers['sec-ch-ua'] = profile['sec_ch_ua']
            headers['sec-ch-ua-mobile'] = '?0'
            headers['sec-ch-ua-platform'] = profile['sec_ch_ua_platform']

        return headers

    def get_next_profile(self) -> Dict[str, str]:
        """Get next profile in rotation (for consistent session behavior)"""
        profile = self.all_profiles[self._current_index % len(self.all_profiles)]
        self._current_index += 1

        headers = {
            'User-Agent': profile['user_agent'],
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': random.choice(self.accept_languages),
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0',
        }

        if profile.get('sec_ch_ua'):
            headers['sec-ch-ua'] = profile['sec_ch_ua']
            headers['sec-ch-ua-mobile'] = '?0'
            headers['sec-ch-ua-platform'] = profile['sec_ch_ua_platform']

        return headers

    def get_session_headers(self) -> Dict[str, str]:
        """Get headers for maintaining a consistent session"""
        # For sessions, use a fixed profile to mimic real browser behavior
        if not hasattr(self, '_session_profile'):
            self._session_profile = random.choice(self.all_profiles)
            self._session_language = random.choice(self.accept_languages)

        headers = {
            'User-Agent': self._session_profile['user_agent'],
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': self._session_language,
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
        }

        if self._session_profile.get('sec_ch_ua'):
            headers['sec-ch-ua'] = self._session_profile['sec_ch_ua']
            headers['sec-ch-ua-mobile'] = '?0'
            headers['sec-ch-ua-platform'] = self._session_profile['sec_ch_ua_platform']

        return headers

    def reset_session(self):
        """Reset the session profile (simulates new browser session)"""
        if hasattr(self, '_session_profile'):
            del self._session_profile
        if hasattr(self, '_session_language'):
            del self._session_language


# Singleton instance
_rotator = None

def get_rotator() -> UserAgentRotator:
    """Get the singleton rotator instance"""
    global _rotator
    if _rotator is None:
        _rotator = UserAgentRotator()
    return _rotator


def get_random_headers() -> Dict[str, str]:
    """Convenience function to get random headers"""
    return get_rotator().get_random_profile()


def get_session_headers() -> Dict[str, str]:
    """Convenience function to get session headers"""
    return get_rotator().get_session_headers()


if __name__ == '__main__':
    # Test the user agent rotator
    rotator = UserAgentRotator()

    print("Testing User Agent Rotator")
    print("=" * 60)

    print("\n5 Random Profiles:")
    for i in range(5):
        headers = rotator.get_random_profile()
        print(f"\n{i+1}. {headers['User-Agent'][:80]}...")

    print("\n\nSession Headers (should be consistent):")
    for i in range(3):
        headers = rotator.get_session_headers()
        print(f"{i+1}. {headers['User-Agent'][:80]}...")

    rotator.reset_session()
    print("\n\nAfter reset (new session):")
    headers = rotator.get_session_headers()
    print(f"New: {headers['User-Agent'][:80]}...")
