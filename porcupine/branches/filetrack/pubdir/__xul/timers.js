function Timer(params) {
	params = params || {};

	this.base = Widget;
	this.base(params);
	
	this.div.style.cursor = 'default';
	
	this._timerid = null;
	this.timeout = null;
	this.interval = null;
	
	this.handler = getEventListener(params.handler);
	if (!this.handler)
		throw new QuiX.Exception("Timer Error", "Timer handler function not defined");
	
	if (params.timeout)
		this.timeout = parseInt(params.timeout);
	else if (params.interval)
		this.interval = parseInt(params.interval);
	else
		throw new QuiX.Exception("Timer Error", "Timer should define a timeout or an interval");

	if (params.auto==true || params.auto=='true') {
		if (this.interval) {
			this.handler(this);
		}
		this.start();
	}
}

Timer.prototype = new Widget;

Timer.prototype.start = function() {
	if (!this.timerid) {
		var oTimer = this;
		var _handler = function() {
			if (oTimer.timeout) {
				this._timerid = null;
			}
			oTimer.handler(oTimer);
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
