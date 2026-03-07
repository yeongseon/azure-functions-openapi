FROM ghcr.io/charmbracelet/vhs

RUN apt-get update -o Acquire::AllowReleaseInfoChange::Suite=true -o Acquire::AllowReleaseInfoChange::Codename=true \
    && apt-get install -y --no-install-recommends python3-pip python3-venv python-is-python3 \
    && rm -rf /var/lib/apt/lists/*
