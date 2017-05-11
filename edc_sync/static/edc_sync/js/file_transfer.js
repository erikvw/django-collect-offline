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
        dumpTransactionFile(server, userName);
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
    	saveApproval();
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

function dumpTransactionFile(server , userName) {

	var url = client + '/edc_sync/';
	var ajDumpFile = $.ajax({
		url: url,
		type: 'GET',
		dataType: 'json ',
		processData: true,
		data: {'action': 'export_file'},
	});
	
	ajDumpFile.done( function ( data ) {
		if(data.error == false) {
			$( '#id-transfer-div' ).hide();
			$( '#id-in-progress-div' ).show();
			$( '#id-transfer-status-div' ).removeClass( 'alert-warning' ).addClass( 'alert-success' );
			$( '#id-transfer-status-div' ).text('Connected to the server.');
			//display files
			$.each( data.transactionFiles, function(index,  file  ) {
				index = index + 1;
				var txFile = new File(file.filename, file.filesize, index);
				fileObjs.push(txFile);
				var spanFile = "<span class='glyphicon glyphicon-level-up'></span>";
				$("<tr><td>" + index + "</td><td>" + spanFile +" "+ file.filename + "</td><td>" + file.filesize + "</td><td></td></tr>").appendTo("#id-file-table tbody");
			});
	
			ajDumpFile.then( function() {
					var firstFile = window.fileObjs[0];
					$( "tr:eq( " +firstFile.index+ " )" ).find('td:eq(3)').html("<span class='fa fa-spinner fa-spin'></span>");
					sendTransactionFile(firstFile);
			});
		} else {
			$( '#btn-sync').prop( "disabled", false );
			$( '#id-transfer-status-div' ).show();
			$( '#id-transfer-status-div' ).text(data.messages);
			$( '#id-transfer-status-div' ).removeClass( 'alert-warning' ).addClass( 'alert-danger' );
		}
	});

	ajDumpFile.fail( function( jqXHR, textStatus, errorThrown ) {
		$( '#id-sync-status' ).removeClass( 'alert-success' ).addClass( 'alert-danger' );
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
			'action': 'send_file',
			'filename': file.filename,
		}
	});
	
	ajSendFile.done( function( data ) {
		if(data.error == false) {
			updateIcon(file.index, 'success');
			$.each(window.fileObjs, function(index, fileObj) {
				if(fileObj.index == file.index ) {
					fileObj.isSend  = true;
					window.fileObjs[index] = fileObj;
					return false;
				}
			});	
			//
			var tmpObj = null;
			$.each(window.fileObjs, function(index, fileObj) { 
				if(fileObj.isSend == false ){
					tmpObj = fileObj;
					return false;
				}
			});
			if (tmpObj != null) {
				sendTransactionFile(tmpObj); //recurse to send another file
			} else {
				$( "#btn-progress" ).click();
				$( '#btn-sync').prop( "disabled", false );
				$( '#progress-status-div' ).removeClass( 'alert-warning' ).addClass( 'alert-success' );
				$( '#progress-status-div' ).text('Completed.');
				$( '#btn-approve' ).removeClass( 'btn-default' ).addClass( 'btn-warning' );
				$.each(window.fileObjs, function( index, fileObj ) {
					if(fileObj.isSend ==  true) {
						index = index + 1;
						//display files
						var spanFile = "<span class='glyphicon glyphicon-level-up'></span>";
						var spanOK = "<span class='glyphicon glyphicon-ok'></span>";
						$("<tr><td>" + index + "</td><td> " + spanFile + " "+fileObj.filename + ", "+ fileObj.filesize+"</td><td>"+spanOK+"</td></tr>").appendTo("#id-file-table-confirmation tbody");
					}
					
				});
			}
		} else {
			/*
				Display the error message.
			*/
			updateIcon(file.index, 'error');
			$( '#progress-status-div' ).text('An error occured. Got ' + data.messages);
			$( '#progress-status-div' ).removeClass( 'alert-warning' ).addClass( 'alert-danger' );
		}
	});

	ajSendFile.then( function() {
		monitorFileSending( file );
	});
	
	ajSendFile.fail( function( jqXHR, textStatus, errorThrown ) {
		updateIcon(file.index, 'error');
		$( '#progress-status-div' ).removeClass( 'alert-warning' ).addClass( 'alert-danger' );
		$( '#progress-status-div' ).text('An error occurred. Got ' + errorThrown + '. Status '+ jqXHR.status);
	});
}

function monitorFileSending( file ) {
	var url = client + '/edc_sync/';
	var ajTransferingFileProgress = $.ajax({
		url: url,
		type: 'GET',
		dataType: 'json ',
		processData: true,
		data: { 'action': 'progress' },
	});

	ajTransferingFileProgress.done( function( data ) {
		//
		$( "tr:eq( " +file.index+ " )" ).find('td:eq(3)').html("<span>100%. sent.</span>");
	});
	ajTransferingFileProgress.fail(function(jqXHR, textStatus, errorThrown) {
		console.log(jqXHR.status, textStatus, errorThrown);
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
			if( data.outgoingtransaction_count == 0 ) {
				$( '#btn-sync' ).removeClass( 'btn-warning' ).addClass( 'btn-default' );
				$( '#btn-sync-middleman' ).removeClass( 'btn-warning' ).addClass( 'btn-default' );
			} 
		}
	});
}

function updateIcon( index, status ) {

	if ( status == 'success' ) {
		$( "tr:eq( " +index+ " )" ).find('td:eq(3)').html("<span class='glyphicon glyphicon-saved alert-success'></span>");
	} else if( status=='error' ) {
		$( "tr:eq( " +index+ " )" ).find('td:eq(3)').html("<span class='glyphicon glyphicon-remove alert-danger'></span>");
	}
}

function saveApproval() {
	var url = client + '/edc_sync/';
	var files = [];
	
	$.each(window.fileObjs, function( index, fileObj ) {
		if(fileObj.isSend ==  true) {
			files.push(fileObj.filename)
		}
	});

	if ( files.length > 0 ) {
		var ajSaveApproval = $.ajax({
			url: url,
			type: 'GET',
			dataType: 'json',
			processData: true,
			data:{'files': files.toString(),
				  'action': 'approve_files'}
		});
	
		ajSaveApproval.fail(function(jqXHR, textStatus, errorThrown) {
			$( '#progress-status-div' ).text('An error occured. Got ' + error);
			$( '#progress-status-div' ).removeClass( 'alert-warning' ).addClass( 'alert-danger' );
			console.log(jqXHR.status, textStatus, errorThrown);
			$('#progressModel').modal('hide');
		});
		
		ajSaveApproval.done( function ( data ) {
			window.location.href = url;
		});
	}
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
		if(data.error == false) {
			$( '#id-transfer-div' ).hide();
			$( '#id-in-progress-div' ).show();
			$( '#id-transfer-status-div' ).removeClass( 'alert-warning' ).addClass( 'alert-success' );
			$( '#id-transfer-status-div' ).text('Connected to the server.');
			$( '#id-in-progress-div-pending-files' ).hide();

			$.each( data.pendingFiles, function(index,  file  ) {
				index = index + 1;
				var txFile = new File(file.filename, file.filesize, index);
				fileObjs.push(txFile);
				var spanFile = "<span class='glyphicon glyphicon-level-up'></span>";
				$("<tr><td>" + index + "</td><td>" + spanFile +" "+ file.filename + "</td><td>" + file.filesize + "</td><td></td></tr>").appendTo("#id-file-table tbody");
			});

		} else {

			$( '#btn-send-again').prop( "disabled", false );
			$( '#id-transfer-status-div' ).show();
			try {
				$( '#id-transfer-status-div' ).text(data.messages);
			} catch(err) { }
			$( '#id-transfer-status-div' ).removeClass( 'alert-warning' ).addClass( 'alert-danger' );
		}
		
	});
	
	ajPendingFiles.then( function( data ) {
		var firstFile = window.fileObjs[0];
		$( "tr:eq( " +firstFile.index+ " )" ).find('td:eq(3)').html("<span class='fa fa-spinner fa-spin'></span>");
		sendTransactionFile(firstFile);
	});
	
	ajPendingFiles.fail(function(jqXHR, textStatus, errorThrown) {

		$( '#progress-status-div' ).text('An error occured. Got ' + error);
		$( '#progress-status-div' ).removeClass( 'alert-warning' ).addClass( 'alert-danger' );
	});
	
}


