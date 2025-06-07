"""Device information parser utility."""

import re
from typing import Dict, Union
from dataclasses import dataclass


@dataclass
class DeviceInfo:
    """Parsed device information."""
    browser: str
    browser_version: str
    os: str
    os_version: str
    device_type: str
    device_name: str


class DeviceParser:
    """Parser for extracting device information from user agent strings."""
    
    # Browser patterns
    BROWSER_PATTERNS = {
        'Chrome': r'Chrome/([0-9.]+)',
        'Firefox': r'Firefox/([0-9.]+)',
        'Safari': r'Safari/([0-9.]+)',
        'Edge': r'Edg/([0-9.]+)',
        'Opera': r'(?:Opera|OPR)/([0-9.]+)',
        'Internet Explorer': r'MSIE ([0-9.]+)',
    }
    
    # Operating system patterns
    OS_PATTERNS: Dict[str, Dict[str, Union[str, Dict[str, str]]]] = {
        'Windows': {
            'pattern': r'Windows NT ([0-9.]+)',
            'versions': {
                '10.0': 'Windows 11/10',
                '6.3': 'Windows 8.1',
                '6.2': 'Windows 8',
                '6.1': 'Windows 7',
                '6.0': 'Windows Vista',
                '5.1': 'Windows XP',
            }
        },
        'macOS': {
            'pattern': r'Mac OS X ([0-9_]+)',
            'versions': {}  # We'll format these dynamically
        },
        'Linux': {
            'pattern': r'Linux',
            'versions': {}
        },
        'Android': {
            'pattern': r'Android ([0-9.]+)',
            'versions': {}
        },
        'iOS': {
            'pattern': r'OS ([0-9_]+)',
            'versions': {}
        }
    }
    
    # Mobile device patterns
    MOBILE_PATTERNS = [
        r'iPhone',
        r'iPad',
        r'Android',
        r'Mobile',
        r'BlackBerry',
        r'Windows Phone'
    ]
    
    def parse_user_agent(self, user_agent: str) -> DeviceInfo:
        """Parse user agent string to extract device information."""
        if not user_agent:
            return DeviceInfo(
                browser="Unknown Browser",
                browser_version="",
                os="Unknown OS",
                os_version="",
                device_type="desktop",
                device_name="Unknown Device"
            )
        
        browser, browser_version = self._detect_browser(user_agent)
        os, os_version = self._detect_os(user_agent)
        device_type = self._detect_device_type(user_agent)
        device_name = self._generate_device_name(browser, os, device_type)
        
        return DeviceInfo(
            browser=browser,
            browser_version=browser_version,
            os=os,
            os_version=os_version,
            device_type=device_type,
            device_name=device_name
        )
    
    def _detect_browser(self, user_agent: str) -> tuple[str, str]:
        """Detect browser and version from user agent."""
        # Special case for Edge (must check before Chrome)
        if 'Edg/' in user_agent:
            match = re.search(self.BROWSER_PATTERNS['Edge'], user_agent)
            return 'Microsoft Edge', match.group(1) if match else ''
        
        # Special case for Opera (must check before Chrome)
        if 'Opera' in user_agent or 'OPR' in user_agent:
            match = re.search(self.BROWSER_PATTERNS['Opera'], user_agent)
            return 'Opera', match.group(1) if match else ''
        
        # Special case for Safari (must check after Chrome check)
        if 'Safari' in user_agent and 'Chrome' not in user_agent:
            match = re.search(self.BROWSER_PATTERNS['Safari'], user_agent)
            return 'Safari', match.group(1) if match else ''
        
        # Check other browsers
        for browser_name, pattern in self.BROWSER_PATTERNS.items():
            if browser_name in ['Edge', 'Opera', 'Safari']:
                continue  # Already handled above
            
            match = re.search(pattern, user_agent)
            if match:
                return browser_name, match.group(1)
        
        return 'Unknown Browser', ''
    
    def _detect_os(self, user_agent: str) -> tuple[str, str]:
        """Detect operating system and version from user agent."""
        # Check for mobile OS first
        if 'iPhone' in user_agent or 'iPad' in user_agent:
            pattern = self.OS_PATTERNS['iOS']['pattern']
            assert isinstance(pattern, str), "Pattern must be a string"
            match = re.search(pattern, user_agent)
            if match:
                version = match.group(1).replace('_', '.')
                return 'iOS', version
        if 'Android' in user_agent:
            pattern = self.OS_PATTERNS['Android']['pattern']
            assert isinstance(pattern, str), "Pattern must be a string"
            match = re.search(pattern, user_agent)
            if match:
                version = match.group(1)
                return 'Android', version
            return 'Android', ''
        # Check desktop OS
        if 'Windows' in user_agent:
            pattern = self.OS_PATTERNS['Windows']['pattern']
            assert isinstance(pattern, str), "Pattern must be a string"
            match = re.search(pattern, user_agent)
            if match:
                nt_version = match.group(1)
                versions = self.OS_PATTERNS['Windows']['versions']
                assert isinstance(versions, dict), "Versions must be a dict"
                windows_version = versions.get(nt_version, f'Windows NT {nt_version}')
                return 'Windows', windows_version
            return 'Windows', ''
        
        if 'Mac OS X' in user_agent:
            pattern = self.OS_PATTERNS['macOS']['pattern']
            assert isinstance(pattern, str), "Pattern must be a string"
            match = re.search(pattern, user_agent)
            if match:
                version = match.group(1).replace('_', '.')
                return 'macOS', version
            return 'macOS', ''
        
        if 'Linux' in user_agent:
            return 'Linux', ''
        
        return 'Unknown OS', ''
    def _detect_device_type(self, user_agent: str) -> str:
        """Detect device type from user agent."""
        user_agent_lower = user_agent.lower()
        
        # Check for mobile indicators
        for pattern in self.MOBILE_PATTERNS:
            if re.search(pattern, user_agent, re.IGNORECASE):
                if 'ipad' in user_agent_lower or 'tablet' in user_agent_lower:
                    return 'tablet'
                return 'mobile'
        
        return 'desktop'
    
    def _generate_device_name(self, browser: str, os: str, device_type: str) -> str:
        """Generate a user-friendly device name."""
        # Handle mobile devices
        if device_type == 'mobile':
            if 'iOS' in os:
                return f"iPhone • {browser}"
            elif 'Android' in os:
                return f"Android Phone • {browser}"
            else:
                return f"Mobile • {browser}"
        
        # Handle tablets
        if device_type == 'tablet':
            if 'iOS' in os:
                return f"iPad • {browser}"
            elif 'Android' in os:
                return f"Android Tablet • {browser}"
            else:
                return f"Tablet • {browser}"
        
        # Handle desktop devices
        if browser == 'Unknown Browser':
            return f"{os} Computer"
        
        # Simplify OS names for better readability
        os_simple = self._simplify_os_name(os)
        return f"{os_simple} • {browser}"
    
    def _simplify_os_name(self, os: str) -> str:
        """Simplify OS name for display."""
        if os.startswith('Windows'):
            if 'Windows 11/10' in os:
                return 'Windows'
            elif 'Windows' in os:
                return 'Windows'
        elif os.startswith('macOS'):
            return 'Mac'
        elif os.startswith('Linux'):
            return 'Linux'
        elif os.startswith('Android'):
            return 'Android'
        elif os.startswith('iOS'):
            return 'iOS'
        
        return os


# Global instance for easy access
device_parser = DeviceParser()


def parse_device_info(user_agent: str) -> DeviceInfo:
    """Parse user agent string and return device information."""
    return device_parser.parse_user_agent(user_agent)


def generate_device_info_string(user_agent: str) -> str:
    """Generate a user-friendly device info string."""
    device_info = parse_device_info(user_agent)
    return device_info.device_name
