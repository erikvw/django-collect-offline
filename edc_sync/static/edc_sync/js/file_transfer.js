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
        dumpTransactionFile(server , userName);
    });
}

function dumpTransactionFile(server , userName) {

	var url = client + '/edc_sync/';
	var ajDumpFile = $.ajax({
		url: url,
		type: 'GET',
		dataType: 'json ',
		processData: true,
		data: {'action': 'dump_transaction_file'},
	});

	ajDumpFile.done( function ( data ) {
	
		$( '#id-transfer-div' ).hide();
		$( '#id-in-progress-div' ).show();
		//display files
		$.each( data.transactionFiles, function(index,  transactionFile  ) {
			index = index + 1;
			spanElemStatus = "<span id=" + transactionFile.filename + "></span>"
			$("<tr><td>" + index + "</td><td>" + transactionFile.filename + "</td><td>" + transactionFile.filesize + "</td><td>" + spanElemStatus + "</td></tr>").appendTo("#id-file-table tbody");
		});
		// transfer each file
		var tIndex = 0;
		$('#id-file-table tbody tr').each( function() {
		    var filename = $(this).find("td").eq(1).html();
		    tIndex = tIndex + 1;
		    $(this).find("td").eq(3).append("<span class='fa fa-spinner fa-spin'></span>");
		    currentRowElement = $(this);
		    sendTransactionFile(currentRowElement, filename, tIndex, data.transactionFiles.length - 1 );
		});
	});

	ajDumpFile.fail( function( jqXHR, textStatus, errorThrown ) {
		$( '#id-sync-status' ).removeClass( 'alert-success' ).addClass( 'alert-danger' );
		$( '#id-sync-status' ).text( 'An error occurred. Got ' + errorThrown);
	});
}

function sendTransactionFile(currentRowElement, filename, tIndex, total) {
	var url = client + '/edc_sync/';
	var ajSendFile = $.ajax({
		url: url,
		type: 'GET',
		dataType: 'json ',
		processData: true,
		data: {'action': 'transfer_transaction_file', 'file': filename},
	});
	
	ajSendFile.done(function(data){
		updateIcon(currentRowElement, 'success');
	});

	ajSendFile.then(function() {
		//Monitor file transfer
		while (tIndex < total + 1) {
			monitorFileSending(currentRowElement, tIndex, total);
		}
	});
	
	ajSendFile.fail( function( jqXHR, textStatus, errorThrown ) {
		updateIcon(currentRowElement, 'error');
		$( '#id-sync-status' ).removeClass( 'alert-success' ).addClass( 'alert-danger' );
		$( '#id-sync-status' ).text( 'An error occurred. Got ' + errorThrown);
	});
}
function monitorFileSending( currentRowElement ) {
	var url = client + '/edc_sync/';
	var ajTransferingFileProgress = $.ajax({
		url: url,
		type: 'GET',
		dataType: 'json ',
		processData: true,
		data: { 'action': 'get_file_transfer_progress' },
	});

	ajTransferingFileProgress.done( function( data ) {
		currentRowElement.find( "td" ).eq( 3 ).text( data.progress );
	});
	ajTransferingFileProgress.fail(function(){
		alert("Error");
	});
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

function updateIcon( currentRowElement, status ) {

	if ( status == 'success' ) {
		currentRowElement.find("td").eq(3).html("<span class='glyphicon glyphicon-saved alert-success'></span>");
	} else if( status=='error' ) {
		currentRowElement.find("td").eq(3).html("<span class='glyphicon glyphicon-remove alert-danger'></span>");
	}
}
