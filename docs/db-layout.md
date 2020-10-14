# Database

## Tables:
- <u>***bot***</u>
    Data essential to running the bot.
    Columns follow id/name/value scheme as exposed by db.py
    - **id**
        *Dataset internal ID.*
    - **name**
        *Name given to variable stored.*
        - <u>**token**</u>
            *Bot Token*
        - <u>**owner_id**</u>
            *ID of user owning the bot*
        - <u>**prefix**</u>
            *Prefix used by the bot for interaction*
        - <u>**status**</u>
            *Status to be displayed by the bot*
        - <u>**twitter**</u>
            *Twitter bearer key for use with the API*
        - <u>**cache**</u>
            *True/False value defining whether image caching should be enabled*
        - <u>**imgur_usr**</u>
            *Imgur API User Key*
        - <u>**imgur_scr**</u>
            *Imgur API Secret Key*
    - **value**
        *Value associated with said variable.*
- <u>***starboardServers***</u>
    Data specific to servers for the Starboard cog.
    - **ignore_list**
        *Array stored as string containing message IDs that are to be ignored by the main loop*
    - **archive_channel**
        *ID of channel to send embeds to about messages reaching the threshold*
    - **archive_emote**
        *ID of emote to be used for threshold counting*
    - **archive_emote_amount**
        *Value defining the threshold*
    - **server_id**
        *ID of server to which these columns apply*
- <u>***starboardOverrides***</u>
    Data specific to channel overrides for Starboard cog.
    - **channel_id**
        *ID of channel with override applied*
    - **channel_am**
        *Threshold for the overriden channel*
- <u>***modMail***</u>
    - **server_id**
        *ID of server to which these columns apply*
    - **type**
        *1/2/3 value specifying what type of modMail is used*
        - <u>***1***</u>
            Embed mode
        - <u>***2***</u>
            Channel mode (channel)
        - <u>***3***</u>
            Channel mode (log)
        - <u>***4***</u>
            Channel mode (category)
    - **location**
        *ID of channel or category to send embed to/create the modchat thread under*
    - **anonymous**
        *True/False value on whether moderator names should be forwarded to the complaintant*
    - **enabled**
        *True/(False/None) value on whether modMail is enabled in this guild*
