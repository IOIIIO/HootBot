# Modmail

---

## Intended functionality

1. User DMs bot with complaint
2. Let user select which guild to send the complaint to.\
*(Only if user shares multiple guilds with bot)*
3. Read guild's settings on how to forward modmail.
4. Forward modmail as defined.

---

## Implemented functionality

- None

---

## Forward models

### Embed mode

Creates a read-only complaint sent to a channel for moderators to read.

1. Create embed containing the following information from the complaint:
    - Complaint content
    - Complaintant server nickname
    - Complaintant username/discriminator
    - Complaintant id
    - Time of complaint
2. Read guild's settings on which channel to forward embeds.
    - Channel ID
    - Log Channel
3. Send Embed

### Channel mode

Creates a channel for the complaint in which the moderators can interact with complaintant.

1. Create channel in guild's specified category to start mail in.
2. Run Embed mode
3. Send result to new channel
4. Forward all messages sent to this channel to the complaintant's DMs and vice versa.
5. End complaint with command sent be either party.

---