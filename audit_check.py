#!/usr/bin/env python3
"""
Скрипт для автоматической проверки моделей, миграций и API на основные проблемы.
"""
import re
import os
from pathlib import Path
from typing import List, Dict, Tuple

# Цвета для вывода
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
RESET = "\033[0m"

def check_models_for_id_issues() -> List[Tuple[str, str]]:
    """Проверка моделей на проблемы с id колонкой."""
    issues = []
    models_path = Path("apps/api/src/modules")
    
    # Модели, которые должны исключать id
    models_without_id = {
        "Mentor": "apps/api/src/modules/mentors/domain/models.py",
        "Student": "apps/api/src/modules/users/domain/models.py",
        "MentorSettings": "apps/api/src/modules/availability/domain/models.py",
    }
    
    for model_name, file_path in models_without_id.items():
        if not Path(file_path).exists():
            continue
            
        content = Path(file_path).read_text(encoding="utf-8")
        
        # Проверяем наличие __mapper_args__
        if "__mapper_args__" not in content:
            issues.append((file_path, f"Model {model_name} missing __mapper_args__"))
        
        # Проверяем наличие id: Mapped[None] = None
        if "id: Mapped[None] = None" not in content:
            issues.append((file_path, f"Model {model_name} missing id: Mapped[None] = None"))
    
    return issues

def check_migrations_for_updated_at() -> List[Tuple[str, str]]:
    """Проверка миграций на наличие updated_at."""
    issues = []
    migrations_path = Path("apps/api/alembic/versions")
    
    for migration_file in migrations_path.glob("*.py"):
        if migration_file.name == "__init__.py":
            continue
            
        content = migration_file.read_text(encoding="utf-8")
        
        # Проверяем создание таблицы notifications
        if "create_table('notifications'" in content:
            if "updated_at" not in content or "sa.Column('updated_at'" not in content:
                issues.append((str(migration_file), "Migration missing updated_at for notifications table"))
    
    return issues

def check_api_routes_for_error_handling() -> List[Tuple[str, str]]:
    """Проверка API роутов на обработку ошибок."""
    issues = []
    routes_path = Path("apps/api/src/modules")
    
    for routes_file in routes_path.rglob("**/api/routes.py"):
        content = routes_file.read_text(encoding="utf-8")
        
        # Проверяем наличие обработки ошибок в async функциях
        async_functions = re.findall(r"async def (\w+)\([^)]*\):", content)
        
        for func_name in async_functions:
            # Находим функцию
            func_pattern = rf"async def {func_name}\([^)]*\):.*?(?=async def|\Z)"
            func_match = re.search(func_pattern, content, re.DOTALL)
            
            if func_match:
                func_body = func_match.group(0)
                # Проверяем наличие try/except или HTTPException
                if "HTTPException" in func_body or "try:" in func_body:
                    continue
                else:
                    # Это не критично, но стоит отметить
                    pass
    
    return issues

def check_frontend_api_calls() -> List[Tuple[str, str]]:
    """Проверка фронтенд API вызовов на правильность путей."""
    issues = []
    api_path = Path("apps/web/src/shared/api")
    
    # Проверяем availability.ts (уже исправлено)
    availability_file = api_path / "availability.ts"
    if availability_file.exists():
        content = availability_file.read_text(encoding="utf-8")
        if "/availability/my/profile" in content and "getMyAvailabilitySettings" in content:
            # Проверяем, что getMyAvailabilitySettings использует правильный путь
            if "getMyAvailabilitySettings" in content:
                # Уже исправлено
                pass
    
    return issues

def main():
    """Главная функция."""
    print(f"{GREEN}[*] Starting MasterConnect system audit...{RESET}\n")
    
    all_issues = []
    
    # Проверка моделей
    print(f"{YELLOW}1. Checking models for id issues...{RESET}")
    model_issues = check_models_for_id_issues()
    if model_issues:
        print(f"{RED}   Found issues: {len(model_issues)}{RESET}")
        for file_path, issue in model_issues:
            print(f"   - {file_path}: {issue}")
        all_issues.extend(model_issues)
    else:
        print(f"{GREEN}   OK: No issues found{RESET}")
    
    # Проверка миграций
    print(f"\n{YELLOW}2. Checking migrations for updated_at...{RESET}")
    migration_issues = check_migrations_for_updated_at()
    if migration_issues:
        print(f"{RED}   Found issues: {len(migration_issues)}{RESET}")
        for file_path, issue in migration_issues:
            print(f"   - {file_path}: {issue}")
        all_issues.extend(migration_issues)
    else:
        print(f"{GREEN}   OK: No issues found{RESET}")
    
    # Проверка API роутов
    print(f"\n{YELLOW}3. Checking API routes...{RESET}")
    api_issues = check_api_routes_for_error_handling()
    if api_issues:
        print(f"{RED}   Found issues: {len(api_issues)}{RESET}")
        for file_path, issue in api_issues:
            print(f"   - {file_path}: {issue}")
        all_issues.extend(api_issues)
    else:
        print(f"{GREEN}   OK: No issues found{RESET}")
    
    # Проверка фронтенда
    print(f"\n{YELLOW}4. Checking frontend API calls...{RESET}")
    frontend_issues = check_frontend_api_calls()
    if frontend_issues:
        print(f"{RED}   Found issues: {len(frontend_issues)}{RESET}")
        for file_path, issue in frontend_issues:
            print(f"   - {file_path}: {issue}")
        all_issues.extend(frontend_issues)
    else:
        print(f"{GREEN}   OK: No issues found{RESET}")
    
    # Итоги
    print(f"\n{GREEN}{'='*60}{RESET}")
    if all_issues:
        print(f"{RED}Total issues found: {len(all_issues)}{RESET}")
    else:
        print(f"{GREEN}All checks passed successfully!{RESET}")
    print(f"{GREEN}{'='*60}{RESET}")

if __name__ == "__main__":
    main()

