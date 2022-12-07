'''
    This file will handle our typical Bottle requests and responses 
    You should not have anything beyond basic page loads, handling forms and 
    maybe some simple program logic
'''

from bottle import route, get, post, error, request, static_file, redirect, response

import model

#-----------------------------------------------------------------------------
# Static file paths
#-----------------------------------------------------------------------------

# Allow image loading
@route('/img/<picture:path>')
def serve_pictures(picture):
    '''
        serve_pictures

        Serves images from static/img/

        :: picture :: A path to the requested picture

        Returns a static file object containing the requested picture
    '''
    return static_file(picture, root='static/img/')

#-----------------------------------------------------------------------------

# Allow CSS
@route('/css/<css:path>')
def serve_css(css):
    '''
        serve_css

        Serves css from static/css/

        :: css :: A path to the requested css

        Returns a static file object containing the requested css
    '''
    return static_file(css, root='static/css/')

#-----------------------------------------------------------------------------

# Allow javascript
@route('/js/<js:path>')
def serve_js(js):
    '''
        serve_js

        Serves js from static/js/

        :: js :: A path to the requested javascript

        Returns a static file object containing the requested javascript
    '''
    return static_file(js, root='static/js/')

#-----------------------------------------------------------------------------
# Pages
#-----------------------------------------------------------------------------

# Redirect to login
@get('/')
@get('/home')
def get_index():
    '''
        get_index
        
        Serves the index page
    '''
    return model.index()

#-----------------------------------------------------------------------------

# Display the login page
@get('/login')
def get_login_controller():
    '''
        get_login
        
        Serves the login page
    '''
    return model.login_form()

#-----------------------------------------------------------------------------

# Attempt the login
@post('/login')
def post_login():
    '''
        post_login
        
        Handles login attempts
        Expects a form containing 'username' and 'password' fields
    '''

    # Handle the form processing
    username = request.forms.get('username')
    password = request.forms.get('password')
    is_admin = request.forms.get('admin') # None when not checkbox not ticked

    # Call the appropriate method
    if is_admin != None: 
        return model.admin_check(username, password)
    # normal user
    return model.login_check(username, password)



#-----------------------------------------------------------------------------
# Display the Register page
@get('/register')
def get_register_controller():
    return model.register_form()


# Attempt the register
@post('/register')
def post_register():
    '''
        post_login
        
        Handles login attempts
        Expects a form containing 'username' and 'password' fields
    '''

    # Handle the form processing
    username = request.forms.get('username')
    password = request.forms.get('password')
    # publickey = request.forms.get('publickey')

    # Call the appropriate method
    result = model.register_check(username, password)
    if result == True:
        response.set_cookie('user', username)
        redirect('/key')
    else:
        return result

#-----------------------------------------------------------------------------

# User to save their private key
# Server to store the public key
@get('/key')
def get_key():
    return model.key_form()

@post('/key')
def post_key():
    publickey = request.forms.get('publickey')
    verifykey = request.forms.get('verifykey')

    return model.key_save(publickey, verifykey)
#---------------------------------------------------------------------------------

#-----------------------------------------------------------------------------
# FriendList
#-----------------------------------------------------------------------------
@route('/friendlist')
def friend_list():
    # redirect to login page if not logged in 
    if request.get_cookie('user') == None:
        redirect('/login')
    
    return model.friends()
    
#-----------------------------------------------------------------------------


#-----------------------------------------------------------------------------
# Chat
#-----------------------------------------------------------------------------
@get('/chat/<friend>')
def chat(friend):
    return model.chat_form(friend)

@post('/chat/<friend>')
def chat(friend):
    cipher = request.forms.get('cipher')
    sign = request.forms.get('sign')

    return model.send_msg(friend, cipher, sign)
#-----------------------------------------------------------------------------

#-----------------------------------------------------------------------------
# Inbox
#-----------------------------------------------------------------------------
@route('/inbox')
def get_inbox():
    # redirect to login page if not logged in 
    if request.get_cookie('user') == None:
        redirect('/login')

    return model.inbox()

#-----------------------------------------------------------------------------
# Logout
#-----------------------------------------------------------------------------
@route('/logout')
def get_logout():
    return model.logout()
#-----------------------------------------------------------------------------


#-----------------------------------------------------------------------------
# User home
#-----------------------------------------------------------------------------
@route('/userhome')
def get_userhone():
    return model.user_home()

#-----------------------------------------------------------------------------
# Manage user (Admin)
#-----------------------------------------------------------------------------
@get('/manage_user')
def get_manage_user():
    return model.manage_user_form()

@post('/manage_user')
def post_manage_user():
    modify_list = request.forms.getall('modfiy_list')
    mute = request.forms.get('mute')
    unmute = request.forms.get('unmute')
    delete = request.forms.get('delete')
    return model.manage_user(modify_list, mute, unmute, delete)


#-----------------------------------------------------------------------------
# Manage course (Admin)
#-----------------------------------------------------------------------------
@get('/manage_course')
def get_manage_course():
    return model.manage_course_form()

@post('/manage_course')
def post_manage_user():
    modify_list = request.forms.getall('modfiy_list')
    print(modify_list)
    return model.manage_course(modify_list)


#-----------------------------------------------------------------------------
# Course List and selection
#-----------------------------------------------------------------------------
@route('/courses')
def get_courses():
    return model.course_form()

@route('/courses/<code>')
def view_course(code):
    return model.view_course(code)


#-----------------------------------------------------------------------------
# Forum
#-----------------------------------------------------------------------------
@get('/forum')
def get_forum():
    return model.forum()

@post('/forum')
def post_forum():
    print("post forum")
    title = request.forms.get('title')
    content = request.forms.get('content')
    sender = request.get_cookie('user')
    return model.post_thread(title, sender, content)

@get('/forum/<id>')
def get_thread(id):
    return model.view_thread(id)

@post('/forum/<id>')
def post_thread(id):
    content = request.forms.get('content')
    replier = request.get_cookie('user')
    return model.reply_thread(id, replier, content)



#-----------------------------------------------------------------------------
# Exercises
#-----------------------------------------------------------------------------
@route('/exercise')
def get_exerciselist():
    return model.exercise_list()

@get('/exercise/<id>')
def get_quiz(id):
    return model.show_quiz(id)

@post('/exercise/<id>')
def post_quiz(id):
    num = int(request.forms.get('num'))
    i = 0
    answers = []
    while i < num:
        a = request.forms.get(str(i))
        answers.append(a)
        i+=1
    print(answers)
    return model.mark_quiz(id, answers) 




#-----------------------------------------------------------------------------
# About
#-----------------------------------------------------------------------------
@get('/about')
def get_about():
    '''
        get_about
        
        Serves the about page
    '''
    return model.about()
#-----------------------------------------------------------------------------

# Help with debugging
@post('/debug/<cmd:path>')
def post_debug(cmd):
    return model.debug(cmd)

#-----------------------------------------------------------------------------

# 404 errors, use the same trick for other types of errors
@error(404)
def error(error): 
    return model.handle_errors(error)
