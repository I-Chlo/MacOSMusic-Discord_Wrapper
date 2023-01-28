document.addEventListener('DOMContentLoaded', (event) => {
    var rpc_toggle_btn = document.getElementById('rpc-toggle');
    rpc_toggle_btn.addEventListener('click', togglerpc);

    var lastfm_login_btn = document.getElementById('lastfm-login');
    lastfm_login_btn.addEventListener('click', lastfm_login);


    function togglerpc(){
        console.log("clicked")
        fetch('/api/toggle-rpc', {state: "toggle"})
        .then(response => {
            console.log(response)
        })
        

    }

    function lastfm_login(){
        window.location.href = "/api/lastfm/login"
        

    }
  })