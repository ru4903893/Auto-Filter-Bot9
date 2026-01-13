import math
from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from utils import get_size, get_name
from database.ia_filterdb import get_search_results
from config import MAX_BTN
import utils, temp


@Client.on_callback_query(filters.regex(r"^next_"))
async def next_page(client, query):
    _, req, key, offset = query.data.split("_")
    offset = int(offset)
    req = int(req)

    if query.from_user.id != req:
        return await query.answer("This is not for you!", show_alert=True)

    settings = await utils.get_settings(query.message.chat.id)

    files, next_offset, total = await get_search_results(
        key,
        offset=offset,
        filter=True
    )

    if not files:
        return await query.answer("No more results!", show_alert=True)

    btn = [[
        InlineKeyboardButton(
            text=f"🔗 {get_size(file.file_size)} ≽ {get_name(file.file_name)}",
            url=f"https://t.me/{temp.U_NAME}?start=file_{query.message.chat.id}_{file.file_id}"
        )
    ] for file in files]

    # ===== TOP BUTTONS =====
    btn.insert(0, [
        InlineKeyboardButton("📂 sᴇᴀsᴏɴ", callback_data=f"season#{key}#{req}#0"),
        InlineKeyboardButton("🎞 qᴜᴀʟɪᴛʏ", callback_data=f"quality#{key}#{req}#0")
    ])
    btn.insert(1, [
        InlineKeyboardButton("♻️ sᴇɴᴅ ᴀʟʟ", callback_data=f"send_all#{key}"),
        InlineKeyboardButton("📰 ʟᴀɴɢᴜᴀɢᴇs", callback_data=f"languages#{key}#{req}#0")
    ])

    # ===== PAGINATION =====
    if 0 < offset <= int(MAX_BTN):
        off_set = 0
    elif offset == 0:
        off_set = None
    else:
        off_set = offset - int(MAX_BTN)

    if next_offset == 0:
        btn.append([
            InlineKeyboardButton("⪻ ʙᴀᴄᴋ", callback_data=f"next_{req}_{key}_{off_set}"),
            InlineKeyboardButton(
                f"ᴘᴀɢᴇ {math.ceil(offset / int(MAX_BTN)) + 1} / {math.ceil(total / int(MAX_BTN))}",
                callback_data="pages"
            )
        ])
    elif off_set is None:
        btn.append([
            InlineKeyboardButton(
                f"{math.ceil(offset / int(MAX_BTN)) + 1} / {math.ceil(total / int(MAX_BTN))}",
                callback_data="pages"
            ),
            InlineKeyboardButton("ɴᴇxᴛ ⪼", callback_data=f"next_{req}_{key}_{next_offset}")
        ])
    else:
        btn.append([
            InlineKeyboardButton("⪻ ʙᴀᴄᴋ", callback_data=f"next_{req}_{key}_{off_set}"),
            InlineKeyboardButton(
                f"{math.ceil(offset / int(MAX_BTN)) + 1} / {math.ceil(total / int(MAX_BTN))}",
                callback_data="pages"
            ),
            InlineKeyboardButton("ɴᴇxᴛ ⪼", callback_data=f"next_{req}_{key}_{next_offset}")
        ])

    # ===== TEXT MODE =====
    if settings.get("link"):
        links = ""
        for i, file in enumerate(files, start=offset + 1):
            links += f"""<b>\n\n{i}. <a href="https://t.me/{temp.U_NAME}?start=file_{query.message.chat.id}_{file.file_id}">
[{get_size(file.file_size)}] {get_name(file.file_name)}
</a></b>"""

        await query.message.edit_text(
            query.message.text.html + links,
            parse_mode=enums.ParseMode.HTML,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(btn)
        )
        return

    await query.message.edit_reply_markup(
        reply_markup=InlineKeyboardMarkup(btn)
    )


# ================= SEASON BUTTON =================
@Client.on_callback_query(filters.regex(r"^season#"))
async def season_cb(client, query):
    _, key, req, offset = query.data.split("#")
    if int(req) != query.from_user.id:
        return await query.answer("This is not for you!", show_alert=True)

    btn = [
        [
            InlineKeyboardButton("Season 1", callback_data=f"season_select#1#{key}#{req}"),
            InlineKeyboardButton("Season 2", callback_data=f"season_select#2#{key}#{req}")
        ],
        [
            InlineKeyboardButton("⪻ Back", callback_data=f"next_{req}_{key}_{offset}")
        ]
    ]

    await query.message.edit_reply_markup(
        reply_markup=InlineKeyboardMarkup(btn)
    )


# ================= QUALITY BUTTON =================
@Client.on_callback_query(filters.regex(r"^quality#"))
async def quality_cb(client, query):
    _, key, req, offset = query.data.split("#")
    if int(req) != query.from_user.id:
        return await query.answer("This is not for you!", show_alert=True)

    btn = [
        [
            InlineKeyboardButton("480p", callback_data=f"quality_select#480#{key}#{req}"),
            InlineKeyboardButton("720p", callback_data=f"quality_select#720#{key}#{req}")
        ],
        [
            InlineKeyboardButton("1080p", callback_data=f"quality_select#1080#{key}#{req}")
        ],
        [
            InlineKeyboardButton("⪻ Back", callback_data=f"next_{req}_{key}_{offset}")
        ]
    ]

    await query.message.edit_reply_markup(
        reply_markup=InlineKeyboardMarkup(btn)
    )
