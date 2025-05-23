#!/bin/bash
uv run uvicorn backend.main:app --reload --port 8000 &
uv run streamlit run frontend/streamlit_app.py