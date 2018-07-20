var outgoingListUrl = '/edc_sync/api/outgoingtransaction/'; //Urls[ 'edc_sync:outgoingtransaction-list' ]();

var client = 'http://' + document.location.host

var fileObjs = [];

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
        $( '#id-transfer-status-div' ).show();
    	$( '#id-transfer-status-div' ).text( 'Connecting to the server. Please wait!' );
    	$( '#id-transfer-status-div' ).removeClass( 'alert-danger' ).addClass( 'alert-warning' );
    	$( '#id-in-progress-div-pending-files' ).hide();
        $(this).prop("disabled", true);
        exportBatch(server, userName);
    });
    
    $('#btn-send-again').click( function(e) {
        e.preventDefault();
        $( '#id-transfer-status-div' ).show();
    	$( '#id-transfer-status-div' ).text( 'Connecting to the server. Please wait!' );
    	$( '#id-transfer-status-div' ).removeClass( 'alert-danger' ).addClass( 'alert-warning' );
    	$( '#id-transfer-div' ).hide();
        $(this).prop("disabled",true);
        processPendingFiles();
    });


    $( '#btn-approve' ).click( function(e) {
    	saveConfirmationCode();
    });

    $( '#id-tx-spinner' ).click(function(){
    	window.location.reload(true);
    });

    $('#element').popover('toggle');
}

function File (filename, filesize, index) {
    this.filename = filename;
    this.filesize = filesize;
    this.index = index;
    this.isSend = false;
    this.active = false;
}

function exportBatch(server , userName) {
	var url = client + '/edc_sync/';
	var ajExportBatch = $.ajax({
		url: url,
		type: 'GET',
		dataType: 'json ',
		processData: true,
		data: {'action': 'export_batch'},
	});
	
	ajExportBatch.done( function ( data ) {
		if( data.errmsg ) {
			$( '#btn-sync').prop( "disabled", false );
			$( '#id-transfer-status-div' ).show();
			$( '#id-transfer-status-div' ).text( data.errmsg );
			$( '#id-transfer-status-div' ).removeClass( 'alert-warning' ).addClass( 'alert-danger' );
		} else {
			$( '#id-transfer-div' ).hide();
			$( '#id-in-progress-div' ).show();
			$( '#id-transfer-status-div' ).removeClass( 'alert-warning' ).addClass( 'alert-success' );
			$( '#id-transfer-status-div' ).text('Ready to transfer files to server.');
			//display files
			$.each( data.pending_files, function( index,  filename  ) {
				index = index + 1;
				var txFile = new File(filename, filename, index);
				fileObjs.push(txFile);
				var spanFile = "<span class='glyphicon glyphicon-level-up'></span>";
				$("<tr><td>" + index + "</td><td>" + spanFile +" "+ filename + "</td><td></td></tr>").appendTo("#id-file-table tbody");
			});

			ajExportBatch.then( function() {
					var firstFile = window.fileObjs[0];
					$( "tr:eq( " +firstFile.index+ " )" ).find('td:eq(2)').html("<span class='fas fa-spinner fa-spin'></span>");
					sendTransactionFile(firstFile); // Attempt to send all files.
			});

		}
	});

	ajExportBatch.fail( function( jqXHR, textStatus, errorThrown ) {
		$( '#id-sync-status' ).rešoveClass( 'alert-success' ).addClass( 'alert-danger' );
		$( '#id-sync-status' ).text( 'An error occurred. Got ' + errorThrown);
	});
}

function sendTransactionFile(file) {
	/*
		Send a file transaction to node server or central server.
	*/
	var url = client + '/edc_sync/';
	var ajSendFile = $.ajax({
		url: url,
		type: 'GET',
		dataType: 'json ',
		processData: true,
		data: {
			'action': 'send_files',
			'filename': file.filename,
		}
	});
	
	ajSendFile.done( function( data ) {
		if( data.errmsg ) {
			// Display error message
			updateIcon( file.index, 'error' );
			$( '#progress-status-div' ).text( 'An error occured. Got ' + data.errmsg );
			$( '#progress-status-div' ).removeClass( 'alert-warning' ).addClass( 'alert-danger' );
		} else {
			$( "#btn-progress" ).click();
			$( '#btn-sync').prop( "disabled", false );
			$( '#progress-status-div' ).removeClass( 'alert-warning' ).addClass( 'alert-success' );
			$( '#progress-status-div' ).text('Completed.');
			$( '#btn-approve' ).removeClass( 'btn-default' ).addClass( 'btn-warning' );
			$.each(window.fileObjs, function( index, fileObj ) {
					index = index + 1;
					//display files
					var spanFile = "<span class='glyphicon glyphicon-level-up'></span>";
					var spanOK = "<span class='glyphicon glyphicon-ok'></span>";
					$("<tr><td>" + index + "</td><td> " + spanFile + " "+ fileObj.filename + "</td><td>"+spanOK+"</td></tr>").appendTo("#id-file-table-confirmation tbody");
			});
		}
	});

	ajSendFile.fail( function( jqXHR, textStatus, errorThrown ) {
		updateIcon(file.index, 'error');
		$( '#progress-status-div' ).removeClass( 'alert-warning' ).addClass( 'alert-danger' );
		$( '#progress-status-div' ).text('An error occurred. Got ' + errorThrown + '. Status '+ jqXHR.status);
	});
}

function getFileTransferStatus( fileName ) {
	//
	var url = client + '/edc_sync/';
	var isTransferred = $.ajax({
		url: url,
		type: 'GET',
		dataType: 'json',
		processData: true,
		data: { 'action': 'pending_files' },
	});
	
	isTransferred.done(function( data ) {
		if (data.pending_files.length > 0 ) {
			$.each( data.pending_files, function(index,  pendingFile  ) {
				if (pendingFile == fileName ) {
					getFileTransferStatus( fileName ); // recurse, while not send.
				} else {
					getNextPendingFile(); // get Next pending file 
					return false;
				}
			});
		} else {
			//alert('all files transferred.');
		}
	});

	isTransferred.fail(function( jqXHR, textStatus, errorThrown){
		alert("Failed to get file transfer status."+ errorThrown);
	});
}

function getNextPendingFile() {
	$.each(window.fileObjs, function( index, fileObj ) {
		if (fileObj.isSend == false){
			getFileTransferStatus(fileObj.filename);
			return false;
		}
	});
}

function updateFromHost( host ) {
	var url = host + '/edc_sync/api/transaction-count/';
	ajTransactionCount = $.ajax({
		url: url,
		type: 'GET',
		dataType: 'json',
		processData: false,
	});
	ajTransactionCount.done( function ( data ) {
		if ( data != null ) {
			$( '#id-pending-transactions').text(' ' + data.outgoingtransaction_count);
			$( '#id-pending-transactions-middleman').text(' '+ data.outgoingtransaction_count);
			if( data.outgoingtransaction_count > 0 ) {
				$( '#btn-sync' ).removeAttr( 'disabled' );
				$( '#btn-sync').removeClass( 'btn-default' ).addClass( 'btn-warning' );
			} else {
				$( '#btn-sync' ).removeClass( 'btn-warning' ).addClass( 'btn-default' );
			}
		} 
	});
}

function updateIcon( index, status ) {

	if ( status == 'success' ) {
		$( "tr:eq( " +index+ " )" ).find('td:eq(2)').html("<span class='glyphicon glyphicon-saved alert-success'></span>");
	} else if( status=='error' ) {
		$( "tr:eq( " +index+ " )" ).find('td:eq(2)').html("<span class='glyphicon glyphicon-remove alert-danger'></span>");
	}
}

function saveConfirmationCode() {
	//
		var url = client + '/edc_sync/';
		var ajSaveConfirmation = $.ajax({
			url: url,
			type: 'GET',
			dataType: 'json',
			processData: true,
			data:{'action': 'confirm_batch'}
		});
		
		ajSaveConfirmation.fail(function() {
			alert('Confirmation Error: '+ errorThrown);
		});
		
		ajSaveConfirmation.done( function ( data ) {
			window.location.reload(true);
		});
}


function processPendingFiles() {
	var url = client + '/edc_sync/';
	var ajPendingFiles = $.ajax({
		url: url,
		type: 'GET',
		dataType: 'json ',
		processData: true,
		data: {'action': 'pending_files'},
	});
	
	ajPendingFiles.done( function( data ) {
		//display files
		if( data.errmsg ) {
			$( '#btn-send-again').prop( "disabled", false );
			$( '#id-transfer-status-div' ).show();
			try {
				$( '#id-transfer-status-div' ).text(data.errmsg);
			} catch(err) { }
			$( '#id-transfer-status-div' ).removeClass( 'alert-warning' ).addClass( 'alert-danger' );
		} else {
			$( '#id-transfer-div' ).hide();
			$( '#id-in-progress-div' ).show();
			$( '#id-transfer-status-div' ).removeClass( 'alert-warning' ).addClass( 'alert-success' );
			$( '#id-transfer-status-div' ).text('Ready to transfer files to server.');
			$( '#id-in-progress-div-pending-files' ).hide();

			$.each( data.pending_files, function(index,  filename  ) {
				index = index + 1;
				var transactionFile = new File(filename, filename, index);
				fileObjs.push(transactionFile);
				var spanFile = "<span class='glyphicon glyphicon-level-up'></span>";
				$("<tr><td>" + index + "</td><td>" + spanFile +" "+ filename + "</td><td></td></tr>").appendTo("#id-file-table tbody");
			});

		}
		
	});
	
	ajPendingFiles.then( function( data ) {
		var firstFile = window.fileObjs[0];
		$( "tr:eq( " + firstFile.index + " )" ).find('td:eq(2)').html("<span class='fas fa-spinner fa-spin'></span>");
		sendTransactionFile(firstFile);
	});
	
	ajPendingFiles.fail(function(jqXHR, textStatus, errorThrown) {

		$( '#progress-status-div' ).text('An error occured. Got ' + error);
		$( '#progress-status-div' ).removeClass( 'alert-warning' ).addClass( 'alert-danger' );
	});
	
}


