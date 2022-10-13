#!/usr/bin/env python3

from datetime import datetime

class Logger:
    @staticmethod
    def create_entry(message: str, entry_type: str):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if not entry_type.upper() in ("ERROR", "WARN", "INFO"):
            entry_type = "UNCATEGORISED"

        print(f"""[{timestamp}] [{entry_type.upper()}] {message}""")
