function validate(){
  var uname = document.getElementById('uname');
  var alphanum = /^[A-Za-z1-9]+$/;
  if(uname.value.trim()==""||!uname.value.match(alphanum))
  {
     alert("Please Enter valid name!");
     return false;
  }
  if(uname.value.length<5||uname.value.length>14)
  {
    alert("Length of your name should be in the range of 5 and 14!!!");
    return false;
  }
  if(document.getElementById('pwd').value.length<8) {
    alert("minimum length of password is 8!!");
    return false;
  }
  var p1 = document.getElementById('pwd');
  var p2 = document.getElementById('pwd1');
  if(p1.value==p2.value){
    return true;
  }
  else {
    alert("passwords did not match!!");
    return false;
  }
  var regxmail = /^\S+@\S+\.\S+$/;
  if(!regxmail.test(mail.value))
  {
    alert("Enter the valid email!");
    return false;
  }
}
