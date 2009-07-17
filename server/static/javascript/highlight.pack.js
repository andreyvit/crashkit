var hljs=new function(){var n={};var a={};function l(c){return c.replace(/&/gm,"&amp;").replace(/</gm,"&lt;").replace(/>/gm,"&gt;")}function j(q,p){if(!q){return false}for(var c=0;c<q.length;c++){if(q[c]==p){return true}}return false}function f(I,C){function J(N,M){N.sm=[];for(var L=0;L<N.c.length;L++){for(var r=0;r<M.m.length;r++){if(M.m[r].cN==N.c[L]){N.sm[N.sm.length]=M.m[r]}}}}function y(r,M){if(!M.c){return null}if(!M.sm){J(M,G)}for(var L=0;L<M.sm.length;L++){if(M.sm[L].bR.test(r)){return M.sm[L]}}return null}function v(L,r){if(B[L].e&&B[L].eR.test(r)){return 1}if(B[L].eW){var M=v(L-1,r);return M?M+1:0}return 0}function w(r,L){return L.iR&&L.iR.test(r)}function z(Q,O){var M=[];function P(R){if(!j(M,R)){M[M.length]=R}}if(Q.c){for(var L=0;L<O.m.length;L++){if(j(Q.c,O.m[L].cN)){P(O.m[L].b)}}}var r=B.length-1;do{if(B[r].e){P(B[r].e)}r--}while(B[r+1].eW);if(Q.i){P(Q.i)}var N="("+M[0];for(var L=0;L<M.length;L++){N+="|"+M[L]}N+=")";return d(O,N)}function q(M,L){var N=B[B.length-1];if(!N.t){N.t=z(N,G)}M=M.substr(L);var r=N.t.exec(M);if(!r){return[M,"",true]}if(r.index==0){return["",r[0],false]}else{return[M.substr(0,r.index),r[0],false]}}function p(O,r){var L=G.cI?r[0].toLowerCase():r[0];for(var N in O.keywordGroups){if(!O.keywordGroups.hasOwnProperty(N)){continue}var M=O.keywordGroups[N].hasOwnProperty(L);if(M){return[N,M]}}return false}function E(N,Q){if(!Q.k||!Q.l){return l(N)}if(!Q.lR){var P="("+Q.l[0];for(var M=1;M<Q.l.length;M++){P+="|"+Q.l[M]}P+=")";Q.lR=d(G,P,true)}var O="";var R=0;Q.lR.lastIndex=0;var L=Q.lR.exec(N);while(L){O+=l(N.substr(R,L.index-R));var r=p(Q,L);if(r){s+=r[1];O+='<span class="'+r[0]+'">'+l(L[0])+"</span>"}else{O+=l(L[0])}R=Q.lR.lastIndex;L=Q.lR.exec(N)}O+=l(N.substr(R,N.length-R));return O}function K(r,M){if(M.subLanguage&&a[M.subLanguage]){var L=f(M.subLanguage,r);s+=L.keyword_count;A+=L.r;return L.value}else{return E(r,M)}}function H(M,r){var L=M.nM?"":'<span class="'+M.cN+'">';if(M.rB){c+=L;M.buffer=""}else{if(M.eB){c+=l(r)+L;M.buffer=""}else{c+=L;M.buffer=r}}B[B.length]=M}function D(P,L,Q){var R=B[B.length-1];if(Q){c+=K(R.buffer+P,R);return false}var M=y(L,R);if(M){c+=K(R.buffer+P,R);H(M,L);A+=M.r;return M.rB}var r=v(B.length-1,L);if(r){var O=R.nM?"":"</span>";if(R.rE){c+=K(R.buffer+P,R)+O}else{if(R.eE){c+=K(R.buffer+P,R)+O+l(L)}else{c+=K(R.buffer+P+L,R)+O}}while(r>1){O=B[B.length-2].nM?"":"</span>";c+=O;r--;B.length--}B.length--;B[B.length-1].buffer="";if(R.starts){for(var N=0;N<G.m.length;N++){if(G.m[N].cN==R.starts){H(G.m[N],"");break}}}return R.rE}if(w(L,R)){throw"Illegal"}}var G=n[I];var B=[G.dM];var A=0;var s=0;var c="";try{var u=0;G.dM.buffer="";do{var x=q(C,u);var t=D(x[0],x[1],x[2]);u+=x[0].length;if(!t){u+=x[1].length}}while(!x[2]);if(B.length>1){throw"Illegal"}return{r:A,keyword_count:s,value:c}}catch(F){if(F=="Illegal"){return{r:0,keyword_count:0,value:l(C)}}else{throw F}}}function g(q){var p="";for(var c=0;c<q.childNodes.length;c++){if(q.childNodes[c].nodeType==3){p+=q.childNodes[c].nodeValue}else{if(q.childNodes[c].nodeName=="BR"){p+="\n"}else{throw"No highlight"}}}return p}function b(q){var p=q.className.split(/\s+/);for(var c=0;c<p.length;c++){if(p[c]=="no-highlight"){throw"No highlight"}if(n[p[c]]){return p[c]}}}function o(u,y){try{var B=g(u);var q=b(u)}catch(v){if(v=="No highlight"){return}}if(q){var x=f(q,B).value}else{var z=0;for(var A in a){if(!a.hasOwnProperty(A)){continue}var p=f(A,B);var c=p.keyword_count+p.r;if(c>z){z=c;var x=p.value;q=A}}}if(x){if(y){x=x.replace(/^(\t+)/gm,function(r,E,D,C){return E.replace(/\t/g,y)})}var t=u.className;if(!t.match(q)){t+=" "+q}var w=document.createElement("div");w.innerHTML='<pre><code class="'+t+'">'+x+"</code></pre>";var s=u.parentNode.parentNode;s.replaceChild(w.firstChild,u.parentNode)}}function d(q,p,c){var r="m"+(q.cI?"i":"")+(c?"g":"");return new RegExp(p,r)}function i(){for(var p in n){if(!n.hasOwnProperty(p)){continue}var q=n[p];for(var c=0;c<q.m.length;c++){if(q.m[c].b){q.m[c].bR=d(q,"^"+q.m[c].b)}if(q.m[c].e){q.m[c].eR=d(q,"^"+q.m[c].e)}if(q.m[c].i){q.m[c].iR=d(q,"^(?:"+q.m[c].i+")")}q.dM.iR=d(q,"^(?:"+q.dM.i+")");if(q.m[c].r==undefined){q.m[c].r=1}}}}function e(){function q(t){if(!t.keywordGroups){for(var s in t.k){if(!t.k.hasOwnProperty(s)){continue}if(t.k[s] instanceof Object){t.keywordGroups=t.k}else{t.keywordGroups={keyword:t.k}}break}}}for(var p in n){if(!n.hasOwnProperty(p)){continue}var r=n[p];q(r.dM);for(var c=0;c<r.m.length;c++){q(r.m[c])}}}function h(p){for(var c=0;c<p.childNodes.length;c++){node=p.childNodes[c];if(node.nodeName=="CODE"){return node}if(!(node.nodeType==3&&node.nodeValue.match(/\s+/))){return null}}}function k(){if(k.called){return}k.called=true;i();e();if(arguments.length){for(var c=0;c<arguments.length;c++){if(n[arguments[c]]){a[arguments[c]]=n[arguments[c]]}}}else{a=n}var q=document.getElementsByTagName("pre");for(var c=0;c<q.length;c++){var p=h(q[c]);if(p){o(p,hljs.tabReplace)}}}function m(){var c=arguments;var p=function(){k.apply(null,c)};if(window.addEventListener){window.addEventListener("DOMContentLoaded",p,false);window.addEventListener("load",p,false)}else{if(window.attachEvent){window.attachEvent("onload",p)}else{window.onload=p}}}this.LANGUAGES=n;this.initHighlightingOnLoad=m;this.highlightBlock=o;this.initHighlighting=k;this.IR="[a-zA-Z][a-zA-Z0-9_]*";this.UIR="[a-zA-Z_][a-zA-Z0-9_]*";this.NR="\\b\\d+(\\.\\d+)?";this.CNR="\\b(0x[A-Za-z0-9]+|\\d+(\\.\\d+)?)";this.RSR="!|!=|!==|%|%=|&|&&|&=|\\*|\\*=|\\+|\\+=|,|\\.|-|-=|/|/=|:|;|<|<<|<<=|<=|=|==|===|>|>=|>>|>>=|>>>|>>>=|\\?|\\[|\\{|\\(|\\^|\\^=|\\||\\|=|\\|\\||~";this.ASM={cN:"string",b:"'",e:"'",i:"\\n",c:["escape"],r:0};this.QSM={cN:"string",b:'"',e:'"',i:"\\n",c:["escape"],r:0};this.BE={cN:"escape",b:"\\\\.",e:"^",nM:true,r:0};this.CLCM={cN:"comment",b:"//",e:"$",r:0};this.CBLCLM={cN:"comment",b:"/\\*",e:"\\*/"};this.HCM={cN:"comment",b:"#",e:"$"};this.CNM={cN:"number",b:this.CNR,e:"^",r:0}}();var initHighlightingOnLoad=hljs.initHighlightingOnLoad;hljs.LANGUAGES.cs={dM:{l:[hljs.UIR],c:["comment","string","number"],k:{"abstract":1,as:1,base:1,bool:1,"break":1,"byte":1,"case":1,"catch":1,"char":1,checked:1,"class":1,"const":1,"continue":1,decimal:1,"default":1,delegate:1,"do":1,"do":1,"double":1,"else":1,"enum":1,event:1,explicit:1,extern:1,"false":1,"finally":1,fixed:1,"float":1,"for":1,foreach:1,"goto":1,"if":1,implicit:1,"in":1,"int":1,"interface":1,internal:1,is:1,lock:1,"long":1,namespace:1,"new":1,"null":1,object:1,operator:1,out:1,override:1,params:1,"private":1,"protected":1,"public":1,readonly:1,ref:1,"return":1,sbyte:1,sealed:1,"short":1,sizeof:1,stackalloc:1,"static":1,string:1,struct:1,"switch":1,"this":1,"throw":1,"true":1,"try":1,"typeof":1,uint:1,ulong:1,unchecked:1,unsafe:1,ushort:1,using:1,virtual:1,"volatile":1,"void":1,"while":1,ascending:1,descending:1,from:1,get:1,group:1,into:1,join:1,let:1,orderby:1,partial:1,select:1,set:1,value:1,"var":1,where:1,yield:1}},m:[{cN:"comment",b:"///",e:"$",rB:true,c:["xmlDocTag"]},{cN:"xmlDocTag",b:"///|<!--|-->",e:"^"},{cN:"xmlDocTag",b:"</?",e:">"},{cN:"string",b:'@"',e:'"',c:["quoteQuote"]},{cN:"quoteQuote",b:'""',e:"^"},hljs.CLCM,hljs.CBLCLM,hljs.ASM,hljs.QSM,hljs.BE,hljs.CNM]};hljs.LANGUAGES.cpp=function(){var a={keyword:{"false":1,"int":1,"float":1,"while":1,"private":1,"char":1,"catch":1,"export":1,virtual:1,operator:2,sizeof:2,dynamic_cast:2,typedef:2,const_cast:2,"const":1,struct:1,"for":1,static_cast:2,union:1,namespace:1,unsigned:1,"long":1,"throw":1,"volatile":2,"static":1,"protected":1,bool:1,template:1,mutable:1,"if":1,"public":1,friend:2,"do":1,"return":1,"goto":1,auto:1,"void":2,"enum":1,"else":1,"break":1,"new":1,extern:1,using:1,"true":1,"class":1,asm:1,"case":1,typeid:1,"short":1,reinterpret_cast:2,"default":1,"double":1,register:1,explicit:1,signed:1,typename:1,"try":1,"this":1,"switch":1,"continue":1,wchar_t:1,inline:1,"delete":1},built_in:{std:1,string:1,cin:1,cout:1,cerr:1,clog:1,stringstream:1,istringstream:1,ostringstream:1,auto_ptr:1,deque:1,list:1,queue:1,stack:1,vector:1,map:1,set:1,bitset:1,multiset:1,multimap:1}};return{dM:{l:[hljs.UIR],i:"</",c:["comment","string","number","preprocessor","stl_container"],k:a},m:[hljs.CLCM,hljs.CBLCLM,hljs.CNM,hljs.QSM,hljs.BE,{cN:"string",b:"'",e:"[^\\\\]'",i:"[^\\\\][^']"},{cN:"preprocessor",b:"#",e:"$"},{cN:"stl_container",b:"\\b(deque|list|queue|stack|vector|map|set|bitset|multiset|multimap)\\s*<",e:">",c:["stl_container"],l:[hljs.UIR],k:a,r:10}]}}();hljs.XML_COMMENT={cN:"comment",b:"<!--",e:"-->"};hljs.XML_ATTR={cN:"attribute",b:"\\s[a-zA-Z\\:-]+=",e:"^",c:["value"]};hljs.XML_VALUE_QUOT={cN:"value",b:'"',e:'"'};hljs.XML_VALUE_APOS={cN:"value",b:"'",e:"'"};hljs.LANGUAGES.xml={dM:{c:["pi","comment","cdata","tag"]},cI:true,m:[{cN:"pi",b:"<\\?",e:"\\?>",r:10},hljs.XML_COMMENT,{cN:"cdata",b:"<\\!\\[CDATA\\[",e:"\\]\\]>"},{cN:"tag",b:"</?",e:">",c:["title","tag_internal"],r:1.5},{cN:"title",b:"[A-Za-z:_][A-Za-z0-9\\._:-]+",e:"^",r:0},{cN:"tag_internal",b:"^",eW:true,nM:true,c:["attribute"],r:0,i:"[\\+\\.]"},hljs.XML_ATTR,hljs.XML_VALUE_QUOT,hljs.XML_VALUE_APOS]};hljs.HTML_TAGS={code:1,kbd:1,font:1,noscript:1,style:1,img:1,title:1,menu:1,tt:1,tr:1,param:1,li:1,tfoot:1,th:1,input:1,td:1,dl:1,blockquote:1,fieldset:1,big:1,dd:1,abbr:1,optgroup:1,dt:1,button:1,isindex:1,p:1,small:1,div:1,dir:1,em:1,frame:1,meta:1,sub:1,bdo:1,label:1,acronym:1,sup:1,body:1,xml:1,basefont:1,base:1,br:1,address:1,strong:1,legend:1,ol:1,script:1,caption:1,s:1,col:1,h2:1,h3:1,h1:1,h6:1,h4:1,h5:1,table:1,select:1,noframes:1,span:1,area:1,dfn:1,strike:1,cite:1,thead:1,head:1,option:1,form:1,hr:1,"var":1,link:1,b:1,colgroup:1,ul:1,applet:1,del:1,iframe:1,pre:1,frameset:1,ins:1,tbody:1,html:1,samp:1,map:1,object:1,a:1,xmlns:1,center:1,textarea:1,i:1,q:1,u:1};hljs.HTML_DOCTYPE={cN:"doctype",b:"<!DOCTYPE",e:">",r:10};hljs.HTML_ATTR={cN:"attribute",b:"\\s[a-zA-Z\\:-]+=",e:"^",c:["value"]};hljs.HTML_SHORT_ATTR={cN:"attribute",b:" [a-zA-Z]+",e:"^"};hljs.HTML_VALUE={cN:"value",b:"[a-zA-Z0-9]+",e:"^"};hljs.LANGUAGES.html={dM:{c:["tag","comment","doctype","vbscript"]},cI:true,m:[hljs.XML_COMMENT,hljs.HTML_DOCTYPE,{cN:"tag",l:[hljs.IR],k:hljs.HTML_TAGS,b:"<style",e:">",c:["attribute"],i:"[\\+\\.]",starts:"css"},{cN:"tag",l:[hljs.IR],k:hljs.HTML_TAGS,b:"<script",e:">",c:["attribute"],i:"[\\+\\.]",starts:"javascript"},{cN:"tag",l:[hljs.IR],k:hljs.HTML_TAGS,b:"<[A-Za-z/]",e:">",c:["attribute"],i:"[\\+\\.]"},{cN:"css",e:"</style>",rE:true,subLanguage:"css"},{cN:"javascript",e:"<\/script>",rE:true,subLanguage:"javascript"},hljs.HTML_ATTR,hljs.HTML_SHORT_ATTR,hljs.XML_VALUE_QUOT,hljs.XML_VALUE_APOS,hljs.HTML_VALUE,{cN:"vbscript",b:"<%",e:"%>",subLanguage:"vbscript"}]};hljs.LANGUAGES.django={dM:{c:["tag","comment","doctype","template_comment","template_tag","variable"]},cI:true,m:[hljs.XML_COMMENT,hljs.HTML_DOCTYPE,{cN:"tag",l:[hljs.IR],k:hljs.HTML_TAGS,b:"<[A-Za-z/]",e:">",c:["attribute","template_comment","template_tag","variable"]},hljs.HTML_ATTR,hljs.HTML_SHORT_ATTR,{cN:"value",b:'"',e:'"',c:["template_comment","template_tag","variable"]},hljs.HTML_VALUE,{cN:"template_comment",b:"\\{\\%\\s*comment\\s*\\%\\}",e:"\\{\\%\\s*endcomment\\s*\\%\\}"},{cN:"template_comment",b:"\\{#",e:"#\\}"},{cN:"template_tag",b:"\\{\\%",e:"\\%\\}",l:[hljs.IR],k:{comment:1,endcomment:1,load:1,templatetag:1,ifchanged:1,endifchanged:1,"if":1,endif:1,firstof:1,"for":1,endfor:1,"in":1,ifnotequal:1,endifnotequal:1,widthratio:1,"extends":1,include:1,spaceless:1,endspaceless:1,regroup:1,by:1,as:1,ifequal:1,endifequal:1,ssi:1,now:1,"with":1,cycle:1,url:1,filter:1,endfilter:1,debug:1,block:1,endblock:1,"else":1},c:["filter"]},{cN:"variable",b:"\\{\\{",e:"\\}\\}",c:["filter"]},{cN:"filter",b:"\\|[A-Za-z]+\\:?",e:"^",eE:true,l:[hljs.IR],k:{truncatewords:1,removetags:1,linebreaksbr:1,yesno:1,get_digit:1,timesince:1,random:1,striptags:1,filesizeformat:1,escape:1,linebreaks:1,length_is:1,ljust:1,rjust:1,cut:1,urlize:1,fix_ampersands:1,title:1,floatformat:1,capfirst:1,pprint:1,divisibleby:1,add:1,make_list:1,unordered_list:1,urlencode:1,timeuntil:1,urlizetrunc:1,wordcount:1,stringformat:1,linenumbers:1,slice:1,date:1,dictsort:1,dictsortreversed:1,default_if_none:1,pluralize:1,lower:1,join:1,center:1,"default":1,truncatewords_html:1,upper:1,length:1,phone2numeric:1,wordwrap:1,time:1,addslashes:1,slugify:1,first:1},c:["argument"]},{cN:"argument",b:'"',e:'"'}]};hljs.LANGUAGES.python={dM:{l:[hljs.UIR],i:"(</|->)",c:["comment","string","function","class","number","decorator"],k:{keyword:{and:1,elif:1,is:1,global:1,as:1,"in":1,"if":1,from:1,raise:1,"for":1,except:1,"finally":1,print:1,"import":1,pass:1,"return":1,exec:1,"else":1,"break":1,not:1,"with":1,"class":1,assert:1,yield:1,"try":1,"while":1,"continue":1,del:1,or:1,def:1,lambda:1},built_in:{None:1,True:1,False:1,Ellipsis:1,NotImplemented:1}}},m:[{cN:"function",l:[hljs.UIR],b:"\\bdef ",e:":",i:"$",k:{def:1},c:["title","params"],r:10},{cN:"class",l:[hljs.UIR],b:"\\bclass ",e:":",i:"[${]",k:{"class":1},c:["title","params",],r:10},{cN:"title",b:hljs.UIR,e:"^"},{cN:"params",b:"\\(",e:"\\)",c:["string"]},hljs.HCM,hljs.CNM,{cN:"string",b:"u?r?'''",e:"'''",r:10},{cN:"string",b:'u?r?"""',e:'"""',r:10},hljs.ASM,hljs.QSM,hljs.BE,{cN:"string",b:"(u|r|ur)'",e:"'",c:["escape"],r:10},{cN:"string",b:'(u|r|ur)"',e:'"',c:["escape"],r:10},{cN:"decorator",b:"@",e:"$"}]};hljs.LANGUAGES.php={dM:{l:[hljs.IR],c:["comment","number","string","variable","preprocessor"],k:{and:1,include_once:1,list:1,"abstract":1,global:1,"private":1,echo:1,"interface":1,as:1,"static":1,endswitch:1,array:1,"null":1,"if":1,endwhile:1,or:1,"const":1,"for":1,endforeach:1,self:1,"var":1,"while":1,isset:1,"public":1,"protected":1,exit:1,foreach:1,"throw":1,elseif:1,"extends":1,include:1,__FILE__:1,empty:1,require_once:1,"function":1,"do":1,xor:1,"return":1,"implements":1,parent:1,clone:1,use:1,__CLASS__:1,__LINE__:1,"else":1,"break":1,print:1,"eval":1,"new":1,"catch":1,__METHOD__:1,"class":1,"case":1,exception:1,php_user_filter:1,"default":1,die:1,require:1,__FUNCTION__:1,enddeclare:1,"final":1,"try":1,"this":1,"switch":1,"continue":1,endfor:1,endif:1,declare:1,unset:1}},cI:true,m:[hljs.CLCM,hljs.HCM,{cN:"comment",b:"/\\*",e:"\\*/",c:["phpdoc"]},{cN:"phpdoc",b:"\\s@[A-Za-z]+",e:"^",r:10},hljs.CNM,{cN:"string",b:"'",e:"'",c:["escape"],r:0},{cN:"string",b:'"',e:'"',c:["escape"],r:0},hljs.BE,{cN:"variable",b:"\\$[a-zA-Z_\x7f-\xff][a-zA-Z0-9_\x7f-\xff]*",e:"^"},{cN:"preprocessor",b:"<\\?php",e:"^",r:10},{cN:"preprocessor",b:"\\?>",e:"^"}]};hljs.LANGUAGES.javascript={dM:{l:[hljs.UIR],c:["string","comment","number","regexp_container","function"],k:{keyword:{"in":1,"if":1,"for":1,"while":1,"finally":1,"var":1,"new":1,"function":1,"do":1,"return":1,"void":1,"else":1,"break":1,"catch":1,"instanceof":1,"with":1,"throw":1,"case":1,"default":1,"try":1,"this":1,"switch":1,"continue":1,"typeof":1,"delete":1},literal:{"true":1,"false":1,"null":1}}},m:[hljs.CLCM,hljs.CBLCLM,hljs.CNM,hljs.ASM,hljs.QSM,hljs.BE,{cN:"regexp_container",b:"("+hljs.RSR+"|case|return|throw)\\s*",e:"^",nM:true,l:[hljs.IR],k:{"return":1,"throw":1,"case":1},c:["comment","regexp"],r:0},{cN:"regexp",b:"/.*?[^\\\\/]/[gim]*",e:"^"},{cN:"function",b:"\\bfunction\\b",e:"{",l:[hljs.UIR],k:{"function":1},c:["title","params"]},{cN:"title",b:"[A-Za-z$_][0-9A-Za-z$_]*",e:"^"},{cN:"params",b:"\\(",e:"\\)",c:["string","comment"]}]};hljs.LANGUAGES.ruby=function(){var a="[a-zA-Z_][a-zA-Z0-9_]*(\\!|\\?)?";var b=["comment","string","char","class","function","symbol","number","variable","regexp_container"];var c={keyword:{and:1,"false":1,then:1,defined:1,module:1,"in":1,"return":1,redo:1,"if":1,BEGIN:1,retry:1,end:1,"for":1,"true":1,self:1,when:1,next:1,until:1,"do":1,begin:1,unless:1,END:1,rescue:1,nil:1,"else":1,"break":1,undef:1,not:1,"super":1,"class":1,"case":1,require:1,yield:1,alias:1,"while":1,ensure:1,elsif:1,or:1,def:1},keymethods:{__id__:1,__send__:1,abort:1,abs:1,"all?":1,allocate:1,ancestors:1,"any?":1,arity:1,assoc:1,at:1,at_exit:1,autoload:1,"autoload?":1,"between?":1,binding:1,binmode:1,"block_given?":1,call:1,callcc:1,caller:1,capitalize:1,"capitalize!":1,casecmp:1,"catch":1,ceil:1,center:1,chomp:1,"chomp!":1,chop:1,"chop!":1,chr:1,"class":1,class_eval:1,"class_variable_defined?":1,class_variables:1,clear:1,clone:1,close:1,close_read:1,close_write:1,"closed?":1,coerce:1,collect:1,"collect!":1,compact:1,"compact!":1,concat:1,"const_defined?":1,const_get:1,const_missing:1,const_set:1,constants:1,count:1,crypt:1,"default":1,default_proc:1,"delete":1,"delete!":1,delete_at:1,delete_if:1,detect:1,display:1,div:1,divmod:1,downcase:1,"downcase!":1,downto:1,dump:1,dup:1,each:1,each_byte:1,each_index:1,each_key:1,each_line:1,each_pair:1,each_value:1,each_with_index:1,"empty?":1,entries:1,eof:1,"eof?":1,"eql?":1,"equal?":1,"eval":1,exec:1,exit:1,"exit!":1,extend:1,fail:1,fcntl:1,fetch:1,fileno:1,fill:1,find:1,find_all:1,first:1,flatten:1,"flatten!":1,floor:1,flush:1,for_fd:1,foreach:1,fork:1,format:1,freeze:1,"frozen?":1,fsync:1,getc:1,gets:1,global_variables:1,grep:1,gsub:1,"gsub!":1,"has_key?":1,"has_value?":1,hash:1,hex:1,id:1,"include?":1,included_modules:1,index:1,indexes:1,indices:1,induced_from:1,inject:1,insert:1,inspect:1,instance_eval:1,instance_method:1,instance_methods:1,"instance_of?":1,"instance_variable_defined?":1,instance_variable_get:1,instance_variable_set:1,instance_variables:1,"integer?":1,intern:1,invert:1,ioctl:1,"is_a?":1,isatty:1,"iterator?":1,join:1,"key?":1,keys:1,"kind_of?":1,lambda:1,last:1,length:1,lineno:1,ljust:1,load:1,local_variables:1,loop:1,lstrip:1,"lstrip!":1,map:1,"map!":1,match:1,max:1,"member?":1,merge:1,"merge!":1,method:1,"method_defined?":1,method_missing:1,methods:1,min:1,module_eval:1,modulo:1,name:1,nesting:1,"new":1,next:1,"next!":1,"nil?":1,nitems:1,"nonzero?":1,object_id:1,oct:1,open:1,pack:1,partition:1,pid:1,pipe:1,pop:1,popen:1,pos:1,prec:1,prec_f:1,prec_i:1,print:1,printf:1,private_class_method:1,private_instance_methods:1,"private_method_defined?":1,private_methods:1,proc:1,protected_instance_methods:1,"protected_method_defined?":1,protected_methods:1,public_class_method:1,public_instance_methods:1,"public_method_defined?":1,public_methods:1,push:1,putc:1,puts:1,quo:1,raise:1,rand:1,rassoc:1,read:1,read_nonblock:1,readchar:1,readline:1,readlines:1,readpartial:1,rehash:1,reject:1,"reject!":1,remainder:1,reopen:1,replace:1,require:1,"respond_to?":1,reverse:1,"reverse!":1,reverse_each:1,rewind:1,rindex:1,rjust:1,round:1,rstrip:1,"rstrip!":1,scan:1,seek:1,select:1,send:1,set_trace_func:1,shift:1,singleton_method_added:1,singleton_methods:1,size:1,sleep:1,slice:1,"slice!":1,sort:1,"sort!":1,sort_by:1,split:1,sprintf:1,squeeze:1,"squeeze!":1,srand:1,stat:1,step:1,store:1,strip:1,"strip!":1,sub:1,"sub!":1,succ:1,"succ!":1,sum:1,superclass:1,swapcase:1,"swapcase!":1,sync:1,syscall:1,sysopen:1,sysread:1,sysseek:1,system:1,syswrite:1,taint:1,"tainted?":1,tell:1,test:1,"throw":1,times:1,to_a:1,to_ary:1,to_f:1,to_hash:1,to_i:1,to_int:1,to_io:1,to_proc:1,to_s:1,to_str:1,to_sym:1,tr:1,"tr!":1,tr_s:1,"tr_s!":1,trace_var:1,transpose:1,trap:1,truncate:1,"tty?":1,type:1,ungetc:1,uniq:1,"uniq!":1,unpack:1,unshift:1,untaint:1,untrace_var:1,upcase:1,"upcase!":1,update:1,upto:1,"value?":1,values:1,values_at:1,warn:1,write:1,write_nonblock:1,"zero?":1,zip:1}};return{dM:{l:[a],c:b,k:c},m:[hljs.HCM,{cN:"comment",b:"^\\=begin",e:"^\\=end",r:10},{cN:"comment",b:"^__END__",e:"\\n$"},{cN:"params",b:"\\(",e:"\\)",l:[a],k:c,c:b},{cN:"function",b:"\\bdef\\b",e:"$|;",l:[a],k:c,c:["title","params","comment"]},{cN:"class",b:"\\b(class|module)\\b",e:"$",l:[hljs.UIR],k:c,c:["title","inheritance","comment"],k:{"class":1,module:1}},{cN:"title",b:"[A-Za-z_]\\w*(::\\w+)*(\\?|\\!)?",e:"^",r:0},{cN:"inheritance",b:"<\\s*",e:"^",c:["parent"]},{cN:"parent",b:"("+hljs.IR+"::)?"+hljs.IR,e:"^"},{cN:"number",b:"(\\b0[0-7_]+)|(\\b0x[0-9a-fA-F_]+)|(\\b[1-9][0-9_]*(\\.[0-9_]+)?)|[0_]\\b",e:"^",r:0},{cN:"number",b:"\\?\\w",e:"^"},{cN:"string",b:"'",e:"'",c:["escape","subst"],r:0},{cN:"string",b:'"',e:'"',c:["escape","subst"],r:0},{cN:"string",b:"%[qw]?\\(",e:"\\)",c:["escape","subst"],r:10},{cN:"string",b:"%[qw]?\\[",e:"\\]",c:["escape","subst"],r:10},{cN:"string",b:"%[qw]?{",e:"}",c:["escape","subst"],r:10},{cN:"string",b:"%[qw]?<",e:">",c:["escape","subst"],r:10},{cN:"string",b:"%[qw]?/",e:"/",c:["escape","subst"],r:10},{cN:"string",b:"%[qw]?%",e:"%",c:["escape","subst"],r:10},{cN:"string",b:"%[qw]?-",e:"-",c:["escape","subst"],r:10},{cN:"string",b:"%[qw]?\\|",e:"\\|",c:["escape","subst"],r:10},{cN:"symbol",b:":"+a,e:"^"},hljs.BE,{cN:"subst",b:"#\\{",e:"}",l:[a],k:c,c:b},{cN:"regexp_container",b:"("+hljs.RSR+")\\s*",e:"^",nM:true,c:["comment","regexp"],r:0},{cN:"regexp",b:"/",e:"/[a-z]*",i:"\\n",c:["escape"]},{cN:"variable",b:"(\\$\\W)|((\\$|\\@\\@?)(\\w+))",e:"^"}]}}();hljs.LANGUAGES.perl=function(){var b=["comment","string","number","regexp","sub","variable","operator","pod"];var a={getpwent:1,getservent:1,quotemeta:1,msgrcv:1,scalar:1,kill:1,dbmclose:1,undef:1,lc:1,ma:1,syswrite:1,tr:1,send:1,umask:1,sysopen:1,shmwrite:1,vec:1,qx:1,utime:1,local:1,oct:1,semctl:1,localtime:1,readpipe:1,"do":1,"return":1,format:1,read:1,sprintf:1,dbmopen:1,pop:1,getpgrp:1,not:1,getpwnam:1,rewinddir:1,qq:1,fileno:1,qw:1,endprotoent:1,wait:1,sethostent:1,bless:1,s:1,opendir:1,"continue":1,each:1,sleep:1,endgrent:1,shutdown:1,dump:1,chomp:1,connect:1,getsockname:1,die:1,socketpair:1,close:1,flock:1,exists:1,index:1,shmget:1,sub:1,"for":1,endpwent:1,redo:1,lstat:1,msgctl:1,setpgrp:1,abs:1,exit:1,select:1,print:1,ref:1,gethostbyaddr:1,unshift:1,fcntl:1,syscall:1,"goto":1,getnetbyaddr:1,join:1,gmtime:1,symlink:1,semget:1,splice:1,x:1,getpeername:1,recv:1,log:1,setsockopt:1,cos:1,last:1,reverse:1,gethostbyname:1,getgrnam:1,study:1,formline:1,endhostent:1,times:1,chop:1,length:1,gethostent:1,getnetent:1,pack:1,getprotoent:1,getservbyname:1,rand:1,mkdir:1,pos:1,chmod:1,y:1,substr:1,endnetent:1,printf:1,next:1,open:1,msgsnd:1,readdir:1,use:1,unlink:1,getsockopt:1,getpriority:1,rindex:1,wantarray:1,hex:1,system:1,getservbyport:1,endservent:1,"int":1,chr:1,untie:1,rmdir:1,prototype:1,tell:1,listen:1,fork:1,shmread:1,ucfirst:1,setprotoent:1,"else":1,sysseek:1,link:1,getgrgid:1,shmctl:1,waitpid:1,unpack:1,getnetbyname:1,reset:1,chdir:1,grep:1,split:1,require:1,caller:1,lcfirst:1,until:1,warn:1,"while":1,values:1,shift:1,telldir:1,getpwuid:1,my:1,getprotobynumber:1,"delete":1,and:1,sort:1,uc:1,defined:1,srand:1,accept:1,"package":1,seekdir:1,getprotobyname:1,semop:1,our:1,rename:1,seek:1,"if":1,q:1,chroot:1,sysread:1,setpwent:1,no:1,crypt:1,getc:1,chown:1,sqrt:1,write:1,setnetent:1,setpriority:1,foreach:1,tie:1,sin:1,msgget:1,map:1,stat:1,getlogin:1,unless:1,elsif:1,truncate:1,exec:1,keys:1,glob:1,tied:1,closedir:1,ioctl:1,socket:1,readlink:1,"eval":1,xor:1,readline:1,binmode:1,setservent:1,eof:1,ord:1,bind:1,alarm:1,pipe:1,atan2:1,getgrent:1,exp:1,time:1,push:1,setgrent:1,gt:1,lt:1,or:1,ne:1,m:1};return{dM:{l:[hljs.IR],c:b,k:a},m:[{cN:"variable",b:"\\$\\d",e:"^"},{cN:"variable",b:"[\\$\\%\\@\\*](\\^\\w\\b|#\\w+(\\:\\:\\w+)*|[^\\s\\w{]|{\\w+}|\\w+(\\:\\:\\w*)*)",e:"^"},{cN:"subst",b:"[$@]\\{",e:"}",l:[hljs.IR],k:a,c:b,r:10},{cN:"number",b:"(\\b0[0-7_]+)|(\\b0x[0-9a-fA-F_]+)|(\\b[1-9][0-9_]*(\\.[0-9_]+)?)|[0_]\\b",e:"^",r:0},{cN:"string",b:"q[qwxr]?\\s*\\(",e:"\\)",c:["escape","subst","variable"],r:5},{cN:"string",b:"q[qwxr]?\\s*\\[",e:"\\]",c:["escape","subst","variable"],r:5},{cN:"string",b:"q[qwxr]?\\s*\\{",e:"\\}",c:["escape","subst","variable"],r:5},{cN:"string",b:"q[qwxr]?\\s*\\|",e:"\\|",c:["escape","subst","variable"],r:5},{cN:"string",b:"q[qwxr]?\\s*\\<",e:"\\>",c:["escape","subst","variable"],r:5},{cN:"string",b:"qw\\s+q",e:"q",c:["escape","subst","variable"],r:5},{cN:"string",b:"'",e:"'",c:["escape"],r:0},{cN:"string",b:'"',e:'"',c:["escape","subst","variable"],r:0},hljs.BE,{cN:"string",b:"`",e:"`",c:["escape"]},{cN:"regexp",b:"(s|tr|y)/(\\\\.|[^/])*/(\\\\.|[^/])*/[a-z]*",e:"^",r:10},{cN:"regexp",b:"(m|qr)?/",e:"/[a-z]*",c:["escape"],r:0},{cN:"string",b:"{\\w+}",e:"^",r:0},{cN:"string",b:"-?\\w+\\s*\\=\\>",e:"^",r:0},{cN:"sub",b:"\\bsub\\b",e:"(\\s*\\(.*?\\))?[;{]",l:[hljs.IR],k:{sub:1},r:5},{cN:"operator",b:"-\\w\\b",e:"^",r:0},hljs.HCM,{cN:"comment",b:"^(__END__|__DATA__)",e:"\\n$",r:5},{cN:"pod",b:"\\=\\w",e:"\\=cut"}]}}();hljs.LANGUAGES.java={dM:{l:[hljs.UIR],c:["javadoc","comment","string","class","number","annotation"],k:{"false":1,"synchronized":1,"int":1,"abstract":1,"float":1,"private":1,"char":1,"interface":1,"boolean":1,"static":1,"null":1,"if":1,"const":1,"for":1,"true":1,"while":1,"long":1,"throw":1,strictfp:1,"finally":1,"protected":1,"extends":1,"import":1,"native":1,"final":1,"implements":1,"return":1,"void":1,"enum":1,"else":1,"break":1,"transient":1,"new":1,"catch":1,"instanceof":1,"byte":1,"super":1,"class":1,"volatile":1,"case":1,assert:1,"short":1,"package":1,"default":1,"double":1,"public":1,"try":1,"this":1,"switch":1,"continue":1,"throws":1}},m:[{cN:"class",l:[hljs.UIR],b:"(class |interface )",e:"{",i:":",k:{"class":1,"interface":1},c:["inheritance","title"]},{cN:"inheritance",b:"(implements|extends)",e:"^",nM:true,l:[hljs.IR],k:{"extends":1,"implements":1},r:10},{cN:"title",b:hljs.UIR,e:"^"},{cN:"params",b:"\\(",e:"\\)",c:["string","annotation"]},hljs.CNM,hljs.ASM,hljs.QSM,hljs.BE,hljs.CLCM,{cN:"javadoc",b:"/\\*\\*",e:"\\*/",c:["javadoctag"],r:10},{cN:"javadoctag",b:"@[A-Za-z]+",e:"^"},hljs.CBLCLM,{cN:"annotation",b:"@[A-Za-z]+",e:"^"}]};