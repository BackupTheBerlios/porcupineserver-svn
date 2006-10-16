/************************
File Control
************************/
function FileInfo() {
	this.filename = '';
	this.id = '';
	this.temp_file = '';
}

function File(params) {
	params = params || {};

	params.height = params.height || 20;
	this.name = params.name;
	this.filename = params.filename;
	this.size = params.size || 0;

	this._tmpfile = '';
	this._fileid = null;
	this.href = params.href;
	
	this.cancelUpload = false;
	this.readonly = (params.readonly=='true')?true:false;

	params.caption = '...';
	params.type = 'menu';

	this.base = FlatButton;
	this.base(params);
	
	if (this.filename) this.setCaption(this._getCaption());
	
	var oFile = this;
	
	this.contextMenu.addOption({ img:'__quix/images/upload.gif', caption:'Upload file', onclick: function(evt, w){oFile.showUploadDialog()} });
	this.contextMenu.addOption({ img:'__quix/images/download.gif', caption:'Download file', onclick: function(evt, w){oFile.openDocument()} });
	
	if (!this.href) this.contextMenu.options[1].disabled = true;
	if (this.readonly)
		this.contextMenu.options[0].disabled = true;
	else {
		//TODO: applet is depreciated. use object instead
		var applet = document.getElementById('_uploaderapplet');
		if (!applet) {
			applet = ce('APPLET');
			applet.id = '_uploaderapplet';
			applet.code = 'ReadFile.class';
			applet.archive = "__quix/ReadFile.jar";
			applet.style.width = "1px";
			applet.style.height = "1px";
			applet.style.visibility = 'hidden';
			document.body.appendChild(applet);
		}
		this.uploader = applet;
	}
}

File.prototype = new FlatButton;

File.prototype.openDocument = function() {
	window.location.href = this.href;
/*
	if (QuiX.browser=='ie')
		window.open(this.href, null, 'location=0,status=0,toolbar=0,menubar=1');
	else
		window.open(this.href, this.filename, 'menubar');
*/
}

File.prototype.showUploadDialog = function() {
	var fileName = this.uploader.selectFiles(false);
	if (fileName != '') {
		this.setFile(new String(fileName));
		this.onbeginupload(this);
		this.upload();
	}
}

File.prototype.onbeginupload = function(filecontrol) {
	var oWin = filecontrol.getParentByType(Window);
	oWin.showWindowFromString('<a:dialog xmlns:a="http://www.innoscript.org/quix"'+
		' title="' + filecontrol.contextMenu.options[0].caption + '"' +
		' width="240" height="100" left="center" top="center">' +
		'<a:wbody>' +
		'<a:progressbar width="90%" height="24" left="center" top="center" ' +
		'maxvalue="' + filecontrol.size + '">' +
		'<a:label align="center" width="100%" height="100%" caption="0%">' +
		'</a:label></a:progressbar>' +
		'</a:wbody>' +
		'<a:dlgbutton width="70" height="22" caption="CANCEL"></a:dlgbutton>' +
		'</a:dialog>',
		function(w) {
			var progressDialog = w;
			filecontrol.attributes.pbar = progressDialog.getWidgetsByType(ProgressBar)[0]
			progressDialog.buttons[0].attachEvent('onclick',
				function (evt, w) {
					filecontrol.cancelUpload = true;
					progressDialog.close();
				}
			);
		}
	);
}

File.prototype.onstatechange = function(filecontrol) {
	var bytes = filecontrol.uploader.getBytesRead(filecontrol._fileid);
	var pbar = filecontrol.attributes.pbar;
	pbar.setValue(bytes);
	pbar.widgets[1].setCaption(parseInt((bytes/pbar.maxvalue)*100) + '%');
}

File.prototype.oncomplete = File.prototype.onerror = function(filecontrol) {
	filecontrol.attributes.pbar.getParentByType(Dialog).close();
}

File.prototype._getCaption = function() {
	return '<b>' + this.filename  + '</b>&nbsp;' +
		'(' + parseInt(this.size/1024) + 'KB)&nbsp;&nbsp;';
}

File.prototype.setFile = function(path) {
	this._fileid = this.uploader.setFile(path);
	this.filename = this.getFileName(path);
	this.size = this.uploader.getFileSize(this._fileid);
	this.cancelUpload = false;
}

File.prototype.getFileName = function(path) {
	path = path.replace(/\\/g, '/');
	var arrPath = path.split('/');
	return(arrPath[arrPath.length-1]);
}

File.prototype.getValue = function() {
	return {
		filename: this.filename,
		tempfile: this._tmpfile
	};
}

File.prototype.saveTextFile = function(fname, text) {
	this.uploader.saveFile(fname, text);
}

File.prototype.upload = function() {
	var ch_size = parseInt((this.size/20)/8192) * 8192;
	if (ch_size<8192) ch_size = 8192;
	if (ch_size>65536) ch_size = 65536;
	this.uploader.ChunkSize = ch_size;
	var chunk = this.uploader.getChunk(this._fileid);
	this._upload(chunk, false);
}

File.prototype._upload = function(chunk, fname) {
	var oFile = this;
	var xmlrpc = new XMLRPCRequest(QuiX.root);
	xmlrpc.oncomplete = function(req) {
		if (!oFile.cancelUpload) {
			var chunk = oFile.uploader.getChunk(oFile._fileid);
			var filename = req.response;
			if (chunk!='' && chunk!=null) {
				if (oFile.onstatechange) oFile.onstatechange(oFile);
				oFile._upload(chunk, filename);
			}
			else {
				oFile.setCaption(oFile._getCaption());
				oFile._tmpfile = filename;
				if (oFile.oncomplete) oFile.oncomplete(oFile);
			}
		} else {
			oFile.cancelUpload = false;
		}
	}
	xmlrpc.onerror = function(req) {
		if (oFile.onerror) oFile.onerror(oFile);
	}
	xmlrpc.callmethod('upload', new String(chunk), fname);
	delete chunk;
}

//multiple file uploader
function MultiFile(params) {
	params = params || {};
	this.name = params.name;
	this.method = params.method;
	this.readonly = (params.readonly=='true')?true:false;

	this.base = Widget;
	this.base(params);

	this.selectlist = new SelectList(
		{
			width: '100%',
			height: 'this.parent.getHeight()-24',
			ondblclick: this.downloadFile
		});
	this.appendChild(this.selectlist);
	
	this.removeButton = new FlatButton(
		{
			width: 24, height: 24,
			img: '__quix/images/remove16.gif',
			top: 'this.parent.getHeight()-24',
			left: 'this.parent.getWidth()-24',
			disabled: this.readonly
		});
	this.appendChild(this.removeButton);
	this.addButton = new FlatButton(
		{
			width: 24, height: 24,
			img: '__quix/images/add16.gif',
			top: 'this.parent.getHeight()-24',
			left: 'this.parent.getWidth()-48',
			disabled: this.readonly
		});
	this.appendChild(this.addButton);
	var oMultiFile = this;
	if (!this.readonly) {
		this.filecontrol = new File();
		this.appendChild(this.filecontrol);
		this.filecontrol.div.style.visibility = 'hidden';
		this.filecontrol.onstatechange = this.statechange;
		this.filecontrol.oncomplete = this.filecontrol.onerror = this.onfilecomplete;
		this.addButton.attachEvent('onclick', function(evt, w) { oMultiFile.showUploadDialog(evt, w); });
		this.removeButton.attachEvent('onclick', function() { oMultiFile.removeSelectedFiles(); });
	}
	this.files = [];
}

MultiFile.prototype = new Widget;

MultiFile.prototype.showUploadDialog = function(evt, w) {
	var file_size;
	var filenames = this.filecontrol.uploader.selectFiles(true);
	
	if (filenames != '') {
		var oWin = this.getParentByType(Window);
		var fileid;
		var files = new String(filenames).split(';');
		files = files.slice(0, files.length-1).reverse();
		this.files4upload = [];
		total_size = 0;
		for (var i=0; i<files.length; i++) {
			fileid = this.filecontrol.uploader.setFile(files[i]);
			file_size = this.filecontrol.uploader.getFileSize(fileid);
			this.files4upload.push({
				path: files[i],
				filename: this.filecontrol.getFileName(files[i]),
				size: file_size
			});			
			total_size += file_size;
			this.filecontrol.uploader.closeFile(fileid);
		}
		
		this.current_file = this.files4upload.pop();
		this.filecontrol.setFile(this.current_file.path);
		this._tmpsize = this.current_file.size;
		
		var oMultiFile = this;
		oWin.showWindowFromString(
			'<a:dialog xmlns:a="http://www.innoscript.org/quix"'+
			' title="' + this.filecontrol.contextMenu.options[0].caption + '"' +
			' width="240" height="140" left="center" top="center">' +
			'<a:wbody>' +

			'<a:progressbar width="90%" height="24" left="center" top="20" ' +
			'maxvalue="' + total_size + '">' +
			'<a:label align="center" width="100%" height="100%" caption="' + this.current_file.filename + '">' +
			'</a:label></a:progressbar>' +

			'<a:progressbar width="90%" height="24" left="center" top="50" ' +
			'maxvalue="' + this.current_file.size + '">' +
			'<a:label align="center" width="100%" height="100%" caption="0%">' +
			'</a:label></a:progressbar>' +

			'</a:wbody>' +
			'<a:dlgbutton width="70" height="22" caption="CANCEL"></a:dlgbutton>' +
			'</a:dialog>',
			function (w) {
				oMultiFile.filecontrol.attributes.pbar1 = w.getWidgetsByType(ProgressBar)[0];
				oMultiFile.filecontrol.attributes.pbar2 = w.getWidgetsByType(ProgressBar)[1];
				oMultiFile.filecontrol.attributes.bytesRead = 0;
				w.buttons[0].attachEvent('onclick',
					function (evt, w) {
						oMultiFile.filecontrol.cancelUpload = true;
						w.getParentByType(Dialog).close();
					}
				);
				oMultiFile.filecontrol.upload();
			}
		);
	}
	QuiX.stopPropag(evt);
}

MultiFile.prototype.removeSelectedFiles = function() {
	this.selectlist.removeSelected();
	this.files = [];
	var opts = this.selectlist.options;
	for (var i=0; i<opts.length; i++) {
		this.files.push(opts[i].attributes.fileinfo);
	}
}

MultiFile.prototype.getValue = function() {
	return(this.files);
}

MultiFile.prototype.addFile = function(params) {
	var oFileInfo = new FileInfo();
	
	oFileInfo.id = params.id || '';
	oFileInfo.filename = params.filename;
	oFileInfo.temp_file = params.tmpfile || '';
	var fileimage = params.img || '__quix/images/document.gif';
	
	this.files.push(oFileInfo);
	var opt = this.selectlist.addOption({
		caption: oFileInfo.filename,
		value: oFileInfo.id,
		img: fileimage
	});
	
	opt.attributes.fileinfo = oFileInfo;
}

MultiFile.prototype.downloadFile = function(evt, w) {
	if (w.selection.length == 1 && w.selection[0].value)
		window.location.href = QuiX.root + w.selection[0].value + '?cmd=' + w.parent.method;
}

MultiFile.prototype.statechange = function(filecontrol) {
	var bytes = filecontrol.uploader.getBytesRead(filecontrol._fileid);
	var pbar1 = filecontrol.attributes.pbar1;
	var pbar2 = filecontrol.attributes.pbar2;
	
	pbar1.setValue(filecontrol.attributes.bytesRead + bytes);
	
	pbar2.setValue(bytes);
	pbar2.widgets[1].setCaption(parseInt((bytes/pbar2.maxvalue)*100) + '%');
}

MultiFile.prototype.onfilecomplete = function(filecontrol) {
	var multifile = filecontrol.parent;
	var pbar1 = filecontrol.attributes.pbar1;
	var pbar2 = filecontrol.attributes.pbar2;
	var file = multifile.current_file;
	var remaining_files = multifile.files4upload;
	
	multifile.addFile({
		filename: file.filename,
		tmpfile: filecontrol._tmpfile,
		img:'__quix/images/file_temporary.gif'
	});

	if (remaining_files.length>0) {
		multifile.current_file = remaining_files.pop();
		pbar1.widgets[1].setCaption(multifile.current_file.filename);
		pbar2.setValue(0);
		pbar2.maxvalue = multifile.current_file.size;
		pbar2.widgets[1].setCaption('0%');
		filecontrol.attributes.bytesRead += multifile._tmpsize;

		multifile._tmpsize = multifile.current_file.size;
		filecontrol.setFile(multifile.current_file.path);
		filecontrol.upload();
	} else
		filecontrol.attributes.pbar1.getParentByType(Dialog).close();
}
