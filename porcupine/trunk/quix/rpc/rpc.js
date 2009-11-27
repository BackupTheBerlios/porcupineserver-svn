//==============================================================================
//  Copyright 2005-2009 Tassos Koutsovassilis and contributors
//
//  This file is part of Porcupine.
//  Porcupine is free software; you can redistribute it and/or modify
//  it under the terms of the GNU Lesser General Public License as published by
//  the Free Software Foundation; either version 2.1 of the License, or
//  (at your option) any later version.
//  Porcupine is distributed in the hope that it will be useful,
//  but WITHOUT ANY WARRANTY; without even the implied warranty of
//  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
//  GNU Lesser General Public License for more details.
//  You should have received a copy of the GNU Lesser General Public License
//  along with Porcupine; if not, write to the Free Software
//  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
//==============================================================================

QuiX.rpc = {};

QuiX.rpc._cache = (function() {
    if (QuiX.persist && QuiX.persist.type) {
        var cache = new QuiX.persist.Store('rpccache');
        return {
            get : function(key, callback) {
                cache.get(key,
                    function(ok, value){
                        if (value) {
                            value = unescape(value);
                            var _pos = value.indexOf('_');
                            callback([value.substring(0, _pos),
                                      value.substring(_pos + 1)]);
                        }
                        else
                            callback(null);
                    });
            },
            set : function(key, etag, response) {
                var value = escape(etag + '_' + response);
                if (!QuiX.persist.size || QuiX.persist.size < 0 ||
                        QuiX.persist.size > value.length) {
                    cache.set(key, value);
                }
            }
        }
    }
    else
        return null;
})();

QuiX.rpc.BaseRPCRequest = function(url /*, async*/) {
    if (url) {
        this.async = arguments[1] || true;
        this.url = url;
        this.xmlhttp = QuiX.XHRPool.getInstance();

        this.onreadystatechange = null;
        this.oncomplete = null;
        this._cached = null;

        this.callback_info = null;
        this.response = null;
        this.use_cache = true;
    }
}

QuiX.rpc.BaseRPCRequest.prototype._contentType = 'text/plain';

QuiX.rpc.BaseRPCRequest.prototype._processResult = function(/*str*/) {
}

QuiX.rpc.BaseRPCRequest.prototype._buildRequestBody =
function(method_name /*, arg1, arg2, ...*/) {
}

QuiX.rpc.BaseRPCRequest.prototype._validateMethodName = function(mname) {
    return true;
}

QuiX.rpc.BaseRPCRequest.prototype.onerror = function(e) {
    QuiX.displayError(e);
}

QuiX.rpc.BaseRPCRequest.prototype.callmethod =
function(method_name /*, arg1, arg2, ...*/) {
    try {
        if (this._validateMethodName(method_name)) {
            var argsArray, key;
            var request = this._buildRequestBody.apply(this, arguments);

            if (this.use_cache) {
                argsArray = Array.prototype.concat.apply([], arguments);
                key = QuiX.utils.hashlib.hex_md5(
                    this.url + QuiX.parsers.JSON.stringify(argsArray));
            }

            QuiX.addLoader();
            this.xmlhttp.open('POST', this.url, this.async);
            this.xmlhttp.setRequestHeader('Content-type', this._contentType);

            var self = this;
            this.xmlhttp.onreadystatechange = function() {
                if (self.xmlhttp.readyState == 4) {
                    var retVal = null;
                    var status = self.xmlhttp.status;
                    // parse response...
                    try {
                        if (status == 304 || status == 0) { //Not modified
                            retVal = self._processResult(self._cached);
                        }
                        else {
                            retVal = self._processResult();
                            var etag = self.xmlhttp.getResponseHeader('Etag');
                            if (QuiX.rpc._cache && etag) {
                                QuiX.rpc._cache.set(key,
                                    etag, self.xmlhttp.responseText);
                            }
                        }
                        if (retVal != null && self.oncomplete) {
                            self.response = retVal;
                            self.oncomplete(self);
                        }
                    }
                    catch(e) {
                        self.onerror(e);
                    }
                    finally {
                        QuiX.removeLoader();
                        QuiX.XHRPool.release(self.xmlhttp);
                        self._cached = null;
                    }
                }
                else {
                    if (self.onreadystatechange)
                        self.onreadystatechange(self);
                }
            }

            if (QuiX.rpc._cache && this.use_cache) {
                QuiX.rpc._cache.get(key, function(val) {
                    if (val != null) {
                        self.xmlhttp.setRequestHeader("If-None-Match", val[0]);
                        self._cached = val[1];
                    }
                    self.xmlhttp.send(request);
                });
            }
            else
                self.xmlhttp.send(request);
        }
        else
            throw new QuiX.Exception('QuiX.rpc.BaseRPCRequest.callMethod',
                                     'Invalid RPC method name "' +
                                     method_name + '"');
	}
    catch (e) {
        QuiX.removeLoader();
        this.onerror(e);
    }
}