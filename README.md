# seneca

## Project Setup

This project contains two `setup.py` files serving different purposes:

1. **Root `setup.py`**: Used for defining the package and its dependencies. It specifies how the package should be installed and what dependencies it requires.

2. **`tools/setup.py`**: A utility script for setting up the development environment. It includes functions to create a virtual environment and install dependencies from `requirements.txt`.

### Getting Started

To get up and running with this project, follow these steps:

1. **Set up the Virtual Environment**:
   - Run the following command to create a virtual environment and install dependencies:
     ```bash
     python tools/setup.py
     ```
   - Activate the virtual environment:
     ```bash
     source .venv/bin/activate
     ```

2. **Install the Package in Editable Mode**:
   - Run the following command to install the package:
     ```bash
     pip install -e .
     ```

3. **Run Tests**:
   - Use `pytest` to run the tests and ensure everything is working correctly:
     ```bash
     pytest tests/
     ```

4. **Working with Notebooks**:
   - The project uses `jupytext` to maintain notebooks in both `.py` and `.ipynb` formats
   - To convert a Python script to a notebook:
     ```bash
     jupytext --to notebook notebooks/translate_letter.py
     ```
   - This will create/update the corresponding `.ipynb` file while preserving the notebook structure
   - Note: Always edit the `.py` files directly and convert to `.ipynb` to ensure version control compatibility

These steps will set up your development environment and ensure that the project is ready for development and testing.
