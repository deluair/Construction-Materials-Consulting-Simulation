from setuptools import setup, find_packages

setup(
    name="construction_materials_sim",
    version="0.1.0",
    description="Construction Materials Transformation Simulation Framework",
    author="Construction Materials Consulting Team",
    packages=find_packages(),
    install_requires=[
        "numpy>=1.21.0",
        "pandas>=1.3.0",
        "scipy>=1.7.0",
        "matplotlib>=3.4.0",
        "seaborn>=0.11.0",
        "scikit-learn>=0.24.0",
        "pymc3>=3.11.0",
        "arviz>=0.11.0",
        "plotly>=5.1.0",
        "dash>=2.0.0",
        "dash-bootstrap-components>=1.0.0",
        "python-dotenv>=0.19.0"
    ],
    extras_require={
        "dev": [
            "pytest>=6.2.0",
            "black>=21.5b2",
            "flake8>=3.9.0"
        ]
    },
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "construction-materials-sim=construction_materials_sim.main:main"
        ]
    }
) 