//Warning: IE has problems with caching.
//To be able to submit multiple bugs in older IE versions, use the following code:
//<meta http-equiv="Pragma" content="no-cache" />
//<meta http-equiv="Expires" content="-1" />

CrashKit = {
  URL: "http://crashkitapp.appspot.com/test/products/js/post-report/0/0",
  Action: "",
};
// Edit these options in your code like this: 
// CrashKit.URL = http://crashkitapp.appspot.com/vasya/products/myproject/post-report/0/0

// Provide the XMLHttpRequest class for IE 5.x-6.x:
if( typeof XMLHttpRequest == "undefined" ) XMLHttpRequest = function() {
  try { return new ActiveXObject("Msxml2.XMLHTTP.6.0") } catch(e) {}
  try { return new ActiveXObject("Msxml2.XMLHTTP.3.0") } catch(e) {}
  try { return new ActiveXObject("Msxml2.XMLHTTP") } catch(e) {}
  try { return new ActiveXObject("Microsoft.XMLHTTP") } catch(e) {}
  throw new Error( "This browser does not support XMLHttpRequest." )
};

CrashKit.Browser = {
	init: function () {
		this.browser = this.searchString(this.dataBrowser) || "An unknown browser";
		this.version = this.searchVersion(navigator.userAgent)
			|| this.searchVersion(navigator.appVersion)
			|| "an unknown version";
		this.OS = this.searchString(this.dataOS) || "an unknown OS";
	},
	searchString: function (data) {
		for (var i=0;i<data.length;i++)	{
			var dataString = data[i].string;
			var dataProp = data[i].prop;
			this.versionSearchString = data[i].versionSearch || data[i].identity;
			if (dataString) {
				if (dataString.indexOf(data[i].subString) != -1)
					return data[i].identity;
			}
			else if (dataProp)
				return data[i].identity;
		}
	},
	searchVersion: function (dataString) {
		var index = dataString.indexOf(this.versionSearchString);
		if (index == -1) return;
		return parseFloat(dataString.substring(index+this.versionSearchString.length+1));
	},
	dataBrowser: [
		{
			string: navigator.userAgent,
			subString: "Chrome",
			identity: "Chrome"
		},
		{ 	string: navigator.userAgent,
			subString: "OmniWeb",
			versionSearch: "OmniWeb/",
			identity: "OmniWeb"
		},
		{
			string: navigator.vendor,
			subString: "Apple",
			identity: "Safari",
			versionSearch: "Version"
		},
		{
			prop: window.opera,
			identity: "Opera"
		},
		{
			string: navigator.vendor,
			subString: "iCab",
			identity: "iCab"
		},
		{
			string: navigator.vendor,
			subString: "KDE",
			identity: "Konqueror"
		},
		{
			string: navigator.userAgent,
			subString: "Firefox",
			identity: "Firefox"
		},
		{
			string: navigator.vendor,
			subString: "Camino",
			identity: "Camino"
		},
		{		// for newer Netscapes (6+)
			string: navigator.userAgent,
			subString: "Netscape",
			identity: "Netscape"
		},
		{
			string: navigator.userAgent,
			subString: "MSIE",
			identity: "Explorer",
			versionSearch: "MSIE"
		},
		{
			string: navigator.userAgent,
			subString: "Gecko",
			identity: "Mozilla",
			versionSearch: "rv"
		},
		{ 		// for older Netscapes (4-)
			string: navigator.userAgent,
			subString: "Mozilla",
			identity: "Netscape",
			versionSearch: "Mozilla"
		}
	],
	dataOS : [
		{
			string: navigator.platform,
			subString: "Win",
			identity: "Windows"
		},
		{
			string: navigator.platform,
			subString: "Mac",
			identity: "Mac"
		},
		{
      string: navigator.userAgent,
      subString: "iPhone",
      identity: "iPhone/iPod"
	    },
		{
			string: navigator.platform,
			subString: "Linux",
			identity: "Linux"
		}
	]

};

JSON = new function(){
  this.encode = function(){
		var	self = arguments.length ? arguments[0] : this,
			result, tmp;
		if(self === null)
			result = "null";
		else if(self !== undefined && (tmp = $[typeof self](self))) {
			switch(tmp){
				case	Array:
					result = [];
					for(var	i = 0, j = 0, k = self.length; j < k; j++) {
						if(self[j] !== undefined && (tmp = JSON.encode(self[j])))
							result[i++] = tmp;
					};
					result = "[".concat(result.join(","), "]");
					break;
				case	Boolean:
					result = String(self);
					break;
				case	Date:
					result = '"'.concat(self.getFullYear(), '-', d(self.getMonth() + 1), '-', d(self.getDate()), '"');
					break;
				case	Function:
					break;
				case	Number:
					result = isFinite(self) ? String(self) : "null";
					break;
				case	String:
					result = '"'.concat(self.replace(rs, s).replace(ru, u), '"');
					break;
				default:
					var	i = 0, key;
					result = [];
					for(key in self) {
						if(self[key] !== undefined && (tmp = JSON.encode(self[key])))
							result[i++] = '"'.concat(key.replace(rs, s).replace(ru, u), '":', tmp);
					};
					result = "{".concat(result.join(","), "}");
					break;
			}
		};
		return result;
	};
	var	c = {"\b":"b","\t":"t","\n":"n","\f":"f","\r":"r",'"':'"',"\\":"\\","/":"/"},
		d = function(n){return n<10?"0".concat(n):n},
		e = function(c,f,e){e=eval;delete eval;if(typeof eval==="undefined")eval=e;f=eval(""+c);eval=e;return f},
		i = function(e,p,l){return 1*e.substr(p,l)},
		p = ["","000","00","0",""],
		rc = null,
		rd = /^[0-9]{4}\-[0-9]{2}\-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}$/,
		rs = /(\x5c|\x2F|\x22|[\x0c-\x0d]|[\x08-\x0a])/g,
		rt = /^([0-9]+|[0-9]+[,\.][0-9]{1,3})$/,
		ru = /([\x00-\x07]|\x0b|[\x0e-\x1f])/g,
		s = function(i,d){return "\\".concat(c[d])},
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
	try{rc=new RegExp('^("(\\\\.|[^"\\\\\\n\\r])*?"|[,:{}\\[\\]0-9.\\-+Eaeflnr-u \\n\\r\\t])+?$')}
	catch(z){rc=/^(true|false|null|\[.*\]|\{.*\}|".*"|\d+|\d+\.\d+)$/}
}

CrashKit.send_error = function(text){
  
  var request =  new XMLHttpRequest();
  request.open("POST", CrashKit.URL, false);
  request.setRequestHeader("Content-Type", "text/plain;charset=UTF-8");
  request.send(text);
  if(!request.getResponseHeader("Date") || request.status != 200) { //send failed
    alert("Please tell this error to the maintainer orally:" + text);
  }
}  


CrashKit.pack_error = function (error, url, line) {
  CrashKit.Browser.init();
  return JSON.encode([
      {
          "date": new Date(),
          "count": 1,
          "userActionOrScreenNameOrBackgroundProcess": CrashKit.Action,
          "severity": "major",
          "exceptions": [
              {
                  "name": error,
                  "locations": [
                      { "file": url, "method": "unknown", "line": line },
                  ]
              }
          ],
          "data": {
          },
          "env": {
              "Browser OS": CrashKit.Browser.OS,
              "Browser Name": CrashKit.Browser.browser,
              "Browser Version": CrashKit.Browser.version
          }
      }
  ]);
}



CrashKit.handleErrors =  function(error, url, line)  {
    // EnableMe: CrashKit.getStackTrace();
    var err = CrashKit.pack_error(error, url, line);
    CrashKit.send_error(err);
    //alert(error);
    //alert('There has been a problem while rendering this page, which may or may not function properly. Our administrators have just been informed about this problem, sorry for any inconviniences and please try again in a few minutes.');
    msg = new Array('The following error has been produced:');
    msg.push('Exception type: ' + error);
    msg.push('In line ' + line + ' of compiled file ' + url + ':');
    msg.push(error);
    msg = msg.join('\n');

    try {
        console.info(msg + '\nAdministrators have just been informed of this problem. Sorry for any inconveniences.');
    } catch(e) {}

    return false;
}

window.onerror = CrashKit.handleErrors;

//alert("installed");

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
          handleErrors( ex.message, ex.fileName, ex.lineNumber );
          // re-throw ex iff error should propogate
          // throw ex;
         }
       };
       fn = wrappedFn;
     }
     return jQueryBind.call( this, type, data, fn );
  };
}