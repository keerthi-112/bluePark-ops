function validate(){
    var uname = document.getElementById('fname');
    var letters = /^[A-Za-z]+$/;
    if(uname.value.trim()==""||!uname.value.test(letters))
    {
        alert("Please Enter valid name!");
        return false;
    }
    if(document.getElementById('ccnum').value.length<16||document.getElementById('ccnum').value.length>16)
    {
        alert("Length of your card number should be 16!!!");
        return false;
    }
    if(document.getElementById('expmonth').value<1||document.getElementById('expmonth').value>12)
    {
        alert("please enter valid month!!");
        return false;
    }
    if(document.getElementById('expyear').value.length<4||document.getElementById('expyear').value.length>4||document.getElementById('expyear').value<2021)
    {
        alert("please enter valid year!!");
        return false;
    }
    
    if(document.getElementById('cvv').value.length<3||document.getElementById('cvv').value.length>3) 
    {
        alert("please enter valid cvv!!");
        return false;
    }
}