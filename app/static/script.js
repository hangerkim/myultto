// Set time limit to the current datetime
var now = moment().utcOffset('+0900').format('YYYY-MM-DDTHH:mm');
$('#timeLimit').val(now);

// Handle request for extracting candidates
$('#extractForm').submit(function(e) {
  e.preventDefault();
  var submitUrl = $(this).attr('action');
  var dcArticleUrl = $.trim($('#dcArticleUrl').val());
  var timeLimit = moment($('#timeLimit').val()).utcOffset('+0900');

  var requestData = {
    article_url: dcArticleUrl,
    time_limit: timeLimit.toISOString(),
    allow_guest: $('#allowGuest').is(':checked'),
  };

  if (dcArticleUrl.length == 0) {
    return false;
  }
  
  $.ajax({
    url: submitUrl,
    data: JSON.stringify(requestData),
    dataType: 'json',
    contentType: 'application/json',
    method: 'POST',
    success: function(r) {
      var cands = r['candidates'];
      $('#candList').tagsinput('removeAll');
      $.each(cands, function(index, item) {
        $('#candList').tagsinput('add', item);
      });
    },
    error: function(r) {
      console.log(r);
    }
  });
});

// Handle request for drawing a lottery
$('#drawForm').submit(function(e) {
  e.preventDefault();
  var submitUrl = $(this).attr('action');
  var numWinnersStr = $.trim($('#numWinners').val());
  var numWinners;
  if (numWinnersStr.length > 0) {
    numWinners = parseInt(numWinnersStr);
  } else {
    return false;
  }

  var candidates = $('#candList').val().split(',');

  var requestData = {
    num_winners: numWinners,
    candidates: candidates
  };

  if (dcArticleUrl.length == 0) {
    return false;
  }
  
  $.ajax({
    url: submitUrl,
    data: JSON.stringify(requestData),
    dataType: 'json',
    contentType: 'application/json',
    method: 'POST',
    success: function(r) {
      var winnerList = $('#winnersList');
      winnerList.html('');
      var winners = r['winners'];
      $.each(winners, function(index, item) {
        var winnerElem = $('<li/>', {
          'class': 'list-group-item',
          text: item
        });
        winnerList.append(winnerElem);
      });
      $('#resultModal').modal();
    },
    error: function(r) {
      console.log(r);
    }
  });
});
