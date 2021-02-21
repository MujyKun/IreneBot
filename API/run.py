from flask import Flask, request, Response, redirect

# expected import error. API is run as a standalone from server.py
# noinspection PyUnresolvedReferences, PyPackageRequirements
from resources.keys import c, private_keys, idol_folder, top_gg_webhook_key, db_conn
# noinspection PyUnresolvedReferences, PyPackageRequirements
from resources.drive import get_file_type, download_media

import random
import os.path

app = Flask(__name__)


@app.route('/members/', methods=['GET'])
def get_all_members():
    """Gets all full names and stage names of idols."""
    c.execute("SELECT id, fullname, stagename FROM groupmembers.member")
    all_members = {}
    for idol_id, full_name, stage_name in c.fetchall():
        all_members[idol_id] = {'full_name': full_name, 'stage_name': stage_name}
    return all_members


@app.route('/members/<idol_id>/', methods=['GET'])
def get_member(idol_id):
    """Get full name and stage name of an idol by it's id."""
    c.execute("SELECT fullname, stagename FROM groupmembers.member WHERE id=%s", (idol_id,))
    all_members = {}
    for full_name, stage_name in c.fetchall():
        all_members[idol_id] = {'full_name': full_name, 'stage_name': stage_name}
    return all_members


@app.route('/groups/', methods=['GET'])
def get_groups():
    """Get all group ids to group names."""
    c.execute("SELECT groupid, groupname FROM groupmembers.groups")
    all_groups = {}
    for group_id, group_name in c.fetchall():
        all_groups[group_id] = group_name
    return all_groups


# noinspection PyBroadException,PyPep8
@app.route('/groups/<group_id>/', methods=['GET'])
def get_group(group_id):
    """Get group name by group id"""
    c.execute("SELECT groupname FROM groupmembers.groups WHERE groupid=%s", (group_id,))
    group = c.fetchone()
    try:
        return {group_id: group[0]}
    except:
        return {}


@app.route('/photos/<idol_id>/list/', methods=['GET'])
def get_image_ids(idol_id):
    """Returns all image ids an idol has."""
    c.execute("SELECT id FROM groupmembers.imagelinks WHERE memberid=%s", (idol_id,))
    all_ids = {'ids': [current_id[0] for current_id in c.fetchall()]}
    return all_ids


# noinspection PyBroadException
@app.route('/photos/<idol_id>/', methods=['POST'])
def get_idol_photo(idol_id):
    """Download an idol's photo and redirect the user to the image link."""
    # check authorization
    if not check_auth_key(request.headers.get('Authorization')):
        # Invalid API Key
        return Response(status=403)

    # delete files after a certain amount exist in the directory.
    currently_existing_photos = os.listdir(idol_folder)
    if len(currently_existing_photos) > 150000:
        # noinspection PyPep8
        try:
            for file in currently_existing_photos:
                os.remove(file)
        except:
            pass

    try:
        allow_group_photos = request.args.get('allow_group_photos')
        # must be None. 0 is an alternative of allow_group_photos, so do not simplify.
        if allow_group_photos is None:
            allow_group_photos = 1

        if allow_group_photos:
            # get all types of photos from the idol.
            c.execute("SELECT id, link FROM groupmembers.imagelinks WHERE memberid=%s", (idol_id,))
        else:
            # only get photos that are not a group photo
            c.execute("SELECT id, link FROM groupmembers.imagelinks WHERE memberid=%s AND groupphoto=%s", (idol_id, 0))
        all_links = c.fetchall()
        if not all_links:
            # idol has no photos
            return Response(status=404)
        random_link = random.choice(all_links)
        return process_image(random_link)

    except Exception as e:
        print(e)
        return Response(status=500)


@app.route('/file/<image_id>/', methods=['POST'])
def get_image(image_id):
    # check authorization
    if not check_auth_key(request.headers.get('Authorization')):
        # Invalid API Key
        return Response(status=403)

    try:
        c.execute("SELECT link FROM groupmembers.imagelinks where id = %s", (image_id,))
        link = c.fetchone()
        if not link:
            return Response(status=404)
        return process_image([image_id, link[0]])
    except Exception as e:
        print(e)
        return Response(status=500)


@app.route('/webhook/', methods=['POST'])
def get_top_gg_vote():
    if not check_webhook_key(request.headers.get('Authorization')):
        # Invalid Webhook Key
        return Response(status=403)

    user_id = (request.get_json()).get('user')
    if not user_id:
        return Response(status=400)

    try:
        c.execute("DELETE FROM general.lastvoted WHERE userid = %s", (user_id,))
        c.execute("INSERT INTO general.lastvoted(userid) values(%s)", (user_id,))
        db_conn.commit()
        print(user_id, " has voted.")
        return Response(status=200)
    except Exception as e:
        print(e)
        return Response(status=500)


@app.route('/', methods=['GET'])
def get_default_route():
    return redirect("https://irenebot.com/api", code=308)


def check_webhook_key(key):
    """Check the Top.GG webhook key with an auth key"""
    if key:
        return key == top_gg_webhook_key


def check_auth_key(key):
    """Check if an authorization key is correct."""
    if key:
        return key in private_keys


def check_file_exists(file_name):
    """Check if a file exists."""
    return os.path.isfile(file_name)


def get_google_drive_id(link):
    """Get a google drive file id by the file url."""
    return link.replace("https://drive.google.com/uc?export=view&id=", "")


def process_image(link_info):
    # get information about the file from google drive
    file_db_id = link_info[0]
    file_url = link_info[1]
    google_drive_id = get_google_drive_id(file_url)
    file_type = get_file_type(google_drive_id)
    file_location = f"{idol_folder}{file_db_id}{file_type}"
    image_host_url = f"https://images.irenebot.com/idol/{file_db_id}{file_type}"
    print(f"Processing {image_host_url}.")
    file_data = {
        'final_image_link': image_host_url,
        'location': file_location,
        'file_name': f"{file_db_id}{file_type}"
    }
    # check if the file is already downloaded
    if not check_file_exists(file_location):
        # download the file
        download_media(google_drive_id, file_location)

    if '.mp4' in file_type or '.webm' in file_type:
        # return a json of the video info
        return file_data, 415

    return redirect(image_host_url, code=308)


app.run(port=5454)

