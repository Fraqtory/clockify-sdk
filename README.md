# Clockify SDK

A Python SDK for interacting with the Clockify API.

## Installation

```bash
pip install clockify-sdk
```

## Usage

```python
from clockify_sdk import ClockifyClient

# Initialize the client
client = ClockifyClient(api_key="your-api-key")

# Get workspace information
workspaces = client.get_workspaces()

# Get time entries
time_entries = client.get_time_entries(workspace_id="workspace-id")
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

## License

This project is licensed under the MIT License - see the LICENSE file for details.
