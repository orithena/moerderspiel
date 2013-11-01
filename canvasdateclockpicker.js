var canvasclock = function(config) {

var canvas = $(config.clockcanvasid)[0];
var $canvas = $(canvas);
var c = canvas.getContext("2d");
var w = canvas.width;
var h = canvas.height;
var lw = w / 32;
var hw = w / 16;
var fs = w / 16;
var mx = w / 2;
var my = h / 2;
var r = mx - lw;
var or = r;
var ir = or * (2.0 / 3);
var tfs = w / 24;
var tfy = 1.5;
var tfx = 3.2;
var style = "circles";
var col = {
    dial: "rgba(0,0,128,0.2)",
    dialh: "rgba(192,64,64,0.7)",
    hand: "rgba(0,0,92,0.7)",
    handh: "rgba(192,0,0,0.7)",
    dialtext: "rgba(255,255,255,1.0)",
    timetext: "rgba(255,255,255,1.0)",
    timeborder: "rgba(64,64,192,0.8)"
}
var oh = 0,
    om = 0,
    od = 0;
var mouseX = 0,
    mouseY = 0;
var wheeltimer;
var drawdata = {
        c: c,
        h: 1,
        m: 1,
        d: 1,
        hl: 1
    };

var drawupdate = true;
var mousedown = false,
    updateminutes = false;

var p2c = function(rad, len) { 
    var normrad = (((-3.0 / 2.0) * Math.PI) - rad) % (2 * Math.PI);
    return {
        x: mx + (Math.cos(normrad) * len),
        y: my - (Math.sin(normrad) * len)
    };
}

function c2r(x, y) { //cartesian to polar radian
    return (Math.atan2(-(y - my), -(x - mx)) + ((3.0 / 2.0) * Math.PI)) % (2 * Math.PI);
}

function c2l(x, y) { //cartesian to polar length
    return (Math.sqrt(Math.pow(x - mx, 2) + Math.pow(y - my, 2)));
}

function h2r(h) { // hour to rad
    return (h * (2.0 / 12.0) * Math.PI);
}

function m2r(m) { // min to rad
    return (m * (2.0 / 60.0) * Math.PI);
}

function hm2r(h, m) { // hour+minute to rad
    return Math.PI * (
    (h * (2.0 / 12.0)) + (m * (2.0 / (60.0 * 12.0))));
}

function r2h(r) { // radian to hour
    return Math.floor(((r + (2 * Math.PI)) % (2 * Math.PI)) / ((2.0 / 12.0) * Math.PI));
}

function r2hm(r) { // radian to a hours minute
    return Math.floor(((r * 12) % (2 * Math.PI)) / ((2.0 / 60.0) * Math.PI));
}

function r2m(r) { // radian to minute
    return Math.floor(
    (r % (2 * Math.PI)) / ((2.0 / 60.0) * Math.PI));
}

function raddiff(r1, r2) {
    var rd = (Math.abs(r1 - r2)) % (2 * Math.PI);
    var ret = (rd > Math.PI ? (2 * Math.PI) - rd : rd);
    return ret;
}

function actuallyDrawClock(c, hour, minute, day, hl) {
//    console.log("drawing");
    c.clearRect(0, 0, w, h);
    c.textBaseline = "middle";
    c.textAlign = "center";
    c.lineWidth = lw;
    c.lineCap = "round";
    c.lineJoin = "round";
    // outer ring
    c.strokeStyle = (hl == 2 ? col.dialh : col.dial);
    c.fillStyle = col.dial;
    c.beginPath();
    c.arc(mx, my, or, 0, 2 * Math.PI);
    c.stroke();
    c.fill();
    // inner ring
    c.strokeStyle = (hl == 1 ? col.dialh : col.dial);
    c.beginPath();
    c.arc(mx, my, ir, 0, 2 * Math.PI);
    c.stroke();
    c.fill();
    if (style == "circles") {
        // dial points
        c.fillStyle = col.dialtext;
        for (var i = 1; i <= 12; i++) {
            p = p2c(h2r(i), ir + ((or - ir) / 2));
            c.beginPath();
            c.arc(p.x, p.y, lw/(i%3==0?1:2), 0, 2*Math.PI);
            c.fill();
        }
        // minutes
        c.lineWidth = lw;
        c.fillStyle = (hl == 2 ? col.handh : col.hand);
        c.strokeStyle = (hl == 2 ? col.dialh : col.dial);
        c.beginPath();
        var p = p2c(m2r(minute), ((or - ir) / 2) + ir);
        c.arc(p.x, p.y, (or - ir) / 2, 0, 2 * Math.PI);
        c.fill();
        c.stroke();
        // dial numerals
        c.fillStyle = col.dialtext;
        c.font = fs + 'px sans-serif';
        c.fillText((minute < 10 ? '0' : '') + minute, p.x, p.y);
        // hours
        c.fillStyle = (hl == 1 ? col.handh : col.hand);
        c.strokeStyle = (hl == 1 ? col.dialh : col.dial);
        c.beginPath();
        p = p2c(hm2r(hour, minute), ir - ((or - ir) / 2));
        c.arc(p.x, p.y, (or - ir) / 2, 0, 2 * Math.PI);
        c.fill();
        c.stroke();
        // dial numerals
        c.fillStyle = col.dialtext;
        c.font = "bold " + fs + "px sans-serif";
        c.fillText(
            hour, 
            p.x, 
            p.y
        );
    } else {
        // minute hand
        c.lineWidth = hw;
        c.strokeStyle = (hl == 2 ? col.handh : col.hand);
        c.beginPath();
        c.moveTo(mx, my);
        p = p2c(m2r(minute), or);
        c.lineTo(p.x, p.y);
        c.stroke();
        // hour hand
        c.strokeStyle = (hl == 1 ? col.handh : col.hand);
        c.beginPath();
        c.moveTo(mx, my);
        p = p2c(hm2r(hour, minute), ir + (lw / 2));
        c.lineTo(p.x, p.y);
        c.stroke();
        // center hand dot
        c.strokeStyle = col.hand;
        c.fillStyle = col.hand;
        c.beginPath();
        c.arc(mx, my, lw, 0, 2 * Math.PI);
        c.fill();
        // dial numerals
        c.fillStyle = col.dialtext;
        c.font = fs + "px sans-serif";
        for (var i = 1; i <= 12; i++) {
            p = p2c(h2r(i), ir + ((or - ir) / 2));
            c.fillText(i, p.x, p.y);
        }
    }
    // center display
    c.lineWidth = lw;
    c.fillStyle = col.timeborder;
    c.strokeStyle = col.timeborder;
    c.fillRect(mx - (tfs * tfx), my - (tfs * tfy), (tfs * 2 * tfx), tfs * 2 * tfy);
    c.strokeRect(mx - (tfs * tfx), my - (tfs * tfy), (tfs * 2 * tfx), tfs * 2 * tfy);
    c.fillStyle = col.timetext;
    c.font = (2 * tfs) + "px sans-serif";
    c.fillText(hour + ":" + (minute < 10 ? '0' : '') + minute, mx, my);
}

function drawClock(c, hour, minute, day, hl) {
    om = minute;
    oh = hour;
    od = day;
    drawupdate = true;
    config.date.setHours(hour);
    config.date.setMinutes(minute);
    $(config.inputfield).val(config.date.toString('dd.MM.yyyy HH:mm'));
    drawdata = {
        c: c,
        h: hour,
        m: minute,
        d: day,
        hl: hl
    };
}

function render() {
    var du = drawupdate;
    drawupdate = false;
    if(du) { 
        actuallyDrawClock(
            c,
            drawdata.h,
            drawdata.m,
            drawdata.d, 
            drawdata.hl
        );
    }
}
window.requestAnimFrame = (function () {
    return window.requestAnimationFrame || window.webkitRequestAnimationFrame || window.mozRequestAnimationFrame || function (callback) {
        window.setTimeout(callback, 1000 / 60);
    };
})();
(function animloop() {
    requestAnimFrame(animloop);
    render();
})();

function timecheckminute(hour, minute, day) {
    minute = (minute + 60) % 60;
    if (minute < om - 30) hour++;
    if (minute > om + 30) hour--;
    if (hour < 0) day--;
    if (hour >= 24) day++;
    hour = ((hour + 48) % 24);
    return {
        u: minute != om,
        h: hour,
        m: minute,
        d: day
    };
}

function timecheckhour(hour, minute, day) {
    hour = (hour + 24) % 24;
    d = (Math.abs(oh - hour))
    if (d > 6 && d < 18) hour += 12;
    hour = ((hour + 48) % 24);
    if (hour < oh - 6) day++;
    if (hour > oh + 6) day--;
    return {
        u: hour != oh,
        h: hour,
        m: minute,
        d: day
    };
}

function checkupdateminutes() {
    updateminutes =
        (   (   c2l(mouseX, mouseY) 
            >   ir 
            )
        ||  (   (   style == "hands" )
            &&  (   raddiff(
                        m2r(om), 
                        c2r(mouseX, mouseY)
                    )
                <   (   Math.PI 
                    *   (1 / 16) 
                    *   (   r 
                        /   (   c2l(mouseX, mouseY)
                            +   (0.25 * r)
        )   )   )   )   )   );
}

function update(force) {
    if (mousedown) {
        if (updateminutes) {
            rad = c2r(mouseX, mouseY);
            t = timecheckminute(oh, r2m(rad), od);
            if (t.u || force) drawClock(c, t.h, t.m, t.d, 2);
        } else {
            rad = c2r(mouseX, mouseY);
            //t = timecheckhour(r2h(rad),r2hm(rad),od)
            t = timecheckhour(r2h(rad), om, od)
            if (t.u || force) drawClock(c, t.h, t.m, t.d, 1);
        }
    } else drawClock(c, oh, om, od, 0);
}
$(canvas).mousemove(function (e) {
    if (mousedown) {
        mouseX = e.offsetX;
        mouseY = e.offsetY;
        update();
    
    e.stopPropagation();
    e.preventDefault();
    return false;
    }
});
$(canvas).mousedown(function (e) {
    e.stopPropagation();
    e.preventDefault();
    mouseX = e.offsetX;
    mouseY = e.offsetY;
    checkupdateminutes();
    mousedown = true;
    update(true);
    return false;
});
$(canvas).mouseup(function (e) {
    e.stopPropagation();
    e.preventDefault();
    mousedown = false;
    update();
    return false;
});
$canvas.bind('touchend', function (e) {
    e.stopPropagation();
    e.preventDefault();
    mousedown = false;
    update();
    return false;
});
$canvas.bind('touchstart', function (e) {
    e.stopPropagation();
    e.preventDefault();
    //mouseX = e.originalEvent.touches[0].pageX;
    //mouseY = e.originalEvent.touches[0].pageY;
    mouseX = e.originalEvent.touches[0].pageX - $canvas.offset().left;
    mouseY = e.originalEvent.touches[0].pageY - $canvas.offset().top;
    checkupdateminutes();
    mousedown = true;
    update();
    return false;
});
$canvas.bind('touchmove', function (e) {
    e.stopPropagation();
    e.preventDefault();
    //mouseX = e.originalEvent.touches[0].pageX;
    //mouseY = e.originalEvent.touches[0].pageY;
    mouseX = e.originalEvent.touches[0].pageX - $canvas.offset().left;
    mouseY = e.originalEvent.touches[0].pageY - $canvas.offset().top;
    update();
    return false;
});
$canvas.bind("dragenter dragstart dragend dragleave dragover drag drop", function (e) {
    e.stopPropagation();
    e.preventDefault();
    return false;
});
$(canvas).bind('mousewheel DOMMouseScroll', function (e) {
    e.stopPropagation();
    e.preventDefault();
    if (typeof (wheeltimeout) != "undefined") clearTimeout(wheeltimeout);
    mouseX = e.offsetX;
    mouseY = e.offsetY;
    delta = e.originalEvent.wheelDelta / 120;
    updateminutes = 
        (   (   c2l(mouseX, mouseY) 
            >   (ir + lw) 
            )
        ||  (   (   mouseX 
                >   mx
                )
            &&  (   mouseX 
                <   (   mx 
                    +   (tfs*tfx) 
                    +   (lw/2)
                    )
                )
            &&  (   mouseY 
                >   (   my 
                    -   (   (   tfs
                            *   tfy
                            +   lw
                            )
                        /   2
                )   )   )
            && (    mouseY 
               <    (   my 
                    +   (   (   tfs
                            *   tfy
                            +   lw
                            )
                        /   2
        )   )   )   )   );
    if (updateminutes) {
        t = timecheckminute(oh, om + delta, od);
        drawClock(c, t.h, t.m, t.d, 2);
    } else {
        t = timecheckhour(oh + delta, om, od)
        drawClock(c, t.h, t.m, t.d, 1);
    }
    wheeltimeout = setTimeout(function () {
        drawClock(c, oh, om, od, 0);
    }, 300);
    return false;
});
drawClock(c, config.date.getHours(), config.date.getMinutes(), config.date.getDay(), 0);

};

var canvasdate = function(config) {
function mod(x, m) {
    r = x % m;
    return r < 0 ? r + m : r;
}
var canvas = $(config.datecanvasid)[0];
var c = canvas.getContext("2d");
var w = canvas.width;
var h = canvas.height;
var dim = Math.max(w,h);
var sdim = Math.min(w,h);
var lw = dim / 96;
var ds = 0.6*Math.min(w,h);
var sf = 0.4;
var cur = config.date.clone().clearTime();
//var notbefore = Date.today().add({days: -5});
//var notafter = Date.today().add({days: 3});
var notbefore = config.notbefore;
var notafter = config.notafter;
var startd = cur.clone();
var curdelta = 0;
var plusminus = Math.round(1.0*dim/ds);
var steps = 8;
var curstep = 0;
var scrolling = false;
var scrolldelta = 0;
var drawupdate = false;

var datearray = new Array();
var shortarray = new Array();

function resetitems() {
    datearray = new Array();
}

function additem(d, index, offset) {
    if( !d.isBefore(notbefore) && !d.isAfter(notafter) ) {
    var start = 0;
    var stop = plusminus * 2 + 1;
    var t = 1.0*(plusminus+index+offset+0.5) / stop;
    datearray.push({
        index: index,
        date: d,
        maj: Math.cos(t * Math.PI),
        min: 1 - (2* Math.sin(t * Math.PI)),
        size: (1-sf*(Math.abs(index+offset)/plusminus))
    });
    }
}

function drawitem(c, d, hi) {
    var landscape = w > h;
    var mx = w/2;
    var my = h/2;
    var ids = ds * d.size;
    var ds2 = ids/2;
    var start = 0;
    var stop = dim-(ids)-lw;
    var t = start+(d.maj*((stop - start)/2));
    var j = (d.min*((sdim-ids)/2));
    var datestr = d.date.toString(" d ").trim();
    var datestr2 = d.date.toString("ddd");
    var datestr3 = d.date.toString("MMM yyyy");
    var x = landscape ? lw+mx-t : lw+mx+j;
    var y = landscape ? lw+my+j : lw+my+t;
    d.x1 = x-ds2;
    d.y1 = y-ds2;
    d.x2 = x+ds2;
    d.y2 = y+ds2;
    c.fillStyle = hi ? "rgba(255,128,128,1.0)": d.date.is().sun() ? "rgba(64,64,192,0.7)" : d.date.is().sat() ? "rgba(128,128,255,0.8)" : "rgba(192,192,255,0.8)";
    c.strokeStyle = hi ? "rgba(255,0,0,0.8)" : "rgba(128,128,255,0.5)";
    c.beginPath();
    c.rect(d.x1,d.y1,ids,ids);
    c.fill();
    c.stroke();
    c.fillStyle = "rgba(255,255,255,0.9)";
    c.font = "bold "+ ids*0.8 +"px sans-serif";
    c.fillText(datestr, x, y);
    c.fillStyle = "rgba(0,0,128,1.0)";
    c.font = ids*0.2 +"px sans-serif";
    c.fillText(datestr2, x, y-(ids/3));
    c.fillText(datestr3, x, y+(ids/3));
}

function drawshortcut(c, e) {
    
}

function updateshortcuts() {
    shortarray = [
        //{    o: Date.getDaysBetween(cur, 
    ];
}

var future = new Date().add({months: 5, days: 4, hours: 3, minutes: 2, seconds: 1}); 
var now = new Date();
var span = new TimeSpan(future - now);
//console.log("Days:", span.getDays());

function draw(c) {
    c.textBaseline = "middle";
    c.textAlign = "center";
    c.lineWidth = lw;
    c.lineCap = "round";
    c.lineJoin = "round";
    c.clearRect(0, 0, w, h);
    $(datearray).each(function(i,e) {
        drawitem(c, e, e.date.equals(cur));
    });
    $(shortarray).each(function(i,e) {
        drawshortcuts(c, e);
    });
}

function render() {
    if (curstep >= 0) {
            var a = steps - curstep;
            var delta = (curdelta*(a/steps));
                var dd = startd.clone();
                genlist(dd.addDays(Math.floor(delta)), mod(delta, 1.0));
                draw(c);
            if( curstep == 0 ) scrolling=false;
            curstep--;
    }
}
window.requestAnimFrame = (function () {
    return window.requestAnimationFrame || window.webkitRequestAnimationFrame || window.mozRequestAnimationFrame || function (callback) {
        window.setTimeout(callback, 1000 / 60);
    };
})();
(function animloop() {
    requestAnimFrame(animloop);
    render();
})();

function genlist(d, offset) {
    resetitems();
    for (a = -plusminus; a < 0; a++) {
        var dt = d.clone();
        additem(dt.addDays(a), a, -offset);
    }
    // adding order matters
    // it equals drawing order
    for (a = plusminus; a >= 0; a--) {
        var dt = d.clone();
        additem(dt.addDays(a), a, -offset);
    }
}

function setCurrent(delta) {
    if( !scrolling ) {
        delta += scrolldelta;
        scrolldelta = 0;
        startd = cur.clone();
        cur = cur.addDays(delta);
        config.date.set({ day: cur.getDate(), month: cur.getMonth(), years: cur.getYear()});
	    $(config.inputfield).val(config.date.toString('dd.MM.yyyy HH:mm'));

        curdelta = delta;
        curstep = steps;
/*        for( var a = 0; a <= steps; a++) {
            setTimeout(function(a, delta, startd) {
                var dd = startd.clone();
                genlist(dd.addDays(Math.floor(delta)), mod(delta, 1.0));
                draw(c);
                if( a == steps ) scrolling=false;
            }, a*(1000/60), a, (delta*(a/steps)), startd);
        } */
    } else {
        scrolldelta += delta;
    }
}

genlist(cur,0);
draw(c);

$(canvas).click(function(e) {
    var delta = 0;
    $(datearray.reverse()).each(function(i,d) {
        if(
            e.offsetX >= d.x1
            && e.offsetX <= d.x2
            && e.offsetY >= d.y1
            && e.offsetY <= d.y2
             ) {
            delta = d.index;
            return false;
        }
    });
    if( delta != 0 ) {
        setCurrent(delta);
    }
    e.preventDefault();
    return false;
});

$(canvas).bind('mousewheel DOMMouseScroll', function (e) {
    var delta = e.originalEvent.wheelDelta / 120;
    if( delta != 0 ) {
        setCurrent(delta);
    }
    e.preventDefault();
    return false;
});
};

var initcanvasses = function(node) {
	var cw = document.documentElement.clientWidth;
	var ch = document.documentElement.clientHeight;
	var dateh = cw > ch ? ch*0.7 : ch*0.2;
	var datew = cw > ch ? cw*0.2 : cw*0.85;
	var clockdim = cw > ch ? ch*0.7 : ch*0.6;
	var overlay = $('<div id="overlay"><div><canvas width="'+datew+'" height="'+dateh+'" id="datecanvas"></canvas><canvas width="'+clockdim+'" height="'+clockdim+'" id="clockcanvas"></canvas><button id="closeoverlay">Fertig!</button></div></div>');
	overlay.appendTo(document.body)
	overlay.bind("touchmove dragenter dragstart dragend dragleave dragover drag drop", function (e) {
		e.preventDefault();
		return false;
	});
	$('#closeoverlay').click(function(e){
		overlay.remove();
		e.stopPropagation();
		e.preventDefault();
		return false;
	});
}

var canvasdateclockpicker = function(config) {
		config.date = Date.parse($(config.inputfield).val());
		initcanvasses();
		canvasclock(config);
		canvasdate(config);
}


