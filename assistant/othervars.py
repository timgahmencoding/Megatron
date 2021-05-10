# Ultroid - UserBot
# Copyright (C) 2020 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

import re
from os import execl, remove

import requests
from telegraph import Telegraph
from telegraph import upload_file as upl

from . import *
from plugins import *

# --------------------------------------------------------------------#
telegraph = Telegraph()
r = telegraph.create_account(short_name="CɪᴘʜᴇʀX")
auth_url = r["auth_url"]
# --------------------------------------------------------------------#


TOKEN_FILE = "resources/auths/auth_token.txt"


@callback("updatenow")
@owner
async def update(eve):
    repo = Repo()
    ac_br = repo.active_branch
    ups_rem = repo.remote("upstream")
    if Var.HEROKU_API:
        import heroku3

        heroku = heroku3.from_key(Var.HEROKU_API)
        heroku_app = None
        heroku_applications = heroku.apps()
        for app in heroku_applications:
            if app.name == Var.HEROKU_APP_NAME:
                heroku_app = app
        if heroku_app is None:
            await eve.edit("`Invᴀlid Kᴇy Sᴇᴛ`")
            repo.__del__()
            return
        await eve.edit(
            "`Uᴩdᴀᴛing CɪᴘʜᴇʀX ᴇxᴄlusivᴇ ʙᴏᴛ...`"
        )
        ups_rem.fetch(ac_br)
        repo.git.reset("--hard", "FETCH_HEAD")
        heroku_git_url = heroku_app.git_url.replace(
            "https://", "https://api:" + Var.HEROKU_API + "@"
        )
        if "heroku" in repo.remotes:
            remote = repo.remote("heroku")
            remote.set_url(heroku_git_url)
        else:
            remote = repo.create_remote("heroku", heroku_git_url)
        try:
            remote.push(refspec=f"HEAD:refs/heads/{ac_br}", force=True)
        except GitCommandError as error:
            await eve.edit(f"`Here is the error log:\n{error}`")
            repo.__del__()
            return
        await eve.edit("`Suᴄᴄᴇssfully Uᴩdᴀᴛᴇd!\nRᴇsᴛᴀrᴛing CɪᴘʜᴇʀX ᴇxᴄlusivᴇ ʙᴏᴛ...`")
    else:
        try:
            ups_rem.pull(ac_br)
        except GitCommandError:
            repo.git.reset("--hard", "FETCH_HEAD")
        await updateme_requirements()
        await eve.edit(
            "`Suᴄᴄᴇssfully Uᴩdᴀᴛᴇd!\nRᴇsᴛᴀrᴛing CɪᴘʜᴇʀX ᴇxᴄlusivᴇ ʙᴏᴛ...`"
        )
        execl(sys.executable, sys.executable, "-m", "cython")


@callback("changes")
@owner
async def changes(okk):
    repo = Repo.init()
    ac_br = repo.active_branch
    changelog, tl_chnglog = await gen_chlog(repo, f"HEAD..upstream/{ac_br}")
    changelog_str = changelog + f"\n\nClick the below button to update!"
    tldr_str = tl_chnglog + f"\n\nClick the below button to update!"
    if len(changelog_str) > 1024:
        await okk.edit(get_string("upd_4"))
        file = open(f"CipherX.txt", "w+")
        file.write(tldr_str)
        file.close()
        await okk.edit(
            get_string("upd_5"),
            file="CipherX.txt",
            buttons=Button.inline("Update Now", data="updatenow"),
        )
        remove(f"CipherX.txt")
        return
    else:
        await okk.edit(
            changelog_str,
            buttons=Button.inline("Update Now", data="updatenow"),
            parse_mode="html",
        )


@callback(re.compile("pasta-(.*)"))
@owner
async def _(e):
    ok = e.data_match.group(1)
    hmm = open(ok)
    hmmm = hmm.read()
    hmm.close()
    key = (
        requests.post("https://nekobin.com/api/documents", json={"content": hmmm})
        .json()
        .get("result")
        .get("key")
    )
    await e.edit(
        f"Pasted to Nekobin\n     👉[Link](https://nekobin.com/{key})\n     👉[Raw Link](https://nekobin.com/raw/{key})",
        buttons=Button.switch_inline(
            "Search Again..?",
            query="send ",
            same_peer=True,
        ),
        link_preview=False,
    )


@callback("authorise")
@owner
async def _(e):
    if not is_fullsudo(event.sender_id):
        return await e.edit("`This Command is Sudo Restricted.`")
    if not e.is_private:
        return
    if not udB.get("GDRIVE_CLIENT_ID"):
        return await e.edit(
            "Client ID and Secret is Empty.\nFill it First.",
            buttons=Button.inline("Back", data="gdrive"),
        )
    storage = await create_token_file(TOKEN_FILE, e)
    authorize(TOKEN_FILE, storage)
    f = open(TOKEN_FILE, "r")
    token_file_data = f.read()
    udB.set("GDRIVE_TOKEN", token_file_data)
    await e.reply(
        "`Success!\nYou are all set to use Google Drive with Ultroid Userbot.`",
        buttons=Button.inline("Main Menu", data="setter"),
    )


@callback("folderid")
@owner
async def _(e):
    if not is_fullsudo(event.sender_id):
        return await e.edit("`This Command is Sudo Restricted.`")
    if not e.is_private:
        return
    await e.edit(
        "Send your FOLDER ID\n\n"
        + "For FOLDER ID:\n"
        + "1. Open Google Drive App.\n"
        + "2. Create Folder.\n"
        + "3. Make that folder public.\n"
        + "4. Copy link of that folder.\n"
        + "5. Send all characters which is after id= ."
    )
    async with ultroid_bot.asst.conversation(e.sender_id) as conv:
        reply = conv.wait_event(events.NewMessage(from_users=e.sender_id))
        repl = await reply
        udB.set("GDRIVE_FOLDER_ID", repl.text)
        await repl.reply(
            "Success Now You Can Authorise.",
            buttons=get_back_button("gdrive"),
        )


@callback("clientsec")
@owner
async def _(e):
    if not is_fullsudo(e.sender_id):
        return await e.edit("`This Command is Sudo Restricted.`")
    if not e.is_private:
        return
    await e.edit("Send your CLIENT SECRET")
    async with ultroid_bot.asst.conversation(e.sender_id) as conv:
        reply = conv.wait_event(events.NewMessage(from_users=e.sender_id))
        repl = await reply
        udB.set("GDRIVE_CLIENT_SECRET", repl.text)
        await repl.reply(
            "Success!\nNow You Can Authorise or add FOLDER ID.",
            buttons=get_back_button("gdrive"),
        )


@callback("clientid")
@owner
async def _(e):
    if not is_fullsudo(e.sender_id):
        return await e.edit("`This Command is Sudo Restricted.`")
    if not e.is_private:
        return
    await e.edit("Send your CLIENT ID ending with .com")
    async with ultroid_bot.asst.conversation(e.sender_id) as conv:
        reply = conv.wait_event(events.NewMessage(from_users=e.sender_id))
        repl = await reply
        if not repl.text.endswith(".com"):
            return await repl.reply("`Wrong CLIENT ID`")
        udB.set("GDRIVE_CLIENT_ID", repl.text)
        await repl.reply(
            "Success now set CLIENT SECRET",
            buttons=get_back_button("gdrive"),
        )


@callback("gdrive")
@owner
async def _(e):
    if not e.is_private:
        return
    await e.edit(
        "Go [here](https://console.developers.google.com/flows/enableapi?apiid=drive) and get your CLIENT ID and CLIENT SECRET",
        buttons=[
            [
                Button.inline("Cʟɪᴇɴᴛ Iᴅ", data="clientid"),
                Button.inline("Cʟɪᴇɴᴛ Sᴇᴄʀᴇᴛ", data="clientsec"),
            ],
            [
                Button.inline("Fᴏʟᴅᴇʀ Iᴅ", data="folderid"),
                Button.inline("Aᴜᴛʜᴏʀɪsᴇ", data="authorise"),
            ],
            [Button.inline("« Bᴀᴄᴋ", data="otvars")],
        ],
        link_preview=False,
    )



@callback("otvars")
@owner
async def otvaar(event):
    await event.edit(
        "Other Variables to set for CɪᴘʜᴇʀX:",
        buttons=[
            [Button.inline("Tᴀɢ Lᴏɢɢᴇʀ", data="taglog")],
            [Button.inline("SᴜᴘᴇʀFʙᴀɴ", data="sfban")],
            [
                Button.inline("Sᴜᴅᴏ Mᴏᴅᴇ", data="sudo"),
                Button.inline("Hᴀɴᴅʟᴇʀ", data="hhndlr"),
            ],
            [
                Button.inline("Exᴛʀᴀ Pʟᴜɢɪɴs", data="plg"),
                Button.inline("Aᴅᴅᴏɴs", data="eaddon"),
            ],
            [
                Button.inline("Eᴍᴏᴊɪ ɪɴ Hᴇʟᴘ", data="emoj"),
                Button.inline("Sᴇᴛ ɢDʀɪᴠᴇ", data="gdrive"),
            ],
            [
                Button.inline("ʙᴏᴛ ᴍᴏᴅᴇ", data="botmode"),
                Button.inline("« Bᴀᴄᴋ", data="setter"),
            ] 
        ],
    )


@callback("emoj")
@owner
async def emoji(event):
    if not is_fullsudo(event.sender_id):
        return await event.edit("`This Command is Sudo Restricted.`")
    await event.delete()
    pru = event.sender_id
    var = "EMOJI_IN_HELP"
    name = f"Emoji in `{HNDLR}help` menu"
    async with event.client.conversation(pru) as conv:
        await conv.send_message("Send emoji you want to set 🙃.\n\nUse /cancel to cancel.")
        response = conv.wait_event(events.NewMessage(chats=pru))
        response = await response
        themssg = response.message.message
        if themssg == "/cancel":
            return await conv.send_message(
                "Cancelled!!",
                buttons=get_back_button("otvars"),
            )
        elif themssg.startswith(("/", HNDLR)):
            return await conv.send_message(
                "Incorrect Emoji",
                buttons=get_back_button("otvars"),
            )
        else:
            await setit(event, var, themssg)
            await conv.send_message(
                f"{name} changed to {themssg}\n",
                buttons=get_back_button("otvars"),
            )


@callback("plg")
@owner
async def pluginch(event):
    if not is_fullsudo(event.sender_id):
        return await event.edit("`This Command is Sudo Restricted.`")
    await event.delete()
    pru = event.sender_id
    var = "PLUGIN_CHANNEL"
    name = "Plugin Channel"
    async with event.client.conversation(pru) as conv:
        await conv.send_message(
            "Send id or username of a channel from where you want to install all plugins\n\nUse /cancel to cancel.",
        )
        response = conv.wait_event(events.NewMessage(chats=pru))
        response = await response
        themssg = response.message.message
        if themssg == "/cancel":
            return await conv.send_message(
                "Cancelled!!",
                buttons=get_back_button("otvars"),
            )
        elif themssg.startswith(("/", HNDLR)):
            return await conv.send_message(
                "Incorrect channel",
                buttons=get_back_button("otvars"),
            )
        else:
            await setit(event, var, themssg)
            await conv.send_message(
                "{} changed to {}\n After Setting All Things Do Restart".format(
                    name,
                    themssg,
                ),
                buttons=get_back_button("otvars"),
            )


@callback("hhndlr")
@owner
async def hndlrr(event):
    if not is_fullsudo(event.sender_id):
        return await event.edit("`This Command is Sudo Restricted.`")
    await event.delete()
    pru = event.sender_id
    var = "HNDLR"
    name = "Handler/ Trigger"
    async with event.client.conversation(pru) as conv:
        await conv.send_message(
            f"Send The Symbol Which you want as Handler/Trigger to use bot\nUr Current Handler is [ `{HNDLR}` ]\n\n use /cancel to cancel.",
        )
        response = conv.wait_event(events.NewMessage(chats=pru))
        response = await response
        themssg = response.message.message
        if themssg == "/cancel":
            return await conv.send_message(
                "Cancelled!!",
                buttons=get_back_button("otvars"),
            )
        elif len(themssg) > 1:
            return await conv.send_message(
                "Incorrect Handler",
                buttons=get_back_button("otvars"),
            )
        elif themssg.startswith(("/", "#", "@")):
            return await conv.send_message(
                "This cannot be used as handler",
                buttons=get_back_button("otvars"),
            )
        else:
            await setit(event, var, themssg)
            await conv.send_message(
                f"{name} changed to {themssg}",
                buttons=get_back_button("otvars"),
            )


@callback("taglog")
@owner
async def tagloggerr(event):
    if not is_fullsudo(event.sender_id):
        return await event.edit("`This Command is Sudo Restricted.`")
    await event.delete()
    pru = event.sender_id
    var = "TAG_LOG"
    name = "Tag Log Group"
    async with event.client.conversation(pru) as conv:
        await conv.send_message(
            f"Make a group, add your assistant and make it admin.\nGet the `{hndlr}id` of that group and send it here for tag logs.\n\nUse /cancel to cancel.",
        )
        response = conv.wait_event(events.NewMessage(chats=pru))
        response = await response
        themssg = response.message.message
        if themssg == "/cancel":
            return await conv.send_message(
                "Cancelled!!",
                buttons=get_back_button("otvars"),
            )
        else:
            await setit(event, var, themssg)
            await conv.send_message(
                f"{name} changed to {themssg}",
                buttons=get_back_button("otvars"),
            )

@callback("botmode")
@owner
async def pmset(event):
    await event.edit(
        "Bot Mode ~:",
        buttons=[
            [Button.inline("ʙᴏᴛ ᴍᴏᴅᴇ  Oɴ", data="onbot")],
            [Button.inline("ʙᴏᴛ ᴍᴏᴅᴇ  Oғғ", data="offbot")],
            [Button.inline("ᴏᴡɴᴇʀ ɪᴅ", data="ownerid")],
            [Button.inline("« Bᴀᴄᴋ", data="otvars")],
        ],
    )

@callback("onbot")
@owner
async def onbott(event):
    if not is_fullsudo(event.sender_id):
        return await event.edit("`This Command is Sudo Restricted.`")
    var = "BOT_MODE"
    await setit(event, var, "True")
    await event.edit(
        "Done! BOT_MODE has been turned on!!\n\n After Setting All Things Do Restart",
        buttons=get_back_button("botmode"),
    )
        
    
@callback("offbot")
@owner
async def offbott(event):
    if not is_fullsudo(event.sender_id):
        return await event.edit("`This Command is Sudo Restricted.`")
    var = "BOT_MODE"
    await setit(event, var, "False")
    await event.edit(
        "Done! BOT_MODE has been turned off!!\n\n After Setting All Things Do Restart",
        buttons=get_back_button("botmode"),
    )

@callback("ownerid")
@owner
async def ownerids(event):
    if not is_fullsudo(event.sender_id):
        return await event.edit("`This Command is Sudo Restricted.`")
    await event.delete()
    pru = event.sender_id
    var = "OWNER_ID"
    name = "Owner ID"
    async with event.client.conversation(pru) as conv:
        await conv.send_message(
            "Send id of my owner\n\nUse /cancel to cancel."
        )
        response = conv.wait_event(events.NewMessage(chats=pru))
        response = await response
        themssg = response.message.message
        if themssg == "/cancel":
            return await conv.send_message("Cancelled!!")
        else:
            await setit(event, var, themssg)
            await conv.send_message(
                "{} changed to {}\n After Setting All Things Do Restart".format(
                    name, themssg
                ),
                buttons=get_back_button("botmode"),
            )

@callback("eaddon")
@owner
async def pmset(event):
    await event.edit(
        "ADDONS~ Extra Plugins:",
        buttons=[
            [Button.inline("Aᴅᴅᴏɴs  Oɴ", data="edon")],
            [Button.inline("Aᴅᴅᴏɴs  Oғғ", data="edof")],
            [Button.inline("« Bᴀᴄᴋ", data="otvars")],
        ],
    )


@callback("edon")
@owner
async def eddon(event)
    if not is_fullsudo(event.sender_id):
        return await event.edit("`This Command is Sudo Restricted.`")
    var = "ADDONS"
    await setit(event, var, "True")
    await event.edit(
        "Done! ADDONS has been turned on!!\n\n After Setting All Things Do Restart",
        buttons=get_back_button("eaddon"),
    )


@callback("edof")
@owner
async def eddof(event):
    if not is_fullsudo(event.sender_id):
        return await event.edit("`This Command is Sudo Restricted.`")
    var = "ADDONS"
    await setit(event, var, "False")
    await event.edit(
        "Done! ADDONS has been turned off!! After Setting All Things Do Restart",
        buttons=get_back_button("eaddon"),
    )


@callback("sudo")
@owner
async def pmset(event):
    await event.edit(
        f"SUDO MODE ~ Some peoples can use your Bot which you selected. To know More use `{HNDLR}help sudo`",
        buttons=[
            [Button.inline("Sᴜᴅᴏ Mᴏᴅᴇ  Oɴ", data="onsudo")],
            [Button.inline("Sᴜᴅᴏ Mᴏᴅᴇ  Oғғ", data="ofsudo")],
            [Button.inline("« Bᴀᴄᴋ", data="otvars")],
        ],
    )


@callback("onsudo")
@owner
async def eddon(event):
    if not is_fullsudo(event.sender_id):
        return await event.edit("`This Command is Sudo Restricted.`")
    var = "SUDO"
    await setit(event, var, "True")
    await event.edit(
        "Done! SUDO MODE has been turned on!!\n\n After Setting All Things Do Restart",
        buttons=get_back_button("sudo"),
    )


@callback("ofsudo")
@owner
async def eddof(event):
    if not is_fullsudo(event.sender_id):
        return await event.edit(event, "`This Command is Sudo Restricted.`")
    var = "SUDO"
    await setit(event, var, "False")
    await event.edit(
        "Done! SUDO MODE has been turned off!! After Setting All Things Do Restart",
        buttons=get_back_button("sudo"),
    )


@callback("sfban")
@owner
async def sfban(event):
    await event.edit(
        "SuperFban Settings:",
        buttons=[
            [Button.inline("FBᴀɴ Gʀᴏᴜᴘ", data="sfgrp")],
            [Button.inline("Exᴄʟᴜᴅᴇ Fᴇᴅs", data="sfexf")],
            [Button.inline("« Bᴀᴄᴋ", data="otvars")],
        ],
    )


@callback("sfgrp")
@owner
async def sfgrp(event):
    if not is_fullsudo(event.sender_id):
        return await event.edit("`This Command is Sudo Restricted.`")
    await event.delete()
    name = "FBan Group ID"
    var = "FBAN_GROUP_ID"
    pru = event.sender_id
    async with asst.conversation(pru) as conv:
        await conv.send_message(
            f"Make a group, add @CipherXBot, send `{hndlr}id`, copy that and send it here.\nUse /cancel to go back.",
        )
        response = conv.wait_event(events.NewMessage(chats=pru))
        response = await response
        themssg = response.message.message
        if themssg == "/cancel":
            return await conv.send_message(
                "Cancelled!!",
                buttons=get_back_button("sfban"),
            )
        else:
            await setit(event, var, themssg)
            await conv.send_message(
                f"{name} changed to {themssg}",
                buttons=get_back_button("sfban"),
            )


@callback("sfexf")
@owner
async def sfexf(event):
    if not is_fullsudo(event.sender_id):
        return await event.edit("`This Command is Sudo Restricted.`")
    await event.delete()
    name = "Excluded Feds"
    var = "EXCLUDE_FED"
    pru = event.sender_id
    async with asst.conversation(pru) as conv:
        await conv.send_message(
            f"Send the Fed IDs you want to exclude in the ban. Split by a space.\neg`id1 id2 id3`\nSet is as `None` if you dont want any.\nUse /cancel to go back.",
        )
        response = conv.wait_event(events.NewMessage(chats=pru))
        response = await response
        themssg = response.message.message
        if themssg == "/cancel":
            return await conv.send_message(
                "Cancelled!!",
                buttons=get_back_button("sfban"),
            )
        else:
            await setit(event, var, themssg)
            await conv.send_message(
                f"{name} changed to {themssg}",
                buttons=get_back_button("sfban"),
            )

# Ultroid - UserBot
# Copyright (C) 2020 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

import os

from telegraph import Telegraph
from telegraph import upload_file as upl

from . import *

# --------------------------------------------------------------------#
telegraph = Telegraph()
r = telegraph.create_account(short_name="CɪᴘʜᴇʀX")
auth_url = r["auth_url"]
# --------------------------------------------------------------------#


@callback("alvcstm")
@owner
async def alvcs(event):
    await event.edit(
        "Customise your {}alive. Choose from the below options -".format(HNDLR),
        buttons=[
            [Button.inline("Aʟɪᴠᴇ Tᴇxᴛ", data="alvtx")],
            [Button.inline("Dᴇʟᴇᴛᴇ Aʟɪᴠᴇ Tᴇxᴛ", data="delvx")], 
            [Button.inline("Aʟɪᴠᴇ ᴍᴇᴅɪᴀ", data="alvmed")],
            [Button.inline("Dᴇʟᴇᴛᴇ Aʟɪᴠᴇ Mᴇᴅɪᴀ", data="delmed")],
            [Button.inline("« Bᴀᴄᴋ", data="setter")],
        ],
    )

@callback("alvtx")
@owner
async def name(event):
    if not is_fullsudo(event.sender_id):
        return await event.edit("`This Command is Sudo Restricted.`")
    await event.delete()
    pru = event.sender_id
    var = "ALIVE_TEXT"
    name = "Alive Text"
    async with event.client.conversation(pru) as conv:
        await conv.send_message(
            "**Alive Text**\nEnter the new alive text.\n\nUse /cancel to terminate the operation.",
        )
        response = conv.wait_event(events.NewMessage(chats=pru))
        response = await response
        themssg = response.message.message
        if themssg == "/cancel":
            return await conv.send_message(
                "Cancelled!!",
                buttons=get_back_button("alvcstm"),
            )
        else:
            await setit(event, var, themssg)
            await conv.send_message(
                "{} changed to {}\n\nAfter Setting All Things Do restart".format(
                    name,
                    themssg,
                ),
                buttons=get_back_button("alvcstm"),
            )

@callback("delvx")
@owner
async def dell(event):
    if not is_fullsudo(event.sender_id):
        return await event.edit("`This Command is Sudo Restricted.`")
    try:
        udB.delete("ALIVE_TEXT")
        return await event.edit("Done!", buttons=get_back_button("alvcstm"))
    except BaseException:
        return await event.edit(
            "Something went wrong...",
            buttons=get_back_button("alvcstm"),
        )

@callback("alvmed")
@owner
async def media(event):
    if not is_fullsudo(event.sender_id):
        return await event.edit("`This Command is Sudo Restricted.`")
    await event.delete()
    pru = event.sender_id
    var = "ALIVE_PIC"
    name = "Alive Media"
    async with event.client.conversation(pru) as conv:
        await conv.send_message(
            "**Alive Media**\nSend me a pic/gif/bot api id of sticker to set as alive media.\n\nUse /cancel to terminate the operation.",
        )
        response = await conv.get_response()
        try:
            themssg = response.message.message
            if themssg == "/cancel":
                return await conv.send_message(
                    "Operation cancelled!!",
                    buttons=get_back_button("alvcstm"),
                )
        except BaseException:
            pass
        media = await event.client.download_media(response, "alvpc")
        if (
            not (response.text).startswith("/")
            and not response.text == ""
            and not response.media
        ):
            url = response.text
        else:
            try:
                x = upl(media)
                url = f"https://telegra.ph/{x[0]}"
                remove(media)
            except BaseException:
                return await conv.send_message(
                    "Terminated.",
                    buttons=get_back_button("alvcstm"),
                )
        await setit(event, var, url)
        await conv.send_message(
            f"{name} has been set.",
            buttons=get_back_button("alvcstm"),
        )

@callback("delmed")
@owner
async def dell(event):
    if not is_fullsudo(event.sender_id):
        return await event.edit("`This Command is Sudo Restricted.`")
    try:
        udB.delete("ALIVE_PIC")
        return await event.edit("Done!", buttons=get_back_button("alvcstm"))
    except BaseException:
        return await event.edit(
            "Something went wrong...",
            buttons=get_back_button("alvcstm"),
        )

@callback("pmcstm")
@owner
async def alvcs(event):
    await event.edit(
        "Customise your PMPERMIT Settings -",
        buttons=[
            [
                Button.inline("Pᴍ Tᴇxᴛ", data="pmtxt"),
                Button.inline("Pᴍ Mᴇᴅɪᴀ", data="pmmed"),
            ],
            [
                Button.inline("Dᴇʟᴇᴛᴇ Pᴍ Tᴇxᴛ", data="delpmtxt"),
                Button.inline("Dᴇʟᴇᴛᴇ Pᴍ Mᴇᴅɪᴀ", data="delpmmed"),
            ],
            [
                Button.inline("Aᴜᴛᴏ Aᴘᴘʀᴏᴠᴇ", data="apauto"),
                Button.inline("PMLOGGER", data="pml"),
            ],
            [
                Button.inline("Sᴇᴛ Wᴀʀɴs", data="swarn"),
            ],
            [Button.inline("« Bᴀᴄᴋ", data="pmset")],
        ],
    )


@callback("pmtxt")
@owner
async def name(event):
    if not is_fullsudo(event.sender_id):
        return await event.edit("`This Command is Sudo Restricted.`")
    await event.delete()
    pru = event.sender_id
    var = "PM_TEXT"
    name = "PM Text"
    async with event.client.conversation(pru) as conv:
        await conv.send_message(
            "**PM Text**\nEnter the new Pmpermit text.\n\nu can use `{name}` `{fullname}` `{count}` `{mention}` `{username}` to get this from user Too\n\nUse /cancel to terminate the operation.",
        )
        response = conv.wait_event(events.NewMessage(chats=pru))
        response = await response
        themssg = response.message.message
        if themssg == "/cancel":
            return await conv.send_message(
                "Cancelled!!",
                buttons=get_back_button("pmcstm"),
            )
        else:
            if len(themssg) > 4090:
                return await conv.send_message(
                    "Message too long!\nGive a shorter message please!!",
                    buttons=get_back_button("pmcstm"),
                )
            await setit(event, var, themssg)
            await conv.send_message(
                "{} changed to {}\n\nAfter Setting All Things Do restart".format(
                    name,
                    themssg,
                ),
                buttons=get_back_button("pmcstm"),
            )


@callback("swarn")
@owner
async def name(event):
    if not is_fullsudo(event.sender_id):
        return await event.edit("`This Command is Sudo Restricted.`")
    m = range(1, 10)
    tultd = [Button.inline(f"{x}", data=f"wrns_{x}") for x in m]
    lst = list(zip(tultd[::3], tultd[1::3], tultd[2::3]))
    lst.append([Button.inline("« Bᴀᴄᴋ", data="pmcstm")])
    await event.edit(
        "Select the number of warnings for a user before getting blocked in PMs.",
        buttons=lst,
    )


@callback(re.compile(b"wrns_(.*)"))
@owner
async def set_wrns(event):
    if not is_fullsudo(event.sender_id):
        return await event.edit("`This Command is Sudo Restricted.`")
    value = int(event.data_match.group(1).decode("UTF-8"))
    dn = udB.set("PMWARNS", value)
    if dn:
        await event.edit(
            f"PM Warns Set to {value}.\nNew users will have {value} chances in PMs before getting banned.",
            buttons=get_back_button("pmcstm"),
        )
    else:
        await event.edit(
            f"Something went wrong, please check your {hndlr}logs!",
            buttons=get_back_button("pmcstm"),
        )


@callback("pmmed")
@owner
async def media(event):
    if not is_fullsudo(event.sender_id):
        return await event.edit("`This Command is Sudo Restricted.`")
    await event.delete()
    pru = event.sender_id
    var = "PMPIC"
    name = "PM Media"
    async with event.client.conversation(pru) as conv:
        await conv.send_message(
            "**PM Media**\nSend me a pic/gif/ or link  to set as pmpermit media.\n\nUse /cancel to terminate the operation.",
        )
        response = await conv.get_response()
        try:
            themssg = response.message.message
            if themssg == "/cancel":
                return await conv.send_message(
                    "Operation cancelled!!",
                    buttons=get_back_button("pmcstm"),
                )
        except BaseException:
            pass
        media = await event.client.download_media(response, "pmpc")
        if (
            not (response.text).startswith("/")
            and not response.text == ""
            and not response.media
        ):
            url = response.text
        else:
            try:
                x = upl(media)
                url = f"https://telegra.ph/{x[0]}"
                remove(media)
            except BaseException:
                return await conv.send_message(
                    "Terminated.",
                    buttons=get_back_button("pmcstm"),
                )
        await setit(event, var, url)
        await conv.send_message(
            f"{name} has been set.",
            buttons=get_back_button("pmcstm"),
        )


@callback("delpmmed")
@owner
async def dell(event):
    if not is_fullsudo(event.sender_id):
        return await event.edit("`This Command is Sudo Restricted.`")
    try:
        udB.delete("PMPIC")
        return await event.edit("Done!", buttons=get_back_button("pmcstm"))
    except BaseException:
        return await event.edit(
            "Something went wrong...",
            buttons=[[Button.inline("« Sᴇᴛᴛɪɴɢs", data="setter")]],
        )

@callback("delpmtxt")
@owner
async def dell(event):
    if not is_fullsudo(event.sender_id):
        return await event.edit("`This Command is Sudo Restricted.`")
    try:
        udB.delete("PM_TEXT")
        return await event.edit("Done!", buttons=get_back_button("pmcstm"))
    except BaseException:
        return await event.edit(
            "Something went wrong...",
            buttons=[[Button.inline("« Sᴇᴛᴛɪɴɢs", data="setter")]],
        )

@callback("apauto")
@owner
async def apauto(event):
    await event.edit(
        "This'll auto approve on outgoing messages",
        buttons=[
            [Button.inline("Aᴜᴛᴏ Aᴘᴘʀᴏᴠᴇ ON", data="apon")],
            [Button.inline("Aᴜᴛᴏ Aᴘᴘʀᴏᴠᴇ OFF", data="apof")],
            [Button.inline("« Bᴀᴄᴋ", data="pmcstm")],
        ],
    )


@callback("apon")
@owner
async def apon(event):
    if not is_fullsudo(event.sender_id):
        return await event.edit("`This Command is Sudo Restricted.`")
    var = "AUTOAPPROVE"
    await setit(event, var, "True")
    await event.edit(
        f"Done!! AUTOAPPROVE  Started!!",
        buttons=[[Button.inline("« Bᴀᴄᴋ", data="apauto")]],
    )


@callback("apof")
@owner
async def apof(event):
    if not is_fullsudo(event.sender_id):
        return await event.edit("`This Command is Sudo Restricted.`")
    try:
        udB.delete("AUTOAPPROVE")
        return await event.edit(
            "Done! AUTOAPPROVE Stopped!!",
            buttons=[[Button.inline("« Bᴀᴄᴋ", data="apauto")]],
        )
    except BaseException:
        return await event.edit(
            "Something went wrong...",
            buttons=[[Button.inline("« Sᴇᴛᴛɪɴɢs", data="setter")]],
        )


@callback("pml")
@owner
async def alvcs(event):
    await event.edit(
        "PMLOGGER This Will Forward Ur Pm to Ur Private Group -",
        buttons=[
            [Button.inline("PMLOGGER ON", data="pmlog")],
            [Button.inline("PMLOGGER OFF", data="pmlogof")],
            [Button.inline("« Bᴀᴄᴋ", data="pmcstm")],
        ],
    )


@callback("pmlog")
@owner
async def pmlog(event):
    if not is_fullsudo(event.sender_id):
        return await event.edit("`This Command is Sudo Restricted.`")
    var = "PMLOG"
    await setit(event, var, "True")
    await event.edit(
        f"Done!! PMLOGGER  Started!!",
        buttons=[[Button.inline("« Bᴀᴄᴋ", data="pml")]],
    )


@callback("pmlogof")
@owner
async def pmlogof(event):
    if not is_fullsudo(event.sender_id):
        return await event.edit("`This Command is Sudo Restricted.`")
    try:
        udB.delete("PMLOG")
        return await event.edit(
            "Done! PMLOGGER Stopped!!",
            buttons=[[Button.inline("« Bᴀᴄᴋ", data="pml")]],
        )
    except BaseException:
        return await event.edit(
            "Something went wrong...",
            buttons=[[Button.inline("« Sᴇᴛᴛɪɴɢs", data="setter")]],
        )


@callback("ppmset")
@owner
async def pmset(event):
    await event.edit(
        "PMPermit Settings:",
        buttons=[
            [Button.inline("Tᴜʀɴ PMPᴇʀᴍɪᴛ Oɴ", data="pmon")],
            [Button.inline("Tᴜʀɴ PMPᴇʀᴍɪᴛ Oғғ", data="pmoff")],
            [Button.inline("Cᴜsᴛᴏᴍɪᴢᴇ PMPᴇʀᴍɪᴛ", data="pmcstm")],
            [Button.inline("« Bᴀᴄᴋ", data="setter")],
        ],
    )


@callback("pmon")
@owner
async def pmonn(event):
    if not is_fullsudo(event.sender_id):
        return await event.edit("`This Command is Sudo Restricted.`")
    var = "PMSETTING"
    await setit(event, var, "True")
    await event.edit(
        f"Done! PMPermit has been turned on!!",
        buttons=[[Button.inline("« Bᴀᴄᴋ", data="ppmset")]],
    )


@callback("pmoff")
@owner
async def pmofff(event):
    if not is_fullsudo(event.sender_id):
        return await event.edit("`This Command is Sudo Restricted.`")
    var = "PMSETTING"
    await setit(event, var, "False")
    await event.edit(
        f"Done! PMPermit has been turned off!!",
        buttons=[[Button.inline("« Bᴀᴄᴋ", data="ppmset")]],
    )


@callback("chatbot")
@owner
async def chbot(event):
    await event.edit(
        f"From This Feature you can chat with others Via your Assistant Bot.",
        buttons=[
            [Button.inline("Cʜᴀᴛ Bᴏᴛ  Oɴ", data="onchbot")],
            [Button.inline("Cʜᴀᴛ Bᴏᴛ  Oғғ", data="ofchbot")],
            [Button.inline("Bᴏᴛ Wᴇʟᴄᴏᴍᴇ", data="bwel")],
            [Button.inline("« Bᴀᴄᴋ", data="setter")],
        ],
        link_preview=False,
    )


@callback("bwel")
@owner
async def name(event):
    if not is_fullsudo(event.sender_id):
        return await event.edit("`This Command is Sudo Restricted.`")
    await event.delete()
    pru = event.sender_id
    var = "STARTMSG"
    name = "Bot Welcome Message:"
    async with event.client.conversation(pru) as conv:
        await conv.send_message(
            "**BOT WELCOME MSG**\nEnter the mssage which you want to show when someone start your assistant Bot.\n\nUse /cancel to terminate the operation.",
        )
        response = conv.wait_event(events.NewMessage(chats=pru))
        response = await response
        themssg = response.message.message
        if themssg == "/cancel":
            return await conv.send_message(
                "Cancelled!!",
                buttons=get_back_button("chatbot"),
            )
        else:
            await setit(event, var, themssg)
            await conv.send_message(
                "{} changed to {}".format(
                    name,
                    themssg,
                ),
                buttons=get_back_button("chatbot"),
            )

    
@callback("onchbot")
@owner
async def chon(event):
    if not is_fullsudo(event.sender_id):
        return await event.edit("`This Command is Sudo Restricted.`")
    var = "PMBOT"
    await setit(event, var, "True")
    await event.edit(
        "Done! Now you Can Chat With People Via This Bot",
        buttons=[Button.inline("« Bᴀᴄᴋ", data="chatbot")],
    )


@callback("ofchbot")
@owner
async def chon(event):
    if not is_fullsudo(event.sender_id):
        return await event.edit("`This Command is Sudo Restricted.`")
    var = "PMBOT"
    await setit(event, var, "False")
    await event.edit(
        "Done! Chat People Via This Bot Stopped.",
        buttons=[Button.inline("« Bᴀᴄᴋ", data="chatbot")],
    )


@callback("vcb")
@owner
async def vcb(event):
    await event.edit(
        "By this feature you can play songs in group voice chat.",
        buttons=[
            [Button.inline("VC Sᴇssɪᴏɴ", data="vcs")],
            [Button.inline("WEBSOCKET", data="vcw")],
            [Button.inline("« Bᴀᴄᴋ", data="setter")],
        ],
        link_preview=False,
    )


@callback("vcs")
@owner
async def name(event):
    if not is_fullsudo(event.sender_id):
        return await event.edit("`This Command is Sudo Restricted.`")
    await event.delete()
    pru = event.sender_id
    var = "VC_SESSION"
    name = "VC SESSION"
    async with event.client.conversation(pru) as conv:
        await conv.send_message(
            "**Vc session**\nEnter the New session you generated for vc bot.\n\nUse /cancel to terminate the operation.",
        )
        response = conv.wait_event(events.NewMessage(chats=pru))
        response = await response
        themssg = response.message.message
        if themssg == "/cancel":
            return await conv.send_message(
                "Cancelled!!",
                buttons=get_back_button("vcb"),
            )
        else:
            await setit(event, var, themssg)
            await conv.send_message(
                "{} changed to {}\n\nAfter Setting All Things Do restart".format(
                    name,
                    themssg,
                ),
                buttons=get_back_button("vcb"),
            )


@callback("vcw")
@owner
async def name(event):
    if not is_fullsudo(event.sender_id):
        return await event.edit("`This Command is Sudo Restricted.`")
    await event.delete()
    pru = event.sender_id
    var = "WEBSOCKET_URL"
    name = "WEBSOCKET URL"
    async with event.client.conversation(pru) as conv:
        await conv.send_message(
            "**WEBSOCKET URL**\nEnter your websocket url means\n`https://{HEROKU_APP_NAME}.herokuapp.com`\nIn place of HEROKU_APP_NAME put your heroku app name\n\nUse /cancel to terminate the operation.",
        )
        response = conv.wait_event(events.NewMessage(chats=pru))
        response = await response
        themssg = response.message.message
        if themssg == "/cancel":
            return await conv.send_message(
                "Cancelled!!",
                buttons=get_back_button("vcb"),
            )
        else:
            await setit(event, var, themssg)
            await conv.send_message(
                "{} changed to {}\n\nAfter Setting All Things Do restart".format(
                    name,
                    themssg,
                ),
                buttons=get_back_button("vcb"),
            )
