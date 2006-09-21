var QuiX = {};

QuiX.addEvent = function(el, type, proc) {
	if (el.addEventListener) {
		el.addEventListener(type.slice(2,type.length), proc, false);
		return true;
	} else if (el.attachEvent) {
		return el.attachEvent(type, proc);
	}
}

QuiX.removeEvent = function(el, type, proc) {
	if (el.removeEventListener) {
		el.removeEventListener(type.slice(2,type.length), proc, false);
		return true;
	} else if (el.detachEvent) {
		return el.detachEvent(type, proc);
	}
}

QuiX.sendEvent = function(el, module, type /*, args*/) {
	if (el.dispatchEvent) {
		if (!document.implementation.hasFeature(module,""))
			return false;
		var e = document.createEvent(module);
		e.initEvent(type.slice(2,type.length), true, false/*, args */);
		el.dispatchEvent(e);
		return true;
	} else if (el.fireEvent) {
		return el.fireEvent(type);
	}
}

QuiX.stopPropag = function(evt) {
	if (evt && evt.stopPropagation) evt.stopPropagation();
	else if (window.event) window.event.cancelBubble = true;
}

QuiX.cancelDefault = function(evt) {
	if (evt && evt.preventDefault) evt.preventDefault();
	else if (window.event) window.event.returnValue = false;
}

QuiX.XMLHttpRequest = function() {
	if (window.XMLHttpRequest)
		return new XMLHttpRequest;
	else if (window.ActiveXObject)
		return new ActiveXObject("microsoft.xmlhttp");
	else
		return null;
}
