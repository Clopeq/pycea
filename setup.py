from setuptools import setup, find_packages

setup(
    name="pycea",                  # Package name
    version="0.1.0",                    # Version
    author="Sebastian Król",
    # author_email="you@example.com",
    description="Chemical Equilibrium Analysis for Rocket Propulsion",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/Clopeq/PyPep3.git",
    packages=find_packages(),           # Automatically finds packages
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=[                  # Dependencies
        "numpy",
        "scipy",
        "cantera",
        "Rocketry_formulas @ git+https://github.com/Clopeq/Rocketry_formulas.git"
    ],
)