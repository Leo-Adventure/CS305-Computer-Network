# Danmuku System 

## Basic part

### Web Socket 

#### Websocket 连接建立

通过

```js
var ws = new WebSocket('ws://localhost:8765');
```

建立到 `localhost:8765` 的 `websocket` 连接

#### 通过 send 按钮接收弹幕并发送

通过下列代码，通过 `click ` 动作接收信息，并将在网页中键入的弹幕信息进行接收，并且将该信息通过 `send` 方法发送到服务器上面

```javascript
$(".send").on("click", function () {
    const v = document.getElementById("danmakutext").value;
    ws.send(v)
});
```



#### 广播给所有客户端并各自展示

在 `python ` 代码当中，在建立与 `websocket` 服务器的连接之后，通过维护一个全局列表，将每一个连接到客户端进行记录，

```python
 connected.append(websocket)
```



不断接收来自任何一个客户端的信息，并将任何一个客户端发送过来的弹幕进行广播，将其在每个客户端都进行显示。

```python
while True: 
    msg = await websocket.recv() 
    websockets.broadcast(connected, msg)
    print ("Receive a message: {}".format(msg))
```

对于每一个客户端来说，每收到一个广播来的弹幕信息，便会在客户端进行对应的显示

```js
ws.onmessage = function (data) {
    const rec_danmuku = createDanmaku(data.data);
    addInterval(rec_danmuku);
}
```



#### 客户端退出

客户端退出会引发一个`websockets.exceptions.ConnectionClosedOK` 的异常，通过捕获该异常，进行对客户端退出信息的告知。

```python
try:
    while True: 
        msg = await websocket.recv() 
        websockets.broadcast(connected, msg)
except websockets.exceptions.ConnectionClosedOK:
    print("Bye{}".format(name))
finally:
    
    connected.remove(websocket)
    websocket.close()
```

#### 新加入客户端历史弹幕显示

通过将每一次发送的历史弹幕存储在一个全局变量当中，可以实现对于新加入的客户端，都进行历史弹幕的重新发送

```python
for msg in history:
    await websocket.send(msg)
```

其中 `history` 存储的是历史弹幕信息

以上就是 `websocket` 进行弹幕显示的 basic 部分

### HTTP Part

#### CORS 跨域错误修复

跨域问题的原因：浏览器出于安全考虑，限制访问本站点以外的资源

可以通过在 HTTP 回复报文的尾部添加以下字段，将访问权限扩大，之后即可解决

```http
'Access-Control-Allow-Origin: * \r\n' \
```

#### 客户端收到弹幕后发送到服务器

#### 服务器收到弹幕后存储

#### 客户端轮询请求弹幕信息

#### 服务器发送弹幕信息

## Bonus Part

### 弹幕颜色大小美化

通过改变前端代码，使得弹幕颜色以及大小遵循一定范围内随机使得弹幕颜色以及大小均变得更加多样

```javascript
var timestamp = Date.parse(new Date());
timestamp = timestamp % 255;
var time_str_r = timestamp + "";
var time_str_g = (timestamp + Math.random() * 100) % 255 + "";
var time_str_b = (timestamp + Math.random() * 200) % 255 + "";
const jqueryDom = $("<div class='bullet'>" + text + "</div>");
const fontColor = "rgb(" + time_str_r + "," + time_str_g + "," + time_str_b + ")";
var fsize = (Math.random() * 20 + 20) + "";
const fontSize = fsize + "px";
```

## Comparision between WebSocket and HTTP

1. Websocket is a two-way communication protocol, which can send or receive information in both directions. While HTTP is a one-way communication protocol, which can only be launched by client, not server.
2. After I implemented the two version of Danmakus system, I noticed that the WebSocket requires a handshake between the browser and the server to establish a connection, while http is a connection initiated by the browser to the server.
3. Because of the polling rule in HTTP, the pressure of server is bigger than the Websocket server.
4. The data transmitted by Websocket is usually less than which sent by HTTP, because the HTTP is stateless, which means that redundant information about the request is sent in every HTTP request and response in order to use Cookie to identify client, while Websocket client has its status. The transmission of Websocket upgrade the efficiency compared to HTTP.
5. The speed of Websocket is faster than the HTTP. Because data is displayed on the client side using a web socket, which is continuously sent by the backend server. In WebSocket, data is continuously pushed/transmitted into the same connection that is already open, while HTTP will somtimes close the connection after return some information, which is why WebSocket is faster than HTTP and improves application performance.
