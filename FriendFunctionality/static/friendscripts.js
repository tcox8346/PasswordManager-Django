<script src="https://ajax.googleapis.com/ajax/libs/jquery/3.5.1/jquery.min.js" type="text/javascript"></script>

  function accept_request_friend(view) {      

    //Create a new connection with server
    const xhttp = new XMLHttpRequest();
    xhttp.onclick = function() {
      // open call to friendrequest instance function via url
      xhttp.open("POST", view);
      xhttp.send();
      };
    
  }

  function decline_request_friend(view) {
    //Create a new connection with server
    const xhttp = new XMLHttpRequest();
    xhttp.onclick = function() {
      // open call to friendrequest instance function via url
      xhttp.open("POST", view);
      xhttp.send();
    };
    
  }
//TODO
  function cancel_request_friend(view) {
    const xhttp = new XMLHttpRequest();
    xhttp.onclick = function() {
      document.getElementById("demo").innerHTML = this.responseText;
      }
    xhttp.open("POST", "ajax_info.txt", true);
    xhttp.send();
  }



  