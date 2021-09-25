var save = document.getElementById("tb").cloneNode(true);
function get(url) {
  var xhr = new XMLHttpRequest();
  xhr.open("GET", url, true);

  xhr.onload = function () {
    //let val = document.getElementById("elem1").value;
    var val = xhr.response;
    if (val == "[]") alert("Нет информации по этому человеку");
    else {
      let json = JSON.parse(val);
      let key = Object.keys(json[0]);
      console.log(key);
      setTableNames(key);
      setTableVal(json);
    }
    // Запрос завершён. Здесь можно обрабатывать результат.
  };

  xhr.send(null);
}
but_a.onclick = function () {
  get("/getMarks");
};
but_s.onclick = function () {
  let val = document.getElementById("elem1").value;
  get("/getMarks?name=" + val);
};
let flag = true;

function setTableNames(keys) {
  let tab = document.getElementById("tb");
  tab.innerHTML = "";
  let row = document.createElement("tr");
  for (let v in keys) {
    let tmp = document.createElement("td");
    let text = document.createTextNode(keys[v]);
    tmp.appendChild(text);
    row.appendChild(tmp);
  }
  tab.appendChild(row);
  if (flag) row.style.backgroundColor = "dimgrey";
  else row.style.backgroundColor = "silver";
  flag = !flag;
}
function setTableVal(arr) {
  let tab = document.getElementById("tb");
  for (let i in arr) {
    let row = document.createElement("tr");
    for (let j in arr[i]) {
      let col = document.createElement("td");
      let text = document.createTextNode(arr[i][j]);
      col.appendChild(text);
      row.appendChild(col);
    }
    tab.appendChild(row);
    if (flag) row.style.backgroundColor = "dimgrey";
    else row.style.backgroundColor = "silver";
    flag = !flag;
  }
}
