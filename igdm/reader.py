import re

from datetime import datetime
from typing import Optional, List, Dict

from igdm.message import MessageLog
from igdm.ig_requests import ig_get
from igdm.credentials.cred_manager import cookies


ansi_escape = re.compile(
    r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])"
)  # Stolen from https://stackoverflow.com/a/14693789


def to_date(timestamp: str) -> datetime:
    return datetime.fromtimestamp(float(timestamp) / 10**6)


def create_log(
    user_info: dict,
    item_id: int,
    is_sent: bool,
    text: str,
    sender: str,
    datestr: str,
    likes: Optional[List[Dict[str, str | int | bool]]] = None,
    reply_data: Optional[Dict[str, str | int | bool]] = None,
) -> MessageLog:
    like_count = len(likes) if likes else 0

    def create_reply_dict(text_src: str) -> Dict[str, str | bool | int]:
        return dict(
            reply_text=text_src,
            reply_id=reply_data["user_id"],  # type: ignore
            reply_sender=user_info[reply_data["user_id"]]["user"],  # type: ignore
            reply_sender_fname=user_info[reply_data["user_id"]]["fname"],  # type: ignore
            reply_is_sent=reply_data["is_sent_by_viewer"],  # type: ignore
            reply_datestr=int(reply_data["timestamp"]),  # type: ignore
        )

    if reply_data:
        match reply_data["item_type"]:
            case "text":
                reply_data = create_reply_dict(reply_data["text"])
            case "link":
                reply_data = create_reply_dict(
                    reply_data["link"]["link_context"]["link_url"]
                )
            case "text":
                reply_data = create_reply_dict(reply_data["text"])
            case "media":
                if reply_data["media"]["media_type"] == 1:
                    reply_data = create_reply_dict(
                        reply_data["media"]["image_versions2"]["candidates"][0]["url"]
                    )
                else:
                    reply_data = create_reply_dict(
                        reply_data["media"]["video_versions"][0]["ur"]
                    )
            case "animated_media":
                reply_data = create_reply_dict(
                    reply_data["animated_media"]["images"]["fixed_height"]["url"]
                )
            case "voice_media":
                reply_data = create_reply_dict(
                    reply_data["voice_media"]["media"]["audio"]["audio_src"]
                )
            case _:
                pass
    try:
        x = MessageLog(
            item_id=item_id,
            is_sent=is_sent,
            sender=user_info[sender]["user"],
            sender_fname=user_info[sender]["fname"],
            date=to_date(datestr),
            like_count=like_count,
            text=text,
            reply_date=to_date(reply_data["reply_datestr"]),
            reply_is_sent=reply_data["reply_is_sent"],
            reply_sender=reply_data["reply_sender"],
            reply_sender_fname=reply_data["reply_sender_fname"],
            reply_text=reply_data["reply_text"],
            reply_sender_id=reply_data["reply_id"],
        )
    except Exception as e:
        x = MessageLog(
            item_id=item_id,
            is_sent=is_sent,
            sender_id=sender,
            sender_is_admin=user_info[sender]["is_admin"],
            sender=user_info[sender]["user"],
            sender_fname=user_info[sender]["fname"],
            date=to_date(datestr),
            like_count=like_count,
            text=text,
        )
    return x


def scrape_users(thread: dict, viewer_json: dict) -> Dict[str, Dict[str, str]]:
    user_data = thread["users"]
    user_info = {
        user["pk"]: {"user": user["username"], "fname": user["full_name"]}
        for user in user_data
    }
    user_info[viewer_json["pk"]] = {
        "user": viewer_json["username"],
        "fname": viewer_json["full_name"],
    }
    for i in user_info.keys():
        user_info[i]["is_admin"] = False
        if i in thread["admin_user_ids"]:
            user_info[i]["is_admin"] = True

    return user_info


def scrape_thread(
    thread_id: str, viewer: dict, out_file: str, max_scroll: Optional[int] = None
):
    final_list = []
    thread_data = ig_get(
        f"https://i.instagram.com/api/v1/direct_v2/threads/{thread_id}", cookies=cookies
    ).json()["thread"]
    user_info = scrape_users(thread_data, viewer)

    messages = thread_data["items"]

    def log_wrapper(text_src: str) -> MessageLog:
        likes = msg["reactions"]["emojis"] if "reactions" in msg.keys() else None
        reply_data = (
            msg["replied_to_message"] if "replied_to_message" in msg.keys() else None
        )
        return create_log(
            user_info=user_info,
            item_id=msg["item_id"],
            is_sent=msg["is_sent_by_viewer"],
            text=text_src,
            sender=msg["user_id"],
            datestr=msg["timestamp"],
            likes=likes,
            reply_data=reply_data,
        )

    count = 0

    if not max_scroll:
        max_scroll = 100

    while count < max_scroll:
        if count != 0:
            cursor = thread_data["oldest_cursor"]
            print(f"Scrolling to {cursor}")
            thread_data = ig_get(
                f"https://i.instagram.com/api/v1/direct_v2/threads/{thread_id}?cursor={cursor}",
                cookies=cookies,
            ).json()["thread"]

            messages = thread_data["items"]

        for msg in messages:
            match msg["item_type"]:
                case "link":
                    final_list.append(
                        log_wrapper(msg["link"]["link_context"]["link_url"])
                    )
                case "text":
                    final_list.append(log_wrapper(msg["text"]))
                case "media":
                    if msg["media"]["media_type"] == 1:
                        final_list.append(
                            log_wrapper(
                                msg["media"]["image_versions2"]["candidates"][0]["url"]
                            )
                        )
                    else:
                        final_list.append(
                            log_wrapper(msg["media"]["video_versions"][0]["url"])
                        )
                case "animated_media":
                    final_list.append(
                        log_wrapper(
                            msg["animated_media"]["images"]["fixed_height"]["url"]
                        )
                    )
                case "voice_media":
                    final_list.append(
                        log_wrapper(msg["voice_media"]["media"]["audio"]["audio_src"])
                    )
                case _:
                    pass
        count += 1

    final_list.reverse()
    with open(out_file, "w", encoding="utf8") as f:
        for index, msg in enumerate(final_list):
            print(str(msg))
            f.write(ansi_escape.sub("", str(msg) + "\n"))

            for user_seen in thread_data["last_seen_at"]:
                seen_str = f" + {user_info[int(user_seen)]['user']} ({datetime.strftime(to_date(thread_data['last_seen_at'][user_seen]['timestamp']), '%Y-%m-%d %H:%M:%S')})"
                try:
                    if (
                        int(thread_data["last_seen_at"][user_seen]["item_id"])
                        > int(msg.item_id)
                        and int(thread_data["last_seen_at"][user_seen]["item_id"])
                        < int(final_list[index + 1].item_id)
                    ) and int(final_list[index + 1].sender_id) != int(user_seen):
                        print(seen_str)
                        f.write(seen_str + "\n\n")
                except IndexError:
                    if int(thread_data["last_seen_at"][user_seen]["item_id"]) > int(
                        msg.item_id
                    ):
                        print(seen_str)
                        f.write(seen_str + "\n\n")
