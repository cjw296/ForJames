
Appl.prototype.initialize = function(){
	/** customize the constructor **/
	this.model = {
		colours: ko.observableArray(),
		colour_entry: ko.observable('')
	};
};

Appl.prototype.opened = function(){
	/** customize the connected **/
	this.colours();
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
	if(message.method=='colours'){
		this.model.colours(message.result);
	}
	else if(message.signal == 'voted'){
		
		var item = message.message;
		var colours = this.model.colours;
		for(var i=0; i < colours().length;i++){
			if(colours()[i][0]==item.id){
				colours.splice(i,1,[item.id,
				                    item.name,
				                    item.votes]);
				break;
			}
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
