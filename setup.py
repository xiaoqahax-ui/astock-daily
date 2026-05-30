from setuptools import setup, find_packages

setup(
    name="astock-daily",
    version="0.1.0",
    description="A股每日复盘CLI工具 — 快速了解今日市场",
    long_description=open("README.md", encoding="utf-8").read() if __import__("os").path.exists("README.md") else "",
    long_description_content_type="text/markdown",
    author="astock-daily",
    packages=find_packages(),
    install_requires=[
        "typer>=0.9",
        "rich>=13.0",
    ],
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "astock-daily=astock_daily.cli:entry",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
