function updateResourceTags(hosts, userName, apiKey) {
	/* prepare tags and hit the list_endpoint */
	hosts = JSON.parse( hosts );
	$.each( hosts, function( host, listEndpoint ) {
        uri = resourceUri( host, listEndpoint, userName, apiKey );
        divId = 'id-nav-pill-resources';
        makeResourceLinkTags( divId, host, listEndpoint, uri, userName )
    });
}

function makeResourceLinkTags ( divId, host, listEndpoint, uri, userName ) {
	/* make and append links to the API */
    $.each( ['show', 'fetch'], function( index, label ){
	    anchorId = 'id-link-' + label + '-' + host.replace( ':', '-' );
	    var li = '<li><a id="' + anchorId + '">'+ label + ' resource on ' + host + '</a></li>';
    	$( '#id-nav-pill-resources' ).append( li );
	    $( '#id-link-show-' + host.replace( ':', '-' ) ).attr( 'href', uri );
	    $( '#id-link-fetch-' + host.replace( ':', '-' ) ).attr( 'href', '#' );
	    $( '#id-link-fetch-' + host.replace( ':', '-' ) ).click( function (e) {
	        e.preventDefault();
			getData(uri, host, listEndpoint, userName);
	    });
    });
};

function getData( uri, host, listEndpoint, userName ) {
	/* GET all data from the uri until next_uri == null */
	var csrftoken = Cookies.get('csrftoken');
	limit = 3;
	$.ajaxSetup({
	    beforeSend: function(xhr, settings) {
	        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
	            xhr.setRequestHeader("X-CSRFToken", csrftoken);
	        }
	    }
	});	
	$.ajax({
    	url: uri + '&limit=' + limit,
    	type: 'GET',
    	dataType: 'json',
    	processData: false,
    	success: function( result, status, xhr ) {
			console.log(result.meta);
			$( '#id-resource-alert' ).remove();
			alert_div = makeHostAlert( 'id-resource-alert', host, 'alert-success' );
			$( '#id-div-resource-alert' ).append( alert_div );
    		$( '#id-resource-alert' ).removeClass( 'alert-danger' ).addClass( 'alert-success' );
			$( '#id-resource-alert-text' ).text( getDataAlertText( host, result ) );
        	$.each( result.objects, function( i, object ) {
            	var date = Date();
            	object.is_consumed_server = true;
            	object.user_modified = userName;
            	object.consumed_datetime = moment().utc().format("YYYY-MM-DDTHH:mm:ss.SSSZZ");
            	object.consumer = host;
            	$.ajax({
            		url: listEndpoint + object.id + '/',
            		type: 'PUT',
            		dataType: 'json',
            		contentType: 'application/json',
            		// processData: false,
            		data: JSON.stringify(object),
            		success: function( result ) {
            			console.log( result );
            		},
            		error: function( xhr, status, error ) {
            			console.log( status );	
            			console.log( error );	
            		},
         		});
            	$.each( object, function( i, field ) {
            		$( '#id-div-show-json' ).append( i + ': ' + field + '</BR>' );	
            	})
        	});
        	if ( result.meta.total_count == 0 ) {
        		$( '#id-resource-alert-text' ).text( 'Done. Host ' + host + ' has ' +  result.meta.total_count + ' pending.');
        	} else {
				$( '#id-resource-alert-text' ).text( getDataAlertText( host, result ) );
				console.log(result.meta.total_count);
        		getData( result.meta.next, host, userName );
        	};
        },
    	error: function( xhr, status, error ) {
    		console.log(error);
    		$( '#id-resource-alert' ).removeClass( 'alert-success' ).addClass( 'alert-danger' );
    		$( '#id-resource-alert-text' ).text( 'An error has occured while contacting ' +  host  + '.' );
    	},
	});
}

function getDataAlertText ( host, result ) {
	var alertText = 'Getting next ' + (result.meta.limit + result.meta.offset) +' of ' + result.meta.total_count + ' data from ' +  host  + '.';
	return alertText
}

function makeHostAlert( id, host, cssClass ) {
	/* return an error alert */
	if ( id == '' || id == null ) {
		id = 'id-resource-alert';
	}
	if ( cssClass == '' || cssClass == null ) {
		cssClass = 'alert-danger';
	}
	alert_div = '<div id="' + id +'" class="alert ' + cssClass + ' text-center">';
	alert_div += '<a href="#" class="close" data-dismiss="alert" aria-label="close">&times;</a>';
	alert_div += '<span id="id-resource-alert-text"></span>';
	alert_div += '</div>';
	return alert_div
}

function resourceUri(host, listEndpoint, userName, apiKey) {
	uri = '';
	if (host != '') {
	 	params = $.param({'format': 'json', 'username': userName, 'api_key': apiKey})
	  	uri = 'http://' + host + listEndpoint + '?' + params;
	}
	return uri;
}