/************************
Timer widget
************************/

function Timer(params) {
	params = params || {};

	this.base = Widget;
	this.base(params);
	
	this.div.style.cursor = 'default';
	
	this._timerid = null;
	this.timeout = null;
	this.interval = null;
	
	this.handler = params.handler;
	
	if (params.timeout)
		this.timeout = parseInt(params.timeout);
	else if (params.interval)
		this.interval = parseInt(params.interval);

	this.auto = (params.auto==true || params.auto=='true');
	if (this.auto) {
		if (this.interval) {
			var h = QuiX.getEventListener(this.handler);
			if (h)
				h(this);
		}
		this.start();
	}
}

QuiX.constructors['timer'] = Timer;
Timer.prototype = new Widget;

Timer.prototype.start = function() {
	if (!this._timerid) {
		var oTimer = this;
		var handler_func = QuiX.getEventListener(this.handler);
		var _handler = function() {
			if (oTimer.timeout) {
				this._timerid = null;
			}
			if (handler_func)
				handler_func(oTimer);
		}
		if (this.timeout)
			this._timerid = window.setTimeout(_handler, this.timeout);
		else
			this._timerid = window.setInterval(_handler, this.interval);
	}
}

Timer.prototype.stop = function() {
	if (this._timerid) {
		if (this.timeout)
			window.clearTimeout(this._timerid);
		else
			window.clearInterval(this._timerid);		
		this._timerid = null;
	}
}

Timer.prototype._detachEvents = function() {
	this.stop();
	Widget.prototype._detachEvents(this);
}
