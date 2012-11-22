
function Appl(){
	var that = this;
	this._sock_ = null;

	this._RECONNECT_TIME_DEFAULT_ = 3000;
	this._RECONNECT_TIME_ = this._RECONNECT_TIME_DEFAULT_;
	this._RECONNECT_TIMEOUT_ = null;
	this._response_callbacks_ = [];
	this._id_seed_ = 0;
	this._status_ = ko.observable();
	this._error_ = ko.observable();
	this._broadcast_ = ko.observable();
	this._broadcast_.subscribe(function(value){
		that.broadcast(value);
	});
	this.initialize();
}		

Appl.prototype.initialize = function(){};	

Appl.prototype.opened = function(){};

Appl.prototype.closed = function(){};

Appl.prototype.broadcast = function(){};


Appl.prototype.request_response = function(method,kwargs,callback){
	this._id_seed_ = this._id_seed_ + 1;
	this._response_callbacks_.push([this._id_seed_, callback || null]);
	var request_id = this._id_seed_;
	var message = {"method": method, "kwargs": kwargs || {}, "request_id": request_id};
	this._sock_.send(JSON.stringify(message));
};



Appl.prototype._reconnect_ = function(callback){
	var that = this;
	this._RECONNECT_TIMEOUT_ = setTimeout(function(){ 
		that._RECONNECT_TIMEOUT_ = null;
		callback();
	}, this._RECONNECT_TIME_);
	this._RECONNECT_TIME_ = this._RECONNECT_TIME_ + this._RECONNECT_TIME_;
};

Appl.prototype._reconnected_ = function(){
	if(this._RECONNECT_TIMEOUT_ !== null){
		clearTimeout(this._RECONNECT_TIMEOUT_);
		this._RECONNECT_TIMEOUT_ = null;
	}
};

Appl.prototype.connect = function(){
	var that = this;
	this._reconnected_();
	this._status_("connecting...");
	/*
	var protocol = document.location.protocol == "https:"? "https://" : "http://";
	this._sock_ = new SockJS(protocol + document.domain + ":" + document.location.port + '/sockjs');
	*/
	var protocol = document.location.protocol == "https:"? "wss://" : "ws://";
	this._sock_ = new WebSocket(protocol + document.domain + ":" + document.location.port + '/websocket');
	this._sock_.onopen = function() {
		that._status_("connected");
		that.opened();
	};
	this._sock_.onmessage = function(e) {
		var message = JSON.parse(e.data);
		var callback = null;
		for(var i=0; i < that._response_callbacks_.length; i++){
			if(that._response_callbacks_[i][0]==message.request_id){
				callback = that._response_callbacks_[i][1];
				that._response_callbacks_.splice(i,1);
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
		that.closed();
		that._status_('reconnecting in ' + (that._RECONNECT_TIME_/1000) + ' secs');
		that._reconnect_(function(){that.connect()});
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

/*** generated method to control here ***/

{% for method in description %}
Appl.prototype.{{ method["name"] }} = function(callback{{ ', ' if method['args'] else '' }}{{ ', '.join(method['args']) }}){
	this.request_response('{{ method["name"] }}',{ {% for arg in method["args"] %}
			{{arg}}: {{arg}},{% end %} 
		},callback);
};
Appl.prototype.{{ method["name"] }}.docs = "{{ method.get("docs").replace('\n',' ') if method.get("docs") else '' }}";
{% end %}
