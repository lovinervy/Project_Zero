function send_video_link() {
    var url = document.getElementById("videoUrl").value;
    console.log(url)
    $.post("/get_video", url, function (data) {
        alert(`Data: ${data}`);
    });
}