const express = require("express");
const app = express();
const port = 3000;

var sqlite3 = require("sqlite3").verbose();
var db = new sqlite3.Database("db.db");

app.use(express.static("public"));

app.get("/getMarks", (req, res) => {
  console.log(req.query.name);
  if (req.query.name == undefined) {
    db.all("SELECT s.fio FROM student s", function (err, rows) {
      if (err) {
        console.log(err);
      }

      console.log(rows);
      res.send(rows);
    });
  } else {
    db.all(
      "SELECT s.fio, su.name, m._mark FROM student s, Subj su, Marks m WHERE s.id=m.studentId AND m.subjId=su.id AND s.fio=?",
      [req.query.name],
      function (err, rows) {
        if (err) {
          console.log(err);
        }

        console.log(rows);
        res.send(rows);
      }
    );
  }
});

app.listen(port, () => {
  console.log(`Example app listening at http://localhost:${port}`);
});
