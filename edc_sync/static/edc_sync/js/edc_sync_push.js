var outgoingListUrl = '/edc_sync/api/outgoingtransaction/'; //Urls[ 'edc_sync:outgoingtransaction-list' ]();

var client = 'http://' + document.location.host

function edcSyncReady(server, userName, apiToken) {
	/* Prepare page elements */
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
	updateFromHost( client );
    $('#btn-sync').click( function(e) {
        e.preventDefault();
        processOutgoingTransactions(server, userName );
    });
}

function processOutgoingTransactions( server, userName ) {
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
	var url = client + outgoingListUrl + '?format=json'  // limit=1
	var ajGetOutgoing = $.ajax({
		url: url,
		type: 'GET',
		dataType: 'json ',
		processData: false,
	});

	ajPostIncoming = ajGetOutgoing.then( function( outgoingtransactions ) {

		var incomingListUrl = '/edc_sync/api/incomingtransaction/'; //Urls[ 'edc-sync:incomingtransaction-list' ]();
		outgoingtransaction_count = outgoingtransactions.count;

		outgoingtransaction = outgoingtransactions.results[0];
		//$( '#id-resource-alert-text' ).text( hostAlertText( host, outgoingtransaction_count ) );
		return $.ajax({
			url: 'http://' + server + incomingListUrl + '?format=json',
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
			url: client + outgoingDetailUrl,
			type: 'PATCH',
			dataType: 'json',
			contentType: 'application/json',
			processData: false,
			data: JSON.stringify( outgoingtransaction_fields ),
		});
	});

	ajPatchOutgoing.done( function ( data ) {
		if (outgoingtransaction_count == 1){
			$( '#id-pending-transactions' ).text( 0 );
			$( '#btn-sync' ).removeClass( 'btn-warning' ).addClass( 'btn-default' );
		} else {
			$( '#id-pending-transactions' ).text( outgoingtransaction_count );
		}
		
		if ( outgoingtransaction_count > 1 ) {
			processOutgoingTransactions( server, userName );  //recursive
		}
	});

	ajGetOutgoing.fail( function( jqXHR, textStatus, errorThrown ) {
		alert("First request error");
		console.log( textStatus + ': ' + errorThrown );
		alert(jqXHR.status);
		$( '#id-sync-status' ).removeClass( 'alert-success' ).addClass( 'alert-danger' );
		$( '#id-sync-status' ).text( 'An error has occured while contacting ' +  host  + '. Got ' + errorThrown );
	});

	ajPostIncoming.fail( function( jqXHR, textStatus, errorThrown ) {
		$( '#id-sync-status' ).removeClass( 'alert-success' ).addClass( 'alert-danger' );
		$( '#id-sync-status' ).text( 'An error has occured while contacting ' +  server  + '. Got ' + errorThrown );
	});

	ajPatchOutgoing.fail(function( jqXHR, textStatus, errorThrown ) {
		$( '#id-sync-status' ).removeClass( 'alert-success' ).addClass( 'alert-danger' );
		$( '#id-sync-status' ).text( 'An error has occured while contacting ' +  server  + '. Got ' + errorThrown );
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

function updateFromHosts( host ) {
    $("#id-tx-spinner").addClass('fa-spin');
	 	updateFromHost( host );
	$("#id-tx-spinner").removeClass('fa-spin');		
}

function updateFromHost( host ) {
	var url = host + '/edc_sync/api/transaction-count/';
	//Urls['edc-sync:transaction-count']();
	ajTransactionCount = $.ajax({
		url: url,
		type: 'GET',
		dataType: 'json',
		processData: false,
	});
	ajTransactionCount.done( function ( data ) {
		if ( data != null ) {
			$( '#id-pending-transactions').text(' ' + data.outgoingtransaction_count)
			if( data.outgoingtransaction_count == 0 ) {
				$( '#btn-sync' ).removeClass( 'btn-warning' ).addClass( 'btn-default' );
			}
		}
	});
}
