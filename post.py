#!/usr/bin/env python
# -*- coding: utf-8 -*-

import tempfile, subprocess
import sqlite3
import os
import sys
from datetime import datetime
import re
import urlify

#
# This script is ridiculous. I have never been so careless and messy. I just
# wanted to make something quick and then refine it. 
# Ridiculous.
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
    while True:
        title = raw_input("Please pick a title: ")
        if title != "":
            break;

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

        cursor.execute("""SELECT title, body, status, created_at FROM posts WHERE status = ? ORDER BY created_at desc LIMIT 10""", (PUBLISHED,))
        rows = cursor.fetchall()

        index_html = ""

        #write individual files
        for row in rows:
            slug = urlify.urlify(row[0])
            post_file_name = "{0}.html".format(slug)
            with open("{0}{1}".format(public_html_path, post_file_name), 'w') as f:
                f.write(row[1])

            index_html = index_html + "<br>" + "<h1>" + row[0] + "</h1><p>" +  row[1].replace("\n", "<br>") + "</p>"

        #write the index
        with open("{0}{1}".format(public_html_path, "index.html"), 'w') as f:
            f.write(index_html)

else:
    print("Okay.")
