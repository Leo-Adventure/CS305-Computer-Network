# Danmuku System 

## Basic part

### Web Socket 

#### Building a Websocket connection

Using

```js
var ws = new WebSocket('ws://localhost:8765');
```

to build the websocket connection to `localhost:8765`

#### Receiving danmakus with "Send" button and send the danmakus

Using the code showing below, we can receive the message by "click" action, then accept the danmakus information in web page. Then I wiil send the message to the server using "send" method.

```javascript
$(".send").on("click", function () {
    const v = document.getElementById("danmakutext").value;
    ws.send(v)
});
```

#### Broadcast to all the clients and show the danmakus in them

In Python code, when I finish building the connection to the websocket server, I can maintein a global list to record all the clients connecting to the server.

```python
 connected.append(websocket)
    
```

Then the server will accept all the information sent by clients, then will broadcast the message to all the clients, then the clients will show the message reveived.

```python
while True: 
    msg = await websocket.recv() 
    websockets.broadcast(connected, msg)
    print ("Receive a message: {}".format(msg))
```

```js
ws.onmessage = function (data) {
    const rec_danmuku = createDanmaku(data.data);
    addInterval(rec_danmuku);
}
```

#### The exit of client

The exit of client will trigger a `websockets.exceptions.ConnectionClosedOK` exception, then we can catch the exception then signal the exit information to user.

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

#### Display the history danmakus in newcomer client

Using a global list to save all the history danmakus, we can make all the newcomer client will display all the history danmakus.

```python
for msg in history:
    await websocket.send(msg)
```

The 'history' in it save the history danmakus.

The basic part of websocket danmakus is shown as above.

### HTTP Part

#### Send Danmakus to Server

By concat the danmakus in the end of url, we can then use POST method to pass the danmakus to the server.

```javascript
$(".send").on("click", function () {

    const v = document.getElementById("danmakutext").value;
    console.log(v)
    url = "http://127.0.0.1:8765/" + v

    $.post(url, v, function (data) {

    });

    });
```

#### Receive and save the danmakus.

By analyze the path information passed by url, the server can extract the danmakus information from  URL and save it.

```python
if httpHeader.get('method') == 'POST':
    danmu = httpHeader.path
    danmu = danmu[1:len(danmu)]
    danmakus.append(danmu) # save in the global list
    httpHeader.set_state('200 OK')
    writer.write(httpHeader.message().encode(encoding='utf-8')
```

#### Require the danmakus by polling

```javascript
 // 发起长轮询，得到弹幕之后进行create 之后addinterval发送
    setInterval("request();", 0.001 * 60 * 1000);//每隔一段时间执行一次request 函数

    function request() {

      request_danmu_url = "http://127.0.0.1:8765/" + id;

      $.get(request_danmu_url, function (data) {
        // console.log("In conducting...")
        // console.log(data)
        // get the id information from data
        if (data != '') {
          // get the danmakus information
          // console.log("data is not empty")
          const danmaku_to_print = createDanmaku(data);
          addInterval(danmaku_to_print);
          id = id + 1;
        }
      })
    }
```

#### Send  the danmakus information

When the server reveive the "GET" request to get new danmakus information, the server will use "writer.write" method to write back the danmakus information to the client.

```javascript
id = httpHeader.get('path')[1:]
    id = int(id)
    httpHeader.set_state('200 OK')
    writer.write(httpHeader.message().encode(encoding='utf-8'))
    if id < len(danmakus): #return the danmakus required by client
        for index in range(id, len(danmakus)):
        	writer.write(danmakus[index].encode(encoding='utf-8'))
```




## Result show

### Websocket

![image-20220427232042671](C:\Users\86181\AppData\Roaming\Typora\typora-user-images\image-20220427232042671.png)

### HTTP

![image-20220427231507893](C:\Users\86181\AppData\Roaming\Typora\typora-user-images\image-20220427231507893.png)



## Bonus Part

### Beautify the Danmakus

Changing the HTML code to make the color and size of danmakus to change in random. Then the users will find it comfortable to watch the danmakus.

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

And I also change the margin color and add background picture, etc to make the system more beatiful.

![image-20220427234720200](C:\Users\86181\AppData\Roaming\Typora\typora-user-images\image-20220427234720200.png)

## Comparision between WebSocket and HTTP

1. Websocket is a two-way communication protocol, which can send or receive information in both directions. While HTTP is a one-way communication protocol, which can only be launched by client, not server.
2. After I implemented the two version of Danmakus system, I noticed that the WebSocket requires a handshake between the browser and the server to establish a connection, while http is a connection initiated by the browser to the server.
3. Because of the polling rule in HTTP, the pressure of server is bigger than the Websocket server.
4. The data transmitted by Websocket is usually less than which sent by HTTP, because the HTTP is stateless, which means that redundant information about the request is sent in every HTTP request and response in order to use Cookie to identify client, while Websocket client has its status. The transmission of Websocket upgrade the efficiency compared to HTTP.
5. The speed of Websocket is faster than the HTTP. Because data is displayed on the client side using a web socket, which is continuously sent by the backend server. In WebSocket, data is continuously pushed/transmitted into the same connection that is already open, while HTTP will somtimes close the connection after return some information, which is why WebSocket is faster than HTTP and improves application performance.
