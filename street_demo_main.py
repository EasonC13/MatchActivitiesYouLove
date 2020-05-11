import configparser
import logging

import telegram
from flask import Flask, request
from telegram import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove
from telegram.ext import Dispatcher, CommandHandler, MessageHandler, Filters, InlineQueryHandler, CallbackQueryHandler
from time import sleep
import time
from easonc.JsonProcessor import dict_to_obj, obj_to_dict
import numpy as np
from numpy.random import randint

config = configparser.ConfigParser()
config.read('/home/eason/Python/config/config.ini')



# Initial Flask app
app = Flask(__name__)

# Initial bot by Telegram access token
bot = telegram.Bot(token=(config['TELEGRAM']['ACCESS_TOKEN_FOR_EYON']))

# New a dispatcher for bot
dispatcher = Dispatcher(bot, None)

path = "/home/eason/Python/"

userPreference = {}
userSendingLocation = {}

# Enable logging
import datetime
ISOTIMEFORMAT = '%Y-%m-%d_%H:%M'
DateTime = datetime.datetime.now().strftime(ISOTIMEFORMAT)

logging.basicConfig(filename=path + "log/"+DateTime+".log", filemode='a',
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

logKey = []
@app.route('/log/<string:key>')
def get_log(key):
    if key in logKey:
        logKey.remove(key)
        return str("<br>".join(open(path + "log/"+DateTime+".log", 'r').readlines()))
    else:
        return "Auth fail."

import hashlib
import time
def key_generator():
    return hashlib.sha224(datetime.datetime.now().strftime(ISOTIMEFORMAT).encode("utf-8")).hexdigest()
def log_handler(bot, update):
    key = hashlib.sha224(datetime.datetime.now().strftime(ISOTIMEFORMAT).encode("utf-8")).hexdigest()
    temp = update.message.reply_text(text = "https://gcp4-2.easonc.tw/log/"+key)
    logKey.append(key)
    #time.sleep(30)
    #bot.edit_message_text(chat_id=temp.chat.id, message_id=temp.message_id, text = "The Admin command is time out.")
    
    try:
        #logKey.remove(key)
        pass
    except:
        pass











def user_setup(update):
    update.message.reply_text("請問你對於「藝術展覽」的喜好程度？", reply_markup=make_init_quiz_interface())
    
quiz_context = ['藝術展覽', '美食', '搖滾音樂', '街頭魔術表演', '武術體操']


def make_init_quiz_interface(front_data=""):
    option_context = ['非常不喜歡', '不喜歡', '普通', '喜歡', '非常喜歡']
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                str(i) + '.' + option_context[i - 1],
                callback_data='/quizdata,' + front_data + (',' if front_data!="" else '') + str(i))
            ] for i in range(5, 0, -1)
        ]
    )


def callback_handler(bot, update):
    """handle callback"""
    # TODO need route design
    query = update.callback_query
    chat_id = query.message.chat_id
    print(query.data)
    raw_data = query.data.replace("/quizdata,", "")
    if len(raw_data.split(",")) < len(quiz_context):
        print(len(raw_data.split(",")))
        query.edit_message_text(
            text="請問你對於「{}」的喜好程度？".format(quiz_context[len(raw_data.split(","))]),
            reply_markup=make_init_quiz_interface(raw_data))
    else:
        # analysis
        print(query)
        bot.delete_message(chat_id=query.message.chat_id, message_id=query.message.message_id)
        bot.send_message(chat_id = query.message.chat_id, text = "感謝你的回答！\n請按下尋找附近的藝文活動按鈕，開始一場街頭藝文探索之旅吧！", reply_markup=KeyBoards.default)
        print(raw_data)
        likely = raw_data.split(",")
        userPreference[chat_id] = likely
        print(userPreference[chat_id])
        #query.edit_message_text(text = "設定完成")
        #query.edit_message_text(text="你已選擇了: {}選項，等待分析".format(raw_data))

Messages = {
    "welcome_message" : """
歡迎使用~
我將媒合你愛的街頭藝文！
在此之前，我需要知道你的喜好。
請回答下列問題，讓我更認識你：""",

    "hello_message" : """
哈囉！
老客戶用 /start 指令
你是在哈囉嗎？
需要幫助歡迎選擇 /help
    """,

    "help_message" : """
R 
就是R
其實這個部分還沒寫啦
因為我們還沒做完嘛...這只是展示品

所以/help並未開放喔！
p.s 你怎麼進來的(?)

但你還是可以用 /start 
來取得指引喔！""",
    "howToUse" : """
1. 按下「尋找在附近的藝文活動」
2. 傳送GPS座標(請用手機版Telegram)
3. 對於我推薦的藝文活動，選擇感/不感興趣
4. 找到感興趣的後，點下地圖圖案，即可選擇Directions，使用地圖導航前往目的地
5. 前往目的地後，享受街頭表演吧！
6. 針對推薦的表演，我們會詢問你的評價，來改進我們的推薦內容。"""}
Messages = dict_to_obj(Messages)

location_keyboard = telegram.KeyboardButton(text="📡 傳送定位資訊", request_location=True)
phone_keyboard = telegram.KeyboardButton(text="📞 綁定手機號碼", request_contact=True)
cancel_keyboard = telegram.KeyboardButton(text="❌ 取消")

KeyBoards = {
    "default" : ReplyKeyboardMarkup([['🔍 尋找在附近的藝文活動'],
                                     ['❓ 如何使用'],
                                     ['🛠 個人設定', "🔄 恢復初始狀態"],
                                     ['🐛 錯誤回報', '✉️ 聯絡作者'], 
                                     ["❓ 關於本機器人"]], resize_keyboard= True),
    "testing" : ReplyKeyboardMarkup([["好的，讓我們開始吧！"]]),
    "request_location" : ReplyKeyboardMarkup([[location_keyboard], [cancel_keyboard]], resize_keyboard= True),
    "request_phone" : ReplyKeyboardMarkup([[phone_keyboard], [cancel_keyboard]], resize_keyboard= True),
    "decide_go_or_not" : ReplyKeyboardMarkup([['⭕️ 我要去'],['❌ 沒興趣，請給我其他活動']], resize_keyboard= True),
    "rate_score" : ReplyKeyboardMarkup([['1'], ['2'], ['3'], ['4'], ['5']]),
    "start" : ReplyKeyboardMarkup([["請按照上方提示作答"]], resize_keyboard= True),
}
KeyBoards = dict_to_obj(KeyBoards)

def send_photos(update, photos, path=path):
    #chat_id = 555773901
    chat_id = update.message.chat.id
    for photo in photos:
        bot.send_photo(chat_id, photo=open(path + photo, 'rb'))

aa = []

def getUserInfo(update):
    userinfo = "%d"%(update.message.chat.id)
    try:
        userinfo += " (@"+update.message.chat.username+') '
        userinfo += update.message.chat.first_name+ " "
        userinfo += update.message.chat.last_name
    except:
        pass
    return userinfo

def reply_processor(update):
    #logger.info('Update "%s" caused error:\nERROR: %s', update, "None")
    text = update.message.text
    reply_text = update.message.reply_text
    chat_id = update.message.chat.id
    aa.append(update)
    userinfo = getUserInfo(update)
    userinfo += " Send: %s"%(text)
    logger.info('user %s'%(userinfo))
    if "eason" in text:
        reply_text("叭叭！@IshengChen 有人叫你啊")
        
    elif text == "...好喔":
        reply_text("嘻嘻，謝謝你的包容", reply_markup=KeyBoards.default)
        
    elif text == "❓ 如何使用":
        reply_text(Messages.howToUse)
        
    elif text == '🐛 錯誤回報' or text == '✉️ 聯絡作者':
        reply_text("請直接聯絡師大特勤隊代表 @EasonC13\nEmail: pricean01@gmail.com")
        
    elif text == "🛠 個人設定":
        reply_text("此功能目前未開放。", reply_markup=KeyBoards.default)
        
    elif text == "🔍 尋找在附近的藝文活動":
        #reply_text("請問你想尋找的活動類型？(還沒寫)", reply_markup=KeyBoards.request_location)
        reply_text("目前僅支援手機版，電腦版無法使用\n\n請提供您的定位資訊：\n(建議開啟GPS以取得最佳體驗)", reply_markup=KeyBoards.request_location)
        userSendingLocation[chat_id] = True
        
    elif text == "❌ 取消":
        reply_text("收到", reply_markup=KeyBoards.default)
        
    elif text == "❓ 關於本機器人":
        reply_text("本聊天機器人將帶領你，\n尋找你喜歡的街頭藝人、藝文活動。\n請趕快安裝Telegram並掃描QR碼，\n來體驗我的原型產品吧！", reply_markup=KeyBoards.default)
        send_photos(update, ["/Pictures/StreetQR.PNG"])
    
    elif text == "❌ 沒興趣，請給我其他活動":
        recommand_handler(update)
        
        
    elif text == "⭕️ 我要去":
        reply_text("祝您觀賞愉快，\n可直接點選上面的地圖做導航喔！", reply_markup=KeyBoards.default)
        ProcessingQueue.remove(chat_id)
        sleep(20)
        ProcessingQueue.append(chat_id)
        #reply_text("詢問結果", reply_markup=KeyBoards.rate_score)
        
    elif text == "🏆查看排名":
        reply_text("目前排名：\nhttps://gcp1.easonc.tw/rank")
        
    elif text == "error":
        int("hi")
        
    elif text == "🔄 恢復初始狀態":
        reply_text("此功能為測試階段專用，方便使用者清空資訊，測試不同的初始偏好選擇所產生的不同AI推薦結果。\n\n如確認重設請按 /start")
    
    elif text == "請按照上方提示作答":
        pass #start時會使用的
    else:
        reply_text("聽不懂QQ", reply_markup=KeyBoards.default)
        
    return True

Recommending = {}
userLocation = {}
def found_preference(update):
    chat_id = update.message.chat.id
    try:
        return Recommending[chat_id].pop(0)[1:]
    except:
        try: #creating prefer
            prefer =  userPreference[chat_id]
            likely = []
            for i in range(len(prefer)):
                likely.append(prefer[i]+quiz_context[i])
            likely.sort(reverse = True)
            out = likely.pop(0)
            Recommending[chat_id] = likely
            return out[1:]
        except: #no prefer, random recommend
            out = quiz_context[randint(len(quiz_context))]
            return out
def recommand_handler(update):
        
    chat_id = update.message.chat.id
    
    try:
        latitude, longitude = update.message.location.latitude, update.message.location.longitude
        userLocation[chat_id] = [latitude, longitude]
        print("update user %d location:"%(chat_id), userLocation[chat_id])
    except:
        pass

    preference = found_preference(update)
    if preference == '藝術展覽':
        bot.send_location(chat_id, 25.027807, 121.530412)
        update.message.reply_text("在台師大美術館，\n「師大攝影社」正在辦展覽。\n今日主題：「山的一百種顏色」",
                                  reply_markup = KeyBoards.decide_go_or_not)
        send_photos(update, ["/Pictures/山的一百種顏色.jpg"])
        pass    
    elif preference == '美食':
        bot.send_location(chat_id, 25.025296, 121.527956)
        update.message.reply_text("在台師大日光大道，\n「師大美食社」正在辦活動。\n今日主題：「五分鐘DIY馬卡龍體驗」",
                                  reply_markup = KeyBoards.decide_go_or_not)
        send_photos(update, ["/Pictures/馬卡龍.jpg"])
        pass
    elif preference == '搖滾音樂':
        bot.send_location(chat_id, 25.0301335, 121.5354529)
        update.message.reply_text("在大安森林公園露天音樂台，\n樂團「師大吉他社」正在演出。\n今日主題：「搖滾青春」",
                  reply_markup = KeyBoards.decide_go_or_not)
        send_photos(update, ["/Pictures/GutlarClub.jpg"])
    elif preference == '街頭魔術表演':
        bot.send_location(chat_id, 25.027429, 121.529123)
        update.message.reply_text('在台師大羅馬廣場，\n街頭魔術師「Eason」正在表演。\n今日主題：「帽子裡除了鴿子，還能跑出什麼？」',
                                  reply_markup = KeyBoards.decide_go_or_not)
        send_photos(update, ["/Pictures/魔術師.jpg"])
        pass
    elif preference == '武術體操':
        bot.send_location(chat_id, 25.027429, 121.529123)
        update.message.reply_text('在台師大羅馬廣場，\n街頭藝人「陳怡升」正在表演武術。\n今日主題：「洪拳三寶：工字伏虎拳」',
                                  reply_markup = KeyBoards.decide_go_or_not)
        send_photos(update, ["/Pictures/工字伏虎.jpg"])














#replace



from os import listdir
from os.path import isfile, join

def get_photo_files():
    #mypath = "/home/eason/Python/ChatBot/User_ChatBot_demo/Pictures/"
    mypath = ""
    onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]
    return onlyfiles

Photos = {
    "cloud" : ['(體驗天氣3)雲種1.PNG', "(體驗天氣3)雲種2.PNG", "(體驗天氣3)雲種3.PNG"],
    "air_quality" : ["(體驗天氣2)空氣品質.PNG", "(天氣賭盤2)空品等級.PNG"],
    "all" : "",#get_photo_files()
}

Photos = dict_to_obj(Photos)

def get_rate_inline_board():
    out = []
    for i in range(10, 50, 10):
        i = float(i/10)
        out.append(str(i))
    return [out]

rate_board = ReplyKeyboardMarkup(get_rate_inline_board(), resize_keyboard = True, one_time_keyboard = True, selective = True)


@app.route('/hook', methods=['POST'])
def webhook_handler():
    """Set route /hook with POST method will trigger this method."""
    if request.method == "POST":
        update = telegram.Update.de_json(request.get_json(force=True), bot)
        dispatcher.process_update(update)
    return 'ok'

@app.route('/validation/<string:name>')
def validation_demo(name = "Default"):
    """provide fake validation for our demo"""
    return 'Validation successful for account %s.  \n 您的帳號 %s 已經驗證成功'%(name,name)

@app.route('/rank')
def get_rank():
    print(websites.send_sorted_text())
    return websites.send_sorted_text()

def start_handler(bot, update):
    """Send a message when the command /start is issued."""
    already_in_use = False
    #print("ST")
    if already_in_use:
        update.message.reply_text(Messages.hello_message, reply_markup=KeyBoards.default)
    else:
        update.message.reply_text(Messages.welcome_message, reply_markup=KeyBoards.start)
        user_setup(update)
        

def help_handler(bot, update):
    """Send a message when the command /help is issued."""
    update.message.reply_text(Messages.help_message, reply_markup = ReplyKeyboardMarkup([["...好喔"]]) )
    


def send_typing_action(update):
    """Show the bot is typing to user."""
    bot.send_chat_action(chat_id=update.message.chat.id, action=telegram.ChatAction.TYPING)


def location_handler(bot, update):
    
    chat_id = update.message.chat.id
    try: #先全開，有的平台好像不會默認回覆
        if userSendingLocation[chat_id] == True:#update.message.reply_to_message.text == "請提供您的定位資訊：\n(建議開啟GPS以取得最佳體驗)":
            ProcessingQueue.append(chat_id)
            temp = update.message.reply_text('請稍後，正在尋找您附近的藝文活動')
            send_typing_action(update)

            sleep(1)

            recommand_handler(update)

            bot.delete_message(chat_id=temp.chat.id, message_id=temp.message_id)
            bot.delete_message(chat_id=update.message.chat.id, message_id=update.message.message_id)

            ProcessingQueue.remove(chat_id)
            userSendingLocation[chat_id] = False
        else:
            update.message.reply_text('請使用尋找在附近的藝文活動，來傳送位置。\n\n提醒您，請勿輸入非鍵盤或聊天機器人提示您輸入的資訊，以免系統出錯。')
    except:
        update.message.reply_text('請使用尋找在附近的藝文活動，來傳送位置。\n\n提醒您，請勿輸入非鍵盤或聊天機器人提示您輸入的資訊，以免系統出錯。')
    
def send_photo(chat_id, photos, path = "/home/eason/Python/ChatBot/User_ChatBot_demo/Pictures/"):
    for photo in photos:
        bot.send_photo(chat_id, photo=open(path + photo, 'rb'))
        






ProcessingQueue = []
def reply_handler(bot, update):
    """Reply message."""
    chat_id = update.message.chat.id
    if chat_id not in ProcessingQueue:
        ProcessingQueue.append(chat_id)
        send_typing_action(update)
        reply_processor(update)
        ProcessingQueue.remove(chat_id)
        

def error_handler(bot, update, error):
    """Log Errors caused by Updates."""
    chat_id = update.message.chat.id
    logger.error('Update "%s" caused error:\nERROR: %s', update, error)
    notCatch = True
    running = "no"
    if notCatch == True:
        try:
            latitude, longitude = update.message.location.latitude, update.message.location.longitude
            print("ready to reply")
            update.message.reply_text(text = "請使用尋找在附近的藝文活動，來傳送位置。\n\n提醒您，請勿輸入非鍵盤或聊天機器人提示您輸入的資訊，以免系統出錯。")
            try:
                ProcessingQueue.remove(chat_id)
            except:
                print("P")
            notCatch = False
            running = "yes"
            print(notCatch, chat_id)
        except:
            pass
        
    print("I'm here", notCatch, running)
    if notCatch == True:
        print("and I'm in here")
        update.message.reply_text(text = '對不起，系統錯誤\n歡迎回報，告訴開發者 @EasonC13，你剛剛按了什麼\n\n提醒您，請勿輸入非鍵盤或聊天機器人提示您輸入的資訊，以免系統出錯。')
        try:
            ProcessingQueue.remove(chat_id)
        except:
            pass



# Add handler for handling message, there are many kinds of message. For this handler, it particular handle text
# message.

dispatcher.add_handler(CallbackQueryHandler(callback_handler, pattern='/quizdata,'))
dispatcher.add_handler(CommandHandler('start', start_handler))
dispatcher.add_handler(CommandHandler('help', help_handler))
dispatcher.add_handler(CommandHandler('log', log_handler))
dispatcher.add_handler(MessageHandler(Filters.location, location_handler))
dispatcher.add_handler(MessageHandler(Filters.text, reply_handler))
dispatcher.add_error_handler(error_handler)





from waitress import serve
if __name__ == "__main__":
    app.run(port = 5002, threaded = True)
    #, ssl_context=("/home/fio/myCA/server_crt.pem","/home/fio/myCA/server_key.pem"))
    
#https://api.telegram.org/bot950339862:AAEojb4NXp-GhVwmms1F0QXn3KC6tEJs4AQ/setWebhook?url=https://gcp1.easonc.tw/hook


#把他Hook起來以後，才會有用