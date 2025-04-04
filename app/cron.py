from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

import sys
import os
import argparse
from lib.mail import fetch_files, GR_FILE, PO_FILE
from lib.streamlit_common import process_gr_file_auto, process_po_file_auto


def import_gr_files():
    files = fetch_files(GR_FILE)
    for date, file in files.items():
        print(f"Importing GR files for {date}")
        process_gr_file_auto(file)

def import_po_files():
    files = fetch_files(PO_FILE)
    for date, file in files.items():
        print(f"Importing PO files for {date}")
        process_po_file_auto(file)

def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command")
    gr_parser = subparsers.add_parser("import-gr-files")
    po_parser = subparsers.add_parser("import-po-files")
    args = parser.parse_args()

    if args.command == "import-gr-files":
        import_gr_files()
    elif args.command == "import-po-files":
        import_po_files()
    else:
        parser.print_help()
        sys.exit(1)

if __name__ == "__main__":
    main()

