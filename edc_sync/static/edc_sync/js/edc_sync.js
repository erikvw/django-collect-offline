var incomingListUrl = Urls[ 'incomingtransaction-list' ]();    
var outgoingListUrl = Urls[ 'outgoingtransaction-list' ]();        
var server = 'http://' + document.location.host

function edcSyncReady(hosts, userName, apiToken) {
	/* prepare page elements and hit the api */
	var hosts = JSON.parse( hosts );
	var csrftoken = Cookies.get('csrftoken');

	// configure AJAX header with csrf and authorization tokens
	$.ajaxSetup({
	    beforeSend: function(xhr, settings) {
	        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
	            xhr.setRequestHeader("X-CSRFToken", csrftoken);
	        };
			xhr.setRequestHeader("Authorization", "Token " + apiToken);
	    }
	});	

	$.each( hosts, function( host ) {
        var divId = 'id-nav-pill-resources';
        makePageElements( divId, host, userName )
    });
}

function makePageElements ( divId, host, resourceName, listUrl, userName ) {
	/* Make and update page elements.
	   The "id-link-fetch- ... " onClick function pokes the API and starts the data
	   transfer and updates.*/
    $.each( ['show', 'fetch'], function( index, label ){
	    var anchorId = 'id-link-' + label + '-' + host.replace( ':', '-' );
	    var li = '<li><a id="' + anchorId + '">'+ label + ' resource on ' + host + '</a></li>';
    	$( '#id-nav-pill-resources' ).append( li );
    });
	$( '#id-link-show-' + host.replace( ':', '-' ) ).attr( 'href', 'http://' + host + outgoingListUrl + '?format=json' );
	$( '#id-link-fetch-' + host.replace( ':', '-' ) ).attr( 'href', '#' );
	
	// this is the onClick event that starts the data transfer for this host.
	$( '#id-link-fetch-' + host.replace( ':', '-' ) ).click( function (e) {
	    e.preventDefault();
		displayGetDataAlert( host );	    
		getOutgoingTransactions( host, userName );
	});
    
}

function getOutgoingTransactions( host, userName ) {
	/* GET all outgoingtransactions from the host until exhausted
	   Called recursively (?? can run away on errors).
	*/

	$.ajax({
    	url: 'http://' + host + outgoingListUrl + '?format=json',
    	type: 'GET',
    	dataType: 'json',
    	processData: false,
    	success: function( data, status, xhr ) {

        	$.each( data.results, function( i, outgoingtransaction ) {
            	postIncomingTransaction( host, outgoingtransaction, userName );
        	});

        	if ( data.count == 0 ) {
        		$( '#id-resource-alert-text' ).text( 'Done. Host ' + host + ' has ' +  data.count + ' pending.');
        	} else {
				$( '#id-resource-alert-text' ).text( getGetDataAlertText( host, data ) );
				getOutgoingTransactions( host, userName );
        	};
        },
    	error: function( xhr, status, error ) {
    		console.log(error);
    		$( '#id-resource-alert' ).removeClass( 'alert-success' ).addClass( 'alert-danger' );
    		$( '#id-resource-alert-text' ).text( 'An error has occured while contacting ' +  host  + '. Got ' + error);
    	},
	});
}

function postIncomingTransaction( host, outgoingtransaction, userName ) {
	/* POST host.outgoingtransaction as server.incomingtransaction */
	// convert outgoingtransaction to incomingtransaction
	incomingtransaction = getAsIncomingTransaction( outgoingtransaction, userName );

	$.ajax({
		url: server + incomingListUrl + '?format=json',
		type: 'POST',
		dataType: 'json',
		contentType: 'application/json',
		processData: false,
		data: JSON.stringify( incomingtransaction ),
		success: function() {
			patchOutgoingTransaction( host, outgoingtransaction, userName );
		},
		error: function( xhr, status, error ) {
			console.log( status );
			console.log( error );
		},
	});
} 

function patchOutgoingTransaction ( host, outgoingtransaction, userName  ) {
	/* PATCH outgoingtransaction on host as consumed by server */

	var json_data = {};

	json_data = {
		'user_modified': userName,
		'modified': moment().utc().format("YYYY-MM-DDTHH:mm:ss.SSSZZ"),
		'is_consumed_server': true,
		'consumed_datetime': moment().utc().format("YYYY-MM-DDTHH:mm:ss.SSSZZ"),
		'consumer': server,
	}
	// PATCH object on remote host
	$.ajax({
		url: 'http://' + host + outgoingListUrl + outgoingtransaction.pk + '/',
		type: 'PATCH',
		dataType: 'json',
		contentType: 'application/json',
		processData: false,
		data: JSON.stringify( json_data ),
		success: function( result ) {},
		error: function( xhr, status, error ) {
			console.log( status );
			console.log( error );	
		},
	});
}

function getAsIncomingTransaction( outgoingtransaction, userName ) {
	/* Return as an incoming transaction given and outgoing transaction JSON. */
	incomingtransaction = outgoingtransaction;
	delete incomingtransaction['using'];
	delete incomingtransaction['is_consumed_middleman'];
	delete incomingtransaction['is_consumed_server'];
	incomingtransaction['is_consumed'] = false;
	incomingtransaction['is_self'] = false;
	incomingtransaction.user_modified = userName;
	incomingtransaction.modified = moment().utc().format("YYYY-MM-DDTHH:mm:ss.SSSZZ");
	incomingtransaction.consumed_datetime = null;
	incomingtransaction.consumer = null;	

	return incomingtransaction;
}

function displayGetDataAlert( host, data ) {
	$( '#id-resource-alert' ).remove();
	alert_div = makeHostAlert( 'id-resource-alert', host, 'alert-success' );
	$( '#id-div-resource-alert' ).append( alert_div );
	$( '#id-resource-alert' ).removeClass( 'alert-danger' ).addClass( 'alert-success' );
	$( '#id-resource-alert-text' ).text( getGetDataAlertText( host, data ) );
}

function getGetDataAlertText ( host, data, done ) {
	var alertText = 'Ready to get data from ' + host;
	if ( done == true ) {
		alertText = 'Done. ' + host;
	}
	if ( data != null ) {
		alertText = 'Processing outgoing transaction' + data.count + ' from ' +  host  + '.';
	}
	return alertText;
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

