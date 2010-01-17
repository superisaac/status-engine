
function format(fmt) {
    for(var i=1; i<arguments.length; i++) {
	fmt = fmt.replace('%s', arguments[i]);
    }
    return fmt;
}

function warn(word) {
    $('#warning').html(word).show();
}

function deleteAttachment(link) {
    $(link).parents('li').remove();
    updateAttachmentInput();
}

function deleteIconHtml() {
    var html = '';
    html += '<a href="#" onclick="deleteAttachment(this); return false;">';
    html += '<img src="/static/pics/delete.png" title="delete">';
    html += '</a>';
    return html;
}


function newAttachmentLi(url, tp) {
    var li = $('<li/>').addClass(tp);
    return li;
}

function updateBlip() {
    var v = $('#id_text', this).val().trim();
    if(v) {
	return true;
    } else {
	return false;
    }
}

function createAttach(dock, attachment_url, description) {
    var a = attachment_url.split('::');
    var tp = a[0];
    var url = a[1];
    if(tp == 'image') {
	var t = $('<img>').attr('src', url).addClass('attach-image');
	var li = newAttachmentLi(url, 'image');
	var anchor = $('<a/>').attr('href', t.attr('src'));
	anchor.attr('target', '_blank');
	anchor.attr('title', t.attr('src'));
	li.append(anchor.append(t));
	$(dock).empty().append(li);
    } else if(tp == 'flash') {
	var t = $(format('<embed type="application/x-shockwave-flash" src="%s"/>',
	    url));
	// TODO check type
	t.attr('quality', 'high');
	t.attr('width', '360');
	t.attr('height', '300');
	t.attr('align', 'middle');
	t.attr('allowScriptAccess', 'sameDomain');
	var li = newAttachmentLi(url, 'flash');
	li.append(t);
	$(dock).empty().append(li);
    } else if(tp == 'map') {
	if(description) {
	    url += '&description=' + description;
	}
	var t = $(format('<iframe class="map" src="%s"></iframe>', url));	
	// TODO check class
	t.attr('width', 360);
	t.attr('height', 360);
	t.attr('noresize', 'noresize');
	t.attr('frameborder', '0');
	t.attr('scrolling', 'no');
	var li = newAttachmentLi(url, 'map');
	li.append(t);
	$(dock).empty().append(li);
    }
}
