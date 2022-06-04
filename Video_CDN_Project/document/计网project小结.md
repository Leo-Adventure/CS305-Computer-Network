```
首先我觉得你需要理解docker端口映射的事情，docker是一个容器，那么他的端口就不是由你的本地能访问到的，那就需要映射
```

 ```
 docker run -it -p 7778:7778 -p 7779:7779 -p 8080:8080 -p 8081:8081 project:latest /bin/bash
 docker run -it -p 7778:7778 -p 7779:7779 project:latest /bin/bash
 docker run -it -p 8080:8080 -p 8081:8081 project:latest /bin/bash
 先准备好环境
 python3 ./netsim.py servers start -s servers/2servers 
 这个是启动服务器最核心的指令
 python3 ./netsim.py servers stop -s servers/2servers 
 这个可以停止服务器
 http://localhost:8080/index.html
 不加http无法访问（这个问题仅存在ie tag里面）
 %systemroot%\system32\f12\IEChooser.exe 
 有可能需要添加127.0.0.1替换localhost（这个在docker里面有点问题）
 
 python3 proxy2.py record.py 0.6 7778 7777 8080
 python3 proxy4.py record.py 0.6 7778 7777 8080
 
 
 启动项目具体操作流程
 python3 ./netsim.py servers start -s servers/2servers
 python3 dns.py
 python3 proxy4.py record.py 0.6 7778 7777 8080
 http://127.0.0.1:7778/index.html
 
 #开启图形化界面调试这个端口是要改变的，没法命令行
 /usr/bin/env /usr/bin/python3 /root/.vscode-server/extensions/ms-python.python-2022.6.2/pythonFiles/lib/python/debugpy/launcher 36441 -- /autograder/netsim/proxy4.py record.py 0.6 7778 7777 8080
 ```

如果遇到这个错误：

![image-20220430153657052](C:\Users\zhangliyu\AppData\Roaming\Typora\typora-user-images\image-20220430153657052.png)

请把github clone 的文件 移动到docker镜像里面去

```
docker ps 可以查看image的id
docker cp 拷贝文件
或者用徐延凯方法也可以
```

vscode可以通过再打开远程窗口的方式更换文件夹，只不过需要在远程资源管理器里面

```
25版本的firefox还是不行，而且还自动卸载新的firefox，现在暂时卡在ie tag插件edge浏览器能打开，debug准备直接开写

```



### 具体实现思路

![image-20220502175746087](C:\Users\zhangliyu\AppData\Roaming\Typora\typora-user-images\image-20220502175746087.png)

我主要想用flask和requests这个2个库去实现，然后完美复刻学姐在腾讯视频里面的这个图的经历

```
主要的学习文档
https://docs.python-requests.org/zh_CN/latest/search.html?q=get&check_keywords=yes&area=default
上面是flask的官方文档
https://zhuanlan.zhihu.com/p/137649301 requests是神库，直接调用

https://dormousehole.readthedocs.io/en/1.1.2/api.html?highlight=request%20arg#flask.Request.args
上面这个网址是对于request该去拿什么信息的一个访问，实际上后来这个网址没有用上，因为传递信息通过另外的方式完成

https://www.w3cschool.cn/flask/flask_variable_rules.html
这个主要是flask路由变量规则可以



```

然后在实际跑在docker上面可能会遇到没有检测到端口的问题，一定要vscode检测到端口外部才能访问



现在遇到问题是没法区分客户端，这个问题暂时搁置，因为理论上确实要多进程



![image-20220503151931943](C:\Users\zhangliyu\AppData\Roaming\Typora\typora-user-images\image-20220503151931943.png)

![image-20220503152023133](C:\Users\zhangliyu\AppData\Roaming\Typora\typora-user-images\image-20220503152023133.png)

flask会遇到外部浏览器不能访问，需要手动开启

![image-20220503173205523](C:\Users\zhangliyu\AppData\Roaming\Typora\typora-user-images\image-20220503173205523.png)

这个暂时不知道解决办法，只能在vscode开启端口





#### 现在发现强行锁清晰度是可以的

你请求10返回的是1000flash也是可以解析的，这是一个好消息



还有就是我在算Throught estimation 的时候其实这个算法是不完备的，因为没有考虑到client到这个proxy之间的时间，然后还有就是多个连接的问题，



退出服务器可能是abort（）函数

记录服务器的单独的id应该是session key

现在发现TCP每次请求都是不一样的，主要返回回去是close对象的

现在要么继续往session key去努力，要么keepalive

### vscode 远程文件复制问题

本地文件可以打开文件资源管理器，remote可以下载到本机的指定位置
