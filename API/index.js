/*
DEV NOTE:

I have no clue what I am doing, but it works.
*/
const fs = require('fs');
const express = require('express');
const postgres = require('postgres');
const papago = require('papago');
var rp = require('request-promise');
const download = require('image-downloader')
require('dotenv').config();
const app = express();
var hateoasLinker = require('express-hateoas-links');
// const { parse } = require('dotenv/types');
app.use(hateoasLinker)
app.use(express.urlencoded());
app.use(express.json());
const port = process.env.API_PORT || 5454;
const host = process.env.POSTGRES_HOST
const database = process.env.POSTGRES_DATABASE
const user = process.env.POSTGRES_USER
const password = process.env.POSTGRES_PASSWORD
const translatePrivateKey = process.env.PRIVATE_KEY
const clientid = process.env.DISCORD_CLIENT_ID
const clientsecret = process.env.DISCORD_CLIENT_SECRET
const endpointauthorize = process.env.DISCORD_ENDPOINT_AUTHORIZE
const endpointtoken = process.env.DISCORD_ENDPOINT_TOKEN
const redirectlogin = process.env.REDIRECT_LOGIN
const scopes = process.env.DISCORD_SCOPES
const dbport = process.env.POSTGRES_PORT || 5432;
const folderLocation = process.env.FOLDER_LOCATION;
const sql = postgres({
	host: host,
	port: dbport,
	database: database,
	username: user,
	password: password
});
Translator = new papago.default(process.env.PAPAGO_CLIENT_ID, process.env.PAPAGO_CLIENT_SECRET);
const none = JSON.parse('[]')
var drive_js = require('./drive.js')
var path = require('path')
var currentlyWorking = 0


app.get('/', (req,res) => {
	res.send(`<h1>Public Endpoints:</h1>
		<br><br>
		<h2>
		GroupMembers:<br>
		/members   --- View information about all members <br>
		/members/:id   --- View information about a specific idol. <br>
		/groups   --- View information about all groups. <br>
		/groups/:id   --- View information about a specific group from their group id. <br>
		Disabled - /images   --- Provides links to the images of all idols. <br>
		Disabled - /images/:id   --- Provides links to the images of a certain idol's ID <br>
		<br><br>
		Dreamcatcher:<br>
		/dc/latest   --- Shows the latest post link from the dc app (ONLY DC MEMBERS)<br>
		/dc/latest/:membername   --- Shows the most recent post number from a specific member
		(:membername can be jiu, sua, siyeon, handong, yoohyeon, dami, gahyeon, or latest)<br>
		/dc/recent   --- Shows the most recent post number from the dc app (ALL USERS)<br>
		/dc/hd   --- Shows the HD Links for the DC MEMBERS from the DC APP<br>
		/dc/hd/:membername   --- Shows the HD Links for a certain dc member.
		(:membername can be jiu, sua, siyeon, handong, yoohyeon, dami, or gahyeon)<br>
		/dc/updates   --- Discord Channel IDs that receive DCAPP updates<br>

		Archive:<br>
		/archive/   --- Show the Drive Folder IDs that Irene auto archives. (ex: https://drive.google.com/drive/folders/:folderid )<br> 
		<br><br>
		</h2><br><br>

		<h1>Private Key Endpoints</h1>
		<h2>
		Translation:<br>
		/translate --- Post -> Send in 'text' to translate, 'src_lang', 'target_lang' as a body. Also send in the private API key as 'p_key'.<br>
		
		Groupmembers:<br>
		/photos/:idolID   --- Get redirected to an image of the Idol. Send in private API key as 'p_key' and send you DO NOT want group photos(0 or 1) as 'no_group_photos' (body). <br>
		</h2>
		`);
});


app.post('/photos/:id', async (req, res) =>{
	try{
	if (req.body.p_key == translatePrivateKey){
		while (currentlyWorking >= 4){
			// sleep for 1.5 seconds
			await sleep(1.5);
		}
		var fileLink = `${await getrandomimage(req.params.id, req.body.no_group_photo)}`;
		if (fileLink == 'undefined'){
			res.sendStatus(404);
			return;
		}
		currentlyWorking++;
		var fileId = fileLink.replace("https://drive.google.com/uc?export=view&id=", "");
		var x = await drive_js.drive.files.get(
			{
			fileId: fileId,
			alt: "media"
			})
		try{
			var allFiles = fs.readdirSync(folderLocation);
			if (Object.keys(allFiles).length > 50000){
				allFiles.forEach(deletedFile => {
					fs.unlink(folderLocation + deletedFile, (err) =>{
						if (err) {
							console.log(err);
						}
					})
				})
			}
		}
		catch(err){
			console.log(err);
		}
		var file_name = `${Math.floor((Math.random() * 1000000000000000000000000000) +1)}${(x.headers['content-type']).replace("/", ".")}`;
		var dest = fs.createWriteStream(`${folderLocation}${file_name}`);
		// var dest = fs.createWriteStream(`idol/${file_name}`);
		var final_image_link = `https://images.irenebot.com/idol/${file_name}/`;
		// console.log(drive_js.drive)
		try{
			await sql`
			INSERT INTO groupmembers.apiurl(driveurl, apiurl) VALUES(${fileLink}, ${final_image_link})
			`;}
		catch(err) {
			await sql`
			UPDATE groupmembers.apiurl SET driveurl = ${fileLink})
			`;
			console.log(err)
			return none;
		}
		drive_js.drive.files.get(
			{
			fileId: fileId,
			alt: "media",
			fields: "name"
			},
			{ responseType: "stream" },
			function(err, { data }) {
			data
				.on("end", () => {
					if (file_name.includes('.mp4') || file_name.includes('.webm')){
						res.send({"final_image_link": final_image_link, "location": folderLocation + file_name, "file_name": file_name, "original_link": fileLink}, 415)
					}
					else{
						res.redirect(final_image_link);
					}
					console.log(`Done - ${final_image_link}`);
				})
				.on("error", err => {
				console.log("Error during download", err);
				res.send('500: Internal Server Error', 500);
				})
				.pipe(dest);
		currentlyWorking--;
	})
		
	}
	else{
		res.send("Invalid p_key.", 403);
	}}
catch(err){
	res.send('500: Internal Server Error', 500);
}
}
)

app.get('/members', async (req, res) => {
	res.send(await getmembers());
});

app.get('/members/:id', async (req, res) => {
	res.send(await getspecificidol(req.params.id));
});

app.get('/groups', async (req, res) => {
	res.send(await getgroups());
});

app.get('/groups/:id', async (req, res) => {
	res.send(await getspecificgroup(req.params.id));
});

/*
app.get('/images', async (req, res) => {
	res.send(await getimages());
});


app.get('/images/:id', async (req, res) => {
	res.send(await getidolimages(req.params.id));
});
*/

app.get('/dc/latest', async (req, res) => {
	res.send(await getdcmemberpost("latest"));
});

app.get('/dc/latest/:membername', async (req, res) => {
	res.send(await getdcmemberpost(req.params.membername));
});

app.get('/dc/recent', async (req, res) => {
	res.send(await getdcrecent());
});

app.get('/dc/hd', async (req, res) => {
	res.send(await gethdlinks());
});

app.get('/dc/hd/:membername', async (req, res) => {
	res.send(await getmemberhdlinks(req.params.membername));
});

app.get('/dc/updates', async (req, res) => {
	res.send(await getdcupdates());
});

app.get('/archive', async (req, res) => {
	res.send(await getarchiveids());
});

app.post('/translate', async (req, res) => {
	if (req.body.p_key == translatePrivateKey){
		responsex = await Translator.translate(req.body.text, req.body.src_lang, req.body.target_lang).catch(responsex = []);
	}
	else{
		responsex = "Invalid p_key."
	}
	res.send(responsex);
});

app.get('/login', async (req, res) => {
	let request = (await send_discord_request(req.query.code));
	console.log(request);
	res.send(request);

});


async function getmembers(){
	try{
	 	return  await sql`
			SELECT id, fullname, stagename FROM groupmembers.member ORDER BY id
		`}
	catch(err) {
		return none;
	}
}

async function getgroups(){
	try{
		return await sql`
			SELECT groupid, groupname FROM groupmembers.groups
		`}
	catch(err) {
		return none;
	}
}

async function getimages(){
	try{
		return await sql`
			SELECT * FROM groupmembers.imagelinks
		`}
	catch(err) {
		return none;
	}
}

async function getidolimages(id, no_group_photos=0){
	try{
	    if (no_group_photos == 0){
	        return await sql`SELECT * FROM groupmembers.imagelinks WHERE memberid = ${id}`;
	    }
	    else{
		    return await sql`SELECT * FROM groupmembers.imagelinks WHERE memberid = ${id} AND groupphoto = ${0}`;
		}}
	catch(err) {
		return none;
	}
}

async function getrandomimage(id, no_group_photos){
	const idolLinks = await getidolimages(id, no_group_photos);
	var links = idolLinks[Math.floor(Math.random() * idolLinks.length)];
	try{
		return links.link;
	}
	catch{
		return 'undefined';
	}
}

async function getspecificgroup(id){
	try{
		return await sql`
			SELECT groupid, groupname FROM groupmembers.groups WHERE groupid = ${id}
		`}
	catch(err) {
		return none;
	}
	
}

async function getspecificidol(id){
	try{
		return await sql`
		SELECT id, fullname, stagename FROM groupmembers.member WHERE id = ${id}
		`}
	catch(err) {
		return none;
	}
}

async function getdcmemberpost(member_name){
	try{
		return await sql`
		SELECT * FROM dreamcatcher.dcurl WHERE member = ${member_name.toLowerCase()}
		`}
	catch(err) {
		return none;
	}
}

async function getdcrecent(){
	try{
		return await sql`
		SELECT * FROM dreamcatcher.dcpost
		`}
	catch(err) {
		return none;
	}
}

async function gethdlinks(){
	try{
		return await sql`
		SELECT * FROM dreamcatcher.dchdlinks ORDER BY postnumber
		`}
	catch(err) {
		return none;
	}
}

async function getmemberhdlinks(member_name){
	try{
		return await sql`
		SELECT * FROM dreamcatcher.dchdlinks WHERE member = ${member_name.toLowerCase()} ORDER BY postnumber
		`}
	catch(err) {
		console.log(err)
		return none;
	}
}

async function getdcupdates(){
	try{
		return await sql`
		SELECT * FROM dreamcatcher.dreamcatcher
		`}
	catch(err) {
		console.log(err)
		return none;
	}
}

async function getarchiveids(){
	try{
		return await sql`
		SELECT name, driveid FROM archive.channellist
		`}
	catch(err) {
		console.log(err)
		return none;
	}
}

async function translate_text(text, source, target){
	try{
		translated_text = Translator.translate(text, source, target).then();
	}
	catch(err){
		translated_text = none
	}
	return translated_text;
	return (Translator.translate(text, source, target)).text;
}

async function send_discord_request(code){
	options = {
		method: "POST",
		uri : endpointtoken,
		json : true,
		form : {
			'client_id': clientid,
			'client_secret': clientsecret,
			'grant_type': 'authorization_code',
			'code': code,
			'redirect_uri': redirectlogin,
			'scope': scopes
		},
		headers : {
			'Content-Type': 'application/x-www-form-urlencoded'
		}
	};
	rp(options)
	.then(function (parsedBody) {
		console.log(parsedBody);
		return (parsedBody);
		// POST succeeded...
	})
	.catch(function (err) {
		console.log(err);
		return (err);
		// POST failed...
	});
}

function sleep(ms) {
	return new Promise(resolve => setTimeout(resolve, ms));
}

app.listen(port, () => console.log(`API Listening on port ${port}`));
