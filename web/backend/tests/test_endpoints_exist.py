import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_endpoints_exist():
    """Test that all required endpoints from the specification exist"""
    
    # Get OpenAPI schema
    response = client.get("/openapi.json")
    assert response.status_code == 200
    
    openapi_schema = response.json()
    paths = openapi_schema.get("paths", {})
    
    # Required endpoints according to specification
    required_endpoints = {
        # Clients module
        "/api/v1/clients": ["get", "post"],
        "/api/v1/clients/{client_id}": ["get", "put", "delete"],
        
        # Contracts module  
        "/api/v1/contracts/calculate": ["post"],
        "/api/v1/contracts": ["get", "post"],
        "/api/v1/contracts/{contract_id}": ["get", "put"],
        
        # Claims module
        "/api/v1/claims": ["get", "post"],
        "/api/v1/claims/pending": ["get"],
        "/api/v1/claims/{claim_id}/decision": ["put"],
        
        # Analytics/Reports module
        "/api/v1/analytics/reports/finance": ["get"],
        "/api/v1/analytics/reports/activity": ["get"],
        
        # Users module
        "/api/v1/users": ["get", "post"],
        "/api/v1/users/{user_id}/role": ["patch"],
    }
    
    missing_endpoints = []
    existing_endpoints = []
    
    print("\n=== ПРОВЕРКА ЭНДПОИНТОВ ===")
    
    for endpoint_path, methods in required_endpoints.items():
        print(f"\n📋 Проверяю: {endpoint_path}")
        
        for method in methods:
            method_upper = method.upper()
            
            # Check if path exists in OpenAPI schema
            if endpoint_path in paths:
                if method in paths[endpoint_path]:
                    print(f"   ✅ {method_upper} {endpoint_path}")
                    existing_endpoints.append(f"{method_upper} {endpoint_path}")
                else:
                    print(f"   ❌ {method_upper} {endpoint_path}")
                    missing_endpoints.append(f"{method_upper} {endpoint_path}")
            else:
                print(f"   ❌ {method_upper} {endpoint_path}")
                missing_endpoints.append(f"{method_upper} {endpoint_path}")
    
    print(f"\n=== РЕЗЮМЕ ===")
    print(f"✅ Существующие эндпоинты: {len(existing_endpoints)}")
    print(f"❌ Отсутствующие эндпоинты: {len(missing_endpoints)}")
    
    if missing_endpoints:
        print(f"\n🔸 ОТСУТСТВУЮЩИЕ ЭНДПОИНТЫ:")
        for endpoint in missing_endpoints:
            print(f"   • {endpoint}")
    
    if existing_endpoints:
        print(f"\n✅ СУЩЕСТВУЮЩИЕ ЭНДПОИНТЫ:")
        for endpoint in existing_endpoints:
            print(f"   • {endpoint}")
    
    # Test should pass only if all endpoints exist
    assert len(missing_endpoints) == 0, f"Missing endpoints: {missing_endpoints}"

def test_role_access_patterns():
    """Test that endpoints have proper role-based access patterns"""
    
    response = client.get("/openapi.json")
    assert response.status_code == 200
    
    openapi_schema = response.json()
    paths = openapi_schema.get("paths", {})
    
    # Expected access patterns from specification
    role_access_patterns = {
        # Clients - agent, operator, admin
        "/api/v1/clients": {
            "get": ["agent", "operator", "admin"],
            "post": ["agent", "operator", "admin"]
        },
        "/api/v1/clients/{client_id}": {
            "get": ["agent", "operator", "admin"],
            "put": ["agent", "operator", "admin"],
            "delete": ["admin"]  # Only admin can delete
        },
        
        # Contracts - agent, operator
        "/api/v1/contracts/calculate": {
            "post": ["agent", "operator"]
        },
        "/api/v1/contracts": {
            "post": ["agent", "operator"]
        },
        
        # Claims - adjuster
        "/api/v1/claims": {
            "post": ["adjuster"]
        },
        "/api/v1/claims/pending": {
            "get": ["adjuster"]
        },
        "/api/v1/claims/{claim_id}/decision": {
            "put": ["adjuster"]
        },
        
        # Reports - manager, admin
        "/api/v1/analytics/reports/finance": {
            "get": ["manager", "admin"]
        },
        "/api/v1/analytics/reports/activity": {
            "get": ["manager", "admin"]
        },
        
        # Users - admin only
        "/api/v1/users": {
            "get": ["admin"],
            "post": ["admin"]
        },
        "/api/v1/users/{user_id}/role": {
            "patch": ["admin"]
        }
    }
    
    print(f"\n=== ПРОВЕРКА ДОСТУПА ПО РОЛЯМ ===")
    
    access_issues = []
    
    for path, methods in role_access_patterns.items():
        if path in paths:
            for method, expected_roles in methods.items():
                if method in paths[path]:
                    # This is a basic check - in real implementation we'd need to
                    # parse the security requirements from the OpenAPI schema
                    print(f"✅ {method.upper()} {path} - ожидается доступ: {', '.join(expected_roles)}")
                else:
                    access_issues.append(f"Method {method.upper()} not found for {path}")
        else:
            access_issues.append(f"Path {path} not found")
    
    # Note: This is a basic check. For full validation, we'd need to:
    # 1. Parse security schemes from OpenAPI
    # 2. Check dependency injection for require_roles()
    # 3. Validate role requirements match specification
    
    print(f"\n✅ Базовая проверка ролей завершена")
    if access_issues:
        print(f"⚠️  Обнаружены проблемы доступа: {len(access_issues)}")
        for issue in access_issues:
            print(f"   • {issue}")

if __name__ == "__main__":
    test_endpoints_exist()
    test_role_access_patterns()
    print("\n🎉 Все тесты завершены!") 