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
        //dumpTransactionMiddlemanFile(server , userName);
    });
}

//function File (filename, filesize, index) {
//    this.filename = filename;
//    this.filesize = filesize;
//    this.index = index;
//    this.isSend = false;
//    this.active = false;
//}

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
		
		if ( data.error == false ){
			alert( data.messages );
		}
		
		//dumpTransactionMiddlemanFile(server , userName);
	});

	checkUSBConnection.fail( function( jqXHR, textStatus, errorThrown ) {
		$( '#id-sync-status' ).removeClass( 'alert-success' ).addClass( 'alert-danger' );
		$( '#id-sync-status' ).text( 'An error occurred. Got ' + errorThrown);
	});
}

//function dumpTransactionMiddlemanFile(server , userName) {
//
//	var url = client + '/edc_sync/';
//	var ajDumpFile = $.ajax({
//		url: url,
//		type: 'GET',
//		dataType: 'json ',
//		processData: true,
//		data: {'action': 'dump_to_usb'},
//	});
//	
//	ajDumpFile.done( function ( data ) {
//		if(data.error == false) {
//			//Sending to USB. 
//			sendTransactionFileToUSB()
//		} else {
//			
//		}
//	});
//
//	ajDumpFile.fail( function( jqXHR, textStatus, errorThrown ) {
//		$( '#id-sync-status' ).removeClass( 'alert-success' ).addClass( 'alert-danger' );
//		$( '#id-sync-status' ).text( 'An error occurred. Got ' + errorThrown);
//	});
//}

//function sendTransactionFileToUSB() {
//	var url = client + '/edc_sync/';
//	var ajSendFileUSB = $.ajax({
//		url: url,
//		type: 'GET',
//		dataType: 'json ',
//		processData: true,
//		data: {
//			'action': 'send_to_usb',
//		}
//	});
//	
//	ajSendFileUSB.done( function( data ) {
//		//
//		
//	});
//	
//	ajSendFileUSB.fail( function( jqXHR, textStatus, errorThrown ) {
//		$( '#progress-status-div' ).removeClass( 'alert-warning' ).addClass( 'alert-danger' );
//		$( '#progress-status-div' ).text('An error occurred. Got ' + errorThrown + '. Status '+ jqXHR.status);
//	});
//}
