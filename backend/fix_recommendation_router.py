#!/usr/bin/env python3
"""
Fix recommendation router to use dependency injection properly.

Changes all endpoints to use user_id as a dependency parameter instead of
calling _get_current_user_id(db) directly, which allows test fixtures to
properly override authentication.
"""


def fix_router():
    """Fix all endpoints in the recommendation router."""
    
    with open('app/modules/recommendations/router.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Fix patterns: Add user_id parameter and remove manual call
    fixes = [
        # get_profile endpoint
        {
            'old': '''@recommendations_router.get("/profile", response_model=ProfileResponse)
async def get_profile(
    db: Session = Depends(get_sync_db),
):
    """
    Get user profile settings.
    
    Args:
        db: Database session
        
    Returns:
        ProfileResponse with user profile settings
    """
    try:
        # Get current user
        user_id = _get_current_user_id(db)''',
            'new': '''@recommendations_router.get("/profile", response_model=ProfileResponse)
async def get_profile(
    db: Session = Depends(get_sync_db),
    user_id: UUID = Depends(_get_current_user_id),
):
    """
    Get user profile settings.
    
    Args:
        db: Database session
        user_id: Current authenticated user ID
        
    Returns:
        ProfileResponse with user profile settings
    """
    try:'''
        },
        # get_user_interactions endpoint
        {
            'old': '''@recommendations_router.get("/interactions", response_model=List[InteractionResponse])
async def get_user_interactions(
    limit: int = Query(100, ge=1, le=1000, description="Number of interactions to return"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    interaction_type: Optional[str] = Query(None, description="Filter by interaction type"),
    db: Session = Depends(get_sync_db),
):
    """
    Get user's interaction history.
    
    Args:
        limit: Number of interactions to return
        offset: Offset for pagination
        interaction_type: Optional filter by interaction type
        db: Database session
        
    Returns:
        List of InteractionResponse objects
    """
    try:
        
        # Get current user
        user_id = _get_current_user_id(db)''',
            'new': '''@recommendations_router.get("/interactions", response_model=List[InteractionResponse])
async def get_user_interactions(
    limit: int = Query(100, ge=1, le=1000, description="Number of interactions to return"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    interaction_type: Optional[str] = Query(None, description="Filter by interaction type"),
    db: Session = Depends(get_sync_db),
    user_id: UUID = Depends(_get_current_user_id),
):
    """
    Get user's interaction history.
    
    Args:
        limit: Number of interactions to return
        offset: Offset for pagination
        interaction_type: Optional filter by interaction type
        db: Database session
        user_id: Current authenticated user ID
        
    Returns:
        List of InteractionResponse objects
    """
    try:'''
        },
        # update_profile endpoint
        {
            'old': '''@recommendations_router.put("/profile", response_model=ProfileResponse)
async def update_profile(
    request: ProfileUpdateRequest,
    db: Session = Depends(get_sync_db),
):
    """
    Update user profile settings.
    
    Args:
        request: ProfileUpdateRequest with updated settings
        db: Database session
        
    Returns:
        ProfileResponse with updated profile
    """
    try:
        # Get current user
        user_id = _get_current_user_id(db)''',
            'new': '''@recommendations_router.put("/profile", response_model=ProfileResponse)
async def update_profile(
    request: ProfileUpdateRequest,
    db: Session = Depends(get_sync_db),
    user_id: UUID = Depends(_get_current_user_id),
):
    """
    Update user profile settings.
    
    Args:
        request: ProfileUpdateRequest with updated settings
        db: Database session
        user_id: Current authenticated user ID
        
    Returns:
        ProfileResponse with updated profile
    """
    try:'''
        },
        # submit_feedback endpoint
        {
            'old': '''@recommendations_router.post("/feedback", response_model=FeedbackResponse, status_code=status.HTTP_201_CREATED)
async def submit_feedback(
    request: FeedbackRequest,
    db: Session = Depends(get_sync_db),
):
    """
    Submit feedback on a recommendation.
    
    Args:
        request: FeedbackRequest with feedback details
        db: Database session
        
    Returns:
        FeedbackResponse with feedback details
    """
    try:
        # Get current user
        user_id = _get_current_user_id(db)''',
            'new': '''@recommendations_router.post("/feedback", response_model=FeedbackResponse, status_code=status.HTTP_201_CREATED)
async def submit_feedback(
    request: FeedbackRequest,
    db: Session = Depends(get_sync_db),
    user_id: UUID = Depends(_get_current_user_id),
):
    """
    Submit feedback on a recommendation.
    
    Args:
        request: FeedbackRequest with feedback details
        db: Database session
        user_id: Current authenticated user ID
        
    Returns:
        FeedbackResponse with feedback details
    """
    try:'''
        },
        # refresh_recommendations endpoint
        {
            'old': '''@recommendations_router.post("/refresh", status_code=status.HTTP_202_ACCEPTED)
async def refresh_recommendations(
    db: Session = Depends(get_sync_db),
):
    """
    Queue a background task to refresh user recommendations.
    
    Args:
        db: Database session
        
    Returns:
        Acceptance message
    """
    try:
        # Get current user
        user_id = _get_current_user_id(db)''',
            'new': '''@recommendations_router.post("/refresh", status_code=status.HTTP_202_ACCEPTED)
async def refresh_recommendations(
    db: Session = Depends(get_sync_db),
    user_id: UUID = Depends(_get_current_user_id),
):
    """
    Queue a background task to refresh user recommendations.
    
    Args:
        db: Database session
        user_id: Current authenticated user ID
        
    Returns:
        Acceptance message
    """
    try:'''
        },
    ]
    
    # Apply all fixes
    for fix in fixes:
        if fix['old'] in content:
            content = content.replace(fix['old'], fix['new'])
            print("✓ Fixed endpoint")
        else:
            print("⚠ Pattern not found (may already be fixed)")
    
    # Write back
    with open('app/modules/recommendations/router.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("\n✓ All recommendation router endpoints fixed!")
    print("  - Added user_id as dependency parameter")
    print("  - Removed manual _get_current_user_id(db) calls")
    print("  - Tests can now properly override authentication")

if __name__ == '__main__':
    fix_router()
