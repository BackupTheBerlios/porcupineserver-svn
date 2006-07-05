/************************
IFrame integration to QuiX framework
************************/
function IFrame(params) {
	params = params || {};
	params.overflow = 'hidden';
	this.base = Widget;
	this.base(params);
	this.div.className = 'ifrm';
	var frame = ce("IFRAME");
	frame.src = params.src || "";
	frame.style.width="100%";
	frame.style.height="100%";
	this.div.appendChild(frame);
}

IFrame.prototype = new Widget;

IFrame.prototype.setSource = function(src)
{
	this.div.firstChild.src = src;
}
