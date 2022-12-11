@app.route('/new-game/', methods=['GET', 'POST'])
def newGame():
    userid = session['name']
    userid2 = "hello2"
    dbCur = db.connection.cursor(MySQLdb.cursors.DictCursor)
    logging.debug("user: %s is requesting to join new game", userid)

    logging.debug("Making sure user does not have an active game already")
    activeGames = Games.get_all_active_games_for_single_user_id(dbCur, userid)

    if activeGames != None:
        logging.info('User: %s is requesting a new game but already has an active one running', userid)
    else:
        logging.debug('User has no active games currently. Creating a new game')
        # checking if anyone else waiting to play...
        opponent = dbCur.execute("SELECT * from login WHERE waiting = 1")

        if opponent == None:
            # Currently no waiting players, so waiting for opponent on open socket.
            dbCur.execute("UPDATE login set waiting = 1 WHERE username = %s", opponent)
            db.connection.commit()
            msg="User waiting for game play. Open socket connection"
            return render_template("game.html", userid=userid, msg=msg)

        else:
            # We found a match thus we are going to join players in a room for game play
            tmp = dbCur.fetchone()
            opponent = tmp['username']

            dbCur.execute("UPDATE login set waiting = 0 WHERE username = %s", (opponent,))
            db.connection.commit()
            dbCur.execute("UPDATE login set waiting = 0 WHERE username = %s", (userid,))
            db.connection.commit()

            logging.info("Join player %s and opponent waiting: %s " % (userid, opponent))

            gameId = Games.add_game(dbCur, userid, userid2)
            db.connection.commit()

            newGame = Games.get_game_by_id(dbCur, gameId)
            playerStats = GamePlay.generate_new_game_stats(dbCur, newGame)
            return render_template('game.html', gameStatus='newGame', playerStats=playerStats, gameID=gameID)
