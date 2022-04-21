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

以上就是 `websocket` 进行弹幕显示的 basic 部分

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

