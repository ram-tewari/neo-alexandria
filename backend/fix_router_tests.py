#!/usr/bin/env python3
"""
Fix recommendation router tests to use test_user fixture.

Replaces manual User creation with test_user fixture parameter.
"""

import re

def fix_tests():
    """Fix all router tests to use test_user fixture."""
    
    with open('tests/modules/recommendations/test_router.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Pattern 1: Add test_user parameter to function signatures that don't have it
    # Find functions that create User but don't have test_user parameter
    
    # List of functions that need test_user added
    functions_to_fix = [
        'test_get_recommendations_with_strategy_parameter',
        'test_get_recommendations_with_invalid_strategy',
        'test_get_recommendations_with_quality_filter',
        'test_get_recommendations_with_diversity_override',
        'test_get_recommendations_pagination',
        'test_get_recommendations_simple_success',
        'test_track_interaction_success',
        'test_track_interaction_with_rating',
        'test_track_interaction_invalid_type',
        'test_track_interaction_invalid_resource',
        'test_get_profile_success',
        'test_update_profile_success',
        'test_update_profile_with_research_domains',
        'test_update_profile_invalid_values',
        'test_submit_feedback_success',
        'test_submit_feedback_minimal',
        'test_refresh_recommendations_success',
    ]
    
    for func_name in functions_to_fix:
        # Pattern: def func_name(client, db_session):
        # Replace with: def func_name(client, db_session, test_user):
        pattern = rf'(def {func_name}\([^)]*db_session)(\))'
        replacement = r'\1, test_user\2'
        content = re.sub(pattern, replacement, content)
    
    # Pattern 2: Remove User creation blocks
    # Pattern: # Create test user\n    user = User(...)\n    db_session.add(user)\n    db_session.commit()
    user_creation_pattern = r'    # Create test user\n    user = User\([^)]+\)\n    db_session\.add\(user\)\n    db_session\.commit\(\)\n'
    content = re.sub(user_creation_pattern, '    # test_user is already created by fixture\n', content)
    
    # Pattern 3: Remove User creation in tests with resources
    # Pattern: # Create test user and resource\n    user = User(...)\n    db_session.add(user)\n    \n
    user_resource_pattern = r'    # Create test user and resource\n    user = User\([^)]+\)\n    db_session\.add\(user\)\n    \n'
    content = re.sub(user_resource_pattern, '    # test_user is already created by fixture\n    \n', content)
    
    with open('tests/modules/recommendations/test_router.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✓ Fixed all router tests!")
    print("  - Added test_user parameter to function signatures")
    print("  - Removed manual User creation")
    print("  - Tests now use shared test_user fixture")

if __name__ == '__main__':
    fix_tests()
