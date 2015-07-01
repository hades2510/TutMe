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