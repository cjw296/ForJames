
;
(function(window, ko, $){
	
var NEXT_REQUEST_ID = 0;
var RECONNECT_TIME_DEFAULT = 3000;
var RECONNECT_TIME = RECONNECT_TIME_DEFAULT;
var RECONNECT_TIMEOUT = null;
var _response_callbacks_ = [];

function _get_next_request_id_(callback){
	NEXT_REQUEST_ID = NEXT_REQUEST_ID + 1;
	_response_callbacks_.push([NEXT_REQUEST_ID, callback]);
	return NEXT_REQUEST_ID;
};

function _reconnect_(callback){
	RECONNECT_TIMEOUT = setTimeout(function(){ 
		RECONNECT_TIMEOUT = null;
		callback();
	}, RECONNECT_TIME);
	RECONNECT_TIME = RECONNECT_TIME + RECONNECT_TIME;
};

function _reconnected_(){
	if(RECONNECT_TIMEOUT !== null){
		clearTimeout(RECONNECT_TIMEOUT);
		RECONNECT_TIMEOUT = null;
	}
};

function Appl(){
	var that = this;
	this._sock_ = null;

	this._status_ = ko.observable();
	this._error_ = ko.observable();
	this._broadcast_ = ko.observable();
	this._broadcast_.subscribe(function(value){
		that.broadcast(value);
	});
	this.initialize();
}

Appl.prototype.request_response = function(method,kwargs,callback){
	var request_id = _get_next_request_id_(callback);
	var message = {"method": method, "kwargs": kwargs || {}, "request_id": request_id};
	this._sock_.send(JSON.stringify(message));
};

Appl.prototype.connect = function(){
	var that = this;
	_reconnected_();
	this._status_("connecting...");
	/*
	var protocol = document.location.protocol == "https:"? "https://" : "http://";
	this._sock_ = new SockJS(protocol + document.domain + ":" + document.location.port + '/sockjs');
	*/
	var protocol = document.location.protocol == "https:"? "wss://" : "ws://";
	this._sock_ = new WebSocket(protocol + document.domain + ":" + document.location.port + '/websocket');
	this._sock_.onopen = function() {
		that._status_("connected");
		that.connected();
	};
	this._sock_.onmessage = function(e) {
		var message = JSON.parse(e.data);
		var callback = null;
		for(var i=0; i < _response_callbacks_.length; i++){
			if(_response_callbacks_[i][0]==message.request_id){
				callback = _response_callbacks_[i][1];
				_response_callbacks_.splice(i,1);
				break;
			}
		}
		if(callback){
			callback.call(this, message);
		} else {
			that._broadcast_(message);
		}
	};
	this._sock_.onclose = function() {
		that._status_("disconnected");
		that.disconnected();
		that._status_('reconnecting in ' + (RECONNECT_TIME/1000) + ' secs');
		_reconnect_(function(){that.connect()});
	};
	this._sock_.onerror = function(evt) {
		that._error_(evt);
	};
};

Appl.prototype.wrap = function(name){
	/*
	 * utility function to wrap a function of this object
	 * so that ko can bind it with a closure containing this
	 * as a that variable.
	 */
	var that = this;
	var fn_args = [].splice.call(arguments,1);
	return function(){
		var args = fn_args.concat([].splice.call(arguments,0));
		return that[name].apply(that,args);
	};
};

Appl.prototype.default_key = function(func){
	return function(d,e){
		if(e.keyCode===13){
			func();
			return false;
		}
		return true;
	}
};

/*** generated method to control here, server-side ***/

{% for method in description %}
Appl.prototype.{{ method["name"] }} = function(callback{{ ', ' if method['args'] else '' }}{{ ', '.join(method['args']) }}){
	this.request_response('{{ method["name"] }}',{ {% for arg in method["args"] %}
			{{arg}}: {{arg}},{% end %} 
		},callback);
};
Appl.prototype.{{ method["name"] }}.docs = "{{ method.get("docs").replace('\n',' ') if method.get("docs") else '' }}";
{% end %}


/** these get over-written for workflow **/

Appl.prototype.initialize = function(){};	

Appl.prototype.connected = function(){};

Appl.prototype.disconnected = function(){};

Appl.prototype.broadcast = function(){};



window['Appl'] = Appl;

}.call({},window, ko, jQuery));
