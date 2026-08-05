"""
Atlas API Authentication & Security Module
Provides API key validation, rate limiting, and role-based access control.
"""
import os
import secrets
import hashlib
import time
from functools import wraps
from typing import Optional, List, Dict, Callable
from dotenv import load_dotenv
from fastapi import Header, HTTPException, Request, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

load_dotenv()

# --- Configuration ---
ATLAS_API_KEY = os.getenv("ATLAS_API_KEY", "")
ATLAS_READ_ONLY_KEY = os.getenv("ATLAS_READ_ONLY_KEY", "")
RATE_LIMIT_REQUESTS = int(os.getenv("RATE_LIMIT_REQUESTS", "60"))  # per minute
RATE_LIMIT_WINDOW = int(os.getenv("RATE_LIMIT_WINDOW", "60"))  # seconds

# Security scheme for OpenAPI docs
security_scheme = HTTPBearer(
    scheme_name="AtlasAPIKey",
    description="Enter your Atlas API key. Format: Bearer your-api-key",
    auto_error=False,
)


# --- In-Memory Rate Limiting Store ---
# Structure: {client_ip: [(timestamp1), (timestamp2), ...]}
_rate_limit_store: Dict[str, List[float]] = {}


def _get_client_ip(request: Request) -> str:
    """Extract client IP from request, handling proxies."""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def _check_rate_limit(client_ip: str) -> bool:
    """Check if client IP has exceeded rate limit. Returns True if allowed."""
    now = time.time()
    window_start = now - RATE_LIMIT_WINDOW

    # Get existing requests for this IP
    requests = _rate_limit_store.get(client_ip, [])
    # Filter to only requests in current window
    requests = [t for t in requests if t > window_start]

    if len(requests) >= RATE_LIMIT_REQUESTS:
        _rate_limit_store[client_ip] = requests
        return False

    requests.append(now)
    _rate_limit_store[client_ip] = requests
    return True


def _hash_key(key: str) -> str:
    """Hash an API key for safe comparison (timing-attack resistant)."""
    return hashlib.sha256(key.encode()).hexdigest()


def _constant_time_compare(a: str, b: str) -> bool:
    """Constant-time string comparison to prevent timing attacks."""
    if len(a) != len(b):
        return False
    result = 0
    for x, y in zip(a, b):
        result |= ord(x) ^ ord(y)
    return result == 0


def _validate_key(provided_key: str, expected_key: str) -> bool:
    """Validate an API key securely."""
    if not expected_key or not provided_key:
        return False
    return _constant_time_compare(
        _hash_key(provided_key),
        _hash_key(expected_key)
    )


# --- Dependency Functions ---

def require_auth(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_scheme),
) -> Dict[str, str]:
    """
    Validate API key from Authorization header.
    Supports: Bearer <key> or raw API key in X-API-Key header.
    Returns user context dict.
    """
    # Check rate limit first
    client_ip = _get_client_ip(request)
    if not _check_rate_limit(client_ip):
        raise HTTPException(
            status_code=429,
            detail={
                "error": "Rate limit exceeded",
                "limit": RATE_LIMIT_REQUESTS,
                "window_seconds": RATE_LIMIT_WINDOW,
                "retry_after": RATE_LIMIT_WINDOW,
            },
        )

    # Extract key from Authorization header (Bearer) or X-API-Key
    api_key = None

    if credentials:
        api_key = credentials.credentials
    else:
        api_key = request.headers.get("X-API-Key")

    if not api_key:
        raise HTTPException(
            status_code=401,
            detail={
                "error": "Authentication required",
                "message": "Provide API key via 'Authorization: Bearer <key>' or 'X-API-Key: <key>' header",
                "docs": "https://github.com/omaryouseef-a11y/atlas-ai#api-authentication",
            },
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Check full-access key
    if _validate_key(api_key, ATLAS_API_KEY):
        return {"role": "admin", "client_ip": client_ip, "access": "full"}

    # Check read-only key
    if _validate_key(api_key, ATLAS_READ_ONLY_KEY):
        return {"role": "readonly", "client_ip": client_ip, "access": "read"}

    # Invalid key
    raise HTTPException(
        status_code=403,
        detail={
            "error": "Invalid API key",
            "message": "The provided API key is not recognized",
        },
    )


def require_admin(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_scheme),
) -> Dict[str, str]:
    """Require full admin access (write operations)."""
    user = require_auth(request, credentials)
    if user["role"] != "admin":
        raise HTTPException(
            status_code=403,
            detail={
                "error": "Insufficient permissions",
                "message": "This endpoint requires admin access. Read-only keys are not allowed.",
                "your_role": user["role"],
            },
        )
    return user


def require_read(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_scheme),
) -> Dict[str, str]:
    """Require any valid API key (read operations)."""
    return require_auth(request, credentials)


# --- Key Generation Utilities ---

def generate_api_key(prefix: str = "atlas") -> str:
    """Generate a secure random API key."""
    token = secrets.token_urlsafe(32)
    return f"{prefix}_{token}"


def setup_env_file(env_path: str = ".env") -> None:
    """
    Generate API keys and write them to .env file if not present.
    Safe to run — won't overwrite existing keys.
    """
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Check if keys already exist
        has_admin = "ATLAS_API_KEY=" in content and "ATLAS_API_KEY=\n" not in content
        has_readonly = "ATLAS_READ_ONLY_KEY=" in content and "ATLAS_READ_ONLY_KEY=\n" not in content

        if has_admin and has_readonly:
            print("[Auth] API keys already configured.")
            return

        lines = content.splitlines()
        new_lines = []
        admin_key = None
        readonly_key = None

        for line in lines:
            if line.startswith("ATLAS_API_KEY=") and not has_admin:
                admin_key = generate_api_key("atlas_admin")
                new_lines.append(f"ATLAS_API_KEY={admin_key}")
            elif line.startswith("ATLAS_READ_ONLY_KEY=") and not has_readonly:
                readonly_key = generate_api_key("atlas_read")
                new_lines.append(f"ATLAS_READ_ONLY_KEY={readonly_key}")
            else:
                new_lines.append(line)

        # If keys weren't in the file at all, append them
        if not has_admin and admin_key is None:
            admin_key = generate_api_key("atlas_admin")
            new_lines.append(f"ATLAS_API_KEY={admin_key}")
        if not has_readonly and readonly_key is None:
            readonly_key = generate_api_key("atlas_read")
            new_lines.append(f"ATLAS_READ_ONLY_KEY={readonly_key}")

        with open(env_path, "w", encoding="utf-8") as f:
            f.write("\n".join(new_lines) + "\n")

        print(f"[Auth] Generated new API keys in {env_path}")
        print(f"  Admin Key:    {admin_key or '(existing)'}")
        print(f"  Read-Only Key: {readonly_key or '(existing)'}")
        print("[Auth] KEEP THESE SECRET — never commit this file!")
    else:
        # Create new .env file
        admin_key = generate_api_key("atlas_admin")
        readonly_key = generate_api_key("atlas_read")
        with open(env_path, "w", encoding="utf-8") as f:
            f.write(f"ATLAS_API_KEY={admin_key}\n")
            f.write(f"ATLAS_READ_ONLY_KEY={readonly_key}\n")
        print(f"[Auth] Created new {env_path} with generated API keys")
        print(f"  Admin Key:    {admin_key}")
        print(f"  Read-Only Key: {readonly_key}")
        print("[Auth] KEEP THESE SECRET — never commit this file!")


# --- Middleware for Request Logging ---

class AuthLogger:
    """Simple request logger for authenticated endpoints."""

    @staticmethod
    def log(request: Request, user: Dict[str, str], endpoint: str, status: int = 200):
        client_ip = user.get("client_ip", "unknown")
        role = user.get("role", "unknown")
        print(f"[API] {client_ip} | {role} | {request.method} {endpoint} | {status}")


if __name__ == "__main__":
    # Generate keys when running this file directly
    setup_env_file()
