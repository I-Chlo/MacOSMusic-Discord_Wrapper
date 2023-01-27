document.addEventListener('DOMContentLoaded', (event) => {
    var rpc_toggle_btn = document.getElementById('rpc-toggle');
    rpc_toggle_btn.addEventListener('click', togglerpc);


    function togglerpc(){
        console.log("clicked")
        fetch('/api/toggle-rpc', {state: "toggle"})
        .then(response => {
            console.log(response)
        })
        

    }
  })