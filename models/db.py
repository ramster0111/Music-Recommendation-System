# coding: utf8

#########################################################################
## This scaffolding model makes your app work on Google App Engine too
#########################################################################

if request.env.web2py_runtime_gae:            # if running on Google App Engine
    db = DAL('gae')                           # connect to Google BigTable
    session.connect(request, response, db=db) # and store sessions and tickets there
    ### or use the following lines to store sessions in Memcache
    # from gluon.contrib.memdb import MEMDB
    # from google.appengine.api.memcache import Client
    # session.connect(request, response, db=MEMDB(Client())
else:                                         # else use a normal relational database
    db = DAL('sqlite://storage.sqlite')       # if not, use SQLite or other DB
## if no need for session
# session.forget()

#########################################################################
## Here is sample code if you need for 
## - email capabilities
## - authentication (registration, login, logout, ... )
## - authorization (role based authorization)
## - services (xml, csv, json, xmlrpc, jsonrpc, amf, rss)
## - crud actions
## comment/uncomment as needed

from gluon.tools import *
mail = Mail()                                  # mailer
auth = Auth(globals(),db)                      # authentication/authorization
crud = Crud(globals(),db)                      # for CRUD helpers using auth
service = Service(globals())                   # for json, xml, jsonrpc, xmlrpc, amfrpc
plugins = PluginManager() 
                   # authentication/authorization
# after
# auth = Auth(globals(),db)

auth.settings.table_user = db.define_table('auth_user',
        db.Field('first_name', 'string', length=128, default=''),
        db.Field('last_name', 'string', length=128, default='', requires = IS_NOT_EMPTY()),
        db.Field('email', 'string', length=128, default=''),
        db.Field('password', 'password', requires = CRYPT(), readable=False),
        db.Field('reset_password_key', length=512, writable=False, readable=False, default=''),
        db.Field('registration_id', length=512, writable=False, readable=False, default=''),   
        db.Field('registration_key', 'string', length=128, writable=False, readable=False, default=''),
        db.Field('pic','upload',label='Profile Pic',requires = IS_NULL_OR(IS_IMAGE(extensions=('png','jpeg','jpg'), maxsize=(2000, 2000))),autodelete=True),
        db.Field('admin_priv', 'boolean', writable=False, readable=False, default='False'))
      #  migrate=False)
t = auth.settings.table_user
t.email.requires = [IS_EMAIL(), IS_NOT_IN_DB(db, 'auth_user.email')]

# before
# auth.define_tables()                     # creates all needed tables
auth.define_tables()  
crud=Crud(globals(),db)                      # for CRUD helpers using auth
service=Service(globals())                   # for json, xml, jsonrpc, xmlrpc, amfrpc
auth.settings.create_user_groups = False

mail.settings.server = 'smtp.gmail.com:587'  # your SMTP server
mail.settings.sender = 'web2pymail@gmail.com'         # your email
mail.settings.login = 'web2pymail@gmail.com:Aakarshit'      # your credentials or None


auth.settings.on_failed_authorization = URL('user',args='login')


auth.settings.hmac_key = 'sha512:018d9980-c436-467a-b4dc-9a4a3a268cf5'   # before define_tables()
auth.define_tables()                           # creates all needed tables
auth.settings.mailer = mail                    # for user email verification
auth.settings.registration_requires_verification = False
auth.settings.registration_requires_approval = False
auth.messages.verify_email = 'Click on the link http://'+request.env.http_host+URL(r=request,c='default',f='user',args=['verify_email'])+'/%(key)s to verify your email'
auth.settings.reset_password_requires_verification = True
auth.messages.reset_password = 'Click on the link http://'+request.env.http_host+URL(r=request,c='default',f='user',args=['reset_password'])+'/%(key)s to reset your password'

#########################################################################

#########################################################################
## Define your tables below, for example
##
## >>> db.define_table('mytable',Field('myfield','string'))
##
## Fields can be 'string','text','password','integer','double','boolean'
##       'date','time','datetime','blob','upload', 'reference TABLENAME'
## There is an implicit 'id integer autoincrement' field
## Consult manual for more options, validators, etc.
##
## More API examples for controllers:
##
## >>> db.mytable.insert(myfield='value')
## >>> rows=db(db.table.myfield=='value).select(db.mytable.ALL)
## >>> for row in rows: print row.id, row.myfield
#########################################################################
import datetime
m=True
dat=datetime.datetime.now().year
today=datetime.date.today()

db.define_table('files',Field('file','upload',label='song',autodelete=True))

db.define_table('song',Field('file',db.files,label='files'),
        Field('name','string'),
                Field('doup','datetime',label="Date of upload",default=today),
                Field('lyrics','text'),
                Field('length','integer',requires=[IS_NOT_EMPTY(),IS_INT_IN_RANGE(5,3500)]),
                Field('btr','integer',label="Bit rate"),
                Field('album','string',default="unknown",),
                Field('artist','string',default="unknown"),
                Field('year','integer',default=dat),
                Field('genere','string',default="unknown"),
                Field('rating','double',default=3.0),
                Field('nod','integer',label="No of downloads",default=0),
                Field('user_id',db.auth_user),
                Field('pic','string'))
#import time
#time.strftime('%M:%S', time.gmtime(12345))

db.define_table('comments', Field('song_id',db.song,label="Song"),
                Field('user_id',db.auth_user,label="User Name"),
                Field('comment','text'),
                Field('date','datetime'))
        
db.define_table('ip_add', 
        Field('ip','string',requires=IS_NOT_EMPTY()),
        Field('hits','integer'),
        Field('last','datetime',label='Last login'),
        Field('port','integer'))
        

db.define_table('prefs', 
               Field('user_id', db.auth_user),
               Field('rating', 'double'),
               Field('song_id', db.song))
               
db.define_table('similarity',
		Field('song1', db.song),
		Field('song2', db.song),
		Field('sim', 'double'))

db.define_table('playlist',
        Field('user',db.auth_user,label='User Name',requires=IS_IN_DB(db,'auth_user.id','%(first_name)s %(last_name)s')),
        Field('name','string',label='Playlist',requires=IS_NOT_EMPTY()))
    
db.define_table('list',
        Field('list',db.playlist,label='Play List',requires=IS_IN_DB(db,'playlist.id','%(name)s')),
        Field('song',db.song,label='Song',requires=IS_IN_DB(db,'song.id','%(name)s')),
            Field('favourite','boolean',default=False),
        Field('listen','integer',default='0',requires=IS_NOT_EMPTY()),
        Field('orders','integer',default='0',requires=IS_NOT_EMPTY()))
            

db.files.file.requires= [IS_UPLOAD_FILENAME(extension='mp3'),
            IS_LENGTH(15728640, 1024)]
            
db.song.file.requires=[IS_IN_DB(db,'files.id'),IS_NOT_IN_DB(db,'song.file')]
db.song.name.requires = IS_NOT_EMPTY()
db.song.doup.requires =IS_NOT_EMPTY()
db.song.lyrics.requires = IS_LENGTH(1000,0)
db.song.year.requires= IS_INT_IN_RANGE(1950,dat+1)
db.song.rating.requires = [IS_NOT_EMPTY(),IS_FLOAT_IN_RANGE(0,5)]
db.song.user_id.requires = IS_IN_DB(db,'auth_user.id','%(first_name)s %(last_name)s')



db.comments.song_id.requires = IS_IN_DB(db,'song.id','%(name)s')
db.comments.user_id.requires = IS_IN_DB(db,'auth_user.id','%(first_name)s %(last_name)s')
db.comments.comment.requires = IS_NOT_EMPTY()
db.comments.date.requires =IS_NOT_EMPTY()
