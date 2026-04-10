# writer.py
import json

def write_phase2_output(path_json, data):
    with open(path_json, "w") as f:
        json.dump(data, f, indent=4)