# Database
---
## Tables

### bot

Data essential to running the bot.
Columns follow id/name/value scheme as exposed by db.py

- **id**
    *Dataset internal ID.*
- **name**
    *Name given to variable stored.*
    - **token**
        *Bot Token*
    - **owner_id**
        *ID of user owning the bot*
    - **prefix**
        *Prefix used by the bot for interaction*
    - **status**
        *Status to be displayed by the bot*
    - **twitter**
        *Twitter bearer key for use with the API*
    - **cache**
        *True/False value defining whether image caching should beenabled*
    - **imgur_usr**
        *Imgur API User Key*
    - **imgur_scr**
        *Imgur API Secret Key*
- **value**
    *Value associated with said variable*

### starboardServers

Data specific to servers for the Starboard cog.

- **ignore_list**
    *Array stored as string containing message IDs that are to beignored by the main loop*
- **archive_channel**
    *ID of channel to send embeds to about messages reaching thethreshold*
- **archive_emote**
    *ID of emote to be used for threshold counting*
- **archive_emote_amount**
    *Value defining the threshold*
- **server_id**
    *ID of server to which these columns apply*

### starboardOverrides

Data specific to channel overrides for Starboard cog.

- **channel_id**
    *ID of channel with override applied*
- **channel_am**
    *Threshold for the overriden channel*

---

### modMail

- **server_id**
    *ID of server to which these columns apply*
- **type**
    *1/2/3 value specifying what type of modMail is used*
    - ***1***
        Embed mode (channel)
    - ***2***
        Embed mode (log)
    - ***3***
        Channel mode (category)
- **location**
    *ID of channel or category to send embed to/create the modchatthread under*
- **anonymous**
    *True/False value on whether moderator names should be forwardedto the complaintant*
- **enabled**
    *True/(False/None) value on whether modMail is enabled in this guild*
- **ping**
    *ID of role or user to be mentioned with the message. Can be None*

### modMailOpen

- **server_id**
    *ID of server to which the channel belongs*
- **channel_id**
    *ID of the channel connected to*
- **user_id**
    *ID of the user connected to*
- **dm_id**
    *ID of the DM channel connected from*

---

