#!/usr/bin/env python3
"""
Generate complete documentation for Neo Alexandria 2.0
Combines all markdown documentation into a single file for PDF generation
"""

import os
from pathlib import Path
from datetime import datetime

# Documentation files to include (in order)
DOC_FILES = [
    # Steering docs
    ("AGENTS.md", "Agent Context Management"),
    (".kiro/steering/product.md", "Product Overview"),
    (".kiro/steering/tech.md", "Technical Stack"),
    (".kiro/steering/structure.md", "Repository Structure"),
    
    # Backend docs - Index
    ("backend/docs/index.md", "Backend Documentation Index"),
    
    # Backend docs - API Reference
    ("backend/docs/api/overview.md", "API Overview"),
    ("backend/docs/api/resources.md", "Resources API"),
    ("backend/docs/api/search.md", "Search API"),
    ("backend/docs/api/collections.md", "Collections API"),
    ("backend/docs/api/annotations.md", "Annotations API"),
    ("backend/docs/api/taxonomy.md", "Taxonomy API"),
    ("backend/docs/api/graph.md", "Graph API"),
    ("backend/docs/api/recommendations.md", "Recommendations API"),
    ("backend/docs/api/quality.md", "Quality API"),
    ("backend/docs/api/scholarly.md", "Scholarly API"),
    ("backend/docs/api/authority.md", "Authority API"),
    ("backend/docs/api/curation.md", "Curation API"),
    ("backend/docs/api/monitoring.md", "Monitoring API"),
    
    # Backend docs - Architecture
    ("backend/docs/architecture/overview.md", "Architecture Overview"),
    ("backend/docs/architecture/database.md", "Database Architecture"),
    ("backend/docs/architecture/event-system.md", "Event System"),
    ("backend/docs/architecture/events.md", "Event Catalog"),
    ("backend/docs/architecture/modules.md", "Module Architecture"),
    ("backend/docs/architecture/decisions.md", "Architecture Decisions"),
    
    # Backend docs - Guides
    ("backend/docs/guides/setup.md", "Setup Guide"),
    ("backend/docs/guides/workflows.md", "Development Workflows"),
    ("backend/docs/guides/testing.md", "Testing Guide"),
    ("backend/docs/guides/deployment.md", "Deployment Guide"),
    ("backend/docs/guides/troubleshooting.md", "Troubleshooting"),
    
    # Backend README
    ("backend/README.md", "Backend Overview"),
]

def read_file_safe(filepath):
    """Read file content safely, return empty string if file doesn't exist"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print(f"Warning: File not found: {filepath}")
        return f"\n\n*File not found: {filepath}*\n\n"
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        return f"\n\n*Error reading file: {filepath}*\n\n"

def generate_toc(doc_files):
    """Generate table of contents"""
    toc = ["# Table of Contents\n"]
    for i, (_, title) in enumerate(doc_files, 1):
        # Create anchor link (lowercase, replace spaces with hyphens)
        anchor = title.lower().replace(" ", "-").replace("/", "-")
        toc.append(f"{i}. [{title}](#{anchor})")
    return "\n".join(toc)

def main():
    output_file = "NEO_ALEXANDRIA_COMPLETE_DOCUMENTATION.md"
    
    print(f"Generating complete documentation...")
    print(f"Output file: {output_file}")
    
    with open(output_file, 'w', encoding='utf-8') as out:
        # Write header
        out.write("# Neo Alexandria 2.0 - Complete Documentation\n\n")
        out.write(f"**Generated:** {datetime.now().strftime('%B %d, %Y at %H:%M:%S')}\n\n")
        out.write("---\n\n")
        
        # Write table of contents
        out.write(generate_toc(DOC_FILES))
        out.write("\n\n---\n\n")
        
        # Write each document
        for i, (filepath, title) in enumerate(DOC_FILES, 1):
            print(f"Processing {i}/{len(DOC_FILES)}: {filepath}")
            
            # Write section header
            out.write(f"\n\n# {i}. {title}\n\n")
            out.write(f"*Source: `{filepath}`*\n\n")
            out.write("---\n\n")
            
            # Write content
            content = read_file_safe(filepath)
            out.write(content)
            
            # Add page break for PDF
            out.write("\n\n<div style='page-break-after: always;'></div>\n\n")
            out.write("---\n\n")
    
    print(f"\n✓ Documentation generated successfully!")
    print(f"✓ Output file: {output_file}")
    print(f"\nTo convert to PDF, you can use:")
    print(f"  - Pandoc: pandoc {output_file} -o neo_alexandria_docs.pdf")
    print(f"  - Online converter: Upload to https://www.markdowntopdf.com/")
    print(f"  - VS Code: Use 'Markdown PDF' extension")

if __name__ == "__main__":
    main()
