from trainfunctions import *
from helperfunctions import *
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, ConversationHandler, MessageHandler, Filters
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ChatAction, ReplyKeyboardMarkup , ParseMode
from telegram.error import TelegramError, Unauthorized, BadRequest, TimedOut, ChatMigrated, NetworkError

import logging
from dbhelper import DBHelper_users



logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


telegram_token = 'INSERT_YOUR_LONG_TELEGRAM_API_KEY_HERE'

STATION, TIME, TRAIN, DIRECTION, DONE = range(5)

userDB = DBHelper_users()
userDB.setup()

stationRes = ''
stationsRes = []
evaIDRes = ''
timeRes = ''
trainsRes = {}
trainRes = ''




def build_menu(buttons, n_cols, header_buttons=None, footer_buttons=None):
    """builds menu from list"""
    menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
    if header_buttons:
        menu.insert(0, header_buttons)
    if footer_buttons:
        menu.append(footer_buttons)
    return menu

def checkDelay(bot, job):
    """daily run job to check for delayed and cancelled trains"""
    userData = list(userDB.getDataForUserID(job.context['chat']['id']))[0]
    
    results = getDelayAndCancelled(userData[1],userData[2], userData[3], userData[4])

    if results != []:
        for result in results:
            bot.send_message(chat_id=job.context.chat_id,
                         text=result)
    else:
        bot.send_message(chat_id=job.context.chat_id, text='Yay, no delays today!')


def start(bot, update):
    """greeting message, called by /start """

    user = update['message']['chat']
    logger.info("User %s started", user.first_name)
    
    bot.send_message(chat_id=update.message.chat_id, 
                     text="*Hi, which station are you leaving from?*",
                     parse_mode=ParseMode.MARKDOWN)
    
    return STATION

def station(bot, update):
    """sends inlinekeyboard based on text answer with station, part of conv_handler flow"""

    bot.send_chat_action(chat_id=update.message.chat_id, action=ChatAction.TYPING)
    
    global stationsRes
    stationsRes = searchStations(update.message.text)
    
    reply_keyboard  = [InlineKeyboardButton(station['name'], callback_data=station['name']) for station in stationsRes]
    reply_markup = InlineKeyboardMarkup(build_menu(reply_keyboard, 1), one_time_keyboard=True)
    bot.send_message(chat_id=update.message.chat_id, text="which station exactly?", reply_markup=reply_markup)
    
    return TIME

def time(bot, update):
    """asks for time at which the user leaves, part of conv_handler flow"""

    callback = update.callback_query
    bot.send_chat_action(chat_id=callback.message.chat_id, action=ChatAction.TYPING)
    
    global stationRes
    global evaIDRes
    user = callback['message']['chat']
    stationRes = callback.data
    evaIDRes = getEvaId(stationsRes, stationRes)
    
    logger.info("User %s picked %s (%s) as station ", user.first_name, stationRes, evaIDRes)
    
    bot.edit_message_text(chat_id=callback.message.chat_id,
                          message_id=callback.message.message_id,
                          text="Great, you are starting from {}".format(stationRes)
                          )
    bot.send_chat_action(chat_id=callback.message.chat_id, action=ChatAction.TYPING)
    t.sleep(0.5)
    
    bot.send_message(chat_id=callback.message.chat_id, text="When are you usually leaving?")
    
    return TRAIN

def train(bot, update):
    """sends inlinekeyboard with possible trains leaving users station, part of conv_handler flow"""

    bot.send_chat_action(chat_id=update.message.chat_id, action=ChatAction.TYPING)
    
    global timeRes
    global evaIDRes
    global trainsRes
    global stationRes
    user = update['message']['chat']
    timeRes = timeConvert(update.message.text)
    logger.info("User %s leaves at %s", user.first_name, timeRes)
    
    bot.send_message(chat_id=update.message.chat_id, text='That\'s my favourite time, too!')
    bot.send_chat_action(chat_id=update.message.chat_id, action=ChatAction.TYPING)
    t.sleep(0.3)
    bot.send_message(chat_id=update.message.chat_id, 
                     text='Let me check which trains/busses are leaving from {}.\n This may take a while! Don\'t run away!'.format(stationRes))
    
    bot.send_chat_action(chat_id=update.message.chat_id, action=ChatAction.TYPING)
    trainsRes = returnTrains(evaIDRes)
    trainNames = list(set([train[1] for train in trainsRes]))
    reply_keyboard  = [InlineKeyboardButton(train, callback_data=train) for train in trainNames]
    reply_markup = InlineKeyboardMarkup(build_menu(reply_keyboard, 1), one_time_keyboard=True)
    bot.send_message(chat_id=update.message.chat_id, text="Which train/bus are you taking?", reply_markup=reply_markup)
    
    return DIRECTION

def direction(bot, update):
    """sends inlinekeyboard with the next stop from users station to figure out the direction, part of conv_handler flow"""

    callback = update.callback_query
    bot.send_chat_action(chat_id=callback.message.chat_id, action=ChatAction.TYPING)
    
    global trainRes
    global evaIDRes
    global trainsRes
    user = callback['message']['chat']
    trainRes = callback.data
    logger.info("User %s picked %s as train", user.first_name, trainRes)
    
    bot.edit_message_text(chat_id=callback.message.chat_id,
                          message_id=callback.message.message_id,
                          text="Understood, you ride with {}".format(trainRes)
                          )
    bot.send_chat_action(chat_id=callback.message.chat_id, action=ChatAction.TYPING)
    t.sleep(0.5)
    
    directions = list(set([train[3] for train in trainsRes]))
    nextStops = getNextStops(evaIDRes, directions)[0]
    
    reply_keyboard  = [InlineKeyboardButton(stop, callback_data=stop) for stop in nextStops]
    reply_markup = InlineKeyboardMarkup(build_menu(reply_keyboard, 1), one_time_keyboard=True)
    text="What is the first stop of the {}?".format(trainRes)
    bot.send_message(chat_id=callback.message.chat_id, text=text, reply_markup=reply_markup)
    
    return DONE
    
def done(bot, update):
    """success statement, writes into userDB, starts jobQueue, part of conv_handler flow"""

    callback = update.callback_query
    bot.send_chat_action(chat_id=callback.message.chat_id, action=ChatAction.TYPING)
    
    global stationRes
    global evaIDRes
    global timeRes
    global trainRes
    global directionRes
    user = callback['message']['chat']
    directionRes = callback.data
    logger.info("User %s picked %s as direction", user.first_name, directionRes)
    
    bot.edit_message_text(chat_id=callback.message.chat_id,
                          message_id=callback.message.message_id,
                          text="Thanks, you picked {}".format(directionRes)
                          )
    bot.send_chat_action(chat_id=callback.message.chat_id, action=ChatAction.TYPING)
    t.sleep(0.5)

    bot.send_message(chat_id=callback.message.chat_id, 
                     text="OK, good. All is set! I will check for delayed and cancelled trains from now on!")
    if list(userDB.getDataForUserID(user.id)) == []:
        userDB.addUser(user.id, stationRes, evaIDRes, timeRes, trainRes, directionRes)
    else:
        userDB.updateUser(user.id, stationRes, evaIDRes, timeRes, trainRes, directionRes)
  
    jobQueue.run_daily(checkDelay, (datetime.time(*t.strptime(timeRes, '%H:%M:%S')[:6])+datetime.timedelta(minutes=-20)).time(), context=callback.message)

def runJob(bot, update):
    jobQueue.run_once(checkDelay, 0, context=update.message)

def fallback(bot, update):
    user = update['message']['chat']
    logger.info("User %s did something strange...", user.first_name)
    bot.send_message(chat_id=update.message.chat_id, text="Huh, what did you do? Please /start again!")
    
conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],

        states={
            STATION: [MessageHandler(Filters.text, station)],

            TIME: [CallbackQueryHandler(time)],
            
            TRAIN: [MessageHandler(Filters.text, train)],
            
            DIRECTION: [CallbackQueryHandler(direction)],
            
            DONE: [CallbackQueryHandler(done)]
        },

        fallbacks=[CommandHandler('fallback', fallback)]
    )


def error_callback(bot, update, error):
    try:
        raise error
    except Unauthorized:
        # remove update.message.chat_id from conversation list
        pass
    except BadRequest:
        # handle malformed requests - read more below!
        pass
    except TimedOut:
        # handle slow connection problems
        pass
    except NetworkError:
        # handle other connection problems
        pass
    except ChatMigrated as e:
        # the chat_id of a group has changed, use e.new_chat_id instead
        pass
    except TelegramError:
        # handle all other telegram related errors
        pass

updater = Updater(token=telegram_token)
jobQueue = updater.job_queue

runJobHandler = CommandHandler('runJob', runJob)

updater.dispatcher.add_handler(conv_handler)
updater.dispatcher.add_error_handler(error_callback)
updater.dispatcher.add_handler(runJobHandler)

def startBot():
    updater.start_polling()
    updater.idle()