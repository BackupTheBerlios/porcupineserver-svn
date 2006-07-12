/************************
GroupBox widget
************************/

function GroupBox(params)
{
	params = params || {};
	params.overflow = 'hidden';
	this.base = Widget;
	this.base(params);
	this.div.className = 'groupbox';
	this.body = this;
	this.border = new Widget({ top: 10,
	                           width:"100%",
				   padding:"8,8,8,8",
	                           height: "this.parent.getHeight()-this.getTop()",
				   border: params.border || 2
				   });
	this.border.div.className = "groupboxframe";
	this.appendChild(this.border);

	this.caption = new Label( { left:5,
	                            bgcolor: params.bgcolor,
	                            caption: params.caption } );
	this.appendChild(this.caption);
	this.caption.div.className = this.div.className;

	this.body = new Widget( { width: "100%",
				  height: "100%" } );
	this.border.appendChild(this.body);
}

GroupBox.prototype = new Widget;

GroupBox.prototype.setBgColor = function(color) {
	Widget.prototype.setBgColor(color,this);
	this.caption.setBgColor(color);
}
