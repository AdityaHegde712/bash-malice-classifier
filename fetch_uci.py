from ucimlrepo import fetch_ucirepo
import json
import os

# Fetch UCI dataset
shell_commands = fetch_ucirepo(id=869)

# Process the data
features = shell_commands.data.features
print(f"Features shape: {features.shape}")
print(f"Features columns: {list(features.columns)}")

# Extract command text - assuming command is in a column named 'command' or similar
command_column = None
for col in features.columns:
    if 'command' in col.lower():
        command_column = col
        break

if command_column is None:
    # Try to find the command column by checking column names
    print("Available columns:", list(features.columns))
    # Based on typical UCI dataset structure, let's check common column names
    possible_cols = ['command', 'Command', 'cmd', 'CommandText', 'command_text']
    for col in possible_cols:
        if col in features.columns:
            command_column = col
            break

if command_column is None:
    # If no command column found, use the first column that looks like text
    for col in features.columns:
        if features[col].dtype == 'object':
            command_column = col
            break

print(f"Using column '{command_column}' for commands")

# Create JSONL file
output_path = "data/raw/uci_shell_commands.jsonl"
os.makedirs(os.path.dirname(output_path), exist_ok=True)

with open(output_path, 'w') as f:
    for idx, row in features.iterrows():
        command = str(row[command_column]) if command_column else f"command_{idx}"
        # Extract additional metadata if available
        record = {
            "command": command,
            "source": "uci"
        }
        # Add other fields if they exist
        for col in features.columns:
            if col != command_column:
                record[col] = str(row[col])
        f.write(json.dumps(record) + '\n')

print(f"Saved {len(features)} records to {output_path}")