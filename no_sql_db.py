# This file provides a very simple "no sql database using python dictionaries"
# If you don't know SQL then you might consider something like this for this course
# We're not using a class here as we're roughly expecting this to be a singleton

# If you need to multithread this, a cheap and easy way is to stick it on its own bottle server on a different port
# Write a few dispatch methods and add routes

# A heads up, this code is for demonstration purposes; you might want to modify it for your own needs
# Currently it does basic insertions and lookups

from asyncore import file_dispatcher
import os.path


class Table():
    def __init__(self, table_name, path):
        self.entries = []
        self.fields = []
        self.name = table_name
        self.path = path

            
    # read table that already exist
    def read_table(self):
        if not os.path.exists(self.path):
            f = open(self.path, "w")
            f.close
            return 

        f = open(self.path, "r")
        lines = f.readlines()
        f.close()
        
        i = 0
        while i < len(lines):
            l = lines[i].strip("\n").split(",")
            if i == 0:
                self.fields = l
            else:
                self.entries.append(l)
            i+=1


    # write a table that does not exist
    def write_table(self, fields):
        self.fields = fields
        f = open(self.path, "w")
        f.write(','.join(fields))
        f.close()

    # rewrite a table 
    def rewrite_table(self):
        f = open(self.path, "w")
        f.write(','.join(self.fields))
        for entry in self.entries:
            f.write('\n')
            f.write(','.join(entry))
        f.close()


    # create new entry and update to file 
    def create_entry(self, data):
        '''
        Inserts an entry in the table
        Doesn't do any type checking
        '''

        # Bare minimum, we'll check the number of fields
        if len(data) != len(self.fields):
            raise ValueError('Wrong number of fields for table')

        self.entries.append(data)
        f = open(self.path, "a")
        f.write('\n' + ','.join(data))
        f.close()
        return

    def search_table(self, target_field_name, target_value):
        '''
            Search the table given a field name and a target value
            Returns the first entry found that matches
        '''
        # Lazy search for matching entries
        for entry in self.entries:
            for field_name, value in zip(self.fields, entry):
                if target_field_name == field_name and target_value == value:
                    return entry

        # Nothing Found
        return None

    def get_field(self, target_field_name):
        # get index field
        i = -1
        try:
            i = self.fields.index(target_field_name)
        except:
            return None 
        
        # get all values
        if i < 0:
            return None
        return [entry[i] for entry in self.entries]



class DB():
    '''
    This is a singleton class that handles all the tables
    You'll probably want to extend this with features like multiple lookups, and deletion
    A method to write to and load from file might also be useful for your purposes
    '''
    def __init__(self):
        self.tables = {}
        return

    def add_table(self, table_name, path):
        '''
            Adds a table to the database
        '''
        table = Table(table_name, path)
        table.read_table()
        self.tables[table_name] = table
        return

    def create_table(self, table_name, fields, path):
        '''
            Adds a table to DB and
            Create a new file to store table data
        '''
        table = Table(table_name, path)
        table.write_table(fields)
        self.tables[table_name] = table
        return


    def search_table(self, table_name, target_field_name, target_value):
        '''
            Calls the search table method on an appropriate table
        '''
        return self.tables[table_name].search_table(target_field_name, target_value)


    def create_table_entry(self, table_name, data):
        '''
            Calls the create entry method on the appropriate table
        '''
        return self.tables[table_name].create_entry(data)


    def get_table_field(self, table_name, field_name):
        '''
            To retreive all data of a field/col of the appropriate table
        '''
        return self.tables[table_name].get_field(field_name)


    def remove_table_entry(self, table_name, target_field, target_values):
        table = self.tables[table_name]
        table_entries = table.entries
        for value in target_values:
            target_entry = self.search_table(table_name, target_field, value)
            table_entries.remove(target_entry)
        # update file
        table.rewrite_table()
        return

    def remove_table(self, table_names):
        for name in table_names:
            # remove corrsponding file
            os.remove(self.tables[name].path)
            # remove from database
            self.tables.pop(name)

    def change_table_entry(self, table_name, target_field, target_values, change_field, change_value):
        table = self.tables[table_name]
        table_entries = table.entries
        i = table.fields.index(change_field)
        for value in target_values:
            target_entry = self.search_table(table_name, target_field, value)
            target_entry[i] = change_value
        # update file
        table.rewrite_table()


#=================
# Course item
#================
class Course():
    def __init__(self, name):
        self.path = 'database/course/{}.txt'.format(name)
        self.name = name
        self.title = name
        self.content = None

        if not os.path.exists(self.path):
            f = open(self.path, "w")
            f.close
            return

        f = open(self.path, "r")
        lines = f.readlines()
        f.close()
        
        self.title = lines[0]
        self.content = lines[1:]
        return


#=================
# Thread item
#================
class Thread():
    def __init__(self, id):
        self.path = 'database/post/{}.txt'.format(id)
        self.id = id
        self.title = None
        self.sender = None
        self.content = None
        self.replies = []

        if not os.path.exists(self.path):
            return

        f = open(self.path, "r")
        lines = f.readlines()
        f.close()
        
        self.title = lines[0]
        self.sender = lines[1]
        self.content = lines[2]
        if len(lines) > 3:
            for line in lines[3:]:
                self.replies.append(line.split('|'))
        return

    def make_thread(self, title, sender, content):
        f = open(self.path, "w")
        f.write(title+'\n')
        f.write(sender+'\n')
        f.write(content)
        f.close()

    def add_reply(self, replier, content):
        f = open(self.path, "a")
        f.write('\n' + '|'.join([replier, content]))
        f.close()
        return



#=================
# Quiz item
#================
class Quiz():
    def __init__(self, id, title):
        self.path = 'database/exercise/{}.txt'.format(id)
        self.title = title 
        self.questions = []
        self.answers = []
        self.options = []

        if not os.path.exists(self.path):
            return

        f = open(self.path, "r")
        lines = f.readlines()
        f.close()
        
        for line in lines:
            l = line.strip('\n').split("|")
            self.questions.append(l[0])
            self.answers.append(l[1])
            self.options.append(l[2].split("~"))
        return


# Our global database
# Invoke this as needed
database = DB()

# fetch userlist data
database.add_table('userlist', 'database/user.csv')

# fetch user public keys
database.add_table('keys','database/keys.csv')

# fetch inboxes
inbox_files = os.listdir('database/inbox')
for inbox in inbox_files:
    table_name = inbox.strip('.csv')
    database.add_table(table_name,'database/inbox/{}'.format(inbox))

# fetch course
database.add_table('courselist', 'database/courses.csv')

# fetch post
database.add_table('forum', 'database/posts.csv')

# fetch exercise
database.add_table('exercises', 'database/exercises.csv')
