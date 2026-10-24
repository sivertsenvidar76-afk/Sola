import base64, http.cookiejar, os, pathlib, re, shutil, socket, sqlite3, subprocess, tempfile, time, urllib.request, urllib.parse
root=pathlib.Path(__file__).resolve().parents[1]
class Client:
 def __init__(self,base):
  self.base=base;self.opener=urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
 def get(self,path='/'):
  with self.opener.open(self.base+path) as r:return r.read().decode()
 def post(self,data,path='/',photo=False):
  data['csrf']=re.search(r'name="csrf" value="([^"]+)"',self.get())[1]
  headers={}
  if photo:
   boundary='SolaTestBoundary';parts=[]
   for k,v in data.items():parts.append(f'--{boundary}\r\nContent-Disposition: form-data; name="{k}"\r\n\r\n{v}\r\n'.encode())
   png=base64.b64decode('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+j5xkAAAAASUVORK5CYII=')
   parts.append(f'--{boundary}\r\nContent-Disposition: form-data; name="photo"; filename="photo.png"\r\nContent-Type: image/png\r\n\r\n'.encode()+png+b'\r\n')
   body=b''.join(parts)+f'--{boundary}--\r\n'.encode();headers['Content-Type']='multipart/form-data; boundary='+boundary
  else:body=urllib.parse.urlencode(data).encode()
  with self.opener.open(urllib.request.Request(self.base+path,data=body,headers=headers)) as r:return r.read().decode()
with tempfile.TemporaryDirectory() as temp:
 copy=pathlib.Path(temp)/'app';shutil.copytree(root,copy,ignore=shutil.ignore_patterns('.git','var'));(copy/'var').mkdir()
 with socket.socket() as s:s.bind(('127.0.0.1',0));port=s.getsockname()[1]
 nested=os.environ.get('SOLA_SUBDIR')=='1'
 docroot=copy/'public'
 if nested:
  docroot=pathlib.Path(temp)/'www';docroot.mkdir();(docroot/'sola').symlink_to(copy/'public',target_is_directory=True)
 with open(pathlib.Path(temp)/'server.log','w+') as log:
  proc=subprocess.Popen([os.environ.get('PHP_BIN','php'),'-S',f'127.0.0.1:{port}','-t',str(docroot)],stdout=log,stderr=log)
  try:
   base=f'http://127.0.0.1:{port}'+('/sola' if nested else '');admin=Client(base)
   for _ in range(50):
    try:admin.get();break
    except OSError:time.sleep(.1)
   assert 'Opprett butikken' in admin.get()
   home=admin.get()
   css=re.search(r'href="([^"]+style.css[^"]*)"',home)
   assert 'href="style.css?v=2"' in home
   with admin.opener.open(urllib.parse.urljoin(base+'/', 'style.css?v=2')) as asset:
    assert 'text/css' in asset.headers['Content-Type'] and b'.login' in asset.read()
   with admin.opener.open(urllib.parse.urljoin(base+'/', 'app.js?v=2')) as asset:
    assert b'lookup' in asset.read()
   admin.post(dict(action='setup',name='Butikkeier',email='admin@example.test',password='AdminPassword123!'))
   for n in (1,2):
    result=admin.post(dict(action='seller',name=f'Selger {n}',email=f's{n}@example.test',password='SellerPassword123!',share='80'))
    assert 'class="alert"' not in result, re.findall(r'<p class="alert">(.*?)</p>',result)
   db=sqlite3.connect(copy/'var/shop.sqlite')
   sellers=[r[0] for r in db.execute("SELECT id FROM users WHERE role='seller' ORDER BY id")]
   seller=Client(base);seller.post(dict(action='login',email='s1@example.test',password='SellerPassword123!'))
   html=seller.post(dict(action='item',seller_id=sellers[1],name='Blå genser',size='M',price='199,90',rack_id='1'),photo=True)
   assert 'SOLA-000001' in html
   assert db.execute('SELECT seller_id FROM items WHERE id=1').fetchone()[0]==sellers[0]
   admin.post(dict(action='item',seller_id=sellers[1],name='Hemmelig kjole',size='S',price='300',rack_id='1'))
   assert 'Hemmelig kjole' not in seller.get()
   assert 'Fant ikke plagget' in seller.get('/?item=2')
   assert 'Kun butikkansatte' in seller.post(dict(action='sell',item_id='1'))
   bad=admin.opener.open(urllib.request.Request(base,data=b'action=sell&item_id=1&csrf=bad')).read().decode()
   assert 'Skjemaet utløp' in bad
   assert 'Solgt' in admin.post(dict(action='sell',item_id='1'))
   assert 'allerede solgt' in admin.post(dict(action='sell',item_id='1'))
   assert db.execute('SELECT seller_amount,shop_amount FROM sales').fetchone()==(15992,3998)
   admin.post(dict(action='payout',seller_id=sellers[0],return_='settlement'))
   assert db.execute('SELECT amount FROM payouts').fetchone()[0]==15992
   assert db.execute('SELECT payout_id FROM sales').fetchone()[0] is not None
   assert 'Ingen utestående' in admin.post(dict(action='payout',seller_id=sellers[0]))
   assert db.execute('SELECT COUNT(*) FROM payouts').fetchone()[0]==1
   assert '159,92 kr' in seller.get('/?page=settlement')
   guest=Client(base)
   assert 'Opprett bruker' in guest.get('/?page=new')
   assert 'Gjenta passord' in guest.get('/?page=register')
   registration=dict(action='register',name='Ny selger',email='new@example.test',password='NewPassword123!',password_confirm='different',role='admin',share='100')
   assert 'Passordene er ikke like' in guest.post(registration,path='/?page=register')
   assert not db.execute("SELECT id FROM users WHERE email='new@example.test'").fetchone()
   registration['password_confirm']=registration['password']
   assert 'Ny selger' in guest.post(registration,path='/?page=register')
   account=db.execute("SELECT role,share,password FROM users WHERE email='new@example.test'").fetchone()
   assert account[:2]==('seller',80) and account[2]!=registration['password']
   assert 'Hemmelig kjole' not in guest.get()
   assert 'Kun butikkansatte' in guest.post(dict(action='sell',item_id='2'))
   guest.post(dict(action='logout'))
   assert 'Kunne ikke lagre' in guest.post(registration,path='/?page=register')
   assert db.execute("SELECT COUNT(*) FROM users WHERE email='new@example.test'").fetchone()[0]==1
   assert 'Ny selger' in guest.post(dict(action='login',email='NEW@example.test',password=registration['password']))
   guest.post(dict(action='logout'));assert 'Logg inn' in guest.get('/?page=settlement')
   admin.post(dict(action='logout'));assert 'Logg inn' in admin.get()
   print('PASS: brukerregistrering, passordbekreftelse, duplikatkontroll, låst selgerrolle, oppsett, innlogging, bilde, eierskap, tilgang, CSRF, salg, 80/20-fordeling, dobbeltsalg, utbetaling, dobbeltutbetaling, utlogging')
  except Exception:
   log.seek(0);print(log.read());raise
  finally:proc.terminate();proc.wait()
