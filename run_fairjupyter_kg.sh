#!/bin/bash

# Define the directory containing RML mapping files
rml_mapping_dir="split_mapping/rml_mapping"

# Define the directory to store config files
config_dir="config"

# Create the config directory if it doesn't exist
mkdir -p "$config_dir"

# Loop over each RML mapping file
for file in "$rml_mapping_dir"/*; do
    if [ -f "$file" ]; then
        # Extract filename without extension
        filename=$(basename "$file")
        filename_without_extension="${filename%%.*}"  # Extract filename before the first dot

        # Create config.ini file
        config_file="$config_dir/${filename_without_extension}_config.ini"
        echo "[CONFIGURATION]" > "$config_file"
        echo "output_file=split_graph/${filename_without_extension}.nt" >> "$config_file"
        echo "number_of_processes=1" >> "$config_file"
        echo "" >> "$config_file"
        echo "# LOGS" >> "$config_file"
        echo "logging_level=DEBUG" >> "$config_file"
        echo "logs_file=logs/${filename_without_extension}.txt" >> "$config_file"
        echo "" >> "$config_file"
        echo "[DataSourceCSV]" >> "$config_file"
        echo "mappings=split_mapping/rml_mapping/${filename}" >> "$config_file"

        echo "Created $config_file"

        # Run Python script for each config file
        start_time=$(date +%s.%N)
        python3 -m morph_kgc "$config_file" &> "logs/${filename_without_extension}.txt"
        end_time=$(date +%s.%N)
        elapsed_time=$(echo "$end_time - $start_time" | bc)
        echo "Time taken for ${filename_without_extension}: $elapsed_time seconds"
    fi
done
