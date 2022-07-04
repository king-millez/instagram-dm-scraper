import os
import argparse

from typing import Optional
from datetime import datetime

from igdm.ig_requests import ig_get
from igdm.credentials.cred_manager import cookies
from igdm.reader import scrape_thread


os.system("color")


def main(limit: Optional[int] = None) -> None:
    init_data = ig_get(
        "https://i.instagram.com/api/v1/direct_v2/inbox/", cookies=cookies
    ).json()
    viewer_data = init_data["viewer"]
    thread_count = len(init_data["inbox"]["threads"])
    thread_to_scrape = None
    for index, thread in enumerate(init_data["inbox"]["threads"]):
        print(f'{index + 1}: {thread["thread_title"]}')

    while thread_to_scrape is None:
        try:
            thread_to_scrape = (
                int(
                    input(f"Which thread do you want to scrape? (1 - {thread_count}): ")
                )
                - 1
            )
            if thread_to_scrape not in range(thread_count):
                thread_to_scrape = None
        except ValueError:
            continue

    thread_data = init_data["inbox"]["threads"][thread_to_scrape]
    out_file = f"{thread_data['thread_v2_id']} ({thread_data['thread_title']}) - {datetime.strftime(datetime.now(), '%Y%m%d%H%M%S')}.txt"
    thread_id = thread_data["thread_id"]

    print(f"Scraping {thread_id}")
    scrape_thread(thread_id, viewer_data, out_file, limit)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Instagram DMs scraper - This probably violates some ToS somewhere so use it at your own risk."
    )
    parser.add_argument(
        "-l",
        "--limit",
        dest="limit",
        type=int,
        help='Maximum amount of "scrolls" the scraper can perform on a thread (See README).',
    )
    args = parser.parse_args()

    main(limit=args.limit)
