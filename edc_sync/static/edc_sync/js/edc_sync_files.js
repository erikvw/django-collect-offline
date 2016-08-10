//var transfer_files_url = Urls[ 'transfer_files_url' ]();

function edcFileTransferReady() {

	$("#btn_transfer").click(function(){
		$("#panel-transfer-files").toggle(); 
		$("#alert-progress-status").toggle();
		$("#alert-progress-status").addClass("alert-info");
		$("#alert-progress-status").text("Transfering files.");
		$("#id-tx-spinner").addClass("fa-spin");
		transfer_files(Urls['transfer_files_url']);
	});
}

function track_file_transfer(total_media_to_send, total_tx_to_send, url, media_files){
	var transfer_progress = $.ajax({
		url: url, 
		data: {action: 'track_stats',  
		media_files:media_files}, 
		dataType: 'json'
	}).promise();

	transfer_progress.then(function(results){
		var sent_tx_files = 0;
		if (total_tx_to_send > 1) {
			sent_tx_files = total_tx_to_send - results;
		} else if(total_tx_to_send == 1) {
			sent_tx_files = 1;
		}

		$("#id-pending-tx").text(sent_tx_files+" sent");
		$("#id-pending-media").text( results.media_to_send+" sent");

		if (results.media_to_send_count != total_media_to_send || results.transaction_file_to_send_count != 0) {
			track_file_transfer(total_media_to_send, total_tx_to_send, url, media_files); //recurse
		} else {
			$("#id-tx-spinner").removeClass("fa-spin");
			$("#alert-progress-status").attr("style", "color:green");
			$("#alert-progress-status").text("Pending transactions have been transfered to the server successfully.");
		}
	});
	transfer_progress.fail(function() {
		//errors
		$("#id-tx-spinner").removeClass("fa-spin");
		$("#alert-progress-status").addClass("alert-danger");
		$("#alert-progress-status").text("Failed to transfer files,(An error has occured).");
	});
}

function transfer_files(url) {
	var dump_transactions_to_file = $.ajax({
		url: url,
		data: {action: 'dump_transactions_to_file'},
		dataType: 'json'
	}).promise();

	dump_transactions_to_file.then(function(results) {
		$("#id-total-media").text(results.media_to_send_count);
		$("#id-tx-files").text(results.transaction_file_to_send_count);
		var transfer = $.ajax({
			url: url,
			data: {action: 'transfer_data_to_remote_device'},
			dataType: 'json'
		}).promise();
		transfer.fail(function(){
			$("#alert-progress-status").text("Failed to transfer files, (An error has occured).");
		});
	});

	dump_transactions_to_file.then(function(results) {
		var total_media_to_send = results.media_to_send_count;
		var total_tx_to_send =  results.transaction_file_to_send_count;
		var media_files = [];
		for (var i = 0; i < results.media_files.length; i++) {
			media_files.push(results.media_files[i]);
		}
		track_file_transfer(total_media_to_send, total_tx_to_send, url, media_files.toString());
	});
	dump_transactions_to_file.fail(function() {
		$("#id-tx-spinner").removeClass("fa-spin");
		$("#id-tx-spinner").addClass("alert-danger");
		$("#alert-progress-status").text("Failed to transfer files,(An error has occured).");
	});
}
