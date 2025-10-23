# ProjectFormWebsite — Dockerized Flask App

This folder contains a small Flask application and a Dockerfile to build a container image.

Build the image (PowerShell):

```powershell
docker build -t projectformwebsite:latest .
```

Run the container and map port 5000:

```powershell
docker run --rm -p 5000:5000 -v ${PWD}\static\images:C:\app\static\images projectformwebsite:latest
```

Run tests locally (recommended inside a virtualenv):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
pip install -r requirements-dev.txt
pytest -q
```

GitHub Actions:
- A workflow is included at `.github/workflows/pytest.yml` which runs pytest on push and pull requests to `main`.
