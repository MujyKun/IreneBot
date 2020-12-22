const express = require('express');
const app = express();
const favicon = require('serve-favicon');
const port = process.env.SITE_PORT || 4848;

// set the public static folder.
app.use(express.static(__dirname + '/public'));


app.get('/', function(req, res){
    res.sendFile(__dirname + '/index.html');
})

app.get('/commands', function(req, res){
    // A list of all IreneBot Commands.
    res.sendFile(__dirname + '/commands.html');
})

app.get('/statistics', function(req, res){
    // DataDog Statistics of IreneBot.
    res.sendFile(__dirname + '/statistics.html');
})

app.get('*', function(req, res){
    res.redirect('/');
})





app.listen(port, () => console.log(`Main Site Listening on port ${port}`));