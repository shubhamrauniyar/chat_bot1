const express = require('express');
const app = express();
const mongoose = require('mongoose');
const bodyparser = require("body-parser");

mongoose.connect('mongodb+srv://shubham024:aman062@cluster0.ujboz.mongodb.net/whatsapp_Db?retryWrites=true&w=majority', {
  useNewUrlParser: true,
  useUnifiedTopology: true
}, function(err) {
  if (!err) {
    console.log("connected to database");
  }

});
app.use(bodyparser.urlencoded({
  extended: true
}));
app.set("view engine", "ejs");
app.use(express.static('Public'));
const com = new mongoose.Schema({
  mobileno: String,
  dept: String,
  uniqid: Number,
  status: String,
});
const con = new mongoose.Schema({
  mobileno: String,
  dept: String,
  uniqid: Number,
  status: String,
});
const sug= new mongoose.Schema({
  mobileno:String,
  suggestion:String,
});
const Complain = mongoose.model('complaintsdb', com, 'complaintsdb');
const Connection= mongoose.model('connectionsdb',con,'connectionsdb');
const Suggestion=mongoose.model("suggestiondb",sug,"suggestiondb");
app.get("/", function(req, res) {
  res.render("home");

})
app.route("/complaint").post((req, res) => {

  Complain.find(function(err, data) {
    if (!err) {

      res.render("complaint", {
        arr: data
      });
    }
  })

}).get(
  (req, res) => {

    Complain.find(function(err, data) {
      if (!err) {

        res.render("complaint", {
          arr: data
        });
      }
    })

  }
)
app.route("/connection").post(function(req,res){
  Connection.find(function(err, data) {
    if (!err) {

      res.render("connection", {
        arr: data
      });
    }
  })

}).get((req, res) => {

  Connection.find(function(err, data) {
    if (!err) {

      res.render("connection", {
        arr: data
      });
    }
  })

});

app.post("/complaintstatus", function(req, res) {

  var resa = req.body.status.split(",");

  Complain.updateOne({mobileno:resa[1]}, {  status:resa[0]},function(){
    res.redirect("/complaint");
  });


})


app.post("/connectionstatus",function(req,res){
  var resa = req.body.status.split(",");

  Connection.updateOne({mobileno:resa[1]}, {  status:resa[0]},function(){
    res.redirect("/connection");
  });
})
app.post("/feedback",function(req,res){
  Suggestion.find(function(err, data) {
    if (!err) {
      
      res.render("feedback", {
        arr: data
      });
    }
  })
})
app.listen(3000, function(err) {
  if (!err) {
    console.log("server started at port 3000");
  }
})
