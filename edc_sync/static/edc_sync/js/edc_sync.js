var outgoingListUrl = '/edc_sync/api/outgoingtransaction/'; //Urls[ 'edc_sync:outgoingtransaction-list' ]();

var server = 'http://' + document.location.host

function edcSyncReady(hosts, userName, apiToken, homeUrl) {
	/* Prepare page elements */
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
	// make elements for each host, set the onClick event
	$.each( hosts, function( host ) {
		var divId = 'id-nav-pill-resources';
		makePageElements( divId, host, userName );
		// this is the onClick event that starts the data transfer for this host.
		$( '#id-link-fetch-' + host.replace( ':', '-' ).split( '.' ).join( '-' ) ).click( function (e) {
			e.preventDefault();
			displayGetDataAlert( host );
			processOutgoingTransactions( host, userName );
		});
	});

	updateFromHosts( hosts ); //Pending transactions client 
	updateFromHost( server, true ); // Pending incoming transactions count server
	
	$( '#id-nav-pill-apply' ).append( '<li><a id="id-link-apply" href="#">Apply Incoming Transactions<span id="bdg-incomingtransaction-count" class="badge pull-right">0</span></a></li>' );
	$('#bdg-refresh-clients').click( function(e) {
        e.preventDefault();
        updateFromHosts( hosts );
    });
    
    $('#id-link-apply').click( function(e) {
        e.preventDefault();
        processIncomingTransactions( homeUrl, userName );
    });
}

function processOutgoingTransactions( host, userName ) {
	/* 
	Process each OutgoingTransaction one at a time.
	Requests are chained: 
		1. GET outgoingtransaction from host;
		2. POST as incomingtransaction to server (me)
		3. PATCH outgoingtransaction on host;
   	Called recursively until outgoingtransaction_list returns nothing.
	*/
	var outgoingtransaction = null;
	var outgoingtransaction_total_count = 0;
	var url = 'http://' + host + outgoingListUrl + '?format=json'  // limit=1

	var ajGetOutgoing = $.ajax({
		url: url,
		type: 'GET',
		dataType: 'json',
		processData: false,
	});

	ajPostIncoming = ajGetOutgoing.then( function( outgoingtransactions ) {

		var incomingListUrl = '/edc_sync/api/incomingtransaction/'; //Urls[ 'edc_sync:incomingtransaction-list' ]();
		outgoingtransaction_count = outgoingtransactions.count;
		outgoingtransaction = outgoingtransactions.results[0];
		$( '#id-resource-alert-text' ).text( hostAlertText( host, outgoingtransaction_count ) );
		
		return $.ajax({
			url: server + incomingListUrl + '?format=json',
			type: 'POST',
			dataType: 'json',
			contentType: 'application/json',
			processData: false,
			data: JSON.stringify( convertToIncomingTransaction( outgoingtransaction, userName ) ),
		});
	});

	ajPatchOutgoing = ajPostIncoming.then( function( incomingtransaction ) {
		var json_data = {};
		var outgoingDetailUrl = '/edc_sync/api/outgoingtransaction/'+ outgoingtransaction.pk + '/';
			//Urls[ 'edc_sync:outgoingtransaction-detail' ]( outgoingtransaction.pk );
		var outgoingtransaction_fields = {
			'user_modified': userName,
			'modified': moment().utc().format("YYYY-MM-DDTHH:mm:ss.SSSZZ"),
			'is_consumed_server': true,
			'consumed_datetime': moment().utc().format("YYYY-MM-DDTHH:mm:ss.SSSZZ"),
			'consumer': server,
		};
		return $.ajax({
			url: 'http://' + host + outgoingDetailUrl,
			type: 'PATCH',
			dataType: 'json',
			contentType: 'application/json',
			processData: false,
			data: JSON.stringify( outgoingtransaction_fields ),
		});
	});

	ajPatchOutgoing.done( function ( data ) {
		var host_string = host.replace( ':', '-' ).split( '.' ).join( '-' );
		$( '#bdg-outgoingtransaction-count-' + host_string ).text(outgoingtransaction_count);
		if ( data != null ) {
			processOutgoingTransactions( host, userName );  //recursive
		}
	});

	ajGetOutgoing.fail( function( jqXHR, textStatus, errorThrown ) {
		console.log( textStatus + ': ' + errorThrown );
		$( '#id-resource-alert' ).removeClass( 'alert-success' ).addClass( 'alert-danger' );
		$( '#id-resource-alert-text' ).text( 'An error has occured while contacting ' +  host  + '. Got ' + errorThrown );
	});

	ajPostIncoming.fail( function( jqXHR, textStatus, errorThrown ) {
		console.log( textStatus + ': ' + errorThrown + '(on POST)' );
		$( '#id-resource-alert-text' ).text( 'Done. Host ' + host + '.');
	});

	ajPatchOutgoing.fail(function( jqXHR, textStatus, errorThrown ) {
		console.log( textStatus + ': ' + errorThrown + '(on PATCH)');
		$( '#id-resource-alert-text' ).text( 'Done. Host ' + host + '.');
	});
}

function convertToIncomingTransaction( outgoingtransaction, userName ) {
	/* Return as an incoming transaction given and outgoing transaction JSON. */
	var incomingtransaction = outgoingtransaction;
	if ( incomingtransaction != null ) {
		delete incomingtransaction['using'];
		delete incomingtransaction['is_consumed_middleman'];
		delete incomingtransaction['is_consumed_server'];
		incomingtransaction['is_consumed'] = false;
		incomingtransaction['is_self'] = false;
		incomingtransaction.user_modified = userName;
		incomingtransaction.modified = moment().utc().format("YYYY-MM-DDTHH:mm:ss.SSSZZ");
		incomingtransaction.consumed_datetime = null;
		incomingtransaction.consumer = null;
	}
	return incomingtransaction;
}

function displayGetDataAlert( host ) {
	$( '#id-resource-alert' ).remove();
	alert_div = makeHostAlert( 'id-resource-alert', host, 'alert-success' );
	$( '#id-div-resource-alert' ).append( alert_div );
	$( '#id-resource-alert' ).removeClass( 'alert-danger' ).addClass( 'alert-success' );
	$( '#id-resource-alert-text' ).text( host + ' is ready.' );
}

function hostAlertText ( host, count ) {

	var alertText = '';

	if ( count > 0 ) {
		alertText = 'Processing outgoing transactions. ' + count + ' records pending on ' +  host  + '.';
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


function makePageElements ( divId, host, resourceName, listUrl, userName ) {
	/* Make and update page elements.
	   The "id-link-fetch- ... " onClick function pokes the API and starts the data
	   transfer and updates.*/
	var host_string = host.replace( ':', '-' ).split( '.' ).join( '-' );
	var anchorId = 'id-link-fetch-' + host_string;
	var li = '<li><a id="' + anchorId + '">Fetch \'OutgoingTransaction\' from ' + host + '&nbsp;<span id="id-hostname-' + host_string +'"></span>&nbsp;<span id="bdg-outgoingtransaction-count-' + host_string + '" class="badge pull-right">?</span></a></li>';
	$( '#id-nav-pill-resources' ).append( li );
	$( '#id-link-fetch-' + host_string ).attr( 'href', '#' );
}

function updateFromHosts( hosts ) {
    $("#bdg-refresh-clients").addClass('fa-spin');
	$.each( hosts, function( host ) {
		var isServer = false;
		updateFromHost( host , isServer);
	});	
	$("#bdg-refresh-clients").removeClass('fa-spin');		
}

function updateFromHost( host , isServer) {
	var host_string = host.replace( ':', '-' ).split( '.' ).join( '-' );
	var url = 'http://' + host + '/edc_sync/api/transaction-count/';
	if (isServer == true){
		var url = host + '/edc_sync/api/transaction-count/';
	}
	//Urls['edc_sync:transaction-count']();
	ajTransactionCount = $.ajax({
		url: url,
		type: 'GET',
		dataType: 'json',
		processData: false,
	});
	ajTransactionCount.fail( function ( jqXHR, textStatus, errorThrown ) {
		console.log( textStatus + ': ' + errorThrown + '(on GET, count transactions)' );
	});
	ajTransactionCount.done( function ( data ) {
		if ( data != null ) {
			if(isServer == false){
				$( '#bdg-outgoingtransaction-count-' + host_string + '').text(data.outgoingtransaction_count)			
				$( '#id-hostname-' + host_string +'').text(' -- ' + data.hostname.toLowerCase() + '')
			} else {
				$( '#bdg-incomingtransaction-count').text(data.incomingtransaction_count)			
				$( '#id-hostname-' + host_string +'').text(' -- ' + data.hostname.toLowerCase() + '')
			}
		}
	});
}

function processIncomingTransactions( homeUrl, userName ) {
	/*
	Process each IncomingTransaction one at a time.
	Requests are chained: 
		1. GET incoming from server;
		2. POST as incomingtransaction to server (me)
		3. Apply IncomingTransaction to server(me)
		4. Update IncomingTransaction to consumed
   	Called recursively until incomingtransactions are all applied.
   	*/

	var incomingListUrl = '/edc_sync/api/incomingtransaction/'; 
	//Urls[ 'edc_sync:incomingtransaction-list' ]();

	var ajGetIncoming = $.ajax({
		url: server + incomingListUrl + '?format=json',
		type: 'GET',
		dataType: 'json',
		contentType: 'application/json',
		processData: false,
	});

	ajPostIncoming = ajGetIncoming.then( function( incomingtransactions ) {

		incomingtransaction_count = incomingtransactions.count;
		incomingtransaction = incomingtransactions.results[0];
		var incoming_fields = {
			'user_modified': userName,
			'modified': moment().utc().format("YYYY-MM-DDTHH:mm:ss.SSSZZ"),
			'is_consumed_server': true,
			'consumed_datetime': moment().utc().format("YYYY-MM-DDTHH:mm:ss.SSSZZ"),
//			'consumer': host,
			'tx_pk': incomingtransaction.tx_pk,
			'action': 'apply_incomingtransactions',
			'total': incomingtransaction_count,
		};
		var playIncomingUrl = server + homeUrl;
		return $.ajax({
			url: playIncomingUrl,
			type: 'GET',
			dataType: 'json',
			contentType: 'application/json',
			processData: false,
			data: JSON.stringify( incoming_fields ),
		});
	});

	ajPostIncoming.done( function ( data ) {

		var consumedAll = incomingtransaction_count;
		new_total = data.total;
		$( '#bdg-incomingtransaction-count' ).text( new_total );
		if ( new_total >  0 ) {
			processIncomingTransactions( homeUrl, userName );  //recursive
		}
	});
	
	ajPostIncoming.fail(function(jqXHR, textStatus, errorThrown) {
		console.log( textStatus + ': ' + errorThrown );
		$( '#id-apply-incoming' ).remove();
		$( '#id-nav-pill-apply').prepend( makeHostAlert( 'id-apply-incoming', server, 'alert-danger' ));
		$( '#id-apply-incoming' ).removeClass( 'alert-success' ).addClass( 'alert-danger' );
		error_message = 'An error has occured while contacting ' +  server  + '. Got ' + errorThrown;
		$( '#id-apply-incoming' ).append( '<span>'+error_message+'</span>' );
	});

	ajGetIncoming.fail(function(jqXHR, textStatus, errorThrown) {
		$( '#bdg-incomingtransaction-count' ).text( '?' );
	});
}
