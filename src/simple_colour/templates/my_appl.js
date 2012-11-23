
Appl.prototype.initialize = function(){
	/** customize the constructor **/
	var that = this;
	this.model = {
		colours: ko.observableArray(),
		colour_entry: ko.observable(''),
		selected_colour: ko.observable()
	};
	var sorting = false;
	this.model.colours.subscribe(function(){
		if(sorting === false){
			sorting = true;
			that.model.colours.sort(function(b,a){
				return a[2] == b[2] ? 0 : (a[2] < b[2] ? -1 : 1);
			});
			sorting = false;
		}
	});
};

Appl.prototype.connected = function(){
	/** customize the connected **/
	var that = this;
	this.colours(function(message){
		that.model.colours(message.result);
	});
};

Appl.prototype.add_colour_btn = function(){
	/** validate input and call add **/
	var that = this;
	blur();
	if(this.model.colour_entry()){
		this.add_colour(function(){
			that.model.colour_entry('');
		}, this.model.colour_entry());
	}
};

Appl.prototype.broadcast = function(message){
	/** others have been busy **/
	if(message.signal == 'voted'){
		
		var item = message.message;
		var colours = this.model.colours;
		var updated = false;
		for(var i=0; i < colours().length;i++){
			if(colours()[i][0]==item.id){
				colours.splice(i,1,[item.id,
				                    item.name,
				                    item.votes]);
				updated = true;
				break;
			}
		}
		if(updated === false){
			this.model.colours.push([item.id,
			                         item.name,
			                         item.votes]);
		}
	} 
	else if(message.signal == 'colour added'){
		var item = message.message;
		this.model.colours.push([item.id,
		                         item.name,
		                         item.votes]);
	}
};


/** instantiate appl, bind to dom and connect **/
var appl = new Appl();
ko.applyBindings(appl);
appl.connect();
