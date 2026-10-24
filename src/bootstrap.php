<?php
declare(strict_types=1);
date_default_timezone_set('Europe/Oslo');
ini_set('session.use_strict_mode', '1');
session_set_cookie_params(['httponly'=>true,'samesite'=>'Lax','secure'=>!empty($_SERVER['HTTPS']) && $_SERVER['HTTPS'] !== 'off']);
@mkdir(__DIR__.'/../var/sessions',0700,true);
session_save_path(__DIR__.'/../var/sessions');
session_start();
const ROOT = __DIR__.'/..';
@mkdir(ROOT.'/var/uploads',0700,true);
$db = new PDO('sqlite:'.ROOT.'/var/shop.sqlite',null,null,[PDO::ATTR_ERRMODE=>PDO::ERRMODE_EXCEPTION,PDO::ATTR_DEFAULT_FETCH_MODE=>PDO::FETCH_ASSOC]);
$db->exec('PRAGMA foreign_keys=ON; PRAGMA busy_timeout=5000; PRAGMA journal_mode=WAL;');
$db->exec("CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY,name TEXT NOT NULL,email TEXT NOT NULL UNIQUE,password TEXT NOT NULL,role TEXT NOT NULL CHECK(role IN ('admin','seller')),share INTEGER NOT NULL DEFAULT 80 CHECK(share BETWEEN 0 AND 100));
CREATE TABLE IF NOT EXISTS racks(id INTEGER PRIMARY KEY,name TEXT NOT NULL UNIQUE);
CREATE TABLE IF NOT EXISTS items(id INTEGER PRIMARY KEY,seller_id INTEGER NOT NULL REFERENCES users(id),rack_id INTEGER NOT NULL REFERENCES racks(id),name TEXT NOT NULL,size TEXT NOT NULL,price INTEGER NOT NULL CHECK(price>0),photo TEXT,created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE IF NOT EXISTS payouts(id INTEGER PRIMARY KEY,seller_id INTEGER NOT NULL REFERENCES users(id),amount INTEGER NOT NULL,created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE IF NOT EXISTS sales(id INTEGER PRIMARY KEY,item_id INTEGER NOT NULL UNIQUE REFERENCES items(id),seller_amount INTEGER NOT NULL,shop_amount INTEGER NOT NULL,sold_by INTEGER NOT NULL REFERENCES users(id),payout_id INTEGER REFERENCES payouts(id),created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP);");
function query(string $sql,array $args=[]): PDOStatement {global $db;$s=$db->prepare($sql);$s->execute($args);return $s;}
function e(mixed $s):string{return htmlspecialchars((string)$s,ENT_QUOTES,'UTF-8');}
function money(int $v):string{return number_format($v/100,2,',',' ').' kr';}
function go(string $path='/'):never{header('Location: '.$path);exit;}
function user():?array{return isset($_SESSION['uid'])?(query('SELECT * FROM users WHERE id=?',[$_SESSION['uid']])->fetch()?:null):null;}
function admin():void{if((user()['role']??'')!=='admin')throw new RuntimeException('Kun butikkansatte har tilgang.');}
function csrf():string{return $_SESSION['csrf']??=bin2hex(random_bytes(32));}
function token():string{return '<input type="hidden" name="csrf" value="'.e(csrf()).'">';}
function cents(string $value):int{if(!preg_match('/^\d{1,7}([,.]\d{1,2})?$/',trim($value)))throw new RuntimeException('Oppgi en gyldig pris.');$v=(int)round((float)str_replace(',','.',$value)*100);if($v<1)throw new RuntimeException('Prisen må være større enn null.');return $v;}
function upload():?string{if(($_FILES['photo']['error']??UPLOAD_ERR_NO_FILE)===UPLOAD_ERR_NO_FILE)return null;$f=$_FILES['photo'];if($f['error']!==UPLOAD_ERR_OK||$f['size']>8*1024*1024)throw new RuntimeException('Bildet må være under 8 MB.');$mime=(new finfo(FILEINFO_MIME_TYPE))->file($f['tmp_name']);$ext=['image/jpeg'=>'jpg','image/png'=>'png','image/webp'=>'webp'][$mime]??null;if(!$ext||!getimagesize($f['tmp_name']))throw new RuntimeException('Bruk et JPG-, PNG- eller WebP-bilde.');$name=bin2hex(random_bytes(16)).'.'.$ext;if(!move_uploaded_file($f['tmp_name'],ROOT.'/var/uploads/'.$name))throw new RuntimeException('Kunne ikke lagre bildet.');return $name;}
