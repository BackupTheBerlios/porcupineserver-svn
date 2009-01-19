/************************
Effect widget
************************/
function Effect(params) {
	params = params || {};
	params.display = 'none';
	params.handler = Effect__play;
	params.interval = params.interval || 50;
	
	this.type = params.type;
	switch (this.type) {
		case 'fade-in':
			this.begin = parseFloat(params.begin) || 0.0;
			this.end = parseFloat(params.end) || 1.0;
			break;
		case 'fade-out':
			this.begin = parseFloat(params.begin) || 1.0;
			this.end = parseFloat(params.end) || 0.0;
			break;
		case 'wipe-out':
			this.direction = params.direction || 'n';
			this.begin = parseFloat(params.begin) || 1.0;
			this.end = parseFloat(params.end) || 0.0;
			break;
		case 'wipe-in':
			this.direction = params.direction || 's';
			this.begin = parseFloat(params.begin) || 0.0;
			this.end = parseFloat(params.end) || 1.0;
			break;
		case 'slide-y':
		case 'slide-x':
			this.begin = params.begin || '100%';
			this.end = params.end || 0;
			break;
			
	}
	this.steps = parseInt(params.steps) || 5;
	this._step = 0;
	this._reverse = false;
	this.base = Timer;
	this.base(params);
}

QuiX.constructors['effect'] = Effect;
Effect.prototype = new Timer;

Effect.prototype.customEvents = 
	Timer.prototype.customEvents.concat(['oncomplete']);

Effect.prototype._apply = function(wd) {
	// calculate value
	var value, begin, end;
	var stepping = 0;
	switch (this.type) {
		case 'slide-x':
		case 'slide-y':
			var f = (this.type=='slide-x')?'_calcLeft':'_calcTop';
			var v = (this.type=='slide-x')?'left':'top';
			this.parent[v] = this.begin;
			begin = this.parent[f]();
			this.parent[v] = this.end;
			end = this.parent[f]();
			break;
		default:
			begin = this.begin;
			end = this.end;
	}
	
	if (this._reverse) {
		var tmp = begin;
		begin = end;
		end = tmp;
	}
	
	stepping = (end - begin) / this.steps;
	if (this._step == this.steps) {
		if (this._reverse)
			value = this.begin;
		else
			value = this.end;
	}
	else
		value = begin + (stepping * this._step);
	
	// apply value
	switch (this.type) {
		case 'fade-in':
		case 'fade-out':
			wd.setOpacity(Math.round(value * 100) / 100);
			break;
		case 'wipe-in':
			switch (this.direction) {
				case 's':
					var h = wd._calcHeight(true);
					wd.div.style.clip = 'rect(auto,auto,' +
										parseInt(h * value) + 'px,auto)';
					break;
				case 'e':
					var w = wd._calcWidth(true);
					wd.div.style.clip = 'rect(auto,' +
										parseInt(w * value) + 'px,auto,auto)';
					break;
				
			}
			break;
		case 'wipe-out':
			if (this.direction == 'n') { 
				var h = wd.getHeight(true);
				wd.div.style.clip = 'rect(auto,auto,' +
									parseInt(h * value) + 'px,auto)';
			}
			break;
		case 'slide-x':
			wd.moveTo(value, wd.top);
			break;
		case 'slide-y':
			wd.moveTo(wd.left, value);
	}
	this._step++;
}

Effect.prototype.stop = function() {
	if (this._timerid) {
		Timer.prototype.stop.apply(this, arguments);
		switch (this.type) {
			case 'wipe-in':
				var ev = this._reverse?this.begin:this.end;
				if (ev==1)
					if (QuiX.browser == 'ie')
						this.parent.div.style.clip = 'rect(auto,auto,auto,auto)';
					else
						this.parent.div.style.clip = '';
		}
		this._step = 0;
		if (this._customRegistry.oncomplete)
			this._customRegistry.oncomplete(this);
	}
}

Effect.prototype.show = function() {}

Effect.prototype.play = function(reverse) {
	this._reverse = reverse;
	Effect__play(this);
	if (this.parent) this.start();
}

function Effect__play(effect) {
	var w = effect.parent;
	if (w) {
		effect._apply(w);
		if (effect._step > effect.steps)
			effect.stop();
	}
}
