# -*- coding: utf-8 -*- 

#########################################################################
## This is a samples controller
## - index is the default action of any application
## - user is required for authentication and authorization
## - download is for downloading files uploaded in the db (does streaming)
## - call exposes all registered services (none by default)
#########################################################################  

#default homepage redirected to home
auth.settings.create_user_groups = False
@auth.requires_login()
def index():
    """
    example action using the internationalizatioREADMEn operator T and flash
    rendered by views/default/index.html or views/generic.html
    """
    is_admin=0
    if session.auth.user.admin_priv == True:
        if auth.has_membership('Secret Agent', session.auth.user.id) == False:
            auth.add_membership('Secret Agent', session.auth.user.id)            
            
    if session.auth.user.admin_priv == False:
        if auth.has_membership('Secret Agent', session.auth.user.id) == True:
            db(db.auth_membership.user_id == session.auth.user.id).delete()                       
            
    redirect(URL(r=request,f='home'))
    return dict(message=T('Hello World'))

#function for user login/logout
def user():
        
    if request.args(0)=='logout':
        ip=0;
        down=0;
        for i in db(db.ip_add.ip==str(request.env.remote_addr)).select():
            ip=i.id
            down=i.hits+1   
        if ip:  db(db.ip_add.id==ip).update(hits=down,last=request.now,port=request.env.remote_port)
        else:  db.ip_add.insert(ip=str(request.env.remote_addr),hits=0,last=request.now,port=request.env.remote_port)
        session.clear()     #if requestfor logout clear the session
        redirect(URL(r=request,f='user',args='login'))#redirect to login page
    
    """
    exposes:
    http://..../[app]/default/user/login 
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    """
    
    down=db(db.song.id>0).select(orderby=~db.song.nod,limitby=(0,10))         #contains details of top download
    recent=db(db.song.id>0).select(orderby=~db.song.doup,limitby=(0,4))       #contains details of recently uploaded files
    return dict(form=auth(),down=down,recent=recent)

#the logout function
def logout():
    session.clear()
    redirect(URL(r=request,f='index'))
    return 


#the page to register
def register():
    session.clear()
    form=SQLFORM(db.auth_user)
    down=db(db.song.id>0).select(orderby=~db.song.nod,limitby=(0,10))
    recent=db(db.song.id>0).select(orderby=~db.song.doup,limitby=(0,4))
        
    if form.accepts(request.vars,session):
            redirect(URL(r=request,f='user',args='login'))#if registeration is sucessful  redirct to homepage
            
    return dict(form=form,down=down,recent=recent)

#default function to download the file in database
@auth.requires_login()
def download():
     
    if(request.vars.has_key('songid')):  #if it is called to download the no of download of that song is increased by one
        rat1=db(db.plugin_rating_master.id>0).select()
        rat=3.0
        for i in rat1:
            rat=i.rating
        so=int(request.vars['songid'])
        curr=db(db.song.id==so).select()
        down=0
        rat1=3.0
        for i in curr:
             down=int(i.nod)+1
             rat1=i.rating
        rat=((rat1*(down-1))+rat)/down
        db(db.song.id==so).update(nod=down,rating=rat)
        
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request,db)


def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    session.forget()
    return service()

#controller for general homepage
    
@auth.requires_login()
def home():
    admin=0
                                                                     
    if(auth.has_membership('adminstration')):admin=1
        
    form = SQLFORM.factory(
            Field('Search'),
            Field('type','boolean', requires=IS_IN_SET(['All','Artist','Album','Titles']),widget=SQLFORM.widgets.radio.widget,default='All'))
    g=[]
     
    if session.string==None:
          session.string=" "
          session.type1="All"
    string=session.string
    type1=session.type1
    pageno=0
    next=0
    pre=0
    no=15
        
        
    if request.vars.has_key('pageno'):
          pageno=int(request.vars['pageno'])
          no=pageno*15+15
    if form.accepts(request.vars, session):
          session.string=request.vars['Search']
          session.type1=request.vars['type']
          redirect(URL(r=request,f='home'))
    elif form.errors:
          response.flash = 'form has errors'
       
    g=process_search(string,type1)
    count=len(g)
       
    found=""
    down=db(db.song.id>0).select(orderby=~db.song.nod,limitby=(0,10))
    recent=db(db.song.id>0).select(orderby=~db.song.doup,limitby=(0,4))
    tmp=db(db.song.id>0).select()
    if(g):
          found=tmp.find(lambda x: x.id in g)
    else: response.flash='no song found'
             
    if pageno>0:
          pre=1
    if no <count:
          next=1
    session.string=string
    session.type1=type1 

    newlink = []
    newlabel = []	

    if  auth.has_membership('Secret Agent', session.auth.user.id) == True:
    	newlink.append('upload')
	newlabel.append('UPLOAD')

        newlink.append('mymusic')
	newlabel.append('MY SONGS')

    else:
	newlink.append('request_upload')
	newlabel.append('REQUEST')

       	newlink.append('update_profile')
	newlabel.append('PROFILE')

    return dict(admin=admin,form=form,found=found,pageno=pageno,pre=pre,next=next,count=count,down=down,recent=recent, newlink = newlink, newlabel = newlabel)
    
    
import os
@auth.requires_membership('adminstration')
def ips():
    ip12=db(db.ip_add.id>0).select()
    return dict(ip=ip12)
    
import re
#function that process the search string and returns the ids of mathched results
@auth.requires_login()
def process_search(s1,p):
    s='\w*\s*\W*'
    reg=s
    for i in s1.split():
        reg=reg+i+s         #create a regular expression
    l=[]
    #search for the regx in database
    for i in db(db.song.id>0).select(db.song.ALL):
        tmp=i.id
       
        if((p=='All' or p=='Album')and (re.search(reg,i.album,re.IGNORECASE))):
           if(i.id not in l):  l+=[i.id]
        if((p=='All' or p=='Titles')and (re.search(reg,i.name,re.IGNORECASE))):
           if(i.id not in l):  l+=[i.id]
        if((p=='All' or p=='Artist')and (re.search(reg,i.artist,re.IGNORECASE))):
           if(i.id not in l):l+=[i.id]   
         
    
    return l
 
import os

#controler for upload page only for admin
@auth.requires_membership('Secret Agent')
def upload():
    up_form=SQLFORM(db.files)
    bol ='dskh' 
 
    if up_form.accepts(request.vars,session):
            response.flash=(T('file uploaded'))
            path = os.path.join(request.folder,'uploads',up_form.vars['file'])
            bol=get_info(path,up_form.vars['id'])   #get the metadata of uploaded file
            if(bol['done']==True):
                 bol=bol['m']
                 #insert the metadata in database
                 db.song.insert(file=up_form.vars['id'],name=bol['title'][0],doup=request.now,lyrics=bol['lyrics'],length=bol['length'],btr=bol['bit_rate'], artist=bol['artist'][0], album=bol['album'][0], year=int(bol['date']),genere=bol['genere'][0],user_id=session.auth.user.id,pic=bol['img'])
                         
            else:db(db.file.id==up_form.vars['id']).delete()#if there is error in extracting metadata delete the file
    elif up_form.errors:
           response.flash=(T('error occured'))
    
    down=db(db.song.id>0).select(orderby=~db.song.nod,limitby=(0,10)) #contains details of recently  uploadded files
    recent=db(db.song.id>0).select(orderby=~db.song.doup,limitby=(0,4)) #contains details of recently uploaded files
    byme=db(db.song.user_id==session.auth.user.id).select(orderby=~db.song.doup,limitby=(0,15)) #contains details of top songs uploaded by user
    return dict(form=up_form,down=down,recent=recent,byme=byme)    


#controller  for mymusic page
@auth.requires_login()
def mymusic():
        down=db(db.song.id>0).select(orderby=~db.song.nod,limitby=(0,10))#contains details of recently  uploadded files
        recent=db(db.song.id>0).select(orderby=~db.song.doup,limitby=(0,4)) #contains details of recently uploaded files
        
        pageno=0
        next=0
        pre=0
        no=15
        n=15
        if request.vars.has_key('pageno'):
            pageno=int(request.vars['pageno'])
            no=pageno*15+15                             #get the current page no
        count=db(db.song.user_id==session.auth.user.id).count() #get the total no of entries
         
        if pageno > 0:
            pre=1
        if no < count:
            next=1
        else :
            no-=15
            n=count-no 
        byme=db(db.song.user_id==session.auth.user.id).select(orderby=~db.song.doup,limitby=(pageno*15,n))#contains details of top songs uploaded by user

        return dict(pageno=pageno,pre=pre,next=next,down=down,recent=recent,byme=byme)
        

#controller for requesting songs to be added only for genral users and not admin
@auth.requires_login()
def request_upload(): 

    form = SQLFORM.factory(
            Field('SongDetails', 'text')) 
 
    if form.accepts(request.vars, session):
          session.string=request.vars['SongDetails']
	  response.flash = 'Your request has been sent to the admin'
    	  mail.send(to=['web2pymail@gmail.com'], subject='Song request', message='I want to request you to add the following song to the database:\n' + session.string + '\nMy email id is ' + session.auth.user.email)	       	  

    elif form.errors:
          response.flash = 'form has errors'
    
    down=db(db.song.id>0).select(orderby=~db.song.nod,limitby=(0,10)) #contains details of recently  uploadded files
    recent=db(db.song.id>0).select(orderby=~db.song.doup,limitby=(0,4)) #contains details of recently uploaded files
    byme=db(db.song.user_id==session.auth.user.id).select(orderby=~db.song.doup,limitby=(0,15)) #contains details of top songs uploaded by user

    return dict(form=form,down=down,recent=recent,byme=byme)
    
 
#controller for updating profile only for genral users and not admin
@auth.requires_login()
def update_profile(): 

    var1 = session.auth.user.id
    form = crud.update(db.auth_user, var1) 
       	      
    down=db(db.song.id>0).select(orderby=~db.song.nod,limitby=(0,10)) #contains details of recently  uploadded files
    recent=db(db.song.id>0).select(orderby=~db.song.doup,limitby=(0,4)) #contains details of recently uploaded files
    byme=db(db.song.user_id==session.auth.user.id).select(orderby=~db.song.doup,limitby=(0,15)) #contains details of top songs uploaded by user

    return dict(form=form,down=down,recent=recent,byme=byme)

      
import os

#controller forhandle playlist page
@auth.requires_login()
def playlist():    
        pageno=0
        next=0
        pre=0
        no=11
        n=11
        if request.vars.has_key('pageno'):
            pageno=int(request.vars['pageno'])      #get the current page no
            if pageno < 0 : redirect(URL(r=request,f='user',c='default',args='logout'))
            no=pageno*11+11
        
        byme=db(db.playlist.user==session.auth.user.id).select()#contains details of top songs uploaded by user
        
        iid=0  
        
          
        li=[]
        for i in byme:
            li+=[i.id]
        if len(li)>0: iid=li[0]
        
                
        if request.vars.has_key('id'):
            iid=int(request.vars['id'])    
            
        if len(li)>0 and iid not in li: redirect(URL(r=request,f='user',c='default',args='logout'))#if passed vars is not in range callfor logout
        
        count=db(db.playlist.user==session.auth.user.id).count()#get the total no of entries
        
        if pageno*11 > count: redirect(URL(r=request,f='user',c='default',args='logout'))#if passed vars is not in range callfor logout
        elif pageno*11==count and pageno >0:redirect(URL(r=request,f='playlist',c='default',vars=dict(pageno=pageno-1)))#redirect to previouspage
      
        song=db((db.list.list==iid)&(db.list.song==db.song.id)&(db.song.file==db.files.id)).select()  #order by orders
        pname=""
        for i in db(db.playlist.id==iid).select():
             pname=i.name
        #create the playlist .xfps file
        str1='﻿<?xml version="1.0" encoding="UTF-8" ?> \n<playlist version="0" xmlns="http://xspf.org/ns/0/">\n <title>'
        str2=''' 
         </title>
         <trackList>'''
        str3='''<track>
          <location>'''

        str4='''</location>
            <image>'''
        str5='''</image>
        <annotation>'''
        str6='''</annotation>
            </track>'''
        str7='''</trackList>
            </playlist>'''
        if len(li)>0 :
            plist=file(os.path.join(request.folder,'static',('tmp'+'.xspf')),'w')
            plist.write(str1)
            plist.write(pname)
            plist.write(str2)
        
            for i in song:
               plist.write(str3)
               plist.write(str(URL(r=request,f='download',c='default',args=i.files.file)))
               plist.write(str4)
               plist.write(str(URL(request.application,'static',i.song.pic)))
               plist.write(str5)
               plist.write(i.song.name)
               plist.write(str6)
               #response.flash=song
            plist.write(str7)        
            plist.close()
            #the playlist is created
            
        if pageno>0:
            pre=1
        if no <count:
            next=1
        else :
            no-=11
            n=count-no
            
        form = SQLFORM.factory(Field('new','string',label="NEW PLAYLIST"))#form to insert new playlist
            
        if form.accepts(request.vars,session):
            response.flash='New Playlist created'
            db.playlist.insert(user=session.auth.user.id,name=form.vars['new'])
            redirect(URL(r=request,f='playlist',vars=dict(pageno=pageno)))
        elif form.errors:
                response.flash='error'
        
                    
        byme=db(db.playlist.user==session.auth.user.id).select(limitby=(pageno*11,n))#contains details of top songs uploaded by user
        scr1=" " 
        if len(li)>0:   
            scr1=URL(request.application,'static','tmp'+'.xspf')
        scr2=URL(request.application,'static',os.path.join('ply','xspf_player.swf'))
            
        ply=XML('<object type="application/x-shockwave-flash" width="650" height="600" data="%(scr2)s?playlist_url=%(scr1)s">  <param name="movie"  value="%(scr2)s?autoplay=1&autoload=1&playlist_url=%(scr1)s"/> <embed  allowfullscreen="false" allowscriptaccess="always" src="%(scr2)s?playlist_url=%(scr1)s pluginspage=”http://www.macromedia.com/go/getflashplayer”" ></embed> </object>'%dict(scr1=scr1,scr2=scr2))#the XML lines for player
       
        
    	newlink = []
	newlabel = []	

	if  auth.has_membership('Secret Agent', session.auth.user.id) == True:
    		newlink.append('upload')
		newlabel.append('UPLOAD')

        	newlink.append('mymusic')
		newlabel.append('MY SONGS')

    	else:
		newlink.append('request_upload')
		newlabel.append('REQUEST')

       		newlink.append('update_profile')
		newlabel.append('PROFILE')
            
        return dict(form=form,ply=ply,pageno=pageno,pre=pre,next=next,byme=byme,pname=pname, newlink=newlink, newlabel=newlabel)
    
#the controller for play song page
@auth.requires_login()
def play():
    
        so=int(request.args(0))
        som1=db(db.song.id==so).select()
        if (db(db.song.id==so).count())<=0:
            redirect(URL(r=request,f='user',args='logout'))#call for logout if vars not in range
        
	session.song_id=so
        soid=0
        for i in som1:
          soid=i.file
          sopic=i.pic
          sonam=i.name
        som=db(db.files.id==soid).select()
        filn=""
        for i in som:
            filn=i.file
        #create form for comment
        form = SQLFORM.factory(Field('comment','text'))
        
        db.list.song.default=so
        db.list.song.readable=False
        db.list.favourite.readable=False
        db.list.listen.readable=False
        db.list.orders.readable=False
        db.list.song.writable=False
        db.list.favourite.writable=False
        db.list.listen.writable=False
        db.list.orders.writable=False
        
        myplaylist=[]
        idform=[]
        for i in db((db.playlist.user==session.auth.user.id)).select():
              myplaylist+=[i.name]
              idform+=[i.id]
        
   
        db.list.list.requires=IS_IN_SET(idform,myplaylist)
        form1=SQLFORM(db.list)
        response.flash=sonam
        if form1.accepts(request.vars,session):
            response.flash="SONG ADDED TO PLAYLIST"
        if form.accepts(request.vars,session):
            response.flash='comment added'
            db.comments.insert(user_id=session.auth.user.id,song_id=so,comment=form.vars['comment'],date=request.now)
            
             
        sopic=URL(request.application,'static',sopic)#the album art pic
        pic=XML('<img src=%(sopic)s align="center"  width="240px" height="240"\>'% dict(sopic=sopic)) 
        src=URL(r=request,c='default',f='download',args=filn)
        width='400'
        height=45
        """
        ## Embeds a media file (such as flash video or an mp3 file)
        - ``src`` is the src of the video
        - ``width`` is the width of the image
        - ``height`` is the height of the image
        """
        #the music player
        ply=XML('<embed allowfullscreen="false" allowscriptaccess="always" flashvars="height=%(height)s&width=%(width)s&file=%(src)s" height="%(height)spx" src="%(url)s" width="%(width)spx"></embed>'%dict(url=URL(request.application,'static','plugin_wiki/mediaplayer.swf'),src=src,width=width,height=height))
        
        #select the comment for the song
        comm=db((db.comments.song_id==so) &( db.comments.user_id==db.auth_user.id)).select(db.auth_user.first_name,db.auth_user.last_name,db.comments.comment,db.comments.date,db.auth_user.pic,db.auth_user.id,db.comments.id,orderby=~db.comments.date,limitby=(0,10))
        down=db(db.song.id>0).select(orderby=~db.song.nod,limitby=(0,10))
        recent=db(db.song.id>0).select(orderby=~db.song.doup,limitby=(0,4))
        byme=db(db.song.user_id==session.auth.user.id).select(orderby=~db.song.doup,limitby=(0,15))
	reco=db((db.similarity.id>0) & (db.similarity.song1==session.song_id)).select(db.similarity.song2, orderby=~db.similarity.sim,distinct=True)


    	newlink = []
	newlabel = []	

	if  auth.has_membership('Secret Agent', session.auth.user.id) == True:
    		newlink.append('upload')
		newlabel.append('UPLOAD')

        	newlink.append('mymusic')
		newlabel.append('MY SONGS')

    	else:
		newlink.append('request_upload')
		newlabel.append('REQUEST')

       		newlink.append('update_profile')
		newlabel.append('PROFILE')
        
        return dict(ply=ply,down=down,recent=recent,byme=byme,comm=comm,form=form,pic=pic,som=som1,ffff=filn,form1=form1, newlink=newlink, newlabel=newlabel, reco=reco)   

#contrller for the deleteplaylist function
@auth.requires_login()        
def deletplaylist():
    playl=int(request.vars['id'])
    pag=int(request.vars['pageno'])
    db(db.list.list==playl).delete()
    db(db.playlist.id==playl).delete()
    redirect(URL(r=request, f='playlist',vars=dict(pageno=pag)))
    return

#contrller for the deletecomment function
@auth.requires_login()
def deletcomment():
    song=int(request.vars['song'])
    com=int(request.vars['com'])
    db(db.comments.id==com).delete()
    redirect(URL(r=request, f='play',args=song))
    return        


@auth.requires_membership('adminstration')
def admins():
    names=[]
    ids=[]
    for i in db(db.auth_user.id>0).select():
              ids+=[i.id]
              names+=[i.first_name+' '+i.last_name]
    for i in db((db.auth_user.id==db.auth_membership.user_id)).select():
           k=ids.index(i.auth_user.id)
           del(ids[k])
           del(names[k])
      #  response.flash="Deleting Options"
           form2 = SQLFORM.factory(
            Field('user',requires=IS_IN_SET(ids,names),label='Delete User'))
    son=db(db.song.id>0).select()
    sonn=[]
    sonid=[]
    for i in son:
        sonid+=[i.id]
        sonn+=[i.name+' artist: '+i.artist]   
    if request.vars.has_key('user'):
       #if form2.accepts(request.vars,session):
       if not form2.errors:
        db(db.comments.user_id==request.vars['user']).delete()
        for i in db(db.playlist.user==request.vars['user']).select():
            db(db.list.list==i.id).delete()
        db(db.playlist.user==request.vars['user']).delete()
        db(db.auth_user.id==request.vars['user']).delete()
        redirect(URL(r=request,f='admins'))
       elif form2.errors: pass  
    
    form1 = SQLFORM.factory(
            Field('song',requires=IS_IN_SET(sonid,sonn),label='Delete Song'))
    
    if form1.accepts(request.vars, session):
           # response.flash="qefw"
            
        db(db.comments.song_id==request.vars['song']).delete()
        
        art=db(db.song.id==request.vars['song']).select()
        artpic=""
        for i in art:
            artpic=os.path.join(request.folder,'static',i.pic)
        try:
            os.remove(artpic)
        except OSError:
             response.flash="error"
        for i in db((db.song.id==request.vars['song'])&(db.files.id==db.song.file)).select():
            db(db.files.id==i.files.id).delete()
        db(db.song.id==request.vars['song']).delete()
        redirect(URL(r=request,f='admins'))
        
    down=db(db.song.id>0).select(orderby=~db.song.nod,limitby=(0,10))
    recent=db(db.song.id>0).select(orderby=~db.song.doup,limitby=(0,4))
    return dict(down=down,recent=recent,form=form2,form1=form1)





from mutagen.mp3 import MP3
from mutagen.easyid3 import EasyID3
import mutagen.id3
from mutagen.id3 import ID3, TIT2, TALB, TPE1, TPE2, COMM, USLT, TCOM, TCON

from mutagen.id3 import ID3NoHeaderError
from mutagen.mp3 import HeaderNotFoundError

#function to extract metadata from MP3 file
@auth.requires_login()
def get_info(f,filen): 
    filen=str(filen)
   
    m={}
    try:
        audio = MP3(f)
    except HeaderNotFoundError:
        response.flash="Error Reading file"
        ##remove the entry
        return dict(m=m,done=False) 
    try:
       tagg = ID3(f)
    except ID3NoHeaderError:
        response.flash="Error Reading file"
        ##remove the entry
        return dict(m=m,done=False)
   
    ext='.img'
    flag=1
    imgfilename=""
    #lookfor albumart
    for frame in tagg.getall("APIC"):
                flag=2
                if (frame.mime == "image/jpeg") or (frame.mime == "image/jpg"): ext = ".jpg"
                if frame.mime == "image/png": ext = ".png"
                if frame.mime == "image/gif": ext = ".gif"

                filen=filen+ext
                #storethe album art
                imgfilename=os.path.join(request.folder,'static',filen)
             
                myfile = file(imgfilename, 'w')
                myfile.write(frame.data)
                myfile.close()
    if(flag==1):
                filen=filen+'.jpg'
                imgfilename=str(URL(request.folder,'static','albumart.jpg'))
                ff=file(imgfilename,'r')
                imgfilename=os.path.join(request.folder,'static',filen)
                myfile = file(imgfilename, 'w')
                myfile.write(ff.read())
                myfile.close()
                ff.close()
    m={}            
    m = dict(MP3(f, ID3=EasyID3))
    l=tagg.getall(u"USLT")
    m['lyrics']=""
    if(not(m.has_key('artist'))):m['artist']=['unknown']
    if(not(m.has_key('album'))):m['album']=['unknown']
    if(not(m.has_key('title'))):m['title']=['unknown']
    if(not(m.has_key('genere'))):m['genere']=['unknown']  
    if(not(m.has_key('date'))):m[u'date']=['2014']
    m['date']=m['date'][0][:4]
    for i in tagg.getall(u"USLT"):
         m['lyrics']=i.text
         
    m['length']=audio.info.length
    m['bit_rate']=audio.info.bitrate/(1000)
    m['img']=filen
    
    return dict(m=m,done=True)

from math import *
@auth.requires_membership('Secret Agent')    
def similarity(item, musicitem):
    si = {}
    f = open('/home/aakarshit/Desktop/test4', 'a')
    f.write('calculating similarity between')
    f.write(str(item)+'and'+str(musicitem)+'\n')    
    rateList1 = db((db.prefs.id>0) & (db.prefs.song_id==item)).select(db.prefs.user_id, db.prefs.rating)
    rateList2 = db((db.prefs.id>0) & (db.prefs.song_id==musicitem)).select(db.prefs.user_id, db.prefs.rating)
    sum1=0
    sum2=0
    n=0
    sum1Sq=0
    sum2Sq=0
    pSum=0
    for x in rateList1:
    	for y in rateList2:
    		if x.user_id==y.user_id:
    			sum1 += x.rating
    			sum2 += y.rating
    			sum1Sq += pow(x.rating, 2)
    			sum2Sq += pow(y.rating, 2)
    			n += 1
    			f.write(str(n))
			pSum += x.rating * y.rating
			
    if n==0: return 0    
    num=pSum-(sum1*sum2/n)
    den=sqrt((sum1Sq-pow(sum1,2)/n)*(sum2Sq-pow(sum2,2)/n))
    if den==0: return 0  
    r = num/den
    db.similarity.insert(song1=item, song2=musicitem, sim=r)
    return r
	
@auth.requires_membership('Secret Agent')	
def topMatches(item):
    f = open('/home/aakarshit/Desktop/test2', 'a')
    var1=str(item)
    f.write('Topmatches for :')
    f.write(var1)
    f.write('\n')
    for musicitem in db(db.prefs.id>0).select(db.prefs.song_id,distinct=True):
    	if musicitem.song_id!=item:
    		var = str(musicitem.song_id)
    		f.write(var)
    		f.write('  ')
    		var3=similarity(item, musicitem.song_id)
		scores = [(musicitem.song_id, var3)]
		f.write('Similarity with :')
		f.write(str(item))
		f.write(' is :')
		f.write(str(var3))
		f.write('\n')
			
    f.write('\n')		
    scores.sort()
    scores.reverse()
    return scores[0:5]
    
@auth.requires_membership('Secret Agent')    
def calcSimilarityItems():
#Input from the database table prefs no need to pass as argument
#for item based filtering find top matches for each song and construct a list<or store in database>
    f = open('/home/aakarshit/Desktop/test3', 'w')
    f.write('hello calcSimilarityItems\n')
    result = {}
    i=0
    for item in db(db.prefs.id>0).select(db.prefs.song_id,distinct=True):
        var = str(item.song_id)
        var2 = str(i)
        f.write(var2)
        f.write('  ')
        f.write(var)
        f.write('\n')
        i+=1 
    	scores = topMatches( item.song_id )
    	result[item.song_id] = scores
    return result
