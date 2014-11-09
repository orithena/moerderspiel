function serialize_form(form) {
  if (!form || !form.elements) return;

  var serial = [], i, j, first;
  var add = function (name, value) {
    serial.push(encodeURIComponent(name) + '=' + escape(value));
  }

  var elems = form.elements;
  for (i = 0; i < elems.length; i += 1, first = false) {
    if (elems[i].name.length > 0) { /* don't include unnamed elements */
      switch (elems[i].type) {
        case 'select-one': first = true;
        case 'select-multiple':
          for (j = 0; j < elems[i].options.length; j += 1)
            if (elems[i].options[j].selected) {
              add(elems[i].name, elems[i].options[j].value);
              if (first) break; /* stop searching for select-one */
            }
          break;
        case 'checkbox':
        case 'radio': if (!elems[i].checked) break; /* else continue */
        default: add(elems[i].name, elems[i].value); break;
      }
    }
  }
  return serial.join('&');
}
function viewport()
{
	var e = window, a = 'inner';
	if ( !( 'innerWidth' in window ) )
	{
		a = 'client';
		e = document.documentElement || document.body;
	}
	return { width : e[ a+'Width' ] , height : e[ a+'Height' ] }
}
function findPos(obj) {
	var curleft = curtop = 0;
	if (obj.offsetParent) {
		do {
			curleft += obj.offsetLeft;
			curtop += obj.offsetTop;
		} while (obj = obj.offsetParent);
	}
	return [curleft,curtop];
}
function setOpacity(nodestyle, percent) {
	nodestyle.opacity = percent/100;
	nodestyle.MozOpacity = percent/100;
	nodestyle.KhtmlOpacity = percent/100;
	nodestyle.filter = "alpha(opacity=" + percent + ")";
}
var timeout;
function fadeout(id, delay, speed) {
	setOpacity(document.getElementById(id).style, 100);
	timeout = setTimeout("fade('" + id + "', 100, " + speed + ");", delay);
}
function fade(id, pos, speed) {
	var e = document.getElementById(id).style;
	if(pos > 0 && e.display != "none") {
		setOpacity(e, pos);
		timeout = setTimeout("fade('" + id + "'," + (pos-1) + ", " + speed + ")", speed);
	} else {
		e.display = "none";
		setOpacity(e, 100);
	}
}
function movemessagetooffset(offset) {
	// position div#errormessage beside form
	var msgnode = document.getElementById('errormessage');
	msgnode.style.top = '0px';
	msgnode.style.left = '0px';
	msgnode.style.position = 'absolute';
	msgnode.style.display = 'block';
	var cw = msgnode.offsetWidth;
	msgnode.style.top = offset[1] + 'px';
	var vw = viewport().width;
	if( offset[0] + cw > vw - 40 ) {
		msgnode.style.left = (vw - 40 - cw) + 'px';
	} else {
		msgnode.style.left = offset[0] + 'px';
	}
	setOpacity(msgnode.style, 100);
}
function movemessage(form) {
	var submitnode;
	if( form.nodeName.toLowerCase() == 'form' ) {
		var inputs = form.getElementsByTagName('input');
		for( var i = 0; i < inputs.length; i++) {
			if( inputs[i].getAttribute('type').toLowerCase() == 'submit' ) {
				submitnode = inputs[i];
			}
		}
	}
	else {
		submitnode = form;
	}
	// get coordinates of submit button
	var offset = findPos(submitnode);
	movemessagetooffset(offset);
}
function hideerrormessage() {
	var msgnode = document.getElementById('errormessage');
	msgnode.style.display = 'none';
}
function showloadinganimation(form) {
	if( form ) {
		clearTimeout(timeout);
		movemessage(form);
		var msgnode = document.getElementById('errormessage');
		msgnode.innerHTML = '<div style="width:15em; height:36px; display:block; background:url(/images/loading.gif) no-repeat center center;"/>';
		msgnode.setAttribute("onclick", 'this.style.display = "none"; clearTimeout(timeout);');
	}
}
function displayerrormessage(form) {
	if( form ) {
		clearTimeout(timeout);
		movemessage(form)
		// start timer to blur the message away (depend on length)
		var msgnode = document.getElementById('errormessage');
		fadeout("errormessage", 4000+(msgnode.textContent.length*50), 5);
		msgnode.setAttribute("onclick", 'this.style.display = "none"; clearTimeout(timeout);');
	}
}
function messageoverlay(text, zoom) {
	if( text ) {
		clearTimeout(timeout);
		// start timer to blur the message away (depend on length)
		var msgnode = document.getElementById('errormessage');
		if(zoom) {
			msgnode.innerHTML = '<div style="zoom:'+zoom+';">'+text+'</div>';
		} else {
			msgnode.innerHTML = '<div>'+text+'</div>';
		}
		fadeout("errormessage", 4000+(msgnode.textContent.length*50), 5);
		movemessagetooffset([$(document).width()/2 - msgnode.offsetWidth/2, $('body').scrollTop()]);
		msgnode.setAttribute("onclick", 'this.style.display = "none"; clearTimeout(timeout);');
	}
}
function rootnode(n) {
	x = n.firstChild;
	while (x && x.nodeType!=1) {
		x=x.nextSibling;
	}
	x=x.firstChild;
	while (x && x.nodeType!=1) {
		x=x.nextSibling;
	}
	return x;
}
function nextnode(n) {
	do {
		x=x.nextSibling;
	} while (x && x.nodeType!=1)
	return x;
}
function ajax(Url, options, node) {
	var x = new Array();
	for(var key in options) {
		var pair = new Array(key, escape(options[key]));
		x.push(pair.join('='));
	}
	x.push('ajax=1');
	var variables = x.join('&');
	_ajax(Url, variables, node);
}
function _ajax(Url, variables, form) {
	var baseurl = document.getElementById('baseurl').getAttribute('content');
	var AJAX;
	try  {
		AJAX = new XMLHttpRequest(); 
	} catch(e) {
		try {
			AJAX = new ActiveXObject("Msxml2.XMLHTTP");
		} catch(e) {
			try {
				AJAX = new ActiveXObject("Microsoft.XMLHTTP");
			} catch(e) {
				alert("Your browser does not support AJAX.");
				return false;
			}
		}
	}
	if( form ) {
		showloadinganimation(form);
	}
	AJAX.onreadystatechange = function() {
		if(AJAX.readyState == 4) {
			if(AJAX.status == 200) {
				if( AJAX.responseXML ) {
					var node = rootnode(AJAX.responseXML);
					while(node) {
						var tobereplaced = document.getElementById(node.getAttribute('id'));
						var serializer = new XMLSerializer();
						var replacement = '';
						for( var ni = 0; ni < node.childNodes.length; ni++) {
							replacement += serializer.serializeToString(node.childNodes[ni]);
						}
						tobereplaced.innerHTML = replacement;
						// check for scripts in the replacement and run them.
						var scripts = tobereplaced.getElementsByTagName("script");
						for( var i = 0; i < scripts.length; i++ ) {
							eval(scripts[i].text)
						}
						// if we sent an ajax form, we'd like to see a message
						if( form && node.getAttribute('id').toLowerCase() == 'errormessage' ) {
							displayerrormessage(form);
						}
						node = nextnode(node)
					}
				} else {
					alert("Error: Something's wrong on the server's side. Received no well-formed XML.\n\nThis came back:\n" + AJAX.responseText);
				}
			} else {
				alert("Error: "+ AJAX.statusText +" "+ AJAX.status);
			}
		}  
	}
	var _url = baseurl + Url;
	if(variables.length > 0) _url += "?" + variables;
	//DEBUG: alert(_url);
	AJAX.open("GET", _url, true);
	AJAX.send(null);
	return false;
}
function ajaxsubmit(form) {
	var _get = serialize_form(form) + '&ajax=1';
	var _url = form.getAttribute('action');
	_ajax(_url, _get, form);
	form.reset();
	return false;
}
function askajaxsubmit(form, message) {
	if(confirm(message)) {
		return ajaxsubmit(form);
	} else {
		return false;
	}
}
function askajax(url, variables, form, message) {
	if(confirm(message)) {
		return ajax(url, variables, form);
	} else {
		return false;
	}
}

