#! /usr/bin/env python
# coding: utf-8
# -*- coding: utf_8 -*-


import sqlite3
import re
import unicodedata
import sys


# def remove_vowels(arabic_text_with_vowels):
#     vowels = u"[\u064B-\u065F]"  # vowel character range
#     arabic_text = re.sub(vowels, u'', arabic_text_with_vowels)
#     return arabic_text


def remove_database_records(sqlite_name):
    conn = sqlite3.connect(sqlite_name)
    cur = conn.cursor()
    cur.execute('delete from pages')
    conn.commit()
    conn.close
    print ("All records are removed from " +sqlite_name)




def strip_diacritics(text):
    import unicodedata
    # return ''.join([c for c in unicodedata.normalize('NFD', text) \
    # if unicodedata.category(c) != 'Mn'])
    if text and len(text) > 0:
        return ''.join([c for c in text if unicodedata.category(c) != 'Mn'])
    else:
        return ''


def get_pop_count(cur_level, new_level):
    cur_level = cur_level.replace("H", "");
    new_level = new_level.replace("H", "")
    return int(cur_level) - int(new_level)


def convert_text_to_sqlite(file_names, sqlite_name): 

    print ("import text files and insert records into sqlite file")

    remove_database_records(sqlite_name)

    conn = sqlite3.connect(sqlite_name)
    cur = conn.cursor()

    page_id = 0
    book_index = 1
# book_code_prefix = u"soura"

    for text_file_name in file_names:
        print "\nfile name:", text_file_name
        parent_id =""
        title =u""
        page =u""
        page_fts =u""
        # book_code =  book_code_prefix + str(book_index)
        book_code = text_file_name.replace(".", "_").replace("-", "_")
        print "working on file", book_code
        book_index += 1
        record =u""
        line = u""
        stack = []
        stack.append("NO_PARENT")
        current_header_level = u"H1"

        with open(text_file_name, 'rU') as file:
            file.readlines
            for line in file:
                line = line.strip()
                if len(line) > 0 :
                    # print "line is[" + line + "]"
                    if line.find("H") == -1 : # NOT FOUND
                        record += line.decode("utf-8") + "\r\n"
                    else:
                        # print "line is [", line, "]"
                        # handle stack of parent ids
                        line = line.strip()
                        #split lines to extract first line as title
                        if(len(record) > 0) : # if empty, just skip it
                            # print "[", record, "]"
                            lines = record.splitlines() #split on new line
                            # print "lines count is", len(lines)
                            title = lines[0]
                            # print "title is:", title
                            lines[0] = ""
                            joinedData = ""
                            for single_line in lines:
                                joinedData += " " + single_line

                            record_fts = strip_diacritics(unicode(joinedData))
                            parent_id = stack[len(stack)-1]
                            joinedData = joinedData.strip()
                            record_fts = record_fts.strip()
                            joinedData = joinedData.replace("\r\n", "\r\n<br>")
                            topic = (page_id, parent_id, book_code, title, joinedData, record_fts)
                            print "RECORD: page_id=", page_id, ";parent_id=", parent_id, ";title=", title
                            cur.execute(u'insert into pages (page_id, parent_id, book_code, title, page, page_fts) Values (?, ?, ?, ?, ?, ?)', topic)
                            record = "" # for the new line processing
                            # print page_id
                            # print record
                            #sys.stdout.write('.')
                            sys.stdout.flush()
                            #handle parent id
                            if line.strip() > current_header_level:
                                #print "Lower level : new level=", line, "; current level", current_header_level
                                stack.append(page_id)
                                current_header_level = line #update current line
                            elif line.strip() < current_header_level:
                                #print "Higher level: new level=", line, "; current level", current_header_level
                                pop_count = get_pop_count(current_header_level, line)
                                current_header_level = line
                                print "poping count", pop_count
                                while pop_count > 0:
                                    stack.pop()
                                    pop_count -= 1
                            #else:
                                #print "Same level  :", line, ";",  current_header_level

                            page_id += 1



    conn.commit()
    conn.close()  # call basic function

    print ""
    print "Warning: you have to add an empty record at the end of file to ensure flushing of data, as example H3 or H4"
    print "Conversion completed for records counted:" + str(page_id)



##################################################################################


file_names = ["azkar.txt"]
sqlite_name = 'azkar.sqlite'

convert_text_to_sqlite(file_names, sqlite_name)

