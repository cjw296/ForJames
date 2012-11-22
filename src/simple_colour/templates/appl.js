
function Appl(){
	var that = this;
	this._sock_ = null;
	this._response_callbacks_ = [];
	this._id_seed_ = 0;
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

Appl.prototype.connect = function(){
	var that = this;
	/*
	var protocol = document.location.protocol == "https:"? "https://" : "http://";
	this._sock_ = new SockJS(protocol + document.domain + ":" + document.location.port + '/sockjs');
	*/
	var protocol = document.location.protocol == "https:"? "wss://" : "ws://";
	this._sock_ = new WebSocket(protocol + document.domain + ":" + document.location.port + '/websocket');
	this._sock_.onopen = function() {
		console.log('open');
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
		console.log('close');
		that.closed();
	};
	this._sock_.onerror = function(evt) {
		console.log(evt);
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

/*** generated method to control here ***/

{% for method in description %}
Appl.prototype.{{ method["name"] }} = function(callback{{ ', ' if method['args'] else '' }}{{ ', '.join(method['args']) }}){
	this.request_response('{{ method["name"] }}',{ {% for arg in method["args"] %}
			{{arg}}: {{arg}},{% end %} 
		},callback);
};
Appl.prototype.{{ method["name"] }}.docs = "{{ method.get("docs").replace('\n',' ') if method.get("docs") else '' }}";
{% end %}
