#!/usr/bin/env python
# -*- coding: utf-8 -*-

import tempfile, subprocess
import sqlite3
import os
import sys
from datetime import datetime

#
# Try to open the database. If you don’t find one then you should ask the user
# if they want to set up a posting database.
#

DRAFT = 0
PUBLISHED = 1


working_path = os.path.expanduser("~/.post/")
database_path = "{0}posts.db".format(working_path)
public_html_path = os.path.expanduser("~/public_html/")

if os.path.exists(database_path):
    conn = sqlite3.connect(database_path, isolation_level=None, 
                            detect_types=sqlite3.PARSE_DECLTYPES|
                                sqlite3.PARSE_COLNAMES)
    cursor = conn.cursor()
else:
    print("Hey, this looks like the first time you’re running post.py")
    wants_weblog = raw_input("Would you like to set up a new weblog? [Y/n]: ")
    wants_weblog = wants_weblog.lower()
    if wants_weblog == "y" or wants_weblog == "":

        print("Great! First I need to know what you want to name your weblog.")
        print("Good names include things like ‘My Weblog’ and ‘Blogging For The Weekend’.")
        weblog_name = raw_input("Enter weblog name here: ")
        print("Cool! Your weblog will be named ‘{0}’. You can change this later.".format(weblog_name))

        try:
            os.mkdir(working_path, 0700)
        except:
            print("I couldn’t create the database file.")
            sys.exit()

        conn = sqlite3.connect(database_path, isolation_level=None)
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE posts (title text, body text, status integer, created_at timestamp)")
        
        print("Your database has been created!")
        print("Now it’s time to write your first post.")
        wants_to_write_post = raw_input("Do you want to create a post now? [Y/n]")
        wants_to_write_post = wants_to_write_post.lower()
        if wants_to_write_post != 'y' and wants_to_write_post != "":
            print("Good luck!")
            sys.exit()

    else:
        print("Enjoy your life!")


with tempfile.NamedTemporaryFile(suffix='task') as temp:
    subprocess.call(['vim', temp.name])
    body = open(temp.name, 'r').read()

if body != "":
    title = raw_input("Please pick a title (You can leave this blank): ")

    cursor.execute("""INSERT INTO posts (title, body, status, created_at)
                    VALUES (?, ?, 0, ?)""", (title, body, datetime.now()))

    print("Here is what you wrote:")
    print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
    print(title)
    print("\n")
    print(body)
    print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
    wants_to_publish = raw_input("Do you want to publish that now? (If you say no, you can publish it later.) [Y/n]")
    wants_to_publish = wants_to_publish.lower()
    if wants_to_publish == 'y' or wants_to_publish == '':
        cursor.execute("""UPDATE posts SET status = ? WHERE rowid = ?""", 
                        (PUBLISHED, cursor.lastrowid))

else:
    print("Okay.")
