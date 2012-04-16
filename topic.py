'''u413 - an open-source BBS/terminal/PI-themed forum
	Copyright (C) 2012 PiMaster
	Copyright (C) 2012 EnKrypt

	This program is free software: you can redistribute it and/or modify
	it under the terms of the GNU Affero General Public License as published by
	the Free Software Foundation, either version 3 of the License, or
	(at your option) any later version.

	This program is distributed in the hope that it will be useful,
	but WITHOUT ANY WARRANTY; without even the implied warranty of
	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
	GNU Affero General Public License for more details.

	You should have received a copy of the GNU Affero General Public License
	along with this program.  If not, see <http://www.gnu.org/licenses/>.'''

'''
+--------+--------------+------+-----+---------+----------------+
| Field  | Type         | Null | Key | Default | Extra          |
+--------+--------------+------+-----+---------+----------------+
| id     | int(11)      | NO   | PRI | NULL    | auto_increment |
| topic  | bit(1)       | YES  |     | NULL    |                |
| title  | varchar(128) | YES  |     | NULL    |                |
| parent | int(11)      | YES  |     | NULL    |                |
| owner  | int(11)      | YES  |     | NULL    |                |
| editor | int(11)      | YES  |     | NULL    |                |
| post   | text         | YES  |     | NULL    |                |
| locked | bit(1)       | YES  |     | NULL    |                |
| edited | datetime     | YES  |     | NULL    |                |
| posted | datetime     | YES  |     | NULL    |                |
+--------+--------------+------+-----+---------+----------------+
'''

import command
import user
import database as db
import math
import bbcode

def output_page(topic,page,u413):
	t=db.query("SELECT * FROM posts WHERE id=%i;"%topic)[0]#topic
	if not bool(t["topic"]):
		u413.type("Invalid topic ID.")
		return
	b=db.query("SELECT name FROM boards WHERE id=%i;"%int(t["parent"]))[0]["name"]#board name
	u=db.query("SELECT username FROM users WHERE id=%i;"%int(t["owner"]))[0]["username"]#username
	c=int(db.query("SELECT COUNT(*) FROM posts WHERE parent=%i;"%topic)[0]["COUNT(*)"])#number of replies
	if page==0 and page>1 or page!=0 and page>math.ceil(c/10.0):
		page=math.ceil(c/10.0)
	if page<1:
		page=1
	r=db.query("SELECT * FROM posts WHERE parent=%i ORDER BY id LIMIT %i,10;"%(topic,(page-1)*10))#replies
	u413.type("Retreiving topic...")
	u413.donttype('{%i} %s {%i} <span class="inverted">%s</span><br/>\n<span class="dim">Posted by %s on %s</span><br/>\n'%(int(t["parent"]),b,topic,t["title"],u,str(t["posted"])))
	u413.donttype(t["post"]+'<br/>\n')
	u413.donttype('Page %i/%i<br/>\n'%(page,math.ceil(c/10.0)))
	if c==0:
		u413.type("There are no replies.")
	else:
		for reply in r:
			owner=db.query("SELECT username FROM users WHERE id=%i;"%int(reply["owner"]))[0]["username"]
			u413.donttype('<table><tr><td style="text-align:center;">&gt;</td><td style="text-align:center;width:160px;border-right:solid 1px lime;">%s</td><td style="padding-left:8px;">{%i} %s<br/><span class="dim">%s</span></td></tr></table><br/>'%(owner,int(reply["id"]),bbcode.bbcodify(bbcode.htmlify(reply["post"])),reply["posted"]))
		u413.donttype('Page %i/%i<br/>\n'%(page,math.ceil(c/10.0)))
	if page==1:
		u413.set_context("TOPIC %i"%topic)
	else:
		u413.set_context("TOPIC %i %i"%(topic,page))

def isint(i):
	try:
		i=int(i)
	except:
		return False
	return True

def topic_func(args,u413):
	params=args.split(' ',2)
	if len(params)==0 or not isint(params[0]):
		u413.type("Invalid topic ID.")
		return
	topic=int(params[0])
	if len(params)==1:
		page=1
		output_page(topic,1,u413)
		u413.clear_screen()
	elif len(params)==2:
		if params[1].upper()=="REPLY":
			u413.j["Command"]="REPLY"
			u413.cmddata["topic"]=topic
			u413.continue_cmd()
		else:
			page=1
			if isint(params[1]):
				page=int(params[1])
			output_page(topic,page,u413)
			u413.clear_screen()
	elif params[1].upper()=="REPLY":
		db.query("INSERT INTO posts (topic,title,parent,owner,editor,post,locked,edited,posted) VALUES(FALSE,'',%i,%i,0,'%s',FALSE,NULL,NOW());"%(topic,u413.user.userid,db.escape(params[3])))
		u413.type("Reply made successfully.")

command.Command("TOPIC","<id> [page | [REPLY <message>]]",{"id":"The topic ID","page":"The topic page to load (defaults to 1)","message":"The message you wish to post"},"Loads a topic",topic_func,user.User.member)