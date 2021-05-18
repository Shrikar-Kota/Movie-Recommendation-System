function authenticate(){
    var email = document.getElementById("email").value;
    var password = document.getElementById("password").value;
    if (email.length != 0){
        if (password.length != 0){
            var path = window.location.origin+"/login";
            $.ajax({
                type: 'POST',
                data: {'email': email, 'password': password},
                url: path,
                dataType: 'html',
                success: function(response){
                    response = JSON.parse(response);
                    if (response['error'] == 1){
                        document.getElementById('error-message').style.display = 'block';
                        document.getElementById("email").value = "";
                        document.getElementById("password").value = "";
                    }
                    else{
                        location.href = window.location.origin+"/home";
                    }
                },
                error: function(){
                    alert("Internal Server Error");
                }
            })
        }
    }
}

function registration(){
    var email = document.getElementById("reg-email").value;
    var p1 = document.getElementById("reg-password1").value;
    var p2 = document.getElementById("reg-password2").value;
    if (email.length != 0){
        var filter = /^([\w-\.]+)@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.)|(([\w-]+\.)+))([a-zA-Z]{2,4}|[0-9]{1,3})(\]?)$/;
        var filter2 = /^\d{10}$/;
        if (filter.test(email) || filter2.test(email)) {
            if ((p1.length != 0 && p2.length != 0)){
                if (p1 === p2){
                    var path = window.location.origin+"/register";
                    $.ajax({
                    type: 'POST',
                    data: {'email': email, 'password': p1},
                    url: path,
                    dataType: 'html',
                    success: function(response){
                        response = JSON.parse(response);
                        if (response['success'] == 0){
                            onModalClose();
                            document.getElementById('reg-error-message').style.display = 'block';
                        }
                        else{
                            onModalClose();
                            document.getElementById('reg-success-message').style.display = 'block';
                        }
                    },
                    error: function(){
                        alert("Internal Server Error");
                    }
                    })
                }
            }
        }
        else{
            onModalOpen();
            document.getElementById('email').style.display = 'block';
            alert("Enter Valid Email Address/Phone Number");
        }
    }
}

function logout(){
    var path = window.location.origin+"/logout"; 
    $.ajax({
    type: 'GET',
    url: path,
    dataType: 'html',
    success: function(response){
        response = JSON.parse(response);
        if (response['logout'] == 1){
            location.href = window.location.origin+"/home";
        }
        else{
            alert("Internal server error");
        }
    },
    error: function(response){
        alert("Internal server error");
    }

})
}

function onModalClose(){
    document.getElementById("reg-email").value = "";
    document.getElementById("reg-password1").value = "";
    document.getElementById("reg-password2").value = "";
    document.getElementById('reg-success-message').style.display = 'none';
    document.getElementById('reg-error-message').style.display = 'none';
}

function onModalOpen(){
    document.getElementById('error-message').style.display = 'none';
    document.getElementById("email").value = "";
    document.getElementById("password").value = "";
}