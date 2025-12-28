"""
Script to move graph services to modules/graph directory with updated imports.
"""

from pathlib import Path

def update_imports(content: str) -> str:
    """Update imports to use shared kernel and module paths."""
    
    # Update config imports
    content = content.replace(
        "from ..config.settings import get_settings",
        "from app.config.settings import get_settings"
    )
    
    # Update database imports
    content = content.replace(
        "from ..database import models as db_models",
        "from app.database import models as db_models"
    )
    content = content.replace(
        "from ..database.models import",
        "from app.database.models import"
    )
    
    # Update schema imports to use module-local
    content = content.replace(
        "from ..schemas.graph import",
        "from app.modules.graph.schema import"
    )
    content = content.replace(
        "from ..schemas.discovery import",
        "from app.modules.graph.schema import"
    )
    
    # Update shared kernel imports
    content = content.replace(
        "from ..shared.base_model import Base",
        "from app.shared.base_model import Base"
    )
    content = content.replace(
        "from ..shared.event_bus import event_bus, EventPriority",
        "from app.shared.event_bus import event_bus, EventPriority"
    )
    content = content.replace(
        "from ..events.event_types import SystemEvent",
        "from app.events.event_types import SystemEvent"
    )
    
    return content

def copy_service_file(source_path: Path, dest_path: Path):
    """Copy service file with updated imports."""
    print(f"Copying {source_path} to {dest_path}")
    
    # Read source
    with open(source_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Update imports
    content = update_imports(content)
    
    # Write to destination
    with open(dest_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✓ Copied and updated {dest_path.name}")

def main():
    """Main function to move all graph services."""
    base_dir = Path(__file__).parent.parent
    services_dir = base_dir / "app" / "services"
    graph_module_dir = base_dir / "app" / "modules" / "graph"
    
    # Mapping of source files to destination files
    file_mappings = [
        ("graph_service.py", "service.py"),
        ("graph_service_phase10.py", "advanced_service.py"),
        ("graph_embeddings_service.py", "embeddings.py"),
        ("citation_service.py", "citations.py"),
        ("lbd_service.py", "discovery.py"),
    ]
    
    for source_name, dest_name in file_mappings:
        source_path = services_dir / source_name
        dest_path = graph_module_dir / dest_name
        
        if source_path.exists():
            copy_service_file(source_path, dest_path)
        else:
            print(f"⚠ Source file not found: {source_path}")
    
    print("\n✓ All graph services moved successfully!")

if __name__ == "__main__":
    main()
