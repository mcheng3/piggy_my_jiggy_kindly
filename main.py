from flask import Flask, flash, render_template, request, session, redirect, url_for
import sqlite3
from utils import api, database, auth
import time, json

app = Flask(__name__)
app.secret_key = "THIS IS NOT SECURE"


#---------------------------------------
# FRONT PAGE
# about information; current top 10 teams
#---------------------------------------
@app.route('/')
def root():
    return render_template("index.html",
                               loggedin = auth.is_logged_in(),
                               top_ten = ["a", "b", "c", "d", "e",
                                          "f", "g", "h", "i", "j"])


#---------------------------------------
# LOGIN PAGE
# authenticate user
#---------------------------------------
@app.route('/login', methods = ['POST', 'GET'])
def login():
    # checks for post method to respond to submit button
    if request.method == 'POST':
        # uses the database method to check the login
        # print "username: " + request.form['usr'] + "\npassword: " + request.form['pwd']
        log_res = auth.login( request.form['usr'], request.form['pwd'] )
        if log_res == 0 :
            return redirect(url_for('root'))
        else:
            return redirect(url_for('login'))
    # just render normally if no post
    else:
        return render_template("login.html", loggedin=auth.is_logged_in())

#---------------------------------------
# SIGN UP PAGE
# add user to database
#---------------------------------------
@app.route('/signup', methods = ['POST', 'GET'])
def signup():
    # CREATE ACCOUNT
    if request.method == 'POST':
        cr_acc_res = auth.sign_up( request.form['usr'], request.form['pwd'] )
        # if successful
        if cr_acc_res == 0:
            flash("Account created!")
            return redirect( url_for('login') )
        # if username already exists
        if cr_acc_res == 1:
            return redirect( url_for('signup') )
    return render_template("signup.html", loggedin=auth.is_logged_in())

#---------------------------------------
# LOGOUT PAGE
#---------------------------------------
@app.route('/logout')
def logout():
    auth.logout();
    return redirect( url_for("root") )


#---------------------------------------
# PROFILE PAGE
# shows user info, created teams, and upvoted teams
#---------------------------------------
@app.route('/profile')
def profile():
    fav_list = database.return_favorites(session["user"])[0][0].split(",")
    fav_teams = list()
    for team in fav_list:
        if team != '':
            fav_teams.append(database.find_team(int(team)))
    return render_template("profile.html",
                               user = session['user'],
                               loggedin = auth.is_logged_in(),
                               fav_teams = fav_teams,
                               my_teams = database.get_teams(session['user']))


#---------------------------------------
# SEARCH PAGE
# shows teams related to search
#---------------------------------------
@app.route('/search', methods = ['POST', 'GET'])
def search():
    print(request.args['search'])
    results = database.search_name(request.args['search'])
    return render_template("search.html",
                           results = results,
                           loggedin = auth.is_logged_in())


#---------------------------------------
# CREATE PAGE
# create a new team
#---------------------------------------
@app.route('/createteam', methods = ['POST', 'GET'])
def create():
    if request.method == 'POST':
        database.update_team(int(request.args['id']), request.form['teamname'], request.form['teamdesc'], request.form['teamvers'], "NONE", "NONE")
        return redirect(url_for("root"))
    else:
        new_teamid = database.next_teamid(session['user'])
        return render_template("edit_team.html",
                               action = "createteam?id=" + str(new_teamid),
                               created = "False",
                               new_teamid = new_teamid,
                               loggedin = auth.is_logged_in())

#---------------------------------------
# VIEW TEAM
# view team details
#---------------------------------------
@app.route('/viewteam', methods = ['POST', 'GET'])
def view_team():
    if request.method == 'POST':
        if 'edit' in request.form:
            return redirect(url_for("edit_team", id = request.args['id']))
        elif 'favorite' in request.form:
            if 'user' in session:
                id = request.args["id"]
                database.add_favorite(session["user"], id)
                return redirect(url_for("view_team", id = id))
            else:
                return redirect(url_for('login'))
        else:
            id = request.args["id"]
            #remove favorite
            return redirect(url_for("view_team", id = id))
    else:
        id = int(request.args["id"])
        team = database.find_team(id)
        mine = 'user' in session and session["user"] == team[1]
        faves = list()
        if 'user' in session:
            faves = database.return_favorites(session["user"])[0][0].split(",")
        return render_template("view_team.html",
                               loggedin = auth.is_logged_in(),
                               team = team,
                               favorited = str(id) in faves,
                               mine = mine,
                               poke_teams = ["yea", "yeas", "sdfa"])

#---------------------------------------
# EDIT PAGE
# edit team pokemon members overall
#---------------------------------------
@app.route('/editteam', methods = ['POST', 'GET'])
def edit_team():
    if request.method == 'POST':
        database.update_team(request.args['id'], request.form['teamname'], request.form['teamdesc'], request.form['teamvers'], "NONE", "NONE")
        return redirect(url_for("view_team", id = request.args['id']))
    else:
        id = int(request.args["id"])
        team = database.find_team(id)
        pokemon = team[8].split(",")
        pokedict2 = {}
        for poke in pokemon:
            print poke
            if poke != '':
                pokedict2[str(poke)] = database.return_pkmn(int(poke))[0][1]
        print pokedict2
        return render_template("edit_team.html",
                               loggedin = auth.is_logged_in(),
                               action = "editteam?id=" + str(team[0]),
                               created = True,
                               pokemon = pokedict2,
                               team = team)

#---------------------------------------
# CREATE POKEMON
# add new pokemon to team
#---------------------------------------
@app.route('/createpokemon', methods = ['POST', 'GET'])
def create_pokemon():
    if request.method == 'POST':
        teamid = request.args['id']
        print teamid
        moves = ""
        for x in range(0, 3):
            moves += (request.form['move' + str(x)]) + ", "
        moves += request.form['move3']
        database.create_poke(request.form['pokemon'], "N/A", 0, request.form['ability'], moves, "N/A", "N/A", int(teamid))
        return redirect(url_for("edit_team", id = request.args['id']))
    else:
        teamid = request.args['teamid']
        return render_template("edit_pokemon.html",
                               loggedin = auth.is_logged_in(),
                               action = "createpokemon?id=" + str(teamid))


#---------------------------------------
# EDIT POKEMON
# edit specific pokemon traits
#---------------------------------------
@app.route('/editpokemon', methods = ['POST', 'GET'])
def edit_pokemon():
    if request.method == 'POST':
        print request.args['id']
        teampkmn = request.args['id'].split(",")
        moves = ""
        for x in range(0, 3):
            moves += (request.form['move' + str(x)]) + ", "
        moves += request.form['move3']
        database.update_poke(int(teampkmn[0]), request.form['pokemon'], "N/A", 0, request.form['ability'], moves, "N/A", "N/A")
        return redirect(url_for("edit_team", id=int(teampkmn[1])))
    else:
        #you're going to need the id of the pokemon and the team
        return render_template("edit_pokemon.html",
                               loggedin = auth.is_logged_in(),
                               action = "editpokemon?id=" + request.args['pkmnid'])


@app.route("/pokedata")
def pokedata():
    data = request.args.get("name")
    results = api.search_poke(data)
    print results
    moves = []
    print results["moves"]
    for each in results["moves"]:
        moves.append(each["move"]["name"])
    print moves
    abilities = []
    for each in results["abilities"]:
        abilities.append(each["ability"]["name"])
    response = {'img': results["sprites"]["front_default"], 'moves': moves, "type": results["types"], 'abilities': abilities}
    return json.dumps(response)

if __name__ == "__main__":
    app.debug = True
    app.run()
