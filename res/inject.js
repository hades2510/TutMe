//check if jquery is included, otherwise included italics
if( window.jQuery )
{
    
}
else
{
    var scriptElem = document.createElement("script");
    scriptElem.type = "text/javascript";
    scriptElem.src = "//ajax.googleapis.com/ajax/libs/jquery/2.1.3/jquery.min.js";
    document.head.appendChild(scriptElem);
}

window.TutMe = {};

window.TutMe.highlightElem = function(locator, time_to_wait)
{
    //keep a ref to the element
    var elem = $(locator).first();
    
    var location = elem.offset();
    
    var x = location.left-1.5;
    var y = location.top-1.5;
    var height = elem.outerHeight()-2;
    var width = elem.outerWidth()-2;
    
    var border = $("<div></div>");
    border.attr({class:"tmigb"});
    border.css({top:y, left:x, width:width, height:height});
    
    $('body').append(border);
    
    //$(locator).first().addClass('tmigb');
    setTimeout(function(){
        $(locator).first().removeClass('tmigb');
        setTimeout(function(){
            var hidden_input = $('<input type="hidden" value="'+locator+'" id="'+locator+'"></input>');
            $('body').append(hidden_input);
        }, time_to_wait);
    }, 2000)
}