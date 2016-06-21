function updateResourceTags(hosts, userName, apiToken) {
	/* prepare tags and hit the list_endpoint */
	var hosts = JSON.parse( hosts );
	$.each( hosts, function( host, resourceName ) {
        var divId = 'id-nav-pill-resources';
		var listUrl = Urls[ resourceName + '-list' ]();        
        makeResourceTags( divId, host, resourceName, listUrl, userName, apiToken )
    });
}

function makeResourceTags ( divId, host, resourceName, listUrl, userName, apiToken ) {
	/* make and append links to the API */
    var fullListUrl = 'http://' + host + listUrl + '?format=json';
    $.each( ['show', 'fetch'], function( index, label ){
	    var anchorId = 'id-link-' + label + '-' + host.replace( ':', '-' );
	    var li = '<li><a id="' + anchorId + '">'+ label + ' resource on ' + host + '</a></li>';
    	$( '#id-nav-pill-resources' ).append( li );
    });
	$( '#id-link-show-' + host.replace( ':', '-' ) ).attr( 'href', fullListUrl );
	$( '#id-link-fetch-' + host.replace( ':', '-' ) ).attr( 'href', '#' );
	$( '#id-link-fetch-' + host.replace( ':', '-' ) ).click( function (e) {
	    e.preventDefault();
		getData(fullListUrl, host, resourceName, listUrl, userName, apiToken);
	});
    
}

function getData( fullListUrl, host, resourceName, listUrl, userName, apiToken ) {
	/* GET all data from the uri until next_uri == null */
	var csrftoken = Cookies.get('csrftoken');
	$.ajaxSetup({
	    beforeSend: function(xhr, settings) {
	        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
	            xhr.setRequestHeader("X-CSRFToken", csrftoken);
	        };
			xhr.setRequestHeader("Authorization", "Token " + apiToken);
	    }
	});	
	$.ajax({
    	url: fullListUrl,
    	type: 'GET',
    	dataType: 'json',
    	processData: false,
    	success: function( result, status, xhr ) {
			$( '#id-resource-alert' ).remove();
			alert_div = makeHostAlert( 'id-resource-alert', host, 'alert-success' );
			$( '#id-div-resource-alert' ).append( alert_div );
    		$( '#id-resource-alert' ).removeClass( 'alert-danger' ).addClass( 'alert-success' );
			$( '#id-resource-alert-text' ).text( getDataAlertText( host, result ) );
        	$.each( result.objects, function( i, object ) {
            	var date = Date();
            	createObject( host, object, userName, apiToken );
            	$.each( object, function( i, field ) {
            		$( '#id-div-show-json' ).append( i + ': ' + field + '</BR>' );	
            	})
        	});
        	if ( result.meta.total_count == 0 ) {
        		$( '#id-resource-alert-text' ).text( 'Done. Host ' + host + ' has ' +  result.meta.total_count + ' pending.');
        	} else {
				$( '#id-resource-alert-text' ).text( getDataAlertText( host, result ) );
				console.log(result.meta.total_count);
				getData( uri, host, listEndpoint, userName, apiToken);
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

function resourceUri(host, listEndpoint, userName, apiToken) {
	uri = '';
	if (host != '') {
	 	params = $.param({'token': apiToken})
	  	uri = 'http://' + host + listEndpoint + '?' + params;
	}
	return uri;
}

function createObject( remoteHost, object, userName, apiToken ) {
	/* save object to local incoming */
	// convert JSON to incoming transaction
	var csrftoken = Cookies.get('csrftoken');

	newObject = object;
	delete newObject['using'];
	delete newObject['is_consumed_middleman'];
	delete newObject['is_consumed_server'];
	newObject['resource_uri'] = newObject.resource_uri.replace('outgoingtransaction', 'incomingtransaction');
	newObject['is_consumed'] = false;
	newObject['is_self'] = false;
	newObject.user_modified = userName;
	newObject.modified = moment().utc().format("YYYY-MM-DDTHH:mm:ss.SSSZZ");
	newObject.consumed_datetime = moment().utc().format("YYYY-MM-DDTHH:mm:ss.SSSZZ");
	newObject.consumer = remoteHost;

	$.ajaxSetup({
	    beforeSend: function(xhr, settings) {
	        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
	            xhr.setRequestHeader("X-CSRFToken", csrftoken);
	        };
			xhr.setRequestHeader("Authorization", "Token " + apiToken);
	    }
	});	
	$.ajax({
		url: 'http://' + document.location.host + '/edc-sync/api/incomingtransaction.json',
		type: 'POST',
		dataType: 'json',
		contentType: 'application/json',
		processData: false,
		data: JSON.stringify( newObject ),
		success: function() {
			updateObjectOnSource( remoteHost, object, userName, apiToken );
		},
		error: function( xhr, status, error ) {
			console.log( status );
			console.log( error );
		},
	});
} 

function updateObjectOnSource ( remoteHost, object, userName, apiToken  ) {
	/* update source object as consumed */
	// update audit fields
	var csrftoken = Cookies.get('csrftoken');
	object.user_modified = userName;
	object.modified = moment().utc().format("YYYY-MM-DDTHH:mm:ss.SSSZZ");
	object.is_consumed_server = true;
	object.consumed_datetime = moment().utc().format("YYYY-MM-DDTHH:mm:ss.SSSZZ");
	object.consumer = remoteHost;
	
	var json_data = {};
	json_data = {
		'user_modified': userName,
		'modified': moment().utc().format("YYYY-MM-DDTHH:mm:ss.SSSZZ"),
		'is_consumed_server': true,
		'consumed_datetime': moment().utc().format("YYYY-MM-DDTHH:mm:ss.SSSZZ"),
		'consumer': remoteHost,
	}


	// PUT object on remote host
	$.ajaxSetup({
	    beforeSend: function(xhr, settings) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
			xhr.setRequestHeader("Authorization", "Token " + apiToken);
	    }
	});	
	$.ajax({
		url: 'http://' + remoteHost + '/edc-sync/api/v1/outgoingtransaction/' + object.id + '/',
		type: 'PATCH',
		dataType: 'json',
		contentType: 'application/json',
		processData: false,
		data: JSON.stringify( json_data ),
		success: function( result ) {
			console.log( result );
		},
		error: function( xhr, status, error ) {
			console.log( status );
			console.log( error );	
		},
	});
}
