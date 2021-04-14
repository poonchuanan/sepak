from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler, ConversationHandler
from telegram.ext import messagequeue as mq
from telegram.utils.request import Request
from telegram.error import Unauthorized
import telegram
from telegram import InlineKeyboardMarkup, InlineKeyboardButton, ParseMode
from telegram.error import (TelegramError, Unauthorized, BadRequest, 
                            TimedOut, ChatMigrated, NetworkError)
import logging
import datetime
import time
from pymongo import MongoClient
import os 

TOKEN =  HEHE
client = MongoClient(HOHO)
db = client.get_database('sepak_users_db')
PORT = int(os.environ.get('PORT', 5000))

sepak_grp_id = '-493576168' #'-427210185'
ACCOUNT_MAIN, ACCOUNT_DELETE_CONFIRM, REGISTER_PASSWORD, REGISTER_ZONE, ATTENDANCE_MAIN, ATTENDANCE_STATUS, ATTENDANCE_MODIFY, NOTIFICATIONS_MAIN = range(8)
volleyball = '\ud83c\udfd0'
middle_finger = '\ud83d\udd95\ud83c\udfff'
tick = '\u2714\ufe0f'
cross = '\u2716\ufe0f'
sleep = '\ud83d\udca4'
key = '\ud83d\udd11'
stop_sign = '\ud83d\udeab'
tear = '\ud83d\udca6'

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)
logger = logging.getLogger(__name__)

def error_callback(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)
    # logger.info("User {user} sent {message}".format(user=update.message.from_user.username, message=update.message.text))

def withintwodays(date_fixed):
    day_fixed = int(date_fixed.split('/')[0])
    month_fixed = int(date_fixed.split('/')[1])
    daymonth_fixed = str(day_fixed)+'/'+str(month_fixed)+'/'
    possible_dates = []
    for i in range(0,3):
        day_check = day_fixed+i
        if day_check > 31:
            exceed_day = day_check-31
            month_check = month_fixed + 1
            if month_check > 12:
                possible_dates.append(str(exceed_day) + '/'+str(1)+'/')
            else:
                possible_dates.append(str(exceed_day) + '/'+str(month_fixed+1)+'/')
        elif day_check < 1:
            exceed_day = 31+day_check
            month_check = month_fixed - 1
            if month_check < 1:
                possible_dates.append(str(exceed_day) + '/'+str(12)+'/')
            else:
                possible_dates.append(str(exceed_day) + '/'+str(month_fixed)+'/')
        else:
            possible_dates.append(str(day_fixed+i) + '/'+str(month_fixed)+'/') 
        
    localtime = time.localtime(time.time())
    datemonth_today = str(localtime.tm_mday)+'/'+str(localtime.tm_mon)+'/'
    if datemonth_today in possible_dates:
        return True
    else:
        return False

def sort_dates(dates_to_sort):
    sorted_dates = sorted(dates_to_sort, key=lambda x: datetime.datetime.strptime(x, '%d/%m/%Y'))
    return sorted_dates

def start(update, context):
    user_id = update.message.from_user.id
    username = update.message.from_user.username
    name = update.message.from_user.first_name
    update.message.reply_text('Hi '+ name+', welcome to Sepak Takraw 2020! '+ volleyball+'\n'
                            'Here are the commands:\n\n'
                            '/account to create your account\n'
                            '/attendance to take your attendance for trainings\n'
                            '/notifications to get reminders for trainings\n')

def account(update,context):
    chat_type = update.message.chat.type
    chat_id = update.message.chat.id
    user_id = update.message.from_user.id
    username = update.message.from_user.username
    name = update.message.from_user.first_name
    users_info = db.sepak_users_info
    account_info = users_info.find_one({'user_id':user_id})
    try:
        if account_info == None:
            keyboard=[[InlineKeyboardButton("Yes", callback_data="Yes, register"),InlineKeyboardButton("No", callback_data="No")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            context.bot.send_message(user_id,'Hi '+ name+', you do not have an account. Do you want to make one?', reply_markup=reply_markup)
        else:
            name = account_info['name']
            zone = account_info['zone']
            keyboard=[[InlineKeyboardButton("Yes", callback_data="Yes, delete"),InlineKeyboardButton("No", callback_data="No")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            context.bot.send_message(user_id,'<u>Account details</u>: \n'
                                        'Name: ' + name + '\n'
                                        'Zone : '+ zone+ '\n\n'
                                        'Hey '+ name+', you already have an account. Do you want to delete it?', parse_mode=ParseMode.HTML, reply_markup=reply_markup)
        return ACCOUNT_MAIN
    except:
        keyboard=[[InlineKeyboardButton("Start chat", url="https://t.me/SepakTakrawKEbot")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text("Please start a private chat with me first.",reply_markup = reply_markup)
        # context.bot.send_message(chat_id,"a")
def account_main(update,context):
    query = update.callback_query
    user_id = query.from_user.id
    query.edit_message_text(text="Selected option: {}".format(query.data))
    if query.data == 'Yes, register':
        context.bot.send_message(user_id,'Please enter the secret key found in the sepak group to continue: ')
        return REGISTER_PASSWORD
        

    elif query.data == 'Yes, delete':
        keyboard=[[InlineKeyboardButton("Yes", callback_data="Yes, confirm delete"),InlineKeyboardButton("No", callback_data="No")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        context.bot.send_message(user_id,'<b>ARE YOU SURE?!?!?</b> This action <i>cannot</i> be undone and '
                                        'you will lose all your data.', parse_mode = ParseMode.HTML, reply_markup=reply_markup)
        return ACCOUNT_DELETE_CONFIRM

    elif query.data == 'No':
        context.bot.send_message(user_id, 'No changes were made!')
    return ConversationHandler.END

def register_password(update,context):
    user_id = update.message.from_user.id
    username = update.message.from_user.username
    name = update.message.from_user.first_name
    users_info = db.sepak_users_info
    password = update.message.text
    if password == 'zoningsucks':
        keyboard=[[InlineKeyboardButton("Zone A", callback_data="A"),
                    InlineKeyboardButton("Zone B", callback_data="B"),
                    InlineKeyboardButton("Zone C", callback_data="C")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        context.bot.send_message(user_id,'Access granted! ' +key+'\n'
                                        'Which zone are you in?\n\n'
                                        '<u>Zones</u>    <u>Blocks</u>\n'
                                        '<b>Zone A</b> - C & D\n'
                                        '<b>Zone B</b> - E, F, G & H\n'
                                        '<b>Zone C</b> - A & B', parse_mode = ParseMode.HTML, reply_markup=reply_markup)
        return REGISTER_ZONE
    else:
        context.bot.send_message(user_id, stop_sign+' Wrong password! Who dafaq are you?! ')
        return REGISTER_PASSWORD

# def wrong_password(update,context):
#     user_id = update.message.from_user.id
#     context.bot.send_message(user_id,'Wrong password! Who dafaq are you?!')
#     return ConversationHandler.END

def register_zone(update,context):
    query = update.callback_query
    user_id = query.from_user.id
    name = query.from_user.first_name
    username = query.from_user.username
    query.edit_message_text(text="Selected zone: {}".format(query.data))

    attendance = db.initial_attendance
    zone_attendance = attendance.find_one({})['zone'][query.data]

    users_info = db.sepak_users_info
    new_user = {
        'user_id':user_id,
        'name':name,
        'username':username,
        'zone':query.data,
        'attendance':zone_attendance
    }
    users_info.update_one({'user_id':user_id}, {'$set':new_user},upsert=True)
    # users_info.insert_one(new_user)
    context.bot.send_message(user_id, 'Account created!')
    context.bot.answer_callback_query(callback_query_id=query.id, text="You have created an account! \nTo delete, use /account command again.", show_alert=True)
    return ConversationHandler.END


def account_delete_confirm(update,context):
    query = update.callback_query
    user_id = query.from_user.id
    query.edit_message_text(text="Selected option: {}".format(query.data))
    if query.data == "Yes, confirm delete":
        users_info = db.sepak_users_info
        users_info.delete_one({'user_id':user_id})
        context.bot.send_message(user_id, 'Account deleted!')
    else:
        context.bot.send_message(user_id, 'HAH pussy!')
    return ConversationHandler.END

def attendance(update,context):
    user_id = update.message.from_user.id
    users_info = db.sepak_users_info
    account_info = users_info.find_one({'user_id':user_id})
    try:
        if account_info == None:
            context.bot.send_message(user_id,'Oi stupid create an account first.')
        else:
            keyboard = [[InlineKeyboardButton('Take attendance', callback_data='Take attendance'),
                            InlineKeyboardButton('Check attendance', callback_data='Check attendance')],
                            [InlineKeyboardButton('Cancel', callback_data='Cancel')]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            context.bot.send_message(user_id,'What would you like to do?', parse_mode = ParseMode.HTML, reply_markup=reply_markup)
            return ATTENDANCE_MAIN

    except Unauthorized:
        keyboard=[[InlineKeyboardButton("Start chat", url="https://t.me/SepakTakrawKEbot")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text("Please start a private chat with me first.",reply_markup = reply_markup)

def attendance_main(update,context):
    query = update.callback_query
    user_id = query.from_user.id
    query.edit_message_text(text="Selected option: {}".format(query.data))
    users_info = db.sepak_users_info
    account_info = users_info.find_one({'user_id':user_id})

    if query.data == "Cancel":
        context.bot.send_message(user_id, "No changes were made!")
        return ConversationHandler.END

    elif query.data == 'Take attendance':
        try:
            keyboard = []
            sorted_date = sort_dates(account_info['attendance'])
            for date in sorted_date:
                if withintwodays(date):
                    keyboard.append([InlineKeyboardButton(date, callback_data=date)])
            # for date, status in account_info['attendance'].items():
            #     keyboard.append([InlineKeyboardButton(date, callback_data=date)])
            keyboard.append([InlineKeyboardButton('Cancel', callback_data='Cancel')])
            reply_markup = InlineKeyboardMarkup(keyboard)
            context.bot.send_message(user_id,'Select your date. Dates shown are in <b>ZONE '+account_info['zone']+'</b>\n'
                                                'Window for attendance taking will only <u>open on the actual day</u> and closes '
                                                'in ~2 days from given date.', parse_mode = ParseMode.HTML, reply_markup=reply_markup)
            return ATTENDANCE_STATUS
        except KeyError:
            context.bot.send_message(user_id, 'Cb wait la i havent update the dates.')
            return ConversationHandler.END

    elif query.data == 'Check attendance':
        try:
            sorted_date = sort_dates(account_info['attendance'])
            attendance_status = account_info['attendance']
            # message = '<b>Here is your current attendance status</b>:\n<i>Note: '+tick+ ' means present, '+cross+' means absent and '+sleep+' means no training.</i>\n============================\n' 
            message = '<b>Here is your current attendance status</b>:\n============================\n' 
            present = 0
            total_trainings_so_far = 0
            localtime = time.localtime(time.time())
            date_today = str(localtime.tm_mday)+'/'+str(localtime.tm_mon)+'/'+str(localtime.tm_year)
            date_today = datetime.datetime.strptime(date_today, '%d/%m/%Y')
            #Check and removes all dates in the future ie show past dates so far
            for date in list(sorted_date): #list it so wont modify 
                date = datetime.datetime.strptime(date, '%d/%m/%Y') #converts to datetime object to compare
                if date_today >= date:
                    total_trainings_so_far += 1
                else:
                    date = datetime.datetime.strftime(date, '%-d/%-m/%Y')  #converts back to string (use - instead of # for unix)
                    sorted_date.remove(date)    

            for date in sorted_date:
                if attendance_status[date] == 1:
                    present += 1
                    message = message + '<b>'+date + ' : </b>' + tick + '\n'
                elif attendance_status[date] == 0:
                    message = message + '<b>'+date + ' : </b>' + cross + '\n'
                else:
                    message = message + '<b>'+date + ' : </b>' + sleep + '\n'
            # for date, status in attendance_status.items():
            #     message = message + date + ' : ' + str(status) + '\n'
            message += '============================\n'
            percentage = round(present/total_trainings_so_far*100,2)
            message += 'Attendance percentage: <b>' + str(present)+'/'+str(total_trainings_so_far)+' ('+str(percentage)+'</b>%)'
            context.bot.send_message(user_id, text=message, parse_mode = ParseMode.HTML)
            return ConversationHandler.END
        except KeyError:
            context.bot.send_message(user_id, text='There is nothing to show for now.')

def attendance_status(update,context):
    query = update.callback_query
    user_id = query.from_user.id
    query.edit_message_text(text="Selected option: {}".format(query.data))
    users_info = db.sepak_users_info
    account_info = users_info.find_one({'user_id':user_id})
    
    if query.data == "Cancel":
        context.bot.send_message(user_id, "No changes were made!")
        return ConversationHandler.END

    else:
        attendance_status = account_info['attendance'][query.data]
        if attendance_status == 0: #attendance not taken
            context.user_data['mark_attendance_date'] = query.data
            keyboard = [[InlineKeyboardButton('Yes', callback_data='Yes, mark attendance'),InlineKeyboardButton('No', callback_data='No')]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            context.bot.send_message(user_id,'You have not taken attendance for <b>'+ query.data+' </b>. Do you want to mark it as present?', parse_mode = ParseMode.HTML, reply_markup=reply_markup)
            return ATTENDANCE_MODIFY

        elif attendance_status == 1: #attendance not taken
            context.user_data['unmark_attendance_date'] = query.data
            keyboard = [[InlineKeyboardButton('Yes', callback_data='Yes, unmark attendance'),InlineKeyboardButton('No', callback_data='No')]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            context.bot.send_message(user_id,'You have already taken attendance for <b>'+ query.data+' </b>. Do you want to mark it as absent?', parse_mode = ParseMode.HTML, reply_markup=reply_markup)
            return ATTENDANCE_MODIFY

        elif attendance_status == -1: #training cancelled
            context.bot.send_message(user_id,'No training today!')
        return ConversationHandler.END    
          

def attendance_modify(update,context):
    query = update.callback_query
    user_id = query.from_user.id
    name = query.from_user.first_name
    query.edit_message_text(text="Selected option: {}".format(query.data))
    users_info = db.sepak_users_info
    account_info = users_info.find_one({'user_id':user_id})
    
    if query.data == 'Yes, mark attendance':
        date_selected = context.user_data['mark_attendance_date']
        user_update = {
            'attendance.'+date_selected : 1
        }
        users_info.update_one({'user_id':user_id}, {'$set':user_update})
        context.bot.send_message(user_id,'Your attendance on '+ date_selected + ' has been <b>marked</b>.', parse_mode = ParseMode.HTML)
        context.bot.send_message(sepak_grp_id, '<b>'+name+'</b> has <i>marked</i> their attendance for <b>'+date_selected +'</b>.', parse_mode = ParseMode.HTML, disable_notification=True)

    elif query.data == 'Yes, unmark attendance':
        date_selected = context.user_data['unmark_attendance_date']
        user_update = {
            'attendance.'+date_selected : 0
        }
        users_info.update_one({'user_id':user_id}, {'$set':user_update})
        context.bot.send_message(user_id,'Your attendance on '+ date_selected + ' has been <b>unmarked</b>.', parse_mode = ParseMode.HTML)
        context.bot.send_message(sepak_grp_id, '<b>'+name+'</b> has <i>unmarked</i> their attendance for <b>'+date_selected +'.</b>', parse_mode = ParseMode.HTML, disable_notification=True) 
    elif query.data == 'No':
        context.bot.send_message(user_id,'No changes were made!')

    return ConversationHandler.END 

def notifications(update,context):
    chat_type = update.message.chat.type
    user_id = update.message.from_user.id
    username = update.message.from_user.username
    name = update.message.from_user.first_name
    users_info = db.sepak_users_info
    account_info = users_info.find_one({'user_id':user_id})
    try:
        if account_info == None:
            context.bot.send_message(user_id,'Oi stupid create an account first.')
        else:
            try:
                notification_status = account_info['notifications']
                if notification_status == True:
                    zone = account_info['zone']
                    if zone == 'A':
                        timing = ' (Wed 6-8pm)'
                    elif zone == 'B':
                        timing = ' (Mon 9-11pm)'
                    elif zone == 'C':
                        timing = ' (Tues 5-7pm)'
                
                    keyboard=[[InlineKeyboardButton('Yes', callback_data='Yes, unsubscribe'),InlineKeyboardButton('No', callback_data='No')]]
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    context.bot.send_message(user_id,'You have subscribed to notifications for <b>Zone '+ zone + timing+'</b>.\n' 
                                                    'Would you like to unsubscribe?', parse_mode = ParseMode.HTML, reply_markup=reply_markup)
                else:
                    keyboard=[[InlineKeyboardButton('Yes', callback_data='Yes, subscribe'),InlineKeyboardButton('No', callback_data='No')]]
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    context.bot.send_message(user_id,'You have not subscribed to notifications.\n' 
                                                    'Would you like to subscribe?', reply_markup=reply_markup)
                
            except KeyError:
                keyboard=[[InlineKeyboardButton('Yes', callback_data='Yes, subscribe'),InlineKeyboardButton('No', callback_data='No')]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                context.bot.send_message(user_id,'You have not subscribed to notifications.\n' 
                                                'Would you like to subscribe?', reply_markup=reply_markup)
            
            return NOTIFICATIONS_MAIN

    except Unauthorized:
        keyboard=[[InlineKeyboardButton("Start chat", url="https://t.me/SepakTakrawKEbot")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text("Please start a private chat with me first.",reply_markup = reply_markup)

def notifications_main(update, context):
    query = update.callback_query
    user_id = query.from_user.id
    name = query.from_user.first_name
    query.edit_message_text(text="Selected option: {}".format(query.data))
    users_info = db.sepak_users_info
    account_info = users_info.find_one({'user_id':user_id})
    if query.data == 'Yes, subscribe':
        user_update = {
            'notifications':True,
        }
        users_info.update_one({'user_id':user_id}, {'$set':user_update},upsert=True)
        context.bot.send_message(user_id,'You have subscribed to notifications for <b>Zone '+ account_info['zone']+'</b>.', parse_mode=ParseMode.HTML)
        context.bot.answer_callback_query(callback_query_id=query.id, text="Notifications are sent 15 mins before training starts.\n\n"
                                                                            "May not be reliable cos limpeh no $$ for good server.", show_alert=True)
    
    elif query.data == 'Yes, unsubscribe':
        user_update = {
            'notifications':False,
        }
        users_info.update_one({'user_id':user_id}, {'$set':user_update},upsert=True)
        context.bot.send_message(user_id,'You have unsubscribed to notifications!', parse_mode=ParseMode.HTML)

    elif query.data == 'No':
        context.bot.send_message(user_id,'No changes were made!')
    return ConversationHandler.END 

def notifications_A(context):
    users_info = db.sepak_users_info
    subscribers = list(users_info.find({'zone':'A','notifications':True}))
    for person in subscribers:
        user_id = person['user_id']
        name = person['name']
        context.bot.send_message(user_id, text='Hey '+ name +'! Sepak training for zone <b>A</b> is starting soon!' , parse_mode=ParseMode.HTML)
  
def notifications_B(context):
    users_info = db.sepak_users_info
    subscribers = list(users_info.find({'zone':'B','notifications':True}))
    for person in subscribers:
        user_id = person['user_id']
        name = person['name']
        context.bot.send_message(user_id, text='Hey '+ name +'! Sepak training for zone <b>B</b> is starting soon!' , parse_mode=ParseMode.HTML)

def notifications_C(context):
    users_info = db.sepak_users_info
    subscribers = list(users_info.find({'zone':'C','notifications':True}))
    for person in subscribers:
        user_id = person['user_id']
        name = person['name']
        context.bot.send_message(user_id, text='Hey '+ name +'! Sepak training for zone <b>C</b> is starting soon!' , parse_mode=ParseMode.HTML)
   
def replymsg(update, context):
    message = update.message.text.lower().replace(" ","")
    if 'fuck' in message:
        update.message.reply_text("<b>KNN NO VULGARITIES U CB!!!!!</b> "+middle_finger, parse_mode = ParseMode.HTML)
    

def welcomemsg(update, context):
    group_id = update.effective_chat.id
    name = update.effective_message.new_chat_members[0].first_name
    context.bot.send_message(group_id,"Sup "+ name+ ", welcome to sepak takraw. Please read the description for more info.", disable_notification=True)

def zone(update, context):
    chat_id = update.message.chat.id
    user_id = update.message.from_user.id
    users_info = db.sepak_users_info
    account_info_A = list(users_info.find({'zone':'A'}))
    account_info_B = list(users_info.find({'zone':'B'}))
    account_info_C = list(users_info.find({'zone':'C'}))

    message = "<b>Zone A:</b>\n"
    for i in account_info_A:
        message += i['name'] + '\n'
    message += "<b>\nZone B:</b>\n"
    for i in account_info_B:
        message += i['name'] + '\n'
    message += "<b>\nZone C:</b>\n"
    for i in account_info_C:
        message += i['name'] + '\n'
    context.bot.send_message(chat_id, message,parse_mode=ParseMode.HTML)

def training_today(update,context):
    chat_id = update.message.chat.id
    user_id = update.message.from_user.id
    attendance = db.initial_attendance
    users_info = db.sepak_users_info

    zone_attendance_A = attendance.find_one({})['zone']['A']
    zone_attendance_B = attendance.find_one({})['zone']['B']
    zone_attendance_C = attendance.find_one({})['zone']['C']
    localtime = time.localtime(time.time())
    date_today = str(localtime.tm_mday)+'/'+str(localtime.tm_mon)+'/'+str(localtime.tm_year)

    if date_today in zone_attendance_A:
        training_today = 'Zone A'
    elif date_today in zone_attendance_B:
        training_today = 'Zone B'
    elif date_today in zone_attendance_C:
        training_today = 'Zone C'
    else:
        training_today = 'None'

    if training_today == 'None':
        context.bot.send_message(chat_id, 'No training today la',parse_mode=ParseMode.HTML)
    else:    
        message = '<b>'+ training_today +' training for ' + date_today + '</b>\n<i>Use /attendance to indicate if you are cumming</i>' + tear + tear +'\n'
        message += '<u>Current list:</u>\n'
        for i in list(users_info.find({'attendance.'+date_today:1})):
            message += i['name']+'\n'

        context.bot.send_message(chat_id, message,parse_mode=ParseMode.HTML)

def timeout(update, context):
    return ConversationHandler.END
# def viewzone(update, context):
#     users_info = db.sepak_users_info
#     account_info = users_info.find_many({'zone':'Zone A'})


# class MQBot(telegram.bot.Bot):
#     '''A subclass of Bot which delegates send method handling to MQ'''
#     def __init__(self, *args, is_queued_def=True, mqueue=None, **kwargs):
#         super(MQBot, self).__init__(*args, **kwargs)
#         # below 2 attributes provided for decorator usage
#         self._is_messages_queued_default = is_queued_def
#         self._msg_queue = mqueue or mq.MessageQueue()

#     def __del__(self):
#         try:
#             self._msg_queue.stop()
#         except:
#             pass

#     @mq.queuedmessage
#     def send_message(self, *args, **kwargs):
#         '''Wrapped method would accept new `queued` and `isgroup`
#         OPTIONAL arguments'''
#         return super(MQBot, self).send_message(*args, **kwargs)

def main():
    
    # q = mq.MessageQueue(all_burst_limit=29, all_time_limit_ms=1017)
    # request = Request(con_pool_size=8)
    # sepakbot = MQBot(TOKEN, request=request, mqueue=q)
    # Create the Updater and pass in bot's token.
    # updater = Updater(bot=sepakbot, use_context = True)

    updater = Updater(TOKEN, use_context = True)
    # Get the dispatcher to register handlers
    dp = updater.dispatcher
    # Create command handlers
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("zone", zone))
    dp.add_handler(CommandHandler("training_today", training_today))
    dp.add_error_handler(error_callback)

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('account', account),CommandHandler('attendance', attendance),CommandHandler('notifications', notifications)],

        states={
            ACCOUNT_MAIN : [CallbackQueryHandler(account_main)],
            ACCOUNT_DELETE_CONFIRM : [CallbackQueryHandler(account_delete_confirm)],
            REGISTER_PASSWORD : [MessageHandler(Filters.text, register_password)],
            REGISTER_ZONE : [CallbackQueryHandler(register_zone)],
            ATTENDANCE_MAIN : [CallbackQueryHandler(attendance_main)],
            ATTENDANCE_STATUS : [CallbackQueryHandler(attendance_status)],
            ATTENDANCE_MODIFY : [CallbackQueryHandler(attendance_modify)],
            NOTIFICATIONS_MAIN : [CallbackQueryHandler(notifications_main)],

            ConversationHandler.TIMEOUT : [MessageHandler(Filters.command, timeout),CallbackQueryHandler(timeout)]
        },

        fallbacks=[CommandHandler('account', account),CommandHandler('attendance', attendance),CommandHandler('notifications', notifications)],
        per_chat = False,
        conversation_timeout=30
    )
    dp.add_handler(conv_handler)

    dp.add_handler(MessageHandler(Filters.text, replymsg))
    dp.add_handler(MessageHandler(Filters.status_update.new_chat_members, welcomemsg))
    # Get job queue
    j = updater.job_queue

    # Set daily notifications
    notifications_A_t = datetime.time(17,45,00,000000) #5.45pm 
    dp.add_handler(CallbackQueryHandler(notifications_A))
    job_daily1 = j.run_daily(callback=notifications_A, time=notifications_A_t, days=(2,)) #WED

    notifications_B_t = datetime.time(20,45,00,000000) #8.45pm 
    dp.add_handler(CallbackQueryHandler(notifications_B))
    job_daily1 = j.run_daily(callback=notifications_B, time=notifications_B_t, days=(0,)) #MON

    notifications_C_t = datetime.time(16,45,00,000000) #4.45pm  
    dp.add_handler(CallbackQueryHandler(notifications_C))
    job_daily1 = j.run_daily(callback=notifications_C, time=notifications_C_t, days=(1,)) #TUE

    # Start the Bot
    # updater.start_polling()

    updater.start_webhook(listen="0.0.0.0",
                      port= int(PORT),
                      url_path=TOKEN)
    updater.bot.setWebhook("https://sepakbot.herokuapp.com/" + TOKEN)
    
    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()


# python -m pip install python-telegram-bot

