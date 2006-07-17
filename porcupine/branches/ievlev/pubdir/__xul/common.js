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

// GroupBox
function GroupBox(params)
{
	params = params || {};
	params.overflow = 'hidden';
	this.base = Widget;
	this.base(params);
	this.div.className = 'groupbox';
	
	this.border = new Widget({
		top: 8,
		width:"100%",
		padding:"8,8,8,8",
		height: "this.parent.getHeight()-this.getTop()",
		border: params.border || 2
	});
	this.border.div.className = "groupboxframe";
	this.appendChild(this.border);

	this.caption = new Label({
		left:5,
		bgcolor: params.bgcolor,
		caption: params.caption
	});
	this.appendChild(this.caption);
	this.caption.div.className = this.div.className;

	this.body = new Widget({
		width: "100%",
		height: "100%"
	});
	this.border.appendChild(this.body);
}

GroupBox.prototype = new Widget;

GroupBox.prototype.setBgColor = function(color) {
	Widget.prototype.setBgColor(color,this);
	this.caption.setBgColor(color);
}