"""
Reddit OAuth2 Authentication System
Handles Reddit API authentication flows, token management, and session handling
"""

import praw
import prawcore
import json
import time
import webbrowser
import urllib.parse
from typing import Optional, Dict, Any, List, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import logging
import sqlite3
from pathlib import Path
import secrets
import hashlib
from http.server import HTTPServer, BaseHTTPRequestHandler
from threading import Thread, Event
import socket

from config.reddit_config import get_config, RedditCredentials

@dataclass
class AuthToken:
    """OAuth2 token container"""
    access_token: str
    refresh_token: Optional[str]
    token_type: str = "bearer"
    expires_at: Optional[datetime] = None
    scopes: List[str] = None
    username: Optional[str] = None
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.scopes is None:
            self.scopes = []
    
    def is_expired(self) -> bool:
        """Check if token is expired"""
        if self.expires_at is None:
            return False
        return datetime.now() >= self.expires_at
    
    def expires_in_seconds(self) -> Optional[int]:
        """Get seconds until token expires"""
        if self.expires_at is None:
            return None
        delta = self.expires_at - datetime.now()
        return max(0, int(delta.total_seconds()))
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage"""
        data = asdict(self)
        # Convert datetime objects to ISO strings
        if self.expires_at:
            data['expires_at'] = self.expires_at.isoformat()
        if self.created_at:
            data['created_at'] = self.created_at.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AuthToken':
        """Create from dictionary"""
        if 'expires_at' in data and data['expires_at']:
            data['expires_at'] = datetime.fromisoformat(data['expires_at'])
        if 'created_at' in data and data['created_at']:
            data['created_at'] = datetime.fromisoformat(data['created_at'])
        return cls(**data)

class AuthCallbackHandler(BaseHTTPRequestHandler):
    """HTTP handler for OAuth2 callback"""
    
    def do_GET(self):
        """Handle GET request from Reddit OAuth callback"""
        # Parse query parameters
        parsed_url = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(parsed_url.query)
        
        # Store callback data in server instance
        self.server.callback_code = params.get('code', [None])[0]
        self.server.callback_state = params.get('state', [None])[0]
        self.server.callback_error = params.get('error', [None])[0]
        
        # Send response to user
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        
        if self.server.callback_code:
            html = """
            <html><body>
            <h1>Authentication Successful!</h1>
            <p>You have successfully authenticated with Reddit. You can close this window.</p>
            <script>setTimeout(function(){ window.close(); }, 3000);</script>
            </body></html>
            """
        else:
            error = self.server.callback_error or "Unknown error"
            html = f"""
            <html><body>
            <h1>Authentication Failed</h1>
            <p>Error: {error}</p>
            <p>Please try again.</p>
            </body></html>
            """
        
        self.wfile.write(html.encode())
        
        # Signal that callback was received
        self.server.callback_received.set()
    
    def log_message(self, format, *args):
        """Suppress default HTTP server logging"""
        pass

class AuthCallbackServer(HTTPServer):
    """HTTP server for handling OAuth2 callbacks"""
    
    def __init__(self, host='localhost', port=8080):
        self.callback_code = None
        self.callback_state = None
        self.callback_error = None
        self.callback_received = Event()
        
        # Find available port if specified port is busy
        if port != 0:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            if sock.connect_ex((host, port)) == 0:
                sock.close()
                # Port is busy, find next available
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.bind((host, 0))
                port = sock.getsockname()[1]
                sock.close()
        
        super().__init__((host, port), AuthCallbackHandler)
        self.host = host
        self.port = port

class RedditAuthenticator:
    """Reddit OAuth2 authentication manager"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config = get_config()
        self.logger = logging.getLogger(__name__)
        
        # Token storage
        self.token_db_path = Path(config_path or "auth_tokens.db")
        self._init_token_storage()
        
        # OAuth state management
        self._oauth_states: Dict[str, datetime] = {}
    
    def _init_token_storage(self) -> None:
        """Initialize SQLite database for token storage"""
        try:
            with sqlite3.connect(self.token_db_path) as conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS auth_tokens (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT UNIQUE NOT NULL,
                        access_token TEXT NOT NULL,
                        refresh_token TEXT,
                        token_type TEXT DEFAULT 'bearer',
                        expires_at TEXT,
                        scopes TEXT,
                        created_at TEXT NOT NULL,
                        updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                conn.execute("""
                    CREATE INDEX IF NOT EXISTS idx_username ON auth_tokens(username)
                """)
                
                conn.execute("""
                    CREATE INDEX IF NOT EXISTS idx_expires_at ON auth_tokens(expires_at)
                """)
                
                conn.commit()
                self.logger.info("Token storage initialized")
                
        except Exception as e:
            self.logger.error(f"Failed to initialize token storage: {e}")
            raise
    
    def generate_oauth_url(self, scopes: Optional[List[str]] = None, 
                          duration: str = "permanent") -> Tuple[str, str]:
        """
        Generate Reddit OAuth2 authorization URL
        
        Args:
            scopes: List of permission scopes to request
            duration: Token duration ("temporary" or "permanent")
            
        Returns:
            Tuple of (authorization_url, state)
        """
        if scopes is None:
            scopes = self.config.credentials.scopes
        
        # Generate secure random state
        state = secrets.token_urlsafe(32)
        self._oauth_states[state] = datetime.now() + timedelta(minutes=10)
        
        # Create Reddit instance for OAuth
        reddit = praw.Reddit(
            client_id=self.config.credentials.client_id,
            client_secret=self.config.credentials.client_secret,
            redirect_uri=self.config.credentials.redirect_uri,
            user_agent=self.config.credentials.user_agent
        )
        
        try:
            auth_url = reddit.auth.url(scopes, state, duration)
            self.logger.info(f"Generated OAuth URL for scopes: {scopes}")
            return auth_url, state
            
        except Exception as e:
            self.logger.error(f"Failed to generate OAuth URL: {e}")
            raise
    
    def authenticate_web_flow(self, scopes: Optional[List[str]] = None,
                            auto_open_browser: bool = True,
                            timeout: int = 300) -> AuthToken:
        """
        Perform web-based OAuth2 authentication flow
        
        Args:
            scopes: Permission scopes to request
            auto_open_browser: Whether to automatically open browser
            timeout: Timeout in seconds for user authorization
            
        Returns:
            AuthToken object with access credentials
        """
        # Generate authorization URL
        auth_url, state = self.generate_oauth_url(scopes)
        
        # Start callback server
        callback_server = AuthCallbackServer()
        server_thread = Thread(target=callback_server.serve_forever, daemon=True)
        server_thread.start()
        
        try:
            # Update redirect URI to match server
            redirect_uri = f"http://{callback_server.host}:{callback_server.port}/callback"
            
            self.logger.info(f"Starting OAuth flow with redirect URI: {redirect_uri}")
            self.logger.info(f"Authorization URL: {auth_url}")
            
            # Open browser if requested
            if auto_open_browser:
                webbrowser.open(auth_url)
                print(f"Opening browser for Reddit authorization...")
            else:
                print(f"Please visit this URL to authorize the application:")
                print(f"{auth_url}")
            
            # Wait for callback
            print(f"Waiting for authorization callback (timeout: {timeout}s)...")
            if not callback_server.callback_received.wait(timeout):
                raise TimeoutError(f"Authentication timeout after {timeout} seconds")
            
            # Validate callback
            if callback_server.callback_error:
                raise ValueError(f"Authentication error: {callback_server.callback_error}")
            
            if not callback_server.callback_code:
                raise ValueError("No authorization code received")
            
            if callback_server.callback_state != state:
                raise ValueError("Invalid OAuth state - possible CSRF attack")
            
            # Exchange code for token
            return self._exchange_code_for_token(callback_server.callback_code, redirect_uri)
            
        finally:
            callback_server.shutdown()
            callback_server.server_close()
    
    def _exchange_code_for_token(self, code: str, redirect_uri: str) -> AuthToken:
        """Exchange authorization code for access token"""
        try:
            # Create Reddit instance
            reddit = praw.Reddit(
                client_id=self.config.credentials.client_id,
                client_secret=self.config.credentials.client_secret,
                redirect_uri=redirect_uri,
                user_agent=self.config.credentials.user_agent
            )
            
            # Exchange code for token
            refresh_token = reddit.auth.authorize(code)
            
            # Get user info
            user = reddit.user.me()
            username = user.name
            
            # Create token object
            token = AuthToken(
                access_token=reddit.config.access_token,
                refresh_token=refresh_token,
                username=username,
                scopes=list(reddit.auth.scopes()),
                expires_at=datetime.now() + timedelta(hours=1)  # Reddit tokens expire in 1 hour
            )
            
            # Store token
            self.store_token(token)
            
            self.logger.info(f"Successfully authenticated user: {username}")
            return token
            
        except Exception as e:
            self.logger.error(f"Failed to exchange code for token: {e}")
            raise
    
    def authenticate_password_flow(self, username: str, password: str) -> AuthToken:
        """
        Authenticate using username/password (script app only)
        
        Args:
            username: Reddit username
            password: Reddit password
            
        Returns:
            AuthToken object with access credentials
        """
        try:
            reddit = praw.Reddit(
                client_id=self.config.credentials.client_id,
                client_secret=self.config.credentials.client_secret,
                username=username,
                password=password,
                user_agent=self.config.credentials.user_agent
            )
            
            # Test authentication by getting user info
            user = reddit.user.me()
            
            # Create token object (password flow doesn't use OAuth tokens)
            token = AuthToken(
                access_token="password_flow",
                refresh_token=None,
                username=user.name,
                scopes=["*"],  # Script apps have all permissions
                expires_at=None  # Password flow doesn't expire
            )
            
            # Store token
            self.store_token(token)
            
            self.logger.info(f"Successfully authenticated user: {user.name}")
            return token
            
        except Exception as e:
            self.logger.error(f"Password authentication failed: {e}")
            raise
    
    def refresh_token(self, token: AuthToken) -> AuthToken:
        """
        Refresh an expired OAuth token
        
        Args:
            token: Expired AuthToken to refresh
            
        Returns:
            New AuthToken with refreshed credentials
        """
        if not token.refresh_token:
            raise ValueError("No refresh token available")
        
        try:
            reddit = praw.Reddit(
                client_id=self.config.credentials.client_id,
                client_secret=self.config.credentials.client_secret,
                refresh_token=token.refresh_token,
                user_agent=self.config.credentials.user_agent
            )
            
            # Refresh the token
            reddit.auth.refresh()
            
            # Create new token object
            new_token = AuthToken(
                access_token=reddit.config.access_token,
                refresh_token=token.refresh_token,  # Keep existing refresh token
                username=token.username,
                scopes=token.scopes,
                expires_at=datetime.now() + timedelta(hours=1)
            )
            
            # Update stored token
            self.store_token(new_token)
            
            self.logger.info(f"Successfully refreshed token for user: {token.username}")
            return new_token
            
        except Exception as e:
            self.logger.error(f"Failed to refresh token: {e}")
            raise
    
    def store_token(self, token: AuthToken) -> None:
        """Store auth token in database"""
        try:
            with sqlite3.connect(self.token_db_path) as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO auth_tokens 
                    (username, access_token, refresh_token, token_type, expires_at, scopes, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                """, (
                    token.username,
                    token.access_token,
                    token.refresh_token,
                    token.token_type,
                    token.expires_at.isoformat() if token.expires_at else None,
                    json.dumps(token.scopes),
                    token.created_at.isoformat()
                ))
                conn.commit()
                
            self.logger.info(f"Stored token for user: {token.username}")
            
        except Exception as e:
            self.logger.error(f"Failed to store token: {e}")
            raise
    
    def load_token(self, username: str) -> Optional[AuthToken]:
        """Load auth token from database"""
        try:
            with sqlite3.connect(self.token_db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute("""
                    SELECT * FROM auth_tokens WHERE username = ?
                """, (username,))
                
                row = cursor.fetchone()
                if not row:
                    return None
                
                # Convert row to AuthToken
                token_data = {
                    'access_token': row['access_token'],
                    'refresh_token': row['refresh_token'],
                    'token_type': row['token_type'] or 'bearer',
                    'expires_at': datetime.fromisoformat(row['expires_at']) if row['expires_at'] else None,
                    'scopes': json.loads(row['scopes']) if row['scopes'] else [],
                    'username': row['username'],
                    'created_at': datetime.fromisoformat(row['created_at'])
                }
                
                return AuthToken(**token_data)
                
        except Exception as e:
            self.logger.error(f"Failed to load token for {username}: {e}")
            return None
    
    def delete_token(self, username: str) -> bool:
        """Delete auth token from database"""
        try:
            with sqlite3.connect(self.token_db_path) as conn:
                cursor = conn.execute("""
                    DELETE FROM auth_tokens WHERE username = ?
                """, (username,))
                conn.commit()
                
                deleted = cursor.rowcount > 0
                if deleted:
                    self.logger.info(f"Deleted token for user: {username}")
                
                return deleted
                
        except Exception as e:
            self.logger.error(f"Failed to delete token for {username}: {e}")
            return False
    
    def list_stored_users(self) -> List[str]:
        """Get list of users with stored tokens"""
        try:
            with sqlite3.connect(self.token_db_path) as conn:
                cursor = conn.execute("SELECT username FROM auth_tokens ORDER BY updated_at DESC")
                return [row[0] for row in cursor.fetchall()]
                
        except Exception as e:
            self.logger.error(f"Failed to list stored users: {e}")
            return []
    
    def validate_token(self, token: AuthToken) -> bool:
        """Validate if token is still valid"""
        try:
            if token.is_expired() and token.refresh_token:
                # Try to refresh if expired
                refreshed_token = self.refresh_token(token)
                return True
            elif token.is_expired():
                return False
            
            # Test token by making API call
            if token.access_token == "password_flow":
                # Password flow - can't validate without creating Reddit instance
                return True
            else:
                # OAuth flow - test with API call
                reddit = praw.Reddit(
                    client_id=self.config.credentials.client_id,
                    client_secret=self.config.credentials.client_secret,
                    access_token=token.access_token,
                    user_agent=self.config.credentials.user_agent
                )
                
                # Simple API test
                reddit.user.me()
                return True
                
        except Exception as e:
            self.logger.warning(f"Token validation failed: {e}")
            return False
    
    def cleanup_expired_tokens(self) -> int:
        """Remove expired tokens from storage"""
        try:
            with sqlite3.connect(self.token_db_path) as conn:
                cursor = conn.execute("""
                    DELETE FROM auth_tokens 
                    WHERE expires_at IS NOT NULL 
                    AND datetime(expires_at) < datetime('now')
                    AND refresh_token IS NULL
                """)
                conn.commit()
                
                count = cursor.rowcount
                if count > 0:
                    self.logger.info(f"Cleaned up {count} expired tokens")
                
                return count
                
        except Exception as e:
            self.logger.error(f"Failed to cleanup expired tokens: {e}")
            return 0


def main():
    """CLI interface for authentication testing"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Reddit Authentication Tool")
    parser.add_argument("--web", action="store_true", help="Use web OAuth flow")
    parser.add_argument("--username", help="Reddit username for password flow")
    parser.add_argument("--password", help="Reddit password for password flow")
    parser.add_argument("--list", action="store_true", help="List stored users")
    parser.add_argument("--validate", help="Validate token for user")
    parser.add_argument("--delete", help="Delete token for user")
    
    args = parser.parse_args()
    
    # Setup logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    try:
        auth = RedditAuthenticator()
        
        if args.list:
            users = auth.list_stored_users()
            print(f"Stored users: {users}")
            
        elif args.validate:
            token = auth.load_token(args.validate)
            if token:
                valid = auth.validate_token(token)
                print(f"Token for {args.validate}: {'Valid' if valid else 'Invalid'}")
            else:
                print(f"No token found for {args.validate}")
                
        elif args.delete:
            deleted = auth.delete_token(args.delete)
            print(f"Token for {args.delete}: {'Deleted' if deleted else 'Not found'}")
            
        elif args.web:
            print("Starting web OAuth flow...")
            token = auth.authenticate_web_flow()
            print(f"Successfully authenticated: {token.username}")
            
        elif args.username and args.password:
            print("Authenticating with username/password...")
            token = auth.authenticate_password_flow(args.username, args.password)
            print(f"Successfully authenticated: {token.username}")
            
        else:
            print("No action specified. Use --help for options.")
            
    except Exception as e:
        print(f"Error: {e}")
        exit(1)


if __name__ == "__main__":
    main()