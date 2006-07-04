// horizontal rule
function HR(params) {
	params = params || {};
	this.base = Widget;
	params.border = params.border || 1;
	params.height = params.height || 2;
	params.overflow = 'hidden';
	this.base(params);
	this.div.className = 'separator';
}

HR.prototype = new Widget;
