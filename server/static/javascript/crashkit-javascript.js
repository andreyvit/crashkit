// Include this file to use CrashKit for reporting errors in your application.
// Visit http://crashkitapp.appspot.com/ for details.
// 
// Copyright (c) 2009 Andrey Tarantsov, YourSway LLC
// 
// Permission to use, copy, modify, and/or distribute this software for any
// purpose with or without fee is hereby granted, provided that the above
// copyright notice and this permission notice appear in all copies.
// 
// THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
// WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
// MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
// ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
// WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
// ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
// OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
//
// Huge thanks goes to Eric Wendelin, Luke Smith and Loic Dachary
// for inpiring us and giving us a head-start in JS stack trace collection.
// See: http://eriwen.com/javascript/js-stack-trace/

CrashKit = {}; // intentionally global

CrashKit.URL = null;
CrashKit.Host = "crashkitapp.appspot.com";
CrashKit.Host = "localhost:5005";
CrashKit.Action = "";
CrashKit.isWebKit = (navigator.userAgent.indexOf("AppleWebKit") >= 0);

CrashKit.report = function(ex) {
    var st = CrashKit.getStackTrace(ex);
    CrashKit.handleError(st);
}

// Provide the XMLHttpRequest class for IE 5.x-6.x:
if (typeof XMLHttpRequest == "undefined") {
    XMLHttpRequest = function() {
        try { return new ActiveXObject("Msxml2.XMLHTTP.6.0") } catch(e) {}
        try { return new ActiveXObject("Msxml2.XMLHTTP.3.0") } catch(e) {}
        try { return new ActiveXObject("Msxml2.XMLHTTP") } catch(e) {}
        try { return new ActiveXObject("Microsoft.XMLHTTP") } catch(e) {}
        throw new Error( "This browser does not support XMLHttpRequest." )
    };
}

CrashKit.computeWebServiceUrl = function() {
    var els = document.getElementsByTagName("SCRIPT");
    for (var i = 0; i < els.length; i++) {
        var el = els[i];
        var src = el.src;
        if (src && src.indexOf("crashkit-javascript.js?") >= 0) {
            var x = src.substring(src.indexOf("?") + 1).split("/");
            var crkHost = (("https:" == document.location.protocol) ? "https://" : "http://");
            CrashKit.URL = crkHost + CrashKit.Host + "/" + x[0] + "/products/" + x[1] + "/post-report/0/0";
        }
    }
}

if (!RegExp.escape)
    RegExp.escape = function(text) {
        if (!arguments.callee.sRE) {
            var specials = ['/', '.', '*', '+', '?', '|', '(', ')', '[', ']', '{', '}', '\\'];
            arguments.callee.sRE = new RegExp('(\\' + specials.join('|\\') + ')', 'g');
        }
        return text.replace(arguments.callee.sRE, '\\$1');
    }

var JSON = function() {
	var	c = {"\b":"b","\t":"t","\n":"n","\f":"f","\r":"r",'"':'"',"\\":"\\","/":"/"},
		d = function(n){return n<10?"0".concat(n):n},
		e = function(c,f,e){e=eval;delete eval;if(typeof eval==="undefined")eval=e;f=eval(""+c);eval=e;return f},
		i = function(e,p,l){return 1*e.substr(p,l)},
		p = ["","000","00","0",""],
		rc = null,
		rd = /^[0-9]{4}\-[0-9]{2}\-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}$/,
		rt = /^([0-9]+|[0-9]+[,\.][0-9]{1,3})$/,
		rs = /(\x5c|\x2F|\x22|[\x0c-\x0d]|[\x08-\x0a])/g,
		s = function(i,d){return "\\".concat(c[d])},
		ru = /([\x00-\x07]|\x0b|[\x0e-\x1f])/g,
		u = function(i,d){
			var	n=d.charCodeAt(0).toString(16);
			return "\\u".concat(p[n.length],n)
		},
		v = function(k,v){return $[typeof result](result)!==Function&&(v.hasOwnProperty?v.hasOwnProperty(k):v.constructor.prototype[k]!==v[k])},
    	$ = {
    		"boolean":function(){return Boolean},
    		"function":function(){return Function},
    		"number":function(){return Number},
    		"object":function(o){return o instanceof o.constructor?o.constructor:null},
    		"string":function(){return String},
    		"undefined":function(){return null}
    	},
		$$ = function(m){
			function $(c,t){t=c[m];delete c[m];try{e(c)}catch(z){c[m]=t;return 1}};
			return $(Array)&&$(Object)
		};
	try { rc = new RegExp('^("(\\\\.|[^"\\\\\\n\\r])*?"|[,:{}\\[\\]0-9.\\-+Eaeflnr-u \\n\\r\\t])+?$') }
	catch(z) { rc=/^(true|false|null|\[.*\]|\{.*\}|".*"|\d+|\d+\.\d+)$/ };
    
    return {
        'encode': function(self) {
            if (self === null) return "null";
            if (self === undefined) return "null";
            var result, type = typeof self;
            var tmp = $[type](self);
            if (tmp == null) return null;
            switch (tmp) {
                case Array:
                    result = [];
                    for(var	i = 0, j = 0, k = self.length; j < k; j++) {
                        if(self[j] !== undefined && (tmp = JSON.encode(self[j])))
                            result[i++] = tmp;
                    };
                    return "[".concat(result.join(","), "]");
                case Boolean:
                    return String(self);
                case Date:
                    return '"'.concat(self.getFullYear(), '-', d(self.getMonth() + 1), '-', d(self.getDate()), '"');
                case Function:
                    return "";
                case Number:
                    return isFinite(self) ? String(self) : "null";
                case String:
                    return '"'.concat(self.replace(rs, s).replace(ru, u), '"');
                default:
                    var	i = 0, key;
                    result = [];
                    for (key in self) {
                        if (self[key] !== undefined && (tmp = JSON.encode(self[key])))
                            result[i++] = '"'.concat(key.replace(rs, s).replace(ru, u), '":', tmp);
                    };
                    return "{".concat(result.join(","), "}");
            }
        }
    };
}();

CrashKit.sendError = function(text){
    var request =  new XMLHttpRequest();
    request.open("POST", CrashKit.URL, false);
    request.setRequestHeader("Content-Type", "text/plain;charset=UTF-8");
    request.send(text);
    if (!request.getResponseHeader("Date") || request.status != 200) { //send failed
        // fun, but dangerous (there might be many errors/sec)
        // alert("Please tell this error to the maintainer orally:" + text);
    }
}  

CrashKit.encodeError = function (stack) {
    return JSON.encode([
        {
            "userActionOrScreenNameOrBackgroundProcess": CrashKit.Action,
            "severity": "major",
            "exception": stack,
            "data": {
                "cookie": document.cookie,
                "url": window.location.href
            },
            "env": {
                "user_agent": navigator.userAgent,
                "opera": !!window.opera,
                "vendor": navigator.vendor,
                "platform": navigator.platform
            },
            "language": "javascript"
        }
    ]);
}

CrashKit.isFirefoxStackTraceSupported = function() {
    try { (0)() } catch (e) {
        return !!e.stack;
    }
};

CrashKit.sourceCache = {};

CrashKit.loadSource = function(url) {
    try {
        var request =  new XMLHttpRequest();
        request.open("GET", url, false);
        request.send("");
        return request.responseText;
    } catch(e) {
        // alert(e.message);
        return "";
    }
};

CrashKit.getSource = function(url) {
    if (!(url in CrashKit.sourceCache))
        CrashKit.sourceCache[url] = CrashKit.loadSource(url).split("\n");
    return CrashKit.sourceCache[url];
};

CrashKit.guessFunctionName = function(url, lineNo) {      
    var source = CrashKit.getSource(url);
    return CrashKit.guessFunctionNameFromLines(lineNo, source);
};

CrashKit.guessFunctionNameFromLines = function(lineNo, source) {
	var reFunctionArgNames = /function ([^(]*)\(([^)]*)\)/;
	var reGuessFunction = /['"]?([0-9A-Za-z$_]+)['"]?\s*[:=]\s*(function|eval|new Function)/;
	// Walk backwards from the first line in the function until we find the line which
	// matches the pattern above, which is the function definition
	var line = "";
	var maxLines = 10;
	for (var i = 0; i < maxLines; ++i) {
        line = source[lineNo-i] + line;
        if (line !== undefined)
        {
            var m = reGuessFunction.exec(line);
            if (m) {
                return m[1];
            } else {
                m = reFunctionArgNames.exec(line);
            } if (m && m[1]) {
                return m[1];
            }
        }
    }
    return "?";
};

CrashKit.gatherContext = function(url, lineNo) {
    var source = CrashKit.getSource(url);
    var context = [], anyDefined = false;
    lineNo = lineNo - 1; // convert to int and to 0-based indexes
    for(var l = lineNo - 2; l <= lineNo + 2; l++) {
        var item = source[l];
        if (typeof item != "undefined")
            anyDefined = true;
        context.push(item);
    }
    return (anyDefined ? context : null);
}

CrashKit.findSourceInUrls = function(re, urls, singleLineExpected) {
    for (var i in urls) {
        var source = CrashKit.getSource(urls[i]);
        if (source) {
            source = source.join("\n");
            var m = re.exec(source);
            if (m) {
                var result = {'url': urls[i], 'line': null};
                result.startLine = source.substring(0, m.index).split("\n").length;
                if (singleLineExpected)
                    result.line = result.startLine;
                console.info("Found function in " + urls[i]);
                return result;
            }
        }
    }
    return null;
}

CrashKit.escapeHtmlBodyForUrl = function(body) {
    return RegExp.escape(body).replace('<', '(?:<|&lt;)').replace('>', '(?:>|&gt;)')
            .replace('&', '(?:&|&amp;)').replace('"', '(?:"|&quot;)').replace(/\s+/g, '\\s+');
}

CrashKit.findSourceByFunctionBody = function(func) {
    var htmlUrls = [window.location.href];
    var urls = [window.location.href];
    var scripts = document.getElementsByTagName("script");
    for (var i = 0; i < scripts.length; i++) {
        var script = scripts[i];
        if (script.src)
            urls.push(script.src);
    }
    var code = ""+func;
    
    var codeRE = /^function(?:\s+([\w$]+))?\s*\(([\w\s,]+)\)\s*{\s*(\S[\s\S]*\S)\s*}\s*$/;
    var eventRE = /^function on([\w$]+)\s*\(event\)\s*{\s*(\S[\s\S]*\S)\s*}\s*$/;
    var re;
    var isOneLiner = false;
    if (!codeRE.test(code))
        re = new RegExp(RegExp.escape(code));
    else {
        var name = RegExp.$1, args = RegExp.$2, body = RegExp.$3;
        args = args.split(",").join("\s*,\s*");
        name = (name ? "\\s+" + name : '');
        isOneLiner = (body.split("\n").length == 1);
        body = RegExp.escape(body).replace(/\s+/g, '\\s+');
        re = new RegExp("function" + name + "\s*\\(" + args + "\\)\\s*{\\s*" + body + "\\s*}");
    }
    
    var result = CrashKit.findSourceInUrls(re, urls, isOneLiner);
    if (result) return result;
    
    if (eventRE.test(code)) {
        var event = RegExp.$1, body = RegExp.$2;
        body = CrashKit.escapeHtmlBodyForUrl(body);
                
        re = new RegExp("on" + event + '=[\\\'"]\\s*' + body + '\\s*[\\\'"]', 'i');
        result = CrashKit.findSourceInUrls(re, urls, true);
        if (result) return result;
                
        re = new RegExp(body);
        result = CrashKit.findSourceInUrls(re, urls, true);
        if (result) return result;
    }
    
    console.info("Not found:\n" + code);
    return null;
}

if (CrashKit.isFirefoxStackTraceSupported()) {
    CrashKit.getStackTrace = function(e) {
        // In Firefox, ex.stack contains a stack trace as a string. Example value is:
        
        // qqq("hi","hi","hi")@file:///Users/andreyvit/Projects/crashkit/javascript-client/sample.js:7
        // ("hi","hi","hi")@file:///Users/andreyvit/Projects/crashkit/javascript-client/sample.js:3
        // ppp("hi","hi","hi")@file:///Users/andreyvit/Projects/crashkit/javascript-client/sample.html#:17
        // ("hi","hi","hi")@file:///Users/andreyvit/Projects/crashkit/javascript-client/sample.html#:12
        // xxx("hi")@file:///Users/andreyvit/Projects/crashkit/javascript-client/sample.html#:8
        // onclick([object MouseEvent])@file:///Users/andreyvit/Projects/crashkit/javascript-client/sample.html#:1        
        
        var lineRE = /^\s*(?:(\w*)\(.*\))?@((?:file|http).*):(\d+)\s*$/i;
        var lines = e.stack.split("\n");
        var stack = [];
        for(var i in lines) {
            var line = lines[i];
            if (lineRE.test(line)) {
                var element = {'url': RegExp.$2, 'func': RegExp.$1, 'line': RegExp.$3};
                if (element.func == "" && element.line != 0)
                    element.func = CrashKit.guessFunctionName(element.url, element.line);
                if (element.line != 0)
                    element.context = CrashKit.gatherContext(element.url, element.line);
                stack.push(element);
            }
        }
        return {'mode': 'firefox', 'name': e.name, 'message': e.message, 'stack': stack};
    };
} else if (CrashKit.isWebKit) {
    CrashKit.getStackTrace = function(e) {
        // WebKit does not provide a stack trace, so we have to walk the chain of callers.
        // Line numbers are impossible to compute, but we can get the line number for
        // the topmost function from the exception object itself, and we can also
        // determine correct line numbers for one-line functions.
        try {
            var fnRE  = /function\s*([\w\-$]+)?\s*\(/i,
                j=0, fn,args,i;
            var initial = {'url': e.sourceURL, 'line': e.line};
            initial.func = CrashKit.guessFunctionName(initial.url, initial.line);
            initial.context = CrashKit.gatherContext(initial.url, initial.line);
            var stack = [initial];

            var funcs = {};
            for(var curr = arguments.callee.caller; curr; curr = curr.caller) {
                if (funcs[curr]) {
                    console.info("Recursion detected on " + curr.name);
                    break;
                }
                funcs[curr] = true;
                
                fn = curr.name;
                if (typeof fn == "undefined" || fn == '')
                    fn = fnRE.test(curr.toString()) ? RegExp.$1 || '' : '';
                
                var source = CrashKit.findSourceByFunctionBody(curr);
                var url = null, line = null;
                if (source != null) {
                    url  = source.url;
                    line = source.line;
                    if (fn == '')
                        fn = CrashKit.guessFunctionName(url, source.startLine);
                }

                stack.push({'url': url, 'func': fn, 'line': line});
            }

            return {'mode': 'webkit', 'name': e.name, 'message': e.message, 'stack': stack};
        } catch(inner) {
            console.info(inner.message);
        }
    };
} else if (window.opera) {
    CrashKit.getStackTrace = function(e) {
        // Opera includes a stack trace into the exception message. A sample message is:
        //
        // Statement on line 3: Undefined variable: undefinedFunc
        // Backtrace:
        //   Line 3 of linked script file://localhost/Users/andreyvit/Projects/crashkit/javascript-client/sample.js: In function zzz
        //         undefinedFunc(a);
        //   Line 7 of inline#1 script in file://localhost/Users/andreyvit/Projects/crashkit/javascript-client/sample.html: In function yyy
        //           zzz(x, y, z);
        //   Line 3 of inline#1 script in file://localhost/Users/andreyvit/Projects/crashkit/javascript-client/sample.html: In function xxx
        //           yyy(a, a, a);
        //   Line 1 of function script 
        //     try { xxx('hi'); return false; } catch(e) { CrashKit.report(e); }
        //   ...
        
        // Note: for <script> blocks inside HTML files the line numbers are relative
        // to the start of the script block, not to the start of the whole file.
        var lines = e.message.split("\n"),
            lineRE1 = /^\s*Line (\d+) of linked script ((?:file|http)\S+)(?:: in function (\S+))?\s*$/i,
            lineRE2 = /^\s*Line (\d+) of inline#(\d+) script in ((?:file|http)\S+)(?:: in function (\S+))?\s*$/i,
            lineRE3 = /^\s*Line (\d+) of function script\s*$/i;

        var stack = [];
        var scripts = document.getElementsByTagName('script');
        var inlineScriptBlocks = [];
        for (var i in scripts)
            if (!scripts[i].src)
                inlineScriptBlocks.push(scripts[i]);
        for (var i=2, len=lines.length; i < len; i += 2) {
            var item = null;
            if (lineRE1.test(lines[i]))
                item = {'url': RegExp.$2, 'func': RegExp.$3, 'line': RegExp.$1};
            else if (lineRE2.test(lines[i])) {
                item = {'url': RegExp.$3, 'func': RegExp.$4};
                var relativeLine = (RegExp.$1 - 0);
                var script = inlineScriptBlocks[RegExp.$2 - 1];
                if (script) {
                    var source = CrashKit.getSource(item.url);
                    if (source) {
                        source = source.join("\n");
                        var pos = source.indexOf(script.innerText);
                        if (pos >= 0) {
                            item.line = relativeLine + source.substring(0, pos).split("\n").length;
                        }
                    }
                }
            } else if (lineRE3.test(lines[i])) {
                var url = window.location.href.replace(/#.*$/, ''), line = RegExp.$1;
                var re = new RegExp(CrashKit.escapeHtmlBodyForUrl(lines[i+1]));
                var source = CrashKit.findSourceInUrls(re, [url], true);
                if (source)
                    item = {'url': url, 'line': source.line, 'func': ''};
            }
            if (item) {
                if (item.func == '')
                    item.func = CrashKit.guessFunctionName(item.url, item.line);
                var context = CrashKit.gatherContext(item.url, item.line);
                var midline = (context ? context[Math.floor(context.length/2)] : null);
                if (context && midline.replace(/^\s*/, '') == lines[i+1].replace(/^\s*/, ''))
                    item.context = context;
                else {
                    // if (context) alert("Context mismatch. Correct midline:\n" + lines[i+1] + "\n\nMidline:\n" + midline + "\n\nContext:\n" + context.join("\n") + "\n\nURL:\n" + item.url);
                    item.context = [lines[i+1]];
                }
                stack.push(item);
            }
        }

        return {'mode': 'opera', 'name': e.name, 'message': lines[0], 'stack': stack};
    };
} else {
    CrashKit.getStackTrace = function(e) {
        // Internet Explorer does not provide a stack trace, so we have to walk the chain of callers.
        // IE also does not expose the line numbers to exception handlers. The only way
        // to get the line number for the topmost function is to delay processing until our
        // window.onerror handler gets called (which does accept a URL and a line number).
        // Of course, we can also determine correct line numbers for one-line functions.
        // IE tries to make our task extra fun by not providing any function names,
        // so we have to search your JS/HTML code to find the name of every function.
        if (window.console) {
            var data = "";
            for (var i in e) {
                data += "e." + i + " = " + e[i] + "\n";
            }
            console.info(data);
        }
        var curr  = arguments.callee.caller,
            FUNC  = 'function', ANON = "{anonymous}",
            fnRE  = /function\s*([\w\-$]+)?\s*\(/i,
            stack = [],j=0,
            fn,args,i;

        while (curr) {
            fn    = fnRE.test(curr.toString()) ? RegExp.$1 || ANON : ANON;
            args  = stack.slice.call(curr.arguments);
            i     = args.length;

            while (i--) {
                switch (typeof args[i]) {
                    case 'string'  : args[i] = '"'+args[i].replace(/"/g,'\\"')+'"'; break;
                    case 'function': args[i] = FUNC; break;
                }
            }

            stack[j++] = fn + '(' + args.join() + ')';
            curr = curr.caller;
        }

        return stack;
    };
}

CrashKit.handleError = function(stack) {
    if (CrashKit.URL == null)
        CrashKit.computeWebServiceUrl();
    if (CrashKit.URL == null)
        return;
    var json = CrashKit.encodeError(stack);
    if (window.console)
        window.console.info("Error report sent to " + CrashKit.Host + ":\n" + json);
    else
        alert(json);
    CrashKit.sendError(json);
}

CrashKit.handleUnhandledError =  function(error, url, line)  {
    var location = {'url': url, 'line': line};
    location.func = CrashKit.guessFunctionName(location.url, location.line);
    CrashKit.handleError({'mode': 'onerror', 'message': error, 'stack': location});
    return false;
}

window.onerror = CrashKit.handleUnhandledError;

if(typeof(jQuery) != 'undefined'){

  // override jQuery.fn.bind to wrap every provided function in try/catch
  var jQueryBind = jQuery.fn.bind;
  jQuery.fn.bind = function( type, data, fn ) { 
    if ( !fn && data && typeof data == 'function' )
    {
      fn = data;
      data = null;
    }
    if ( fn )
    {
      var origFn = fn;
      var wrappedFn = function() { 
        try 
        {
          return origFn.apply( this, arguments );
        }
        catch ( ex )
        {
          CrashKit.report(ex);
          // re-throw ex iff error should propogate
          // throw ex;
         }
       };
       fn = wrappedFn;
     }
     return jQueryBind.call( this, type, data, fn );
  };
}
