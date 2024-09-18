from pathlib import Path
from setuptools import setup

local_path: str = (Path(__file__).parent / "lib" / "aicore-0.1.0.tar.gz").as_uri()

setup(
    install_requires=[
        f"aicore[search] @ {local_path}",
        "datasets",
        "gradio",
    ]
)
