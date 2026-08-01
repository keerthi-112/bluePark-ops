function validate(){
  var uname = document.getElementById('username');
  var letters = /^[A-Za-z]+$/;
  if(uname.value.trim()==""||!uname.value.test(letters))
  {
     alert("Please Enter valid name!");
     return false;
  }
  if(uname.value.length<3||uname.value.length>16)
  {
    alert("Length of your name should be in the range of 3 and 16!!!");
    return false;
  }
  var mail = document.getElementById('email');
  if(mail.value.trim()=="")
  {
    alert("Please Enter your Mail-id");
    return false;
  }
  var regxmail = /^\S+@\S+\.\S+$/;
  if(!regxmail.test(mail.value)){
    alert("Enter the valid email");
    return false;
  }
  var heard = document.querySelector( 'input[name="heard"]:checked');
  if(heard == null){
    alert("Select all the options!");
    return false;
  }
  var purchase = document.querySelector( 'input[name="purchase"]:checked');
  if(purchase == null){
    alert("Select all the options!");
    return false;
  }
  var feedback = document.getElementById('feedback');
  if(feedback.value==''){
    alert("Please enter your response in feedback field!!");
    return false;
  }
  if(document.getElementById('rating').value==0){
    alert("Minimum rating you can provide is 1 !");
    return false;
  }
  if(document.getElementById('favourite').value.length<=3||document.getElementById('favourite').value.length>100){
    alert("Please let us know your favourite food items within length of 100 characters!!");
    return false;
  }
}
