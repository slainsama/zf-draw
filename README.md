# zf-draw

Automated spider for zfrontier lottery with a web manager.



## Statement

This program is just for learn, don't use it to do anything illegal.

If this program violates your rights, please contact me to delete.



## Quick Start

*Read this for a quick use.*

### Install requirements

```shell
pip install -r requirements.txt
```
### Fill the config file

such as this.
```ini
[database]
host = localhost
port = 3306
name = test
user = test
password = test

[token]
manager_token = secretkey
```
> The token is **the only key** to ensure your access to manage the spider.

Please **make sure to modify** the `manager_token` !

### Start the server

Start with flask's developing server
```shell
flask run
```
Start with gunicorn
```shell
gunicorn -w 3 -b 127.0.0.1:8080 main:app
# -w for num of worker
# -b for port binding
# main for your file name
# app for your instance name
```
> In consideration of all aspects, it is recommended that you do not use the server that comes with flask to start.

## Documents

If you don't want to re-develop this program, you can ignore the following part.

```
.
├── README.md
├── config.exsample.ini
├── config.ini
├── globals
│   ├── __init__.py
│   ├── config.py
│   └── database.py
├── main.py
├── models
│   ├── __init__.py
│   └── user_picked.py
├── requirements.txt
├── spider_models
│   ├── __init__.py
│   └── user.py
├── templates
│   ├── index.html
│   └── status.html
└── utils
    ├── __init__.py
    ├── post_utils.py
    ├── schedule_utils.py
    └── user_utils.py

```

The core code for zfrontier's api is in the `spider_models.user.User`.

It's a encapsulation of the user-api.

### about User init

We have 2 ways to login, with password or with qrcode, correspondingly, as the `login_with_passwd` method and the `login` method. Mostly, we use `login_with_passwd` to get auth because of its convinience.

Once we new a `User` obj, it will be append to `User.user_list`.

Once we login successfully, its information will be insert  to database.

And we have some methods to pickle or unpickle user object to or from database.

#### login_with_passwd()

Method of `spider_models.user.User`

Just login with your password!

for a exsample:

```python
new_user = User()
new_user.login_with_passwd('12345678901', 'password')
```

#### login()

Method of `spider_models.user.User`

Login with a qrcode.

It will show you a QRimage, scan the image to get in with  your phone zfrontier app.

This method has no arg, use it like this.

```python
new_user = User()
new_user.login()
```

#### pickle_self()

Method of `spider_models.user.User`

Pickle self to `database.userpickled.data` .

```python
new_user = User()
new_user.pickle_self()
```

#### add_user()

In `utils.user_utils`

A encapsulation for `login_with_passwd()`, but just write data to database.

Return "Success added!" or `Exception`

```python
add_user('12345678901', 'password')
```

#### load_from_database()

In `utils.user_utils`

Load all record from database.

No return.

```python
load_from_database()
```

#### cleanup_all()

In `utils.user_utils`

Pickle all obj of class `User` to database.

Use to save obj in some unexcepted situations mostly.

```python
except Exception as e:
	print(e)
	cleanup_all()
```

### get posts with lottery

According to observation, most the drawing posts in `/app/circle/1#2007`, so we just get posts from that.

#### get_list()

In `utils.post_utils`

```python
get_list(offset=False)
```

The `offset` is a signal for the list of flow type from the website.

It's the last one post's id in your previous request.

We suppose you've just got a json(simplified) like this.

```json
{
  "ok":0,
  "msg":"",
  "data":{
    "list":[
      {"id":114514,...},
       {"id":114513,...},
    {"id":114512,...}]
  } 
}
```

If you wanna get the post that id=114511, you need to request like this.

```python
get_list(offset=114512)
```

Actually, `get_list` is a recursive function, it will request posts until the post_id less than the min last_replied. So it suppose to return a list that include post_id that your users hasn't requested.

### Participate in the lottery

#### User.reply()

The way that you participate in a lottery is by replying to it.

So, use `User.reply()` to participate in.

```python
test=User()
test.reply(114514)
```

### scheduled task

#### scheduled_task()

In `utils.schedule_utils`

This func is for the scheduled task, it will call the `get_list()`, then choose right users to reply it.

```python
scheduled_task(User.user_list
```

