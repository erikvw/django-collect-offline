function edcSyncFilesReady() {

	$( "#id-files-transfer-btn" ).click( function() {
		$("#id-files-transfer-status").toggle();
		// $("#id-files-progress-title").toggle();
		// $("#id-files-progress-title").addClass("alert-info");
		$("#id-files-tx-spinner").addClass("fa-spin");
		transfer_files();
		blinker();
		// $("#id-files-progress-title").toggle();
		$("#id-files-transfer-status").toggle();
	});
}

function blinker() {
    $('#id-files-progress-title').fadeOut(500);
    $('#id-files-progress-title').fadeIn(500);
}

function track_file_transfer( total_media_to_send, total_tx_to_send ){

	var transfer_progress = $.ajax({
		url: Urls['transfer_files_url'],
		data: {action: 'track_stats'},
		dataType: 'json'}).promise();

	transfer_progress.then(function( results ){
		var sent_tx_files = 0;
		if (total_tx_to_send > 1){
			sent_tx_files = total_tx_to_send - results.tx_to_send;
		} else if(total_tx_to_send == 1){
			sent_tx_files = 1;
		}
		
		var sent_media_files = 0 ;
		if (total_media_to_send > 1){
			sent_media_files = total_media_to_send - results.media_to_send;
			console.log(sent_media_files);
		}
		$("#pending_tx").text(sent_tx_files+" sent");
		$("#pending_media").text(sent_media_files+" sent");
		console.log(results.media_files);
		console.log(results.tx_files);
		console.log("media files to send" + results.media_to_send);
		console.log("tx files to send" +results.tx_to_send);
		if (results.media_to_send != 0 || results.tx_to_send != 0){
			track_file_transfer(total_media_to_send, total_tx_to_send); //recurse
		} else {
			$("#id-files-tx-spinner").removeClass("fa-spin");
			$("#id-files-progress-title").attr("style", "color:green");
			blinker();
			$("#id-files-progress-title").text("Pending transactions have been transfered to the server successfully.");
		}
	});
	transfer_progress.fail(function(){
		//errors
		$("#id-files-tx-spinner").removeClass("fa-spin");
		$("#id-files-progress-title").addClass("alert-danger");
		$("#id-files-progress-title").text("Failed to transfer files,(An error has occured), check machine is connected to wifi.");
	});
}

function transfer_files(){

	var dump_info = $.ajax({
		url: Urls['transfer_files_url'],
		data: {action: 'dump_transactions'},
		dataType: 'json'}).promise();

	dump_info.then(function(results){
		console.log( "track_file_transfer here, transfer;" );
		$( "#total_media" ).text(results.media_to_send);
		$( "#tx_files" ).text(results.tx_to_send);
		
		var transfer = $.ajax({
			url: Urls['transfer_files_url'],
			data: {action: 'transfer'},
			dataType: 'json'}).promise();

		transfer.fail(function(){
			$("#id-files-progress-title").text("Failed to transfer files, (An error has occured).");
		});
	});
	
	dump_info.then(function(results){
		console.log( "track_file_transfer here, get_stats;" );

		var get_stats = $.ajax({
			url: Urls['transfer_files_url'],
			data: {action: 'file_statistics'},
			dataType: 'json'}).promise();

		get_stats.then(function(results){
			$( "#total_media" ).text( results.media_to_send );
			$( "#tx_files" ).text( results.tx_to_send );
		});

		get_stats.fail( function(){
			$( "#id-files-progress-title" ).text("Failed to transfer files,(An error has occured).");
		});
	});

	dump_info.then( function( results ){
		console.log("track_file_transfer here, track_file_transfer(total_media_to_send, total_tx_to_send);");
		track_file_transfer(results.media_to_send, results.tx_to_send);
	});

	dump_info.fail( function(){
		$( "#id-files-tx-spinner" ).removeClass( "fa-spin" );
		$( "#id-files-tx-spinner" ).addClass( "alert-danger" );
		$( "#id-files-progress-title" ).text( "Failed to transfer files,(An error has occured), check machine is connected to wifi." );
	});
}
