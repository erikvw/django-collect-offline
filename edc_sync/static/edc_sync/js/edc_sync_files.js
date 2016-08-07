//var transfer_files_url = Urls[ 'transfer_files_url' ]();

function edcFileTransferReady(hosts, userName, apiToken, url) {
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
	 
	$("#btn_transfer").click(function(){
		$("#transfer_status").toggle();
		$("#alert-progress-status").toggle();
		$("#alert-progress-status").addClass("alert-info");
		$("#id-tx-spinner").addClass("fa-spin");
		transfer_files(url);
		blinker();
	});

	$("#alert-progress-status").toggle();
	$("#transfer_status").toggle();
}

function blinker() {
    $('#alert-progress-status').fadeOut(500);
    $('#alert-progress-status').fadeIn(500);
}

function track_file_transfer(total_media_to_send, total_tx_to_send, url, media_files){
	var transfer_progress = $.ajax({url: url, data: {action: 'track_stats',  media_files:media_files}, dataType: 'json'}).promise();
	transfer_progress.then(function(results){
		var sent_tx_files = 0;
		if (total_tx_to_send > 1){
			sent_tx_files = total_tx_to_send - results.tx_to_send;
		}else if(total_tx_to_send == 1){
			sent_tx_files = 1;
		}

		$("#id-pending-tx").text(sent_tx_files+" sent");
		$("#id-pending-media").text( results.media_to_send+" sent");

		if (results.media_to_send != total_media_to_send || results.tx_to_send != 0){
			track_file_transfer(total_media_to_send, total_tx_to_send, url, media_files); //recurse
		}else{
			$("#id-tx-spinner").removeClass("fa-spin");
			$("#alert-progress-status").attr("style", "color:green");
			blinker();
			$("#alert-progress-status").text("Pending transactions have been transfered to the server successfully.");
		}
	});
	transfer_progress.fail(function(){
		//errors
		$("#id-tx-spinner").removeClass("fa-spin");
		$("#alert-progress-status").addClass("alert-danger");
		$("#alert-progress-status").text("Failed to transfer files,(An error has occured).");
	});
}

function transfer_files(url){
	var dump_info = $.ajax({url: url, data: {action: 'dump_transactions'}, dataType: 'json'}).promise();

	dump_info.then(function(results){
		console.log("track_file_transfer here, transfer;");
		$("#id-total-media").text(results.media_to_send);
		$("#id-tx-files").text(results.tx_to_send);
		var transfer = $.ajax({url: url, data: {action: 'transfer'}, dataType: 'json'}).promise();
		transfer.fail(function(){
			$("#alert-progress-status").text("Failed to transfer files, (An error has occured).");
		});
	});

	dump_info.then(function(results){
		var total_media_to_send = results.media_to_send;
		var total_tx_to_send =  results.tx_to_send;
		var media_files = [];
		for (var i = 0; i < results.media_files.length; i++) {
			media_files.push(results.media_files[i]);
		}
		console.log("track_file_transfer here, track_file_transfer(total_media_to_send, total_tx_to_send);");
		track_file_transfer(total_media_to_send, total_tx_to_send, url, media_files.toString());
	});
	dump_info.fail(function(){
		$("#id-tx-spinner").removeClass("fa-spin");
		$("#id-tx-spinner").addClass("alert-danger");
		$("#alert-progress-status").text("Failed to transfer files,(An error has occured), check machine is connected to wifi.");
	});
}
