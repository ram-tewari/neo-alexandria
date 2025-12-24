# Developer Guides

Practical guides for developing with Neo Alexandria 2.0.

## Quick Links

| Guide | Description | File |
|-------|-------------|------|
| Setup | Installation & environment | [setup.md](setup.md) |
| Workflows | Common development tasks | [workflows.md](workflows.md) |
| Testing | Testing strategies | [testing.md](testing.md) |
| Deployment | Docker & production | [deployment.md](deployment.md) |
| Troubleshooting | Common issues | [troubleshooting.md](troubleshooting.md) |

## Getting Started

1. **Setup** - Install dependencies and configure environment
2. **Workflows** - Learn common development patterns
3. **Testing** - Write and run tests
4. **Deployment** - Deploy to production

## Development Workflow

```
1. Setup environment → setup.md
2. Create feature branch
3. Implement feature → workflows.md
4. Write tests → testing.md
5. Run tests locally
6. Submit PR
7. Deploy → deployment.md
```

## Quick Commands

```bash
# Start dev server
cd backend
uvicorn app.main:app --reload

# Run tests
pytest tests/ -v

# Run migrations
alembic upgrade head

# Format code
ruff format .
```

## Related Documentation

- [API Reference](../api/) - API endpoints
- [Architecture](../architecture/) - System design
- [Steering: Tech](../../../.kiro/steering/tech.md) - Tech stack
