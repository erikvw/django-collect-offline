var outgoingListUrl = '/edc_sync/api/outgoingtransaction/'; //Urls[ 'edc_sync:outgoingtransaction-list' ]();

var client = 'http://' + document.location.host

var fileObjs = [];

function edcSyncUSBReady(server, userName, apiToken) {
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
    $('#btn-sync-middleman').click( function(e) {
        e.preventDefault();
        $( '#id-transfer-status-div' ).show();
    	$( '#id-transfer-status-div' ).text( 'Searching for USB. Please wait!' );
    	$( '#id-transfer-status-div' ).removeClass( 'alert-danger' ).addClass( 'alert-warning' );
        $(this).prop("disabled",true);
        checkUSBConnectivity(server, userName);
    });
}

function checkUSBConnectivity(server , userName) {
	var url = client + '/edc_sync/dump-to-usb/';
	var checkUSBConnection = $.ajax({
		url: url,
		type: 'GET',
		dataType: 'json ',
		processData: true,
		data: {
			'action': 'check_usb_connection'
		},
	});
	
	checkUSBConnection.done(function( data ) {
		if ( data.error == false ) {
			dumpTransactionMiddlemanFile(server, userName);
		} else {
	        $( '#id-transfer-status-div' ).show();
	    	$( '#id-transfer-status-div' ).text( 'USB connected.' );
	    	$( '#id-transfer-status-div' ).removeClass( 'alert-warning' ).addClass( 'alert-success' );
			$( '#id-transfer-status-div' ).show();
			displayErrorMessage();
		}
	});

	checkUSBConnection.fail( function( jqXHR, textStatus, errorThrown ) {
		$( '#id-transfer-status-div' ).removeClass( 'alert-success' ).addClass( 'alert-danger' );
		$( '#id-transfer-status-div' ).text( 'An error occurred. Got ' + errorThrown);
	});
}

function loadUsbTransactionFile(server , userName) {
	var url = client + '/edc_sync/dump-to-usb/';
	var ajloadFile = $.ajax({
		url: url,
		type: 'GET',
		dataType: 'json ',
		processData: true,
		data: {
			'action': 'load_json_file'
		},
	});
	ajloadFile.done( function ( data ) {
		if(data.error == false) {
	        $( '#id-transfer-status-div' ).show();
	    	$( '#id-transfer-status-div' ).text( 'Transaction file:'+ data.filename+ 'have been copied to usb successfuly.' );
	    	$( '#id-transfer-status-div' ).removeClass( 'alert-warning' ).addClass( 'alert-success' );
		} else {
			displayErrorMessage();
		}
	});
}


function dumpTransactionMiddlemanFile(server , userName) {

	var url = client + '/edc_sync/';
	var ajDumpFile = $.ajax({
		url: url,
		type: 'GET',
		dataType: 'json ',
		processData: true,
		data: {'action': 'dump_to_usb'},
	});
	
	ajDumpFile.done( function ( data ) {
		if(data.error == false) {
	        $( '#id-transfer-status-div' ).show();
	    	$( '#id-transfer-status-div' ).text( 'Transaction file:'+ data.filename+ 'have been copied to usb successfuly.' );
	    	$( '#id-transfer-status-div' ).removeClass( 'alert-warning' ).addClass( 'alert-success' );
		} else {
			displayErrorMessage();
		}
	});

	ajDumpFile.fail( function( jqXHR, textStatus, errorThrown ) {
		$( '#id-sync-status' ).removeClass( 'alert-success' ).addClass( 'alert-danger' );
		$( '#id-sync-status' ).text( 'An error occurred. Got ' + errorThrown);
	});
}


function displayErrorMessage() {
	var error = "";
	$.each( data.messages, function(index,  message  ) {
		try {
			error = message.error.network;
			$( '#id-transfer-status-div' ).text('Unable to connect to the usb. Got '+error);
		} catch(err) { }
		
		try {
			error = message.error.permission;
			if( error !== void 0){
				$( '#id-transfer-status-div' ).text('An error occurred. Got, '+error);
			}
		} catch(err) { }
		
		try {
			error = message.other.action;
			if( error !== void 0){
				$( '#id-transfer-status-div' ).text('An error occurred. Got, '+error);
			}
		} catch(err) { }
	});
	$( '#id-transfer-status-div' ).removeClass( 'alert-warning' ).addClass( 'alert-danger' );
}
