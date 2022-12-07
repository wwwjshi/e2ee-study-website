'''
    Our Model class
    This should control the actual "logic" of your website
    And nicely abstracts away the program logic from your page loading
    It should exist as a separate layer to any database or data structure that you might be using
    Nothing here should be stateful, if it's stateful let the database handle it
'''

from cmath import log
from bottle import response, request
import view
import random

import hashlib
import os

from no_sql_db import *

# Initialise our views, all arguments are defaults for the template
page_view = view.View()

# Account
admin = request.get_cookie('admin')
login = request.get_cookie('user')
name = None

def update_login():
    global admin 
    admin = request.get_cookie('admin')
    global login 
    login = request.get_cookie('user')
    global name
    name = login or admin

#-----------------------------------------------------------------------------
# Index
#-----------------------------------------------------------------------------

def index():
    '''
        index
        Returns the view for the index
    '''
    update_login()
    return page_view("index", login=login, admin=admin)

#-----------------------------------------------------------------------------
# Register
#-----------------------------------------------------------------------------

def register_form():
    response.delete_cookie('user')
    response.delete_cookie('admin')
    update_login()
    return page_view("register", login=login, admin=admin)

#-----------------------------------------------------------------------------

# Check the Registering credentials
def register_check(username, password):
    
    # By default assume not user not exist
    new_user = True
    err_str = "Invalid username or password"

    # check empty input
    if username == '' or password == '':
        new_user = False
    else:
        # Check if username already exist
        if database.search_table('userlist', 'username', username) != None:
            err_str = "Username Already exist"
            new_user = False
        else:
            # hashed pwd
            salt = os.urandom(32) #random 32 bytes
            key = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)
            # store entry 
            database.create_table_entry('userlist', [username, salt.hex(), key.hex(), 'active'])
    
    # next steps
    if new_user: 
        response.set_cookie('user', username)
        update_login()
        # create inbox file
        database.create_table(username, ['sender', 'cipher', 'sign'], 'database/inbox/'+username+'.csv')
        return True
    else:
        response.delete_cookie('user')
        response.delete_cookie('admin')
        update_login()
        return page_view("invalid", reason=err_str, login=login, admin=admin)

#-----------------------------------------------------------------------------

#----------------------------------------------------------------------------
# Key 
#---------------------------------------------------------------------------
def key_form():
    update_login()
    return page_view("key", login=login, admin=admin)

#def key_save(username, publickey):
def key_save(publickey, verifykey):

    # save public key to server 
    user = request.get_cookie('user')
    database.create_table_entry('keys', [user, publickey, verifykey])

    # bring back to log in page 
    update_login()
    return user_home()
#------------------------------------------------------------------

#-----------------------------------------------------------------------------
# Login
#-----------------------------------------------------------------------------

def login_form():
    '''
        login_form
        Returns the view for the login_form
    '''
    response.delete_cookie('admin')
    response.delete_cookie('user')
    update_login()
    return page_view("login", login=login, admin=admin)

#-----------------------------------------------------------------------------

# Check the login credentials
def login_check(username, password):
    '''
        login_check
        Checks usernames and passwords

        :: username :: The username
        :: password :: The password

        Returns either a view for valid credentials, or a view for invalid credentials
    '''
    # By default assume good creds
    login_c = True
    err_str = "Incorrect Username"

    # retrieve entry with given username
    entry = database.search_table('userlist', 'username', username)

    # no such entry found
    if entry == None: 
        login_c = False
    # entry found, check pwd
    else:
        key = hashlib.pbkdf2_hmac('sha256', password.encode(), bytearray.fromhex(entry[1]), 100000)
        if bytearray.fromhex(entry[2]) != key:
            login_c = False
        
    if login_c: 
        #response.delete_cookie('admin')
        response.set_cookie('user', username)
        update_login()
        return page_view("valid", name=username, login=username, admin=None)
    else:
        response.delete_cookie('user')
        response.delete_cookie('admin')
        update_login()
        return page_view("invalid", reason=err_str, login=login, admin=admin)


#===========================================================
def logout():
    response.delete_cookie('admin')
    response.delete_cookie('user')
    update_login()
    return page_view("logout", login=None, admin=None)

#=======================================================

#===========================================================
# Admin
#===========================================================

def admin_check(username, password):
    # By default assume good creds
    err_str = "Incorrect Username"

    # for simplicity
    if username == 'admin' and password == 'admin':
        response.set_cookie('admin', 'admin')
        response.delete_cookie('user')
        update_login()
        return page_view("valid", name='admin', login=None, admin='admin')
    else:
        update_login()
        return page_view("invalid", reason=err_str, login=login, admin=admin)


def user_home():
    update_login()
    if login == None and admin == None:
        return login_form()

    update_login()
    return page_view("valid", name=name, login=login, admin=admin)

#-----------------------------------------------------------------------------
# Friendlist
#-----------------------------------------------------------------------------
def friends():
    # Assume all users are friends
    # so retrieve list of users as friends
    friends = database.get_table_field('userlist', 'username')
    friends.remove(request.get_cookie('user')) # remove user him/her self
    update_login()
    return page_view("friends", friends=friends, login=login, admin=admin)

#-----------------------------------------------------------------------------
# Chat
#------------------------------------------------------------------------------
def chat_form(friend):
    # get public key of friend
    f_keys = database.search_table('keys', 'username', friend)
    pbk = f_keys[1]
    update_login()
    return page_view("chat", friend=friend, pbk=pbk, login=login, admin=admin)

def send_msg(friend, cipher, sign):
    # store in friend's inbox
    sender = request.get_cookie('user')
    database.create_table_entry(friend, [sender, cipher, sign])
    return chat_form(friend)

#-----------------------------------------------------------------------------
# Inbox
#-----------------------------------------------------------------------------
def inbox():
    user = request.get_cookie('user')

    xmsg = database.tables[user].entries
    # provide verify keys to each msg 
    for msg in xmsg:
        keys = database.search_table('keys', 'username', msg[0])
        vfk = keys[2]
        msg.append(vfk)

    update_login()
    return page_view("inbox", xmsg=xmsg, login=login, admin=admin)



#-----------------------------------------------------------------------------
# Manage User
#-----------------------------------------------------------------------------
def manage_user_form():
    userlist = database.get_table_field('userlist', 'username')
    status = database.get_table_field('userlist', 'status')
    userlist = zip(userlist, status)
    update_login()
    return page_view("manage_user", name='admin', userlist=userlist, login=login, admin=admin)


def manage_user(modify_list, mute, unmute, delete):
    # delete
    print(modify_list, mute, unmute, delete)
    if delete != None:
        # delete users from database 
        # user list file
        database.remove_table_entry('userlist', 'username', modify_list)
        # key file
        database.remove_table_entry('keys', 'username', modify_list)
        # inbox file
        database.remove_table(modify_list)

    # mute
    elif mute != None:
        database.change_table_entry('userlist', 'username', modify_list, 'status', mute)

    elif unmute != None:
        database.change_table_entry('userlist', 'username', modify_list, 'status', 'active')

    return manage_user_form()   


#-----------------------------------------------------------------------------
# Manage Course
#-----------------------------------------------------------------------------
def manage_course_form():
    courselist = database.get_table_field('courselist', 'code')
    update_login()
    return page_view("manage_course", name='admin', courselist=courselist, login=login, admin='admin')


def manage_course(modify_list):
    database.remove_table_entry('courselist', 'code', modify_list)
    return manage_course_form()   


#-----------------------------------------------------------------------------
# Course
#-----------------------------------------------------------------------------
def course_form():
    codes = database.get_table_field('courselist', 'code')
    names = database.get_table_field('courselist', 'name')
    courselist = zip(codes,names)
    update_login()
    return page_view("courses", name=name, courselist=courselist, login=login, admin=admin)


def view_course(code):
    course = Course(code)
    update_login()
    return page_view("course", name=name, course=course, login=login, admin=admin)



#-----------------------------------------------------------------------------
# Forum
#-----------------------------------------------------------------------------
def forum():
    ids = database.get_table_field('forum', 'id')
    titles = database.get_table_field('forum', 'title')
    threads = zip(ids,titles)
    status = None
    update_login()
    if login != None:
        status = database.search_table('userlist', 'username', login)[3]
    return page_view("forum", name=name, threads=threads, login=login, admin=admin, status=status)

def view_thread(id):
    # get thread content
    thread = Thread(id)
    update_login()
    return page_view("thread", id=id, thread=thread, name=name, login=login, admin=admin) 

def reply_thread(id, replier, content):
    thread = Thread(id)
    thread.add_reply(replier, content)
    return view_thread(id)

def post_thread(title, sender, content):
    id = str(len(database.get_table_field('forum', 'id'))+1)
    # table
    database.create_table_entry('forum', [id,title])
    # post file
    thread = Thread(id)
    thread.make_thread(title, sender, content)
    return forum()



#-----------------------------------------------------------------------------
# Exercise
#-----------------------------------------------------------------------------
def exercise_list():
    ids = database.get_table_field('exercises', 'id')
    names = database.get_table_field('exercises', 'name')
    exercises = zip(ids,names)
    update_login()
    return page_view("exercise", name=name, exercises=exercises, login=login, admin=admin)


def show_quiz(id):
    title = database.search_table('exercises', 'id', str(id))[1]
    quiz = Quiz(id, title)
    questions = quiz.questions
    options = quiz.options
    i = 0
    while i < len(options):
        options[i].append(quiz.answers[i])
        random.shuffle(options[i])
        i+=1
    update_login()
    return page_view("quiz", id=id, title=title, name=name, questions=questions, options=options, login=login, admin=admin)


def mark_quiz(id, answers):
    title = database.search_table('exercises', 'id', str(id))[1]
    quiz = Quiz(id, title)
    user_answers = answers
    solutions = quiz.answers 
    questions = quiz.questions

    total = len(user_answers)
    mark = 0
    correctness = []
    i = 0
    while i < total:
        if user_answers[i] == solutions[i]:
            mark += 1
            correctness.append('Correct')
        else:
            correctness.append('Wrong')
        i+=1
    
    percentage = str(round(mark/total*100)) + '%'
    update_login()
    return page_view("quiz_result", id=id, title=title, name=name, percentage=percentage,  questions=questions, solutions=solutions, correctness=correctness, user_answers=user_answers, login=login, admin=admin)

#-----------------------------------------------------------------------------
# About
#-----------------------------------------------------------------------------

def about():
    '''
        about
        Returns the view for the about page
    '''

    update_login()
    return page_view("about", garble=about_garble(), login=login, admin=admin)



# Returns a random string each time
def about_garble():
    '''
        about_garble
        Returns one of several strings for the about page
    '''
    garble = ["leverage agile frameworks to provide a robust synopsis for high level overviews.", 
    "iterate approaches to corporate strategy and foster collaborative thinking to further the overall value proposition.",
    "organically grow the holistic world view of disruptive innovation via workplace change management and empowerment.",
    "bring to the table win-win survival strategies to ensure proactive and progressive competitive domination.",
    "ensure the end of the day advancement, a new normal that has evolved from epistemic management approaches and is on the runway towards a streamlined cloud solution.",
    "provide user generated content in real-time will have multiple touchpoints for offshoring."]
    return garble[random.randint(0, len(garble) - 1)]


#-----------------------------------------------------------------------------
# Debug
#-----------------------------------------------------------------------------

def debug(cmd):
    try:
        return str(eval(cmd))
    except:
        pass


#-----------------------------------------------------------------------------
# 404
# Custom 404 error page
#-----------------------------------------------------------------------------

def handle_errors(error):
    error_type = error.status_line
    error_msg = error.body
    update_login()
    return page_view("error", error_type=error_type, error_msg=error_msg, login=login, admin=admin)