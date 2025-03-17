# Clockify SDK

A Python SDK for interacting with the Clockify API. This SDK provides a simple and intuitive interface to manage your Clockify workspace, including time entries, projects, tasks, and reports.

## Features

- 🔑 Simple authentication with API key
- 📊 Manage time entries
- 📁 Handle projects and tasks
- 👥 Manage clients and users
- 📈 Generate reports
- 🔄 Workspace management
- ✨ Type hints for better IDE support

## Installation

```bash
pip install clockify-sdk
```

## Quick Start

First, create a `.env` file in your project root:

```env
CLOCKIFY_API_KEY=your-api-key
CLOCKIFY_WORKSPACE_ID=your-workspace-id  # Optional, defaults to first workspace
```

Then use the SDK:

```python
from dotenv import load_dotenv
import os
from clockify_sdk import Clockify

# Load environment variables from .env file
load_dotenv()

# Initialize the client
client = Clockify(
    api_key=os.getenv("CLOCKIFY_API_KEY"),
    workspace_id=os.getenv("CLOCKIFY_WORKSPACE_ID")  # Optional
)

# Get all your workspaces
workspaces = client.get_workspaces()

# Create a new time entry
time_entry = client.time_entries.create(
    project_id="project-id",
    description="Working on feature X",
    start_time="2024-03-17T10:00:00Z",
    end_time="2024-03-17T11:00:00Z"
)

# Get all projects
projects = client.projects.get_all()

# Create a new project
project = client.projects.create(
    name="New Project",
    client_id="client-id",
    is_public=True
)

# Get time entries for a specific date range
time_entries = client.time_entries.get_all(
    start_date="2024-03-01",
    end_date="2024-03-17"
)

# Generate a detailed report
report = client.reports.generate(
    start_date="2024-03-01",
    end_date="2024-03-17",
    project_ids=["project-id-1", "project-id-2"]
)
```

## Advanced Usage

### Working with Tasks

```python
# Create a new task
task = client.tasks.create(
    project_id="project-id",
    name="Implement new feature",
    assignee_id="user-id"
)

# Get all tasks for a project
tasks = client.tasks.get_by_project(project_id="project-id")
```

### Managing Clients

```python
# Create a new client
client = client.clients.create(
    name="New Client",
    note="Important client"
)

# Get all clients
clients = client.clients.get_all()
```

### User Management

```python
# Get current user information
current_user = client.user_manager.get_current_user()

# Get all users in workspace
users = client.user_manager.get_all()
```

## Error Handling

The SDK provides clear error messages and exceptions:

```python
from clockify_sdk.exceptions import ClockifyError

try:
    client.time_entries.create(
        project_id="invalid-id",
        description="Test entry"
    )
except ClockifyError as e:
    print(f"Error: {e.message}")
```

## Development

1. Clone the repository:
```bash
git clone https://github.com/fraqtory/clockify-sdk.git
cd clockify-sdk
```

2. Create and activate a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows, use `.venv\Scripts\activate`
```

3. Install development dependencies:
```bash
pip install -e ".[dev]"
```

4. Run tests:
```bash
pytest
```

5. Run type checking:
```bash
mypy clockify_sdk
```

6. Run linting:
```bash
ruff check .
black .
isort .
```

## Documentation

For detailed documentation, visit [https://clockify-sdk.readthedocs.io](https://clockify-sdk.readthedocs.io)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
