$.fn.teletype = function(opts){
    var $this = this,
        defaults = {
            animDelay: 50
        },
        settings = $.extend(defaults, opts);

    $.each(settings.text.split(''), function(i, letter){
        setTimeout(function(){
            $this.html($this.html() + letter);
        }, settings.animDelay * i);
    });
};

function allType(text, timeafter, first){
    console.log(text, timeafter);
    setTimeout(function(){

            var span = $('#terminal .messages').append('<span>'+first+' </span>').children().last();
            messageCheckCount();
            span.teletype({
                            animDelay: 50, 
                            text: text
                            });
    }, timeafter);    
}

function messageCheckCount() {
    var count = $('#terminal .messages span').size();
    if(count>30){
        for (var i = 0; i < count-30; i++) {
           $('#terminal .messages span').first().remove();
        };
    }
};

$(function() {

    $("#terminalsend").keypress(function(e) {
        if (e.keyCode == 13) {
            var data = { "text" : e.target.value };
            var request = $.ajax({
              url: "/handler",
              type: "POST",
              data: JSON.stringify(data),
              dataType: "json",
            });
             
            request.done(function( msg ) {
              
            if(msg.userdata!=null){
                $('#terminal .messages').append('<span>>> '+msg.userdata+'</span>');
                messageCheckCount();
            }
            if(msg.data!=null){
                var previoslen = 0;
                for(text in msg.data){
                    var txt = msg.data[text];
                    allType(txt, previoslen*50*text, text==0?'<<':'&nbsp&nbsp');
                    previoslen = msg.data[text].length;
                }
            }
            $("#terminalsend").val('');
                
            });
             
            request.fail(function( jqXHR, textStatus ) {
              $('#terminal .messages').append('<span>!! Connection error </span>');
              messageCheckCount();
            });
            return false; // prevent the button click from happening
        }
    });
    var updateTimer = setInterval(update, 500);
});



function update(){
            $.ajax({
           type: "GET",
           dataType: "json",
           url: '/handler',
           success: updateTerminal
         });
}

function updateTerminal (data) {
    if(data == null)
        return;
    if(data.messages){
        previoslen = 0;
        for(m in data.messages){
            message = data.messages[m];
            allType(message, previoslen*50*m, m==0?'<<':'&nbsp&nbsp');
            previoslen = message.length;
        }
    }
}