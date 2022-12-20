# sendIPの使い方
## ファイルを実行
`python3 /home/pi/demo_python/sendIP.py`
***
## raspberrypi起動時にファイルが自動実行
### /etc/rc.localにプログラムファイルの実行を追記
```
#!/bin/sh -e
...

# Line Notify
su pi -c "/home/pi/demo_python/sendIP.py" &

exit 0
```
* `su pi`とは、ユーザーpiでコマンドを実行する。
* `-c`とは、コマンドを実行した後に、元のユーザーに戻ります。
## raspberry pi3のconfigを設定する
1. `sudo raspi-config`コマンドでconfigを開く。
2. `System Options > Network at Boot`を選択する。
3. `sudo reboot`で再起動する。
