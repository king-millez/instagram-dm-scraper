from typing import Optional
from termcolor import colored  # type: ignore
from datetime import datetime
from dataclasses import dataclass


SENT = "green"
RECEIVED = "yellow"


@dataclass
class MessageLog:
    item_id: str
    is_sent: bool
    sender: str
    sender_id: int
    sender_is_admin: bool
    sender_fname: str
    text: str
    date: datetime
    like_count: int
    reply_text: Optional[str] = None
    reply_sender: Optional[str] = None
    reply_sender_id: Optional[int] = None
    reply_sender_fname: Optional[str] = None
    reply_date: Optional[datetime] = None
    reply_is_sent: Optional[bool] = None

    def __str__(self) -> str:
        colour = RECEIVED
        reply_colour = RECEIVED

        if self.is_sent:
            colour = SENT

        if self.reply_is_sent:
            reply_colour = SENT

        ret_str = colored(
            f'{datetime.strftime(self.date, "%Y-%m-%d %H:%M:%S")} - [{self.sender} - {self.sender_id}] ({self.sender_fname}): {self.text}',
            colour,
        )

        if self.reply_text and self.reply_date:
            ret_str += colored(
                f' ({datetime.strftime(self.reply_date, "%Y-%m-%d %H:%M:%S")} - [{self.reply_sender} - {self.reply_sender_id}] ({self.reply_sender_fname}): {self.reply_text})',
                reply_colour,
            )

        if self.like_count > 0:
            ret_str += colored(f" [Likes: {self.like_count}]", "white")

        ret_str += "\n"
        return ret_str
