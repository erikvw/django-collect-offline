//var mediaCountUrl = Urls[ 'edc-sync:media-count' ]();

function edcSyncMediaFilesReady(hosts, url) {
	/* Prepare page elements */
	var hosts = JSON.parse( hosts );

	// make elements for each host, set the onClick event
	$.each( hosts, function( host ) {
		ip_address = host;
		var divId = 'id-nav-pull-resources';
		makePageElementsMediaDiv( divId, host, userName );
		mediaCount( ip_address );
		/* this is the onClick event that starts the data transfer for this host.*/
		$( '#id-link-pull-' + host.replace( ':', '-' ).split( '.' ).join( '-' ) ).click( function (e) {
			e.preventDefault();
			$( "#alert-progress-status" ).show();
			var mediaData = mediaCount( $( this ).val() );
			mediaData.done( function( data ) {
				alert(data.host);
				$.each( data.mediafiles, function(idx, filename ) {
					 $( "#id-tx-spinner" ).addClass('fa-spin');
					 $("#alert-progress-status").text( "Transferring files." );
					 $("#alert-progress-status").addClass( 'alert-info' );
					 processMediaFiles( ip_address, filename, url , idx, data.mediafiles.length);
				});
			});
			mediaData.fail(function( data ) {
				$("#alert-progress-status").text( "An error occurred." );
				$("#alert-progress-status").removeClass( 'alert-info' ).addClass( 'alert-danger' );
			} ); 
		});
	});
}

function mediaCount(host) {

	var mediaCountResponse = $.ajax({
		url: url,
		type: 'GET',
		dataType: 'json',
		data: {
			host: host,
			action: 'media-count'
		},
	}).promise();

	mediaCountResponse.done(function( data ) {
		var mediaCount = data.mediafiles.length;
		$( "#id-link-pull-" + host ).text( mediaCount );
		// $( 'alert-progress-status' ).text( 'Media file have been transfer to server.' );
	} );
	return mediaCountResponse;
}

function processMediaFiles ( host, filename, url, sent_media, total_media) {

	var pendingMediaFiles = $.ajax({
		url: url,
		type: 'GET',
		dataType: 'json',
		data: {
			action: 'pull',
			host: host,
			filename: filename,
		}
	}).promise();

	pendingMediaFiles.done(function( response_data ) {
		/* on success */ 
		$("#id-media-count").text( " " + sent_media + "/" + total_media + " sent." );
		$("#alert-progress-status").addClass( 'alert-info' );
		if (sent_media == total_media){
			$("#alert-progress-status").text("All media file transferred to server.");
			$("#alert-progress-status").addClass( 'alert-success' );
		} else {
			$("#alert-progress-status").text("Transferring files");	
		}
	});

	pendingMediaFiles.fail(function() {
		/* Display error */
		$("#alert-progress-status").text( "An error occurred." );
		$("#alert-progress-status").removeClass( 'alert-info' ).addClass( 'alert-danger' );
	});

	pendingMediaFiles.always(function() {
		/* stop the spinner */
		$("#id-tx-spinner").removeClass( 'fa-spin' );
	});
}

function makePageElementsMediaDiv ( divId, host, userName ) {
	/* Make and update page elements.
	   The "id-link-fetch- ... " onClick function pokes the API and starts the data
	   transfer and updates.*/
	var host_string = host.replace( ':', '-' ).split( '.' ).join( '-' );
	var anchorId = 'id-link-pull-' + host_string;
	var li = '<li><a id="' + anchorId + '">Fetch \'Media Files\' from ' + host + '&nbsp;<span id="id-hostname-' + host_string +'"></span>&nbsp;<span id="id-media-count-' + host_string + '" class="badge pull-right">?</span></a></li>';
	$( '#id-nav-pull-resources' ).append( li );
	$( '#id-link-pull-' + host_string ).attr( 'href', '#' );
	$( '#id-link-pull-' + host_string ).val(host);
}
