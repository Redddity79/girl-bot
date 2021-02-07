from aiogram import Bot, Dispatcher, executor
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, InputMediaPhoto
import random, json, requests, config
from io import BytesIO
import base64

girlBot = Bot(token=config.TOKEN)
dp = Dispatcher(girlBot)

# inline keyboard with votes (callback data)
inline = InlineKeyboardMarkup()
b1 = InlineKeyboardButton("--- 1 ---", callback_data="b1")
b2 = InlineKeyboardButton("--- 2 ---", callback_data="b2")
inline.add(b1,b2)

def update_users(data):
	with open('users.txt', 'w') as file:
		file.write(json.dumps(data))
	file.close()

def get_users():
	with open('users.txt') as file:
		data = json.load(file)
	file.close()
	return data
#qqqqqqqqqqqqqqqqqqqqq
def update_results(data):
	with open('results.txt', 'w') as file:
		file.write(json.dumps(data))
	file.close()

def get_results():
	with open('results.txt') as file:
		data = json.load(file)
	file.close()
	return data
#qqqqqqqqqqqqqqqqqqqqq
def update_urls(data):
	with open('girls-data.txt', 'w') as file:
		file.write(json.dumps(data))
	file.close()

def get_urls():
	with open('girls-data.txt') as file:
		data = json.load(file)
	file.close()
	return data

def pack(userId):
	urls = get_urls()
	users = get_users()
	
	new_pack = list(urls.keys())
	random.shuffle(new_pack)
	
	if len(new_pack)%2==1:
		new_pack.append(new_pack[0])
	new_pack = [[new_pack[i-1],new_pack[i]] for i in range(1,len(new_pack),2)]
	
	users[userId] = {"pack": new_pack, "pause": 0}
	
	update_users(users)

@dp.callback_query_handler(lambda c: c.data and c.data.startswith("b"))
async def choose(callback_query: CallbackQuery):
	id = callback_query.message["chat"]["id"]
	
	users = get_users()
	
	if str(id) not in list(users.keys()):
		await girlBot.send_message(id,"Напиши /start")
		return
	
	if users[str(id)]["pause"] == 8888:
		await girlBot.send_message(id, "тяночки кончились, проверяй статистику (/stats)")
		return

	print(id)
	if callback_query.data[-1] == "1":
		stats = get_results()
		
		a = users[str(id)]["pack"][int(users[str(id)]["pause"])]
		print(a)
		stats[a[0]] += 1
		
		update_results(stats)
		
		users[str(id)]["pause"] = int(users[str(id)]["pause"]) + 1
		if int(users[str(id)]["pause"]) > len(users[str(id)]["pack"]):
			users[str(id)]["pause"] = 8888
			await girlBot.send_message(id, "тяночки кончились, проверяй статистику (/stats)")
		
		urls = get_urls()
		
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
		
		update_users(users)
		
		await girlBot.send_media_group(id, media)
		await girlBot.send_message(id, "кого ты выберешь? (/stats для статистики)",reply_markup=inline)
		
	if callback_query.data[-1] == "2":
		stats = get_results()
		
		a = users[str(id)]["pack"][int(users[str(id)]["pause"])]
		print(a)
		stats[a[-1]] += 1
		
		update_results(stats)
		
		users[str(id)]["pause"] = int(users[str(id)]["pause"]) + 1
		if int(users[str(id)]["pause"]) > len(users[str(id)]["pack"]):
			users[str(id)]["pause"] = 0
			await girlBot.send_message(id, "тяночки кончились, проверяй статистику (/stats)") 
		
		urls = get_urls()
		
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
		
		update_users(users)
		
		await girlBot.send_media_group(id, media)
		await girlBot.send_message(id, "кого ты выберешь? (/stats для статистики)",reply_markup=inline)

@dp.message_handler(commands=['stats'])
async def stats(message: Message):
	users = get_users()
	
	if str(message['from']['id']) not in list(users.keys()):
		await message.reply("Напиши /start")
		return
	
	if users[str(message['from']['id'])]["pause"] == 8888:
		await girlBot.send_message(message['from']['id'], "тяночки кончились, проверяй статистику (/stats)")
		return
	
	stats = get_results()
	
	result = sorted(stats.items(), key=lambda i: i[1], reverse=True)[:10]
	
	urls = get_urls()
	
	text = "--- ТОП 10 ---\n"
	
	for id in range(len(result)):
		text += f"{id+1}. vk.com/id{result[id][0]} - {result[id][-1]} votes\n"
	
	media = [InputMediaPhoto(BytesIO(requests.get(urls[result[0][0]]).content), text)]
	
	for id in result[1:]:
		image = BytesIO(requests.get(urls[id[0]]).content)
		media.append(InputMediaPhoto(image))
	await girlBot.send_media_group(message["from"]["id"], media)

@dp.message_handler(commands=['contact'])
async def contact(message: Message):
	
	await message.reply("пишите по претензиям и прочим штукам - @woman_helper")

@dp.message_handler(commands=['start', 'vote'])
async def start(message: Message):
	users = get_users()
	
	if message['from']['id'] not in list(users.keys()):
		pack(message['from']['id'])
		urls = get_urls()
			
		media = []
		for img in users[str(message["from"]["id"])]["pack"][int(users[str(message["from"]["id"])]["pause"])]:
			image = BytesIO(requests.get(urls[img]).content)
			media.append(InputMediaPhoto(image, img))
		await girlBot.send_media_group(message["from"]["id"], media)
		await girlBot.send_message(message["from"]["id"], "кого ты выберешь? (/stats для статистики)",reply_markup=inline)
		return
	
	if users[str(message['from']['id'])]["pause"] == 8888:
		await girlBot.send_message(message['from']['id'], "тяночки кончились, проверяй статистику (/stats)")
		return
	
	urls = get_urls()
		
	media = []
	for img in users[str(message["from"]["id"])]["pack"][int(users[str(message["from"]["id"])]["pause"])]:
		image = BytesIO(requests.get(urls[img]).content)
		media.append(InputMediaPhoto(image, img))
	await girlBot.send_media_group(message["from"]["id"], media)
	await girlBot.send_message(message["from"]["id"], "кого ты выберешь? (/stats для статистики)",reply_markup=inline)

executor.start_polling(dp, skip_updates=False)