function validate(){
  var uname = document.getElementById('uname');
  var letters = /^[A-Za-z]+$/;
  if(uname.value.trim()==""||!uname.value.match(letters))
  {
     alert("Please Enter valid name!");
     return false;
  }
  if(uname.value.length<5||uname.value.length>12)
  {
    alert("Length of your name should be in the range of 5 and 12!!!");
    return false;
  }
  if(document.getElementById('pwd').value.length<=8) {
    alert("minimum length of password is 8!!");
    return false;
  }
  var p1 = document.getElementById('pwd');
  var p2 = document.getElementById('pwd1');
  if(p1==p2){
    return true;
  }
  else {
    return false;
  }
}
