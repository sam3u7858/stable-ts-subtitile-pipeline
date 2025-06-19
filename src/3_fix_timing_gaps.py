import re
from datetime import datetime, timedelta


def read_srt_file(filename):
    with open(filename, 'r', encoding='utf-8') as file:
        return file.read()


def write_srt_file(filename, content):
    with open(filename, 'w', encoding='utf-8') as file:
        file.write(content)


def parse_time(s):
    return datetime.strptime(s, '%H:%M:%S,%f')


def time_to_str(d):
    return d.strftime('%H:%M:%S,%f')[:-3]


def process_subtitles(content):
    subtitles = content.split('\n\n')
    for i in range(len(subtitles) - 1):
        current_sub = subtitles[i]
        next_sub = subtitles[i + 1]
        current_sub_lines = current_sub.split('\n')
        next_sub_lines = next_sub.split('\n')
        if len(current_sub_lines) < 3 or len(next_sub_lines) < 3:
            continue

        current_end_time_str = current_sub_lines[1].split(' --> ')[1]
        next_start_time_str = next_sub_lines[1].split(' --> ')[0]

        current_end_time = parse_time(current_end_time_str)
        next_start_time = parse_time(next_start_time_str)
        if (next_start_time - current_end_time) < timedelta(seconds=0.5):
            # Set current end time to the next start time directly
            current_sub_lines[1] = current_sub_lines[1].split(
                ' --> ')[0] + ' --> ' + next_start_time_str
            subtitles[i] = '\n'.join(current_sub_lines)
    return '\n\n'.join(subtitles)


# filename = input("Enter the filename of the .srt file: ")
filename = "fullvoice23_prunedpt2.srt"
content = read_srt_file(filename)
processed_content = process_subtitles(content)
output_filename = "processed_" + filename
write_srt_file(output_filename, processed_content)

print(f"Processed subtitle file has been saved as {output_filename}")
