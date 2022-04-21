const timers = [];
const jqueryDom = createDanmaku('hihihi'); // test danmaku, delete it as you like
addInterval(jqueryDom);// test danmaku, delete it as you like

// TODO: construct websocket for communication
var ws = new WebSocket('ws://localhost:8765');
// ws.onopen = function () {
//     console.log('ws连接状态：' + ws.readyState);
//     //连接成功则发送一个数据
//     // ws.send('test1');
// }
ws.onmessage = function (data) {
    console.log('接收到来自服务器的消息：');
    console.log(data);
    const rec_danmuku = createDanmaku(data.data);
    addInterval(rec_danmuku);
}

$(".send").on("click", function () {
    // TODO: send danmaku to server
    const v = document.getElementById("danmakutext").value;
    console.log("Send!");
    // const enprint_danmuku = createDanmaku(v);
    // addInterval(enprint_danmuku);
    ws.send(v)
});

// create a Dom object corresponding to a danmaku
function createDanmaku(text) {
    var timestamp = Date.parse(new Date());
    timestamp = timestamp % 255;
    var time_str_r = timestamp + "";
    var time_str_g = (timestamp + Math.random() * 100) % 255 + "";
    var time_str_b = (timestamp + Math.random() * 200) % 255 + "";
    const jqueryDom = $("<div class='bullet'>" + text + "</div>");
    const fontColor = "rgb(" + time_str_r + "," + time_str_g + "," + time_str_b + ")";
    var fsize = (Math.random() * 20 + 20) + "";
    const fontSize = fsize + "px";
    let top = Math.floor(Math.random() * 400) + "px";
    const left = $(".screen_container").width() + "px";
    jqueryDom.css({
        "position": 'absolute',
        "color": fontColor,
        "font-size": fontSize,
        "left": left,
        "top": top,
    });
    $(".screen_container").append(jqueryDom);
    return jqueryDom;
}
// add timer task to let the danmaku fly from right to left
function addInterval(jqueryDom) {
    let left = jqueryDom.offset().left - $(".screen_container").offset().left;
    const timer = setInterval(function () {
        left--;
        jqueryDom.css("left", left + "px");
        if (jqueryDom.offset().left + jqueryDom.width() < $(".screen_container").offset().left) {
            jqueryDom.remove();
            clearInterval(timer);
        }
    }, 5); // set delay as 5ms,which means the danmaku changes its position every 5ms
    timers.push(timer);
}