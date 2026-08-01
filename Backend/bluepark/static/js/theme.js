function changeTheme(){
    var iname = document.getElementById("mode").innerText;
    if(iname=="Light Mode"){
        document.getElementById("menu").style.background="#999696";
        //document.getElementById("menu-mid").style.color="black";
        //document.getElementById("menu-heading").style.color="black";
        document.getElementById("mode").innerText = "Dark Mode";
    }
    else if(iname=="Dark Mode")
    {
        document.getElementById("menu").style.background="red";
        document.getElementById("mode").innerText = "Light Mode";
    }
    console.log(iname)
}