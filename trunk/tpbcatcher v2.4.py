"""
encoding: utf-8
language:  python 2.7.3
author:   shijie
date:     Mar. 25th,2012
version   2.4.1
purpose:  Spider for the Pirate Bay
modified: Mar. 30th,2012

"""
#==========================================================================================
import urllib,urllib2
import re,os,sys
import codecs
import socket
import datetime,time
import threading
from bs4 import BeautifulSoup 
from django.utils.encoding import smart_str, smart_unicode
#==========================================================================================
#GLOBAL VARIABLES
FLAGTITLE=r"Download music, movies, games, software! The Pirate Bay - The galaxy's most resilient BitTorrent site"
FLAGTPB=r"Not Found | The Pirate Bay - The world's most resilient BitTorrent site"
Table=[100, 101, 102, 103, 104, 199, 200, 201, 202, 203, 204, 205, 206, 207, 208, 209, 299, 300, 301, 302, 303, 304, 305, 306, 399, 400, 401, 402, 403, 404, 405, 406, 407, 408, 499, 500, 501, 502, 503, 504, 505, 506, 599, 600, 601, 602, 603, 604, 605, 699]
Chars=[r'/',r'\\',r':',r'?',r'"',r'<',r'>',r'|',r'*']
Ger2Eng={'Porno':'Porn','Programma\'s':'Applications','Andere':'Other','Anders':'Other','Film':'Movie','TV-programma\'s':'TV shows','Hoezen':'Covers','video\'s':'videos','Strips':'Comics','Foto\'s':'Pictures','Gesproken boeken':'Audio books','Muziek':'Music'}
tpbURL=['thepiratebay.se','malaysiabay.org','all4xs.net/repress/thepiratebay.se','labaia.ws']

totDict={} 
url=''
socket.setdefaulttimeout(6000)

switch=False
update=False
copy=True
mode=0
#==========================================================================================
#Regular Expression
re_name=re.compile(r'<optgroup label=\".*\">')
re_title=re.compile(r'/torrent/[0-9]+/(.*)')
re_type=re.compile(r'option value=\">.*</option>')
re_info=re.compile(r'<pre>.*')
re_size=re.compile(r'<dd>.*\.*&nbsp;.iB&nbsp;\(.*&nbsp;Bytes\)')
re_file=re.compile(r'return false;\">(.*)</a></dd>')
re_by=re.compile(r'\/user\/(.*)\/\"')
re_anoymous=re.compile(r'<i>(Anonymous)</i>')
re_uploaded=re.compile(r'<dd>[0-9]{4}-..-.. ..:..:.. ...')
re_comments=re.compile(r'<a href=\"/user/(.*)/\" title="Browse .*\">.*</a>.*\n</p>')
re_infohash=re.compile(r'<dt>Info Hash:</dt><dd>&nbsp;</dd>\n.*</dl>')
re_magnet=re.compile(r'\"(magnet:?.*)\" title=\"Get this torrent\">')
re_mag=re.compile(r'\"(magnet:?.*)\" title=\"Download this torrent using magnet\">')
re_magex=re.compile(r'(magnet:?.*)&dn=')
re_url=re.compile(r'<a href=\"(.*)\" class=\"detLink\"')
re_genre=re.compile(r'<a href=\"/.+/.+\" title=\".*\">(.*)<(/)a><br />\n.*\(<a href=\"/.+/.+\" title=\".*\">(.*)</a>\)')
#============================================================================================
class item:
    def __init__(self):
        self.title=''
        self.file=''
        self.size=''
        self.id=''
        self.url=''
        self.comments=''
        self.type=''
        self.by=''
        self.magnet=''
        self.info=''
        self.torrent=''
        self.path=''
#============================================================================================
def fetch_dir(pageURL):
    webpage=urllib.urlopen(pageURL) 
    soup=BeautifulSoup(webpage.read())

    #Retrieve category
    catList=[]   
    for tag in soup.find_all('optgroup'):
        name=tag.get('label').replace('/','_')
        catList.append(name)
        
        #Retrieve Sub-category
        urlDict={}
        for sub in tag.find_all('option'):
            code=sub.contents[0].replace('/','_')             
            urlDict[sub.get('value')]=code
        totDict[name]=urlDict
        
    #Make directory
    output=open(r'index.txt','w')    
    for i in totDict:
        output.write(i+'\n')
        if not os.path.exists(i):
            os.mkdir(i)
        for j in totDict[i]:
            output.write(r'    '+''.join(totDict[i][j]+' '+j)+'\n')
            path=os.curdir+r'/'+i+r'/'+''.join(totDict[i][j])             
            if not os.path.exists(path):
                os.mkdir(path)
    output.close()
#======================================================================================        
def fetch_page(pageURL,which,spirit=None):    
    try: 
        webpage=urllib2.urlopen(pageURL,None,600)
        if webpage == None:
            print pageURL,'...reconnecting...'  
            return -1
    except:
    #except(urllib2.HTTPError,urllib2.URLError,IOError,Exception):
        print pageURL,'...reconnecting...' 
        return -1
    
    stream=webpage.read()
    soup=BeautifulSoup(stream)
    
    #print stream    
    #print soup.original_encoding

    #SWITCH BETWEEN PROXY AND ORIGINAL SITE
    pid=''.join(re.findall(re.compile(r"/torrent/([0-9]*)"),pageURL))
    SIGNATURE=u''
    for sig in soup.title.contents:
        SIGNATURE=SIGNATURE+smart_unicode(sig)
    if(switch):        
        if SIGNATURE== FLAGTITLE:
            print pid,'....none....'  
            return 0
    else:
        if SIGNATURE == FLAGTPB:
            print pid,'....none....'  
            return 0
    enableWrite=False
    #See if in search mode
    if spirit== None:        
        temp=item()
        temp.id = ''.join(re.findall(re.compile(r"/torrent/([0-9]*)"),pageURL))
                           
        categoryList=soup.find_all('a',title='More from this category')
        
        nameList= soup.find_all('div',id='title')        
        magnetList= re.findall(re_magnet,stream)
        if len(magnetList) > 0:
            mag_info=urllib.unquote(str(magnetList[0]))        
            temp.magnet=urllib.unquote(mag_info)        
        temp.type=  smart_unicode(''.join(categoryList[0].contents)).strip().replace(' > ',r'/')            
        temp.title= smart_unicode(filter_char(''.join(nameList[0].contents).strip())).replace('\t','')
          
        spirit=temp        
                
        enableWrite=True

    #Path 
    path=os.curdir+'/'+spirit.type.replace('(iPad/iPhone)','(iPad_iPhone)')
    target=path+'/'+spirit.title+'.index'   
    
    if update == True:
        if os.path.exists(target):
            print spirit.id,'...skipped....',target
            return 1
        elif enableWrite==True:
            save_all(spirit,which)
            
        
    output=codecs.open(target,'w','utf-8')  
    output.write( "%-15s%s\r\n"%(u'[Title]',spirit.title))
    
    #File
    number=re.findall(re_file,stream)
    spirit.file=''.join(number)
     
    output.write("%-15s%s\r\n"%(u'[Id ]',spirit.id))
    output.write("%-15s%s\r\n"%(u'[Files]',spirit.file))     
                
    #Size
    size= re.findall(re_size,stream)
    spirit.size=''.join(size)[4:].replace(r'&nbsp;',' ')
    output.write("%-15s"%(u'[Size]'))
    output.write(spirit.size)
    output.write('\r\n')
    
    #User
    user = re.findall(re_anonymous,stream)
    if len(user) > 0:
        output.write("%-15s%s\r\n"%('[User] ',smart_unicode(user[0])))
    else:
        user=re.findall(re_by,stream)
        if len(user) > 0:
           output.write("%-15s%s\r\n"%('[User] ',smart_unicode(user[0]))) 
        #spirit.by=smart_str(user[0])
    
    #Type
    output.write("%-15s"%'[Type]')
    output.write(smart_unicode(spirit.type))
    output.write('\r\n')
    
    #Time
    upload= re.findall(re_uploaded,stream)
    #spirit.upload=''.join(upload)[4:]          
    output.write("%-15s%s\r\n"%('[Upload] ',''.join(upload)[4:]))
    
    #Hash    
    hashinfo= re.findall(re_infohash,stream)
    #spirit.hash=''.join(hashinfo)[35:].replace('</dl>','').strip()
    output.write("%-15s%s\r\n"%('[Hash Info] ',''.join(hashinfo)[35:].replace('</dl>','').strip()))
    
    #Torrent
    download= re.findall(re_torrent,stream)                
    if download != None and len(download)>0:
        torrent=smart_unicode(download[0])         
        #spirit.torrent=torrent
        output.write("%-15s"%('[Torrent]'))
        output.write(torrent)
        output.write("\r\n")
        src=r'http://torrents.'+url+r'/'+torrent
        tar=path+r'/torrents/'+spirit.title+r'.torrent'
        
        if copy == True:            
            if not os.path.exists(path+r'/torrents'):
                os.mkdir(path+r'/torrents')
            if not os.path.exists(tar) or not update:
                try:
                    urllib.urlretrieve(src, urllib.unquote(tar))
                except IOError:
                    pass
    
    output.write("%-15s"%(u'[Magnet]'))
    output.write(smart_unicode(spirit.magnet))
    output.write('\r\n')
    
    #Description
    info=soup.find_all('pre')
    output.write(u'[Description]'+'\r\n')
    for inf in info:
        for t in inf.contents:
            #spirit.info=spirit.info+smart_unicode(t).replace(r'<a href="','').replace(r'</a>','').replace(r'rel="nofollow">','').replace(r'&quot;','')
            output.write(smart_unicode(t).replace(r'<a href="','').replace(r'</a>','').replace(r'rel="nofollow">','').replace(r'&quot;','') ) 
              
    #Comments
    comment_usr= re.findall(re_comments,stream)    
    
    k=0
    output.write("\r\n%-15s\r\n"%(u'[Comments]'))
    for cmt in soup.find_all('div','comment'):  
        #output.write(unicode(comment_usr[k],errors='ignore')+': ')
        output.write(smart_unicode(comment_usr[k])+': ' )
        #spirit.comments=spirit.comments+smart_unicode(comment_usr[k])+': '                     
        k=k+1  
        for c in cmt.contents:
            output.write(smart_unicode(c).replace(r'<br/>','').replace(r'<br />','').replace('\n','').replace('\r','').replace('</a>','').replace(r'<a href="',''))
            #spirit.comments=spirit.comments+smart_unicode(c).replace(r'<br/>','').replace(r'<br />','').replace('\n','').replace('\r','')+'\n'
        output.write('\r\n')
        
    output.close()   
    
    print spirit.id,'....done....',target 
    return 1
#==========================================================================================
def save_all(spirit,which):
    path = os.curdir+r'/'+spirit.type+r'/'+spirit.title
    filename = path + '.index' 
    mag_info=''.join(re.findall(re_magex,spirit.magnet))
    index_path=os.curdir+'/index/'+spirit.type.replace('iPad/iPhone','iPad_iPhone').replace('/','.')+'.index'
    index_content= spirit.id+'|'+spirit.title+'|'+spirit.type.replace('/','|')+'|'+mag_info    
    
    if not os.path.exists(filename):
        #print '@',index_path,index_content
        save_index(index_path,index_content)
        if  which == 1 :
            save_index(os.curdir+'/index/recent.index',index_content)
        elif which == 2:
            save_index(os.curdir+'/index/top/'+spirit.type.replace('/','.')+'.index',index_content)    

def save_index(path,content):     
    out=codecs.open(path,'a','utf8')
    out.write(content)
    out.write('\n')
    out.close()

def filter_char(string):
    for ch in Chars:
        string=string.replace(ch,'_')
    return string

def convert(string):
    for word in Ger2Eng:
        string=string.replace(word,Ger2Eng[word])
    return string
#==========================================================================================            
def fetch_url(pageURL,which):   
    try: 
        webpage=urllib2.urlopen(pageURL,None,600)
        if webpage == None:
            print pageURL,'...reconnecting...'
            return None
    except:
    #except(urllib2.HTTPError,urllib2.URLError,IOError,Exception):
        print pageURL,'...reconnecting...' 
        return None
    
    stream=webpage.read()
    sp=BeautifulSoup(stream)

    urlList=[]
    magList=[]
    titleList=[]

    genList=re.findall(re_genre,stream)
    
    rawList=sp.find_all('a','detLink')
    for u in rawList:
        urlList.append(u.get('href'))
        titleList.append( smart_unicode(''.join(u.contents)))
         
    rawList=sp.find_all('a',title='Download this torrent using magnet')
    for u in rawList:
        magList.append(u.get('href'))
        
    if len(magList)!= len(urlList):
        print len(magList),len(urlList)
        for i in range(len(urlList)):
            u=''.join(re.findall(re.compile(r"/(torrent/[0-9]*/)"),urlList[i]))
            fetch_page(baseURL+u,which)            
        return -1
        
    itemList=[]
    for i in range(len(urlList)):
        it=item()
        it.title=filter_char(titleList[i]).strip().replace('\t','')
        it.type=convert(''.join(genList[i]))
        it.url=''.join(re.findall(re.compile(r"/(torrent/[0-9]*/)"),urlList[i]))        
        it.id=''.join(re.findall(re.compile(r"torrent/([0-9]*)"),it.url))       
        it.magnet=urllib.unquote(magList[i])         
        itemList.append(it)
    
    return itemList
#==========================================================================================
def fetch(pageURL, which):    
    itemList=fetch_url(pageURL,which)
    print pageURL,'...loaded...'
    if itemList==-1:
        return
    while itemList==None or itemList==[]:
        itemList=fetch_url(pageURL,which)
    if len(itemList) <=0: return
    for i in range(len(itemList)): 
        new_url=baseURL+itemList[i].url
        path =os.curdir+r'/'+itemList[i].type+r'/'+itemList[i].title
        filename = path + '.index' 
        
        save_all(itemList[i],which)
        if update == False or not os.path.exists(filename):
            result=fetch_page(new_url,which,itemList[i])
            while result == -1:
                result=fetch_page(new_url,which,itemList[i])
            continue
        print itemList[i].id,'....skipped....',filename

def fetch_recent(): 
    for i in range(0,101):
        pageURL= baseURL+'recent/'+str(i)      
        fetch(pageURL,1)

def fetch_top(which=0):
    if which == 0:
        for u in Table:
            pageURL= baseURL+'top/'+str(u)              
            fetch(pageURL,2)
            if u%10==0:
                pageURL=baseURL+'top/48h'+str(u)
                fetch(pageURL,2)
        pageURL=baseURL+'top/0'
        fetch(pageURL,2)
        pageURL=baseURL+'top/all'
        fetch(pageURL,2)
        pageURL=baseURL+'top/48hall'
        fetch(pageURL,2)
    else:
        pageURL= baseURL+'top/'+str(which)          
        fetch(pageURL,2)             

def fetch_all(n,s=0,e=100,x=0,y=16):    
    for i in range(s,e):
        for j in range(x, y):            
            pageURL= baseURL+'browse/'+str(n) +'/'+ str(i) + '/' + str(j) + '/'             
            fetch(pageURL,0)
            
def fetch_range(s,e):
    for i in range(s,e+1):
        pageURL=baseURL+r'torrent/'+str(i)
        while True:
            if fetch_page(pageURL,0) != -1: break        
#========================================================================================== 
def header():
    head='[resource id]:\n'
    sss=''.join(str(Table))
    mark=0
    for i in Table:
        head=head+str(i)+' '
        mark=mark+1
        if mark%10==0: head=head+'\n'
    print head 
#==========================================================================================
if __name__ =='__main__':
     
    k=0
    for u in tpbURL:
        print k,'('+u+')'
        k=k+1
    k=int(raw_input('choose a site: '))
    url=tpbURL[k]
   
    if k== len(tpbURL)-1:
        switch=True
    else:
        switch=False

    baseURL=r'http://'+url+r'/'        
    re_torrent=re.compile(r'<a href=\"//torrents.'+url+r'/(.*)\" title=\"Torrent File\">Get Torrent File</a>')

    if int(raw_input(r'0(all) 1(update): '))==1:  update=True
    else:  update=False 
    
    if not os.path.exists(os.curdir+'/index.txt'):
        fetch_dir(baseURL+r'browse')
        
    mode=int(raw_input(r'0(normal) 1(recent) 2(top100) 3(search):'))

    begin_time = time.time()   

    if mode == 0:
        header()
        n=int(raw_input(r'code: '))
        auto=int(raw_input(r'0(all) 1(single) 2(partial): '))
        if auto == 0:  
            fetch_all(n)
        elif auto==1:
            c=int(raw_input('page: '))
            x=int(raw_input('min:  '))
            y=int(raw_input('max:  '))
            fetch_all(n,c,c+1,x,y)
        elif auto == 2:
            s=int(raw_input('min:  '))
            e=int(raw_input('max:  '))
            fetch_all(n,s,e)
    elif mode==1:
        fetch_recent()
    elif mode==2:
        auto=int(raw_input(r'0(auto) 1(single): '))
        if auto == 0 :
            fetch_top()
        else:
            header()
            print '48h100 48h200 48h300 48h400 \n48h500 48h600 48hall 0 all'
            n=str(raw_input(r'code: '))
            fetch_top(n)
    elif mode==3:
        s=int(raw_input('min: '))
        e=int(raw_input('max: '))
        fetch_range(s,e)

    print 'total time: ',time.time()-begin_time,'seconds'
