import logging
import asyncio

from aiogram import Bot, Dispatcher, executor, types
from DataBase import SQL
from Parse import Parsing

#logs level
logging.basicConfig(level=logging.INFO)

#bot init
bot = Bot(token="1329191191:AAEsWQ9JBOMv2cUZTufiNHBdJWCahTP2EBM")
dp = Dispatcher(bot)

#db init
db = SQL('db.db')

#init parse
sg = Parsing('lastkey.txt')
    
#sub activation
@dp.message_handler(commands=['subscribe'])
async def subscribe(message: types.message):
    if(not db.subscriber_exists(message.from_user.id)):
        db.add_subscriber(message.from_user.id)
    else:
        db.update_subscription(message.from_user.id, True)
        
    await message.answer("Вы подписаны")
    
#unsub activation
@dp.message_handler(commands=['unsubscribe'])
async def unsubscribe(message: types.message):
    if(not db.subscriber_exists(message.from_user.id)):
        db.add_subscription(message.from_user.id, False)
        await message.answer("йоу, ты и так не подписан")
    else:
        db.update_subscription(message.from_user.id, False)
        await message.answer("Пока пока")
        
#Check new game and get new game
async def scheduled(wait_for):
    while True:
        await asyncio.sleep(wait_for)

        new_games = sg.new_games()

        if(new_games):
            new_games.reverse()
            for ng in new_games:
                nfo = sg.game_info(ng)

                subscriptions = db.get_subscriptions()

                with open(sg.download_image(nfo['image']), 'rb') as photo:
                    for s in subscriptions:
                        await bot.send_photo(
                            s[1],
                            photo,
                            caption = nfo['title'] + "\n" + "Оценка: " + nfo['score'] + "\n" + nfo['excerpt'] + "\n\n" + nfo['link'],
                            disable_notification = True
                        )
                
                sg.update_lastkey(nfo['id'])

if __name__ == '__main__':
    dp.loop.create_task(scheduled(10))
    executor.start_polling(dp, skip_updates=False)