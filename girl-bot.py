from aiogram import Bot, Dispatcher, executor
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, InputMediaPhoto
import random, json, requests, config
from io import BytesIO

girlBot = Bot(token=config.TOKEN)
dp = Dispatcher(girlBot)

# inline keyboard with votes (callback data)
inline = InlineKeyboardMarkup()
b1 = InlineKeyboardButton("--- 1 ---", callback_data="b1")
b2 = InlineKeyboardButton("--- 2 ---", callback_data="b2")
inline.add(b1,b2)

u = {"girls-data": "https://api.jsonbin.io/b/600b81cea3d8a0580c350185", "results": "https://api.jsonbin.io/b/600b8241bca934583e407470", "users": "https://api.jsonbin.io/b/600b826fa3d8a0580c3501ab"}

SECRET_KEY = '$2b$10$FyaFZ3DqdWEHYUch0yU90uL.8prii18XOrTSgfC4L9hSMKzuzX6dq'

headers = {'Content-Type': 'application/json', 'secret-key': '$2b$10$FyaFZ3DqdWEHYUch0yU90uL.8prii18XOrTSgfC4L9hSMKzuzX6dq', 'versioning': 'false'}

def pack(userId):
	req = requests.get(u['girls-data'], headers=headers)
	urls = json.loads(req.text)
	
	req = requests.get(u['users'], headers=headers)
	users = json.loads(req.text)
	
	new_pack = list(urls.keys())
	random.shuffle(new_pack)
	
	if len(new_pack)%2==1:
		new_pack.append(new_pack[0])
	new_pack = [[new_pack[i-1],new_pack[i]] for i in range(1,len(new_pack),2)]
	
	users[userId] = {"pack": new_pack, "pause": 0}
	
	requests.put(u['users'], json=users, headers=headers)

@dp.callback_query_handler(lambda c: c.data and c.data.startswith("b"))
async def choose(callback_query: CallbackQuery):
	id = callback_query.message["chat"]["id"]
	print(id)
	if callback_query.data[-1] == "1":
		req = requests.get(u['results'], headers=headers)
		stats = json.loads(req.text)
		
		req = requests.get(u['users'], headers=headers)
		users = json.loads(req.text)
		
		a = users[str(id)]["pack"][int(users[str(id)]["pause"])]
		print(a)
		stats[a[0]] += 1
		
		requests.put(u['results'], json=stats, headers=headers)
		
		users[str(id)]["pause"] = int(users[str(id)]["pause"]) + 1
		if int(users[str(id)]["pause"]) > len(users[str(id)]["pack"]):
			users[str(id)]["pause"] = 0
			await girlBot.send_message(id, "тяночки кончились, проверяй статистику (/stats)")
		
		req = requests.get(u['girls-data'], headers=headers)
		urls = json.loads(req.text)
		
		media = []
		try:
			for img in users[str(id)]["pack"][int(users[str(id)]["pause"])]:
				image = BytesIO(requests.get(urls[img]).content)
				media.append(InputMediaPhoto(image, img))
		except:
			users[str(id)]["pause"] = int(users[str(id)]["pause"]) + 1
			for img in users[str(id)]["pack"][int(users[str(id)]["pause"])]:
				image = BytesIO(requests.get(urls[img]).content)
				media.append(InputMediaPhoto(image, img))
		
		requests.put(u['users'], json=users, headers=headers)
		
		await girlBot.send_media_group(id, media)
		await girlBot.send_message(id, "кого ты выберешь? (/stats для статистики)",reply_markup=inline)
		
	if callback_query.data[-1] == "2":
		req = requests.get(u['results'], headers=headers)
		stats = json.loads(req.text)
		
		req = requests.get(u['users'], headers=headers)
		users = json.loads(req.text)
		
		stats[users[str(id)]["pack"][int(users[str(id)]["pause"])][-1]] += 1
		
		requests.put(u['results'], json=stats, headers=headers)
		
		users[str(id)]["pause"] = int(users[str(id)]["pause"]) + 1
		if int(users[str(id)]["pause"]) > len(users[str(id)]["pack"]):
			users[str(id)]["pause"] = 0
			await girlBot.send_message(id, "тяночки кончились, проверяй статистику (/stats)") 
		
		req = requests.get(u['girls-data'], headers=headers)
		urls = json.loads(req.text)
		
		media = []
		try:
			for img in users[str(id)]["pack"][int(users[str(id)]["pause"])]:
				image = BytesIO(requests.get(urls[img]).content)
				media.append(InputMediaPhoto(image, img))
		except:
			users[str(id)]["pause"] = int(users[str(id)]["pause"]) + 1
			for img in users[str(id)]["pack"][int(users[str(id)]["pause"])]:
				image = BytesIO(requests.get(urls[img]).content)
				media.append(InputMediaPhoto(image, img))
		
		requests.put(u['users'], json=users, headers=headers)
		
		await girlBot.send_media_group(id, media)
		await girlBot.send_message(id, "кого ты выберешь? (/stats для статистики)",reply_markup=inline)

@dp.message_handler(commands=['stats'])
async def stats(message: Message):
	req = requests.get(u['results'], headers=headers)
	stats = json.loads(req.text)
	
	result = sorted(stats.items(), key=lambda i: i[1], reverse=True)[:10]
	
	req = requests.get(u['girls-data'], headers=headers)
	urls = json.loads(req.text)
	
	media = []
	
	for id in result:
		image = BytesIO(requests.get(urls[id[0]]).content)
		media.append(InputMediaPhoto(image, f"{id[-1]} votes - {id[0]}"))
	await girlBot.send_media_group(message["from"]["id"], media)

@dp.message_handler(commands=['contact'])
async def contact(message: Message):
	await message.reply("пишите по претензиям и прочим штукам - @woman_helper")

@dp.message_handler(commands=['start', 'vote'])
async def start(message: Message):
	req = requests.get(u['users'], headers=headers)
	users = json.loads(req.text)
	
	req = requests.get(u['girls-data'], headers=headers)
	urls = json.loads(req.text)
	
	if str(message['from']['id']) not in list(users.keys()):
		pack(message['from']['id'])
		
	media = []
	for img in users[str(message["from"]["id"])]["pack"][int(users[str(message["from"]["id"])]["pause"])]:
		image = BytesIO(requests.get(urls[img]).content)
		media.append(InputMediaPhoto(image, img))
	await girlBot.send_media_group(message["from"]["id"], media)
	await girlBot.send_message(message["from"]["id"], "кого ты выберешь? (/stats для статистики)",reply_markup=inline)

executor.start_polling(dp, skip_updates=False)