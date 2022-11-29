from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="batvis",
    version="0.1.0",
    author="Vivian Hafener",
    author_email="vhafener@lanl.gov",
    description="A package that generates charts for batsim outputs",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.newmexicoconsortium.org/lanl-ccu/batsimGantt",
    # include_package_data=True,
    project_urls={
        "Bug Tracker": "https://gitlab.newmexicoconsortium.org/lanl-ccu/batsimGantt/-/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    # py_modules=["main", "utils", "gantt", "plots"],
    packages=['batvis'],
    install_requires=[
        "matplotlib",
        "seaborn",
        "yaspin",
        "pandas",
    ],
    entry_points={
        "console_scripts": [
            "runbatvis=batvis:main",
        ],
    },
    # packages=find_packages(include=['prompt-toolkit', 'Click'])
    # install_requires=['prompt-toolkit', 'Click']
    python_requires=">=3.6",
)