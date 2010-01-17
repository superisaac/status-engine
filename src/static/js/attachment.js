
function AttachEditor() {
    this.kind = null;
}

AttachEditor.prototype.showDialog = function(anchor, kind) {
    this.kind = kind;
    this.url = '';
    var href=$(anchor).attr('href');

    if(kind == 'image' || kind == 'flash') {
	$('#attachment-stage').empty().append($(href).clone().show());
    } else if(kind == 'map') {
	var div = $(href).clone();
	$('iframe', div).attr('src', '/map/edit');
	$('#attachment-stage').empty().append(div.show());
    }
}

AttachEditor.prototype._prepareMapParams = function(form) {
    var editor = $('#attachment-stage iframe#map-edit');
    var lat = parseFloat(editor.contents().find('#selected_lat').html());
    var lng = parseFloat(editor.contents().find('#selected_lng').html());
    var zoomLevel = parseInt(editor.contents().find('#selected_zoom_level').html());
    if(!isNaN(lat) && !isNaN(lng)) {
	var mapUrl = format('/map?lat=%s&lng=%s&zoom_level=%s', lat, lng, zoomLevel);
	return mapUrl;
    } else {
	warn("Illegal latitude or longitude");
    }
}

AttachEditor.prototype.attachUrl = function(url) {
    var fullUrl = this.kind + '::' + url;
    createAttach('ul#attachments', fullUrl);
    $('input#id_attachment').val(fullUrl);
}

AttachEditor.prototype.dialogSubmit = function(form) {
    if(this.kind == 'image' || this.kind == 'flash') {
	var url = $('#url', form).val().trim();
	if(/^https?:\/\/\S+$/.test(url)) {
	    this.attachUrl(url);
	}
    } else if(this.kind == 'map') {
	var mapUrl = this._prepareMapParams(form);
	console.info(mapUrl);
	if(mapUrl) {
	    this.attachUrl(mapUrl);
	}
    }
    $('#attachment-stage').empty();
}
