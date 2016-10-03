
function RepeatIt()
{
document.getElementById('div1').style.display = "none";
document.getElementById('div2').style.display = "inline";
document.getElementById('answer').style.display = "inline";
}


function ShowMenu(id_in)
{
var id=id_in.toString();
var menu_id='menu_' + id;
document.getElementById(menu_id).style.display = "inline";
}

function HideMenu(id_in)
{
var id=id_in.toString();
var menu_id='menu_' + id;
document.getElementById(menu_id).style.display = "none";
}

function ShowDir(id_in)
{
var id=id_in.toString();
var menu_id='dir_' + id;
document.getElementById(menu_id).style.display = "inline";
}

function HideDir(id_in)
{
var id=id_in.toString();
var menu_id='dir_' + id;
document.getElementById(menu_id).style.display = "none";
}

function ShowShare(id_in)
{
var id=id_in.toString();
var menu_id='share_' + id;
document.getElementById(menu_id).style.display = "inline";
}

function HideShare(id_in)
{
var id=id_in.toString();
var menu_id='share_' + id;
document.getElementById(menu_id).style.display = "none";
}

