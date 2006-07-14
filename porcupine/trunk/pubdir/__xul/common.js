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

// iframe
function IFrame(params) {
	params = params || {};
	params.overflow = 'hidden';
	this.base = Widget;
	this.base(params);
	this.div.className = 'ifrm';
	var frame = ce("IFRAME");
	frame.frameBorder = 0;
	frame.src = params.src || "";
	frame.style.width = "100%";
	frame.style.height = "100%";
	this.div.appendChild(frame);
}

IFrame.prototype = new Widget;

IFrame.prototype.setSource = function(src)
{
	this.div.firstChild.src = src;
}

IFrame.prototype.getSource = function() {
	return this.div.firstChild.src;
}