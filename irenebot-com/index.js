const express = require('express');
const app = express();
app.use(express.urlencoded());
app.use(express.json());
require('dotenv').config();
const papago = require('papago');
Translator = new papago.default(process.env.PAPAGO_CLIENT_ID, process.env.PAPAGO_CLIENT_SECRET);
const translatePrivateKeys = (process.env.PRIVATE_KEYS).split(',');
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

app.get('/api', function(req, res){
    // API Info for api.irenebot.com
    res.sendFile(__dirname + '/api.html');
})

app.post('/jsonifyform', function(req, res){
    // addgroup and addidol json for command usage.
    res.send(req.body);
})

app.post('/translate', async (req, res) => {
    authorization = req.headers.authorization;
    textToTranslate = req.body.text;
    sourceLanguage = req.body.src_lang;
    targetLanguage = req.body.target_lang;
	if (checkKey(authorization)){
		try{
            responsex = await Translator.translate(textToTranslate, sourceLanguage, targetLanguage).catch(responsex = []);
		}
		catch(err){
			responsex = [];
		}
	}
	else{
		responsex = "Invalid p_key.";
	}
    return res.send(responsex);
});

app.get('*', function(req, res){
    res.redirect('/');
})

function checkKey(userKey){
	return (translatePrivateKeys.indexOf(userKey) > -1);

}

app.listen(port, () => console.log(`Main Site Listening on port ${port}`));