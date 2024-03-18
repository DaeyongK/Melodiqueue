var input_box = document.getElementById("userInput");

input_box.addEventListener("keypress", function(e) {
    if (e.code === "Enter" && !e.shiftKey && input_box.value != "") {
        sendMessage();
        document.getElementById("userInput").value = '';
    }
});

input_box.addEventListener("input", function(e) {
    if (e.inputType === "insertLineBreak") {
        input_box.value = input_box.value.replace(/\n/g, '')
    }
});

function sendMessage() {
    const userInput = input_box.value;
    const chatBox = document.getElementById('chatBox');

    const userMessage = document.createElement('div');
    userMessage.className = 'container message user-message';
    userMessage.innerText = userInput;
    chatBox.appendChild(userMessage);
    const encodedUserInput = `/generate_response/`+ encodeURIComponent(encodeURIComponent(userInput));

    var result = "";
    fetch(encodedUserInput)
        .then(response => response.json())
        .then(data => {
            result = data.result;

            const botMessage = document.createElement('div');
            botMessage.className = 'container message bot-message';
            botMessage.innerText = `${result}`;
            chatBox.appendChild(botMessage);
            
            chatBox.scrollTop = chatBox.scrollHeight;
        })
        .catch(error => console.error('Error:', error));
}

function deleteFile(filename) {
    var csrftoken = $("[name=csrfmiddlewaretoken]").val();  

    $.ajax({
        url: 'delete_file/',
        type: 'POST',
        headers: { 'X-CSRFToken': csrftoken },  
        data: { filename: filename },
        success: function (response) {
            $('#file-list li:contains("' + filename + '")').remove();
        },
        error: function (error) {
            console.log(error);
        }
    });
}
