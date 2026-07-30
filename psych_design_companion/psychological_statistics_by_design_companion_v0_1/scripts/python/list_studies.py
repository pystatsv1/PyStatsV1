#!/usr/bin/env python3
from companion_runtime import study_index
if __name__ == '__main__':
    for sid, row in study_index().items():
        print(f"{sid} | chapters {','.join(row['book_chapters'])} | {row['claim_type']} | {row['reader_command']}")
