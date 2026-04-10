import os
import sys


# ------------------------------------------------------------------
# PATH RESOLUTION
# ------------------------------------------------------------------
def get_base_dir():
    """
    Returns the base directory where the executable or script is located.

    Supports both execution modes:
    - Python script (dev environment)
    - PyInstaller executable (prod environment)

    Returns:
        str: Absolute path to base directory
    """
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    else:
        return os.path.dirname(os.path.abspath(__file__))


def get_project_root():
    """
    Returns the root directory of the project.

    Assumes this file is located inside a /utils directory.

    Returns:
        str: Absolute path to project root
    """
    return os.path.dirname(get_base_dir())


def get_data_path(filename: str) -> str:
    """
    Builds an absolute path to a file inside the /data directory.

    Args:
        filename (str): File name (e.g. 'input.csv')

    Returns:
        str: Absolute path to the target file
    """
    return os.path.join(get_project_root(), "data", filename)


# ------------------------------------------------------------------
# READ HELPERS
# ------------------------------------------------------------------
def read_csv_rows(filename: str):
    """
    Reads a CSV file from /data and returns raw rows.

    This function does NOT apply any transformation or business logic.
    It is intentionally generic and reusable.

    Args:
        filename (str): CSV file name (e.g. 'input.csv')

    Returns:
        list[list[str]]: Raw rows from CSV file
    """
    import csv

    file_path = get_data_path(filename)

    try:
        with open(file_path, "r", encoding="utf-8", newline="") as f:
            reader = csv.reader(f)
            return list(reader)
    except FileNotFoundError:
        raise FileNotFoundError(
            f"CSV file not found at path: {file_path}"
        )
    except Exception as e:
        raise Exception(
            f"Error reading CSV file '{file_path}': {str(e)}"
        )


def read_json_file(filename: str):
    """
    Reads and parses a JSON file from /data.

    Args:
        filename (str): JSON file name

    Returns:
        dict | list: Parsed JSON content
    """
    import json

    file_path = get_data_path(filename)

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        raise FileNotFoundError(
            f"JSON file not found at path: {file_path}"
        )
    except json.JSONDecodeError as e:
        raise Exception(
            f"Error parsing JSON file '{file_path}': {str(e)}"
        )


def read_text_file(filename: str):
    """
    Reads a plain text file from /data.

    Args:
        filename (str): File name

    Returns:
        str: File content as string
    """
    file_path = get_data_path(filename)

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        raise FileNotFoundError(
            f"Text file not found at path: {file_path}"
        )
    except Exception as e:
        raise Exception(
            f"Error reading text file '{file_path}': {str(e)}"
        )


def read_xml_file(filename: str):
    """
    Reads and parses an XML file from /data.

    Args:
        filename (str): XML file name

    Returns:
        xml.etree.ElementTree.ElementTree: Parsed XML tree
    """
    from xml.etree import ElementTree as ET

    file_path = get_data_path(filename)

    try:
        return ET.parse(file_path)
    except FileNotFoundError:
        raise FileNotFoundError(
            f"XML file not found at path: {file_path}"
        )
    except ET.ParseError as e:
        raise Exception(
            f"Error parsing XML file '{file_path}': {str(e)}"
        )


# ------------------------------------------------------------------
# WRITE HELPERS
# ------------------------------------------------------------------
def write_json_file(filename: str, data, indent: int = 4):
    """
    Writes data to a JSON file inside /data.

    Creates the directory if it does not exist.

    Args:
        filename (str): Target file name
        data (any): Serializable data
        indent (int): JSON indentation level (default: 4)
    """
    import json

    file_path = get_data_path(filename)

    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=indent)
    except Exception as e:
        raise Exception(
            f"Error writing JSON file '{file_path}': {str(e)}"
        )


def write_text_file(filename: str, content: str):
    """
    Writes plain text content to a file inside /data.

    Creates the directory if it does not exist.

    Args:
        filename (str): Target file name
        content (str): Text content to write
    """
    file_path = get_data_path(filename)

    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
    except Exception as e:
        raise Exception(
            f"Error writing text file '{file_path}': {str(e)}"
        )


def append_log_file(filename: str, message: str):
    """
    Appends a log message to a file inside /data.

    If the file does not exist, it will be created automatically.

    Args:
        filename (str): Log file name (e.g. 'debug_matcher.log')
        message (str): Message to append (single line)
    """
    file_path = get_data_path(filename)

    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        with open(file_path, "a", encoding="utf-8") as f:
            f.write(message + "\n")
    except Exception as e:
        raise Exception(
            f"Error writing log file '{file_path}': {str(e)}"
        )