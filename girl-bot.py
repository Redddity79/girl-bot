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

def pack(userId):
	with open("girls-data.txt") as file:
		urls = json.load(file)
	file.close()
	
	with open("users.txt") as file:
		users = json.load(file)
	file.close()
	
	new_pack = list(urls.keys())
	random.shuffle(new_pack)
	
	if len(new_pack)%2==1:
		new_pack.append(new_pack[0])
	new_pack = [[new_pack[i-1],new_pack[i]] for i in range(1,len(new_pack),2)]
	
	users[userId] = {"pack": new_pack, "pause": 0}
	
	with open("users.txt",'w') as file:
		file.write(json.dumps(users))
	file.close()

@dp.callback_query_handler(lambda c: c.data and c.data.startswith("b"))
async def choose(callback_query: CallbackQuery):
	id = callback_query.message["chat"]["id"]
	print(id)
	if callback_query.data[-1] == "1":
		with open("results.txt") as file:
			res = json.load(file)
		file.close()
		with open("users.txt") as file:
			users = json.load(file)
		file.close()
		a = users[str(id)]["pack"][int(users[str(id)]["pause"])]
		print(a)
		res[a[0]] += 1
		
		with open("results.txt","w") as file:
			file.write(json.dumps(res))
		file.close()
		
		users[str(id)]["pause"] = int(users[str(id)]["pause"]) + 1
		if int(users[str(id)]["pause"]) > len(users[str(id)]["pack"]):
			users[str(id)]["pause"] = 0
			await girlBot.send_message(id, "тяночки кончились, проверяй статистику (/stats)") 
		
		with open("users.txt","w") as file:
			file.write(json.dumps(users))
		file.close()
		
		with open("girls-data.txt") as file:
			urls = json.load(file)
		file.close()
		
		media = []
		try:
			for img in users[str(id)]["pack"][int(users[str(id)]["pause"])]:
				image = BytesIO(requests.get(urls[img]).content)
				media.append(InputMediaPhoto(image, img))
		except:
			img = users[str(id)]["pack"][int(users[str(id)]["pause"])]
			image = [BytesIO(requests.get(urls[img]).content), BytesIO(requests.get(urls[img]).content)]
			media.append(InputMediaPhoto(image, img))
		
		await girlBot.send_media_group(id, media)
		await girlBot.send_message(id, "кого ты выберешь? (/stats для статистики)",reply_markup=inline)
		
	if callback_query.data[-1] == "2":
		with open("results.txt") as file:
			res = json.load(file)
		file.close()
		with open("users.txt") as file:
			users = json.load(file)
		file.close()
		
		res[users[str(id)]["pack"][int(users[str(id)]["pause"])][-1]] += 1
		
		with open("results.txt","w") as file:
			file.write(json.dumps(res))
		file.close()
		
		users[str(id)]["pause"] = int(users[str(id)]["pause"]) + 1
		if int(users[str(id)]["pause"]) > len(users[str(id)]["pack"]):
			users[str(id)]["pause"] = 0
			await girlBot.send_message(id, "тяночки кончились, проверяй статистику (/stats)") 
		
		with open("users.txt","w") as file:
			file.write(json.dumps(users))
		file.close()
		
		with open("girls-data.txt") as file:
			urls = json.load(file)
		file.close()
		
		media = []
		try:
			for img in users[str(id)]["pack"][int(users[str(id)]["pause"])]:
				image = BytesIO(requests.get(urls[img]).content)
				media.append(InputMediaPhoto(image, img))
		except:
			img = users[str(id)]["pack"][int(users[str(id)]["pause"])]
			image = [BytesIO(requests.get(urls[img]).content), BytesIO(requests.get(urls[img]).content)]
			media.append(InputMediaPhoto(image, img))
		
		await girlBot.send_media_group(id, media)
		await girlBot.send_message(id, "кого ты выберешь? (/stats для статистики)",reply_markup=inline)

@dp.message_handler(commands=['stats'])
async def stats(message: Message):
	with open('results.txt') as file:
		stats = json.load(file)
	file.close()
	
	result = sorted(stats.items(), key=lambda i: i[1], reverse=True)[:10]
	
	with open("girls-data.txt") as file:
		urls = json.load(file)
	file.close()
	
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
	with open("users.txt") as file:
		users = json.load(file)
	file.close()
	
	with open("girls-data.txt") as file:
		urls = json.load(file)
	file.close()
	
	if str(message['from']['id']) not in list(users.keys()):
		pack(message['from']['id'])
		
	media = []
	for img in users[str(message["from"]["id"])]["pack"][int(users[str(message["from"]["id"])]["pause"])]:
		image = BytesIO(requests.get(urls[img]).content)
		media.append(InputMediaPhoto(image, img))
	await girlBot.send_media_group(message["from"]["id"], media)
	await girlBot.send_message(message["from"]["id"], "кого ты выберешь? (/stats для статистики)",reply_markup=inline)

executor.start_polling(dp, skip_updates=False)