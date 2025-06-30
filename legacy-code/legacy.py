import asyncio

from google.cloud import secretmanager, storage

import telegram

# beyond cloud-function-base
import numpy as np
import pandas as pd
import fear_and_greed
import yfinance as yf


def access_secret(secret_name):

    secret_dict = {
        'financial-chameleon': 'the-financial-chameleon-tele-bot',
        'trading-chameleon': 'the-trading-chameleon-tele-bot',
        'crypto-chameleon': 'the-crypto-chameleon-tele-bot'
    }

    client = secretmanager.SecretManagerServiceClient()
    project_id = "the-financial-chameleon"
    secret_id = secret_dict[secret_name]
    name = f"projects/{project_id}/secrets/{secret_id}/versions/latest"
    response = client.access_secret_version(request={"name": name})

    return response.payload.data.decode('UTF-8')


def download_blob_into_memory(bucket_name, blob_name):
    # bucket_name = 'your-bucket-name'
    # blob_name = 'storage-object-name'

    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)

    blob = bucket.blob(blob_name)
    contents = blob.download_as_bytes()

    return contents

def create_decision_tables():
    columns = ['extreme fear', 'fear', 'neutral', 'greed', 'extreme greed']
    rows = ['50ma+-', '50ma', '100ma', '200ma']

    bull_decision_table = pd.DataFrame(index=rows, columns=columns)
    bear_decision_table = bull_decision_table.copy()

    bull_decision_table.loc['50ma+-', 'extreme fear'] =  f'Should I invest today \U0001F52E:\n\U0001F9D8 Get ready, the time to invest may be near.'
    bull_decision_table.loc['50ma+-', 'fear'] =  f'Should I invest today \U0001F52E:\n\U0001F9D8 Get ready, the time to invest may be near.'
    bull_decision_table.loc['50ma+-', 'neutral'] =  f'Should I invest today \U0001F52E:\n\U0001F9D8 Get ready, the time to invest may be near.'
    bull_decision_table.loc['50ma+-', 'greed'] =  f'Should I invest today \U0001F52E:\nBe patient, do not FOMO. \U0001F645\nToday is not a good day to invest.'
    bull_decision_table.loc['50ma+-', 'extreme greed'] =  f'Should I invest today \U0001F52E:\nBe patient, do not FOMO. \U0001F645\nToday is not a good day to invest.'

    bull_decision_table.loc['50ma', 'extreme fear'] =  f'Should I invest today \U0001F52E:\n\U0001F402 Opportunity is here, time to DCA!'
    bull_decision_table.loc['50ma', 'fear'] =  f'Should I invest today \U0001F52E:\n\U0001F402 Opportunity is here, time to DCA!'
    bull_decision_table.loc['50ma', 'neutral'] =  f'Should I invest today \U0001F52E:\n\U0001F9D8 Get ready, the time to invest may be near.'
    bull_decision_table.loc['50ma', 'greed'] =  f'Should I invest today \U0001F52E:\n\U0001F9D8 Get ready, the time to invest may be near.'
    bull_decision_table.loc['50ma', 'extreme greed'] =  f'Should I invest today \U0001F52E:\n\U0001F9D8 Get ready, the time to invest may be near.'

    bull_decision_table.loc['100ma', 'extreme fear'] =  f'Should I invest today \U0001F52E:\n\U0001FA78 Blood on the streets, good time to invest!'
    bull_decision_table.loc['100ma', 'fear'] =  f'Should I invest today \U0001F52E:\n\U0001FA78 Blood on the streets, good time to invest!'
    bull_decision_table.loc['100ma', 'neutral'] =  f'Should I invest today \U0001F52E:\n\U0001F402 Opportunity is here, time to DCA!'
    bull_decision_table.loc['100ma', 'greed'] =  f'Should I invest today \U0001F52E:\n\U0001F402 Opportunity is here, time to DCA!'
    bull_decision_table.loc['100ma', 'extreme greed'] =  f'Should I invest today \U0001F52E:\n\U0001F402 Opportunity is here, time to DCA!'

    bull_decision_table.loc['200ma', 'extreme fear'] =  f'Should I invest today \U0001F52E:\n\U0001FA78 Blood on the streets, good time to invest!'
    bull_decision_table.loc['200ma', 'fear'] =  f'Should I invest today \U0001F52E:\n\U0001FA78 Blood on the streets, good time to invest!'
    bull_decision_table.loc['200ma', 'neutral'] =  f'Should I invest today \U0001F52E:\n\U0001F402 Opportunity is here, time to DCA!'
    bull_decision_table.loc['200ma', 'greed'] =  f'Should I invest today \U0001F52E:\n\U0001F402 Opportunity is here, time to DCA!'
    bull_decision_table.loc['200ma', 'extreme greed'] =  f'Should I invest today \U0001F52E:\n\U0001F402 Opportunity is here, time to DCA!'



    bear_decision_table.loc['50ma+-', 'extreme fear'] =  f'Should I invest today \U0001F52E:\n\U0001F43B A bear market is always a good time to invest. Start to DCA if you have not started. \U0000E420'
    bear_decision_table.loc['50ma+-', 'fear'] =  f'Should I invest today \U0001F52E:\n\U0001F43B A bear market is always a good time to invest. Start to DCA if you have not started. \U0000E420'
    bear_decision_table.loc['50ma+-', 'neutral'] =  f'Should I invest today \U0001F52E:\n\U0001F43B A bear market is always a good time to invest. Start to DCA if you have not started. \U0000E420'
    bear_decision_table.loc['50ma+-', 'greed'] =  f'Should I invest today \U0001F52E:\n\U0001F43B A bear market is always a good time to invest. Start to DCA if you have not started. \U0000E420'
    bear_decision_table.loc['50ma+-', 'extreme greed'] =  f'Should I invest today \U0001F52E:\n\U0001F43B A bear market is always a good time to invest. Start to DCA if you have not started. \U0000E420'

    bear_decision_table.loc['50ma', 'extreme fear'] =  f'Should I invest today \U0001F52E:\n\U0001F3AF DCA if today is a huge red day.'
    bear_decision_table.loc['50ma', 'fear'] =  f'Should I invest today \U0001F52E:\n\U0001F3AF DCA if today is a huge red day.'
    bear_decision_table.loc['50ma', 'neutral'] =  f'Should I invest today \U0001F52E:\n\U0001F3AF DCA if today is a huge red day.'
    bear_decision_table.loc['50ma', 'greed'] =  f'Should I invest today \U0001F52E:\n\U0001F3AF DCA if today is a huge red day.'
    bear_decision_table.loc['50ma', 'extreme greed'] =  f'Should I invest today \U0001F52E:\n\U0001F3AF DCA if today is a huge red day.'

    bear_decision_table.loc['100ma', 'extreme fear'] =  f'Should I invest today \U0001F52E:\n\U0001F9D8 Get ready, the time to invest may be near.'
    bear_decision_table.loc['100ma', 'fear'] =  f'Should I invest today \U0001F52E:\n\U0001F9D8 Get ready, the time to invest may be near.'
    bear_decision_table.loc['100ma', 'neutral'] =  f'Should I invest today \U0001F52E:\n\U0001F9D8 Get ready, the time to invest may be near.'
    bear_decision_table.loc['100ma', 'greed'] =  f'Should I invest today \U0001F52E:\nBe patient, do not FOMO. \U0001F645\nToday is not a good day to invest.'
    bear_decision_table.loc['100ma', 'extreme greed'] =  f'Should I invest today \U0001F52E:\nBe patient, do not FOMO. \U0001F645\nToday is not a good day to invest.'

    bear_decision_table.loc['200ma', 'extreme fear'] =  f'Should I invest today \U0001F52E:\nBe patient, do not FOMO. \U0001F645\nToday is not a good day to invest.'
    bear_decision_table.loc['200ma', 'fear'] =  f'Should I invest today \U0001F52E:\nBe patient, do not FOMO. \U0001F645\nToday is not a good day to invest.'
    bear_decision_table.loc['200ma', 'neutral'] =  f'Should I invest today \U0001F52E:\nBe patient, do not FOMO. \U0001F645\nToday is not a good day to invest.'
    bear_decision_table.loc['200ma', 'greed'] =  f'Should I invest today \U0001F52E:\nBe patient, do not FOMO. \U0001F645\nToday is not a good day to invest.'
    bear_decision_table.loc['200ma', 'extreme greed'] =  f'Should I invest today \U0001F52E:\nBe patient, do not FOMO. \U0001F645\nToday is not a good day to invest.'

    return bull_decision_table, bear_decision_table

def get_fng():
    fng = fear_and_greed.get()
    fng_value, fng_desc = int(round(fng[0])), fng[1]
    return fng_value, fng_desc

def get_moving_averages(ticker):

    ticker_data = yf.Ticker(ticker)
    df = ticker_data.history(period='201d')

    df['50ma'] = df['Close'].rolling(window=50, center=False).mean()
    df['100ma'] = df['Close'].rolling(window=100, center=False).mean()
    df['200ma'] = df['Close'].rolling(window=200, center=False).mean()
    
    ma50 = df.iloc[-1]['50ma']
    ma100 = df.iloc[-1]['100ma']
    ma200 = df.iloc[-1]['200ma']
    
    return (ma50, ma100, ma200)

def is_between(price, num1, num2):
    lower_bound = min(num1, num2)
    upper_bound = max(num1, num2)
    return lower_bound < price < upper_bound

def get_siit_debug(ticker):
    ma50, ma100, ma200 = get_moving_averages(ticker)
    fng_value, fng_desc = get_fng()
    latest_close = yf.Ticker(ticker).history(period='1d').iloc[-1]['Close']

    return (ma50, ma100, ma200, fng_value, fng_desc, latest_close)

def get_siit(ticker):

    ma50, ma100, ma200 = get_moving_averages(ticker)
    fng_value, fng_desc = get_fng()
    latest_close = yf.Ticker(ticker).history(period='1d').iloc[-1]['Close']

    # determing to use bull or bear table:

    bull = True

    if ma50 > ma200:
        # bull
        decision_table = create_decision_tables()[0]
    else:
        # bear
        bull = False
        decision_table = create_decision_tables()[1]

    catch_all = False
    catch_all_msg = f'Should I invest today \U0001F52E:\nWait for a couple of days, let the market settle. \U0000E433'

    if bull:
        if latest_close < ma200:
            row = '200ma'
        elif is_between(latest_close, ma100, ma200):
            row = '100ma'
        elif is_between(latest_close, ma50, ma100):
            row = '50ma'
        elif latest_close > ma50:
            row = '50ma+-'
        else:
            catch_all = True

    else:
        # bear
        if latest_close < ma50:
            row = '50ma+-'
        elif is_between(latest_close, ma50, ma100):
            row = '50ma'
        elif is_between(latest_close, ma100, ma200):
            row = '100ma'
        elif latest_close < ma200:
            row = '200ma'
        else:
            catch_all = True

    if catch_all:
        siit = catch_all_msg
    else:
        siit = decision_table.loc[row, fng_desc]

    return siit


async def send_message(bot_name, chat_id, msg, parse_mode=None):
    token = access_secret(bot_name)
    bot = telegram.Bot(token=token)
    async with bot:
        await bot.send_message(chat_id=chat_id, text=msg, parse_mode=parse_mode)

async def send_photo(bot_name, chat_id, pic, filetype='obj', caption=None):

    valid = {'obj', 'path'}
    if filetype not in valid:
        raise ValueError(f'send_photo: filetype must bu one of {valid}')

    token = access_secret(bot_name)
    bot = telegram.Bot(token=token)

    if filetype == 'path':
        with open(pic, 'rb') as image_file:
            async with bot:
                await bot.send_photo(chat_id=chat_id, photo=image_file, caption=caption)

    elif filetype == 'obj':
        async with bot:
            await bot.send_photo(chat_id=chat_id, photo=pic, caption=caption)

# template main function
def main(request):
    # the bot to use
    # 'financial-chameleon' or 'trading-chameleon'
    bot_name = 'financial-chameleon'

    # which chat to send to
    chat_id = '@thefinancialchameleon'

    msg = get_siit('VOO')

    asyncio.run(send_message(
        bot_name=bot_name,
        chat_id=chat_id,
        msg=msg,
    ))

    debug_bot_name = 'financial-chameleon'
    debug_chat_id = '@testchameleonchannel'
    ma50, ma100, ma200, fng_value, fng_desc, latest_close = get_siit_debug('VOO')

    debug_msg = f'VOO\nLatest Close: {latest_close}\nMA50: {ma50}\nMA100: {ma100}\nMA200: {ma200}\nFNG: {fng_value}\nFNG Desc: {fng_desc}\n\nSIIT: {msg}'

    asyncio.run(send_message(
        bot_name=debug_bot_name,
        chat_id=debug_chat_id,
        msg=debug_msg
    ))

    return ('Done', 200)