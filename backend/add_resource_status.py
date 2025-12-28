"""Script to add ResourceStatus enum to models.py"""

with open('app/database/models.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find the line with "class Resource(Base):"
resource_line_idx = None
for i, line in enumerate(lines):
    if 'class Resource(Base):' in line:
        resource_line_idx = i
        break

if resource_line_idx is None:
    print('✗ Could not find Resource class')
    exit(1)

# Insert the enum before the Resource class
enum_lines = [
    '\n',
    '# ============================================================================\n',
    '# Enums\n',
    '# ============================================================================\n',
    '\n',
    'class ResourceStatus(str, enum.Enum):\n',
    '    """Resource ingestion status."""\n',
    '    PENDING = "pending"\n',
    '    PROCESSING = "processing"\n',
    '    COMPLETED = "completed"\n',
    '    FAILED = "failed"\n',
    '\n',
    '# ============================================================================\n',
    '# Resource Models\n',
    '# ============================================================================\n',
    '\n',
]

# Insert the enum lines before the Resource class
lines = lines[:resource_line_idx] + enum_lines + lines[resource_line_idx:]

with open('app/database/models.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)

print('ResourceStatus enum added successfully!')
print('Verifying...')

# Verify
with open('app/database/models.py', 'r', encoding='utf-8') as f:
    content = f.read()
    if 'class ResourceStatus' in content:
        print('✓ ResourceStatus enum is now in the file')
    else:
        print('✗ Failed to add ResourceStatus enum')
