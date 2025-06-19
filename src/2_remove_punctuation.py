import re


def is_timestamp_line(line):
    # Check if the line follows the SRT timestamp format
    return bool(re.match(r'\d{2}:\d{2}:\d{2},\d{3} --> \d{2}:\d{2}:\d{2},\d{3}', line))


def remove_commas_from_subtitle_text(input_file_path, output_file_path):
    try:
        with open(input_file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()

        modified_lines = []
        for line in lines:
            # Only remove commas from lines that do not contain timestamps
            if not is_timestamp_line(line):
                line = line.replace(',', '').replace('、', '')
            modified_lines.append(line)

        with open(output_file_path, 'w', encoding='utf-8') as file:
            file.writelines(modified_lines)

        print(f"Processed file saved as {output_file_path}")
    except Exception as e:
        print(f"An error occurred: {e}")


# Example usage
input_srt = 'fullvoicev23.srt'  # Replace this with the path to your input .srt file
# Replace this with the path you want for the output .srt file
output_srt = 'fullvoice23_prunedpt2.srt'

remove_commas_from_subtitle_text(input_srt, output_srt)
