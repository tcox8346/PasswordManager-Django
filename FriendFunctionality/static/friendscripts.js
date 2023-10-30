<script src="https://ajax.googleapis.com/ajax/libs/jquery/3.5.1/jquery.min.js" type="text/javascript"></script>

  function accept_request_friend(view) {      

    $.ajax({
      url: view, 
      type: "POST",
      headers: 
          {
          "X-Requested-With": "XMLHttpRequest",
          'X-CSRFToken': csrftoken,
          mode: 'same-origin'
          },
      data: {  'purpose': 'accept_request', 'request_id': instance_id, 'user_response':'1', 'user_instance': '{{user}}'},
      dataType: 'json',
      success: function () {
          console.log("done");
      }
  });
    
  }

  function decline_request_friend(view) {
    $.ajax({
      url: view, 
      type: "POST",
      headers: 
          {
          "X-Requested-With": "XMLHttpRequest",
          'X-CSRFToken': csrftoken,
          mode: 'same-origin'
          },
      data: {  'purpose': 'decline_request', 'request_id': instance_id, 'user_response':'0', 'user_instance': '{{user}}'},
      dataType: 'json',
      success: function () {
          console.log("done");
      }
    });
    
  }
//TODO
function cancel_request_friend(view) {
    $.ajax({
      url: view, 
      type: "POST",
      headers: 
          {
          "X-Requested-With": "XMLHttpRequest",
          'X-CSRFToken': csrftoken,
          mode: 'same-origin'
          },
      data: {  'purpose': 'cancel_request', 'request_id': instance_id, 'user_response':'NONE', 'user_instance': '{{user}}'},
      dataType: 'json',
      success: function () {
          console.log("done");
      }
    });
  }


  