import configparser
import json
import asyncio
import pandas as pd
import re

from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError
from telethon.tl.functions.messages import GetHistoryRequest
from telethon.tl.types import (
    PeerChannel
)

# Setting configuration values
api_id = 24864343
api_hash = 'a778eb81abfdf6a16597a619e6bc0e62'
api_hash = str(api_hash)
phone = '+13128025707'
username = "merizulan"

# Create the client and connect
client = TelegramClient(username, api_id, api_hash)

async def main(phone):
    await client.start()
    print("Client Created")
    # Ensure you're authorized
    if await client.is_user_authorized() == False:
        await client.send_code_request(phone)
        try:
            await client.sign_in(phone, input('Enter the code: '))
        except SessionPasswordNeededError:
            await client.sign_in(password=input('Password: '))

    me = await client.get_me()

    user_input_channel = input("enter entity(telegram URL or entity id):")

    if user_input_channel.isdigit():
        entity = PeerChannel(int(user_input_channel))
    else:
        entity = user_input_channel

    my_channel = await client.get_entity(entity)

    offset = 0
    limit = 100
    all_messages = []

    while True:
        messages = await client(GetHistoryRequest(
            peer=my_channel,
            offset_id=0,
            offset_date=None,
            add_offset=offset,
            limit=limit,
            max_id=0,
            min_id=0,
            hash=0
        ))
        if not messages.messages:
            break
        all_messages.extend(messages.messages)
        offset += len(messages.messages)

    messages_first =  all_messages[::-1]
    #print(messages_first)
    all_message_details = []
    all_id = []
    for message in messages_first:
        if message.from_id is None:
            continue
        elif not message.message:
            continue
        else:
            links = re.findall('(?:(?:https?|ftp):\/\/)?[\w/\-?=%.]+\.[\w/\-?=%.]+', str(message.message))
            from_id = re.findall('[0-9]+', str(message.from_id))
            [all_message_details.append(
                {"sender":from_id[0], 
                "date": message.date, 
                "message": message.message,
                "links":links}) if from_id[0] not in all_id else print("already in list")]
            all_id.append(from_id[0])
    #with open('message_data.json', 'w') as outfile:
    #    json.dump(all_message_details, outfile)

    filename = user_input_channel.replace("/","_").replace(":","")
    df = pd.DataFrame(all_message_details)
    df.to_csv('messages_'+filename+'.csv', index = True) # column names ekler

with client:
    client.loop.run_until_complete(main(phone))
