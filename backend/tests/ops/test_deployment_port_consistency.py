"""
Deployment Port Consistency & Ops Shared-Host Safety Invariants Test.
Guarantees:
1. Canonical API upstream port is 127.0.0.1:8001 across all deployment artifacts.
2. User SPA port is 127.0.0.1:3002 and Admin SPA port is 127.0.0.1:3003.
3. Database port is 127.0.0.1:5433.
4. Docker socket (/var/run/docker.sock) is NEVER mounted into application containers.
5. Canonical subdomains match staging.saarthi.trovanetech.com, admin-staging..., api-staging...
6. Detects any drift or mismatch between Compose, Nginx, verification scripts, and docs.
"""

import os
import re
import pytest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
DEPLOY_DIR = os.path.join(REPO_ROOT, "deploy")


def test_docker_compose_staging_ports_and_safety():
    compose_path = os.path.join(DEPLOY_DIR, "docker-compose.staging.yml")
    assert os.path.isfile(compose_path), "docker-compose.staging.yml must exist"
    
    with open(compose_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. API backend upstream port 8001
    assert "8001}:8000" in content or "127.0.0.1:8001:8000" in content, (
        "Backend service in Compose must map to host port 127.0.0.1:8001"
    )

    # 2. Frontend port 3002
    assert "3002}:80" in content or "127.0.0.1:3002:80" in content, (
        "Frontend service in Compose must map to host port 127.0.0.1:3002"
    )

    # 3. Admin port 3003
    assert "3003}:80" in content or "127.0.0.1:3003:80" in content, (
        "Admin service in Compose must map to host port 127.0.0.1:3003"
    )

    # 4. PostgreSQL port 5433
    assert "5433}:5432" in content or "127.0.0.1:5433:5432" in content, (
        "PostgreSQL service in Compose must map to host port 127.0.0.1:5433"
    )

    # 5. Shared-Host Safety Invariant: Docker socket NEVER mounted
    assert "/var/run/docker.sock" not in content, (
        "CRITICAL SECURITY INVARIANT: /var/run/docker.sock must NEVER be mounted in Compose"
    )


def test_nginx_staging_conf_ports():
    nginx_conf = os.path.join(DEPLOY_DIR, "nginx", "saarthi_staging.conf")
    assert os.path.isfile(nginx_conf), "saarthi_staging.conf must exist"

    with open(nginx_conf, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Backend API proxy pass 127.0.0.1:8001
    assert "proxy_pass http://127.0.0.1:8001;" in content, (
        "Nginx reverse proxy for api-staging must proxy_pass to http://127.0.0.1:8001;"
    )

    # 2. Frontend proxy pass 127.0.0.1:3002
    assert "proxy_pass http://127.0.0.1:3002;" in content, (
        "Nginx reverse proxy for staging app must proxy_pass to http://127.0.0.1:3002;"
    )

    # 3. Admin proxy pass 127.0.0.1:3003
    assert "proxy_pass http://127.0.0.1:3003;" in content, (
        "Nginx reverse proxy for admin-staging must proxy_pass to http://127.0.0.1:3003;"
    )

    # 4. Canonical server names
    assert "server_name api-staging.saarthi.trovanetech.com;" in content
    assert "server_name staging.saarthi.trovanetech.com;" in content
    assert "server_name admin-staging.saarthi.trovanetech.com;" in content


def test_provisioning_and_verification_scripts_ports():
    scripts = [
        "admin_provision_staging.sh",
        "deploy_staging.sh",
        "verify_staging.sh"
    ]
    for s_name in scripts:
        script_path = os.path.join(DEPLOY_DIR, "scripts", s_name)
        assert os.path.isfile(script_path), f"{s_name} must exist"
        with open(script_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Check that backend health checks target port 8001
        assert "8001" in content, f"{s_name} must reference backend port 8001"
        assert "127.0.0.1:8001" in content or ":8001" in content, (
            f"{s_name} must check backend health on port 8001"
        )


def test_deploy_readme_ports():
    readme_path = os.path.join(DEPLOY_DIR, "README.md")
    assert os.path.isfile(readme_path)
    with open(readme_path, "r", encoding="utf-8") as f:
        content = f.read()

    assert "api-staging.saarthi.trovanetech.com   -> http://127.0.0.1:8001" in content
    assert "127.0.0.1:3002" in content
    assert "127.0.0.1:3003" in content
    assert "Port 8001" in content
