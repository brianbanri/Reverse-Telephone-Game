import pyaudio

import wave
import os
import shutil
import threading
from time import sleep
import binascii

import Pyro4
import Pyro4.naming
import socket

import click
from colorama import Fore, Back
from colorama import init as colorama_init
from art import text2art
from tqdm import trange


# Globals Variables for Audio Setup
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 512
RECORD_SECONDS = 3
audio = pyaudio.PyAudio()
promptingDelay = 1
FILE_NUM = 0

# Globals for the Server Thread
players = []
game_start = 0

#Beginning of CLUI
os.system('mode con: cols=170 lines=40')
click.clear()
colorama_init(autoreset=True)
Art = text2art("                                               WELCOME", font='big')
print(f"{Fore.LIGHTGREEN_EX}{Art}")

class Player:
  def __init__(self, name, id):
    self.name = name
    self.id = id

def waitForFile(file_path):
	while(os.path.exists(file_path) != 1):
		pass

@Pyro4.expose
class ServerHost(object):
    def register(self, player_name):
    	players.append(player_name)
    	return players.index(player_name)

    def getPlayerList(self):
    	return players

    def startGame(self):
    	global game_start
    	game_start = 1

    def ready(self):
    	return game_start

    def writeInitPhrase(self, phrase, playerID):
        fp = open('./hostedGame/game'+str(playerID)+'/init-phrase.txt', 'w')
        fp.write(phrase)
        fp.close()

    def writeFinalGuess(self, phrase, playerID, roundNumber):
        file_path = './hostedGame/game'+str((playerID+roundNumber-1)%len(players))+'/'+'final-guess.txt'
        fp = open(file_path, 'w')
        fp.write(phrase)
        fp.close()

    def getInitPhrase(self, game):
        fp = open('./hostedGame/game'+str(game)+'/init-phrase.txt', 'r')
        phrase = fp.read()
        fp.close()
        return phrase


    def getFinalGuess(self, game):
        file_path = './hostedGame/game'+str(game)+'/'+'final-guess.txt'

        wait_for_file_thread = threading.Thread(target=waitForFile, args=(file_path,), daemon=True)
        wait_for_file_thread.start()
        wait_for_file_thread.join()

        fp = open(file_path, 'r')
        phrase = fp.read()
        fp.close()
        return phrase

    def getAudio(self, game, round, reverse):
        if (reverse):
            file_path = './hostedGame/game'+str(game)+'/'+str(round+1)+'-reverse.wav'

            wf = wave.open(file_path, 'rb')
            data = wf.readframes(CHUNK)
            b = bytearray()
            while len(data) > 0:
            	b.extend(data)
            	data = wf.readframes(CHUNK)

            #b = ''.join(chr(x) for x in b)
            hex_data = binascii.hexlify(b)
            str_data = hex_data.decode('utf-8')
        else:
            file_path = './hostedGame/game'+str(game)+'/'+str(round+1)+'.wav'
            wf = wave.open(file_path, 'rb')
            data = wf.readframes(CHUNK)
            b = bytearray()
            while len(data) > 0:
            	b.extend(data)
            	data = wf.readframes(CHUNK)
            #b = ''.join(chr(x) for x in b)
            hex_data = binascii.hexlify(b)
            str_data = hex_data.decode('utf-8')

        wf.close()

        return str_data


    def get_round_data(self, playerID, roundNumber):
    	if (roundNumber == 2):
    		file_path = './hostedGame/game'+str((playerID+1)%len(players))+'/init-phrase.txt'

    		wait_for_file_thread = threading.Thread(target=waitForFile, args=(file_path,), daemon=True)
    		wait_for_file_thread.start()
    		wait_for_file_thread.join()
			
    		f = open(file_path, "r")
    		phrase = f.read()
    		f.close()
    		return phrase
    	elif (roundNumber < len(players) + 1):
            
            if (roundNumber == len(players) and len(players) % 2 == 1):
                file_path = './hostedGame/game'+str((playerID+roundNumber-1)%len(players))+'/'+str(roundNumber-1)+'.wav'
            else:
                file_path = './hostedGame/game'+str((playerID+roundNumber-1)%len(players))+'/'+str(roundNumber-1)+'-reverse.wav'

            
            wait_for_file_thread = threading.Thread(target=waitForFile, args=(file_path,), daemon=True)
            wait_for_file_thread.start()
            wait_for_file_thread.join()
            

            wf = wave.open(file_path, 'rb')
            data = wf.readframes(CHUNK)
            b = bytearray()
            while len(data) > 0:
            	b.extend(data)
            	data = wf.readframes(CHUNK)
            

            #b = ''.join(chr(x) for x in b)
            hex_data = binascii.hexlify(b)
            str_data = hex_data.decode('utf-8')
            

            wf.close()

            return str_data

    def send_audio_round_data(self, data):
    	playerID = data[0]
    	roundNumber = data[1]
    	audioStr = data[2]
    	audioStr = binascii.unhexlify(audioStr.encode('utf-8'))
    	waveFile = wave.open('./hostedGame/game'+str((playerID+roundNumber-1)%len(players))+'/'+str(roundNumber)+'.wav', 'wb')
    	waveFile.setnchannels(CHANNELS)
    	waveFile.setsampwidth(audio.get_sample_size(FORMAT))
    	waveFile.setframerate(RATE)
    	waveFile.writeframes(audioStr)
    	waveFile.close()

    	wf = wave.open('./hostedGame/game'+str((playerID+roundNumber-1)%len(players))+'/'+str(roundNumber)+'.wav', 'rb')

    	stream = audio.open(
    		format = audio.get_format_from_width(wf.getsampwidth()),
    		channels = wf.getnchannels(),
    		rate = wf.getframerate(),
    		output = True
    	)

    	recording = []
    	data = wf.readframes(CHUNK)
    	while len(data) > 0:
    		data = wf.readframes(CHUNK)
    		recording.append(data)
    	wf.close()
    	recording = recording[::-1]
    	waveFile = wave.open('./hostedGame/game'+str((playerID+roundNumber-1)%len(players))+'/'+str(roundNumber)+'-reverse'+'.wav', 'wb')
    	waveFile.setnchannels(CHANNELS)
    	waveFile.setsampwidth(audio.get_sample_size(FORMAT))
    	waveFile.setframerate(RATE)
    	waveFile.writeframes(b''.join(recording))
    	waveFile.close()
    	stream.close()

def start_name_server():
    Pyro4.naming.startNSloop(host="0.0.0.0")

def start_server_host():
	daemon = Pyro4.Daemon(host=socket.gethostbyname(socket.gethostname()))                # make a Pyro daemon
	ns = Pyro4.locateNS()                  # find the name server
	uri = daemon.register(ServerHost)   # register the greeting maker as a Pyro object
	ns.register("reversetelephone.serverhost", uri)   # register the object with a name in the name server

	daemon.requestLoop()                   # start the event loop of the server to wait for calls


def waitingBar(seconds):
	for i in trange(seconds*10):
		sleep(0.1)

# Function that puts the players on the title screen to start or join a game
def titleScreen():
    while(1):
        resetGameVariables()
        clearConsole()

        # UI Prompt
        titleScreen = text2art("                       WELCOME                   TO \nREVERSE TELEPHONE GAME", font='big')
        print(f"{Fore.LIGHTGREEN_EX}{titleScreen}")
        sleep(promptingDelay)
        print(Fore.LIGHTRED_EX + "Type \"Start Local Game\" to start a new game on this device")
        print(Fore.LIGHTRED_EX + "Type \"Host Game\" to host a new game")
        print(Fore.LIGHTRED_EX + "Type \"Join Game\" to join an existing game")

        # Takes user input and lets the user continue when a valid input is given
        user_input = ""
        while(not (user_input.lower() in ["host game", "join game", "start local game"])):
        	user_input = input()
        print()

        # Starts the program for the following selection
        if user_input.lower() == "host game":
        	host_game()
        elif user_input.lower() == "join game":
        	join_game()
        elif user_input.lower() == "start local game":
        	start_local_game()

def start_local_game():
	clearConsole()

	if (os.path.exists("./localGame")):
		shutil.rmtree("./localGame", ignore_errors=False, onerror=None)
		

	os.makedirs("./localGame")

	print(Fore.LIGHTRED_EX + "Starting Local Game...\n")

	waitingBar(1)

	sleep(promptingDelay)
	print()
	print(Fore.LIGHTRED_EX + "Enter number of players:")
	player_count = int(input())
	print()
	if(player_count < 4):
		print(Fore.LIGHTRED_EX +"You need 4 or more players to play this game.")
		sleep(promptingDelay)
		print(Fore.LIGHTRED_EX +"Exiting to title screen...")
		shutil.rmtree("./localGame", ignore_errors=False, onerror=None)
		titleScreen()
	else:
		start_game(player_count)
		shutil.rmtree("./localGame", ignore_errors=False, onerror=None)

def createGameDirectories():
	for i in range(len(players)):
		os.makedirs("./hostedGame/game%d" %i)

def createLocalDirectory(playerID):
	if (os.path.exists("./%d" %playerID)):
		shutil.rmtree("./%d" %playerID, ignore_errors=False, onerror=None)

	os.makedirs("./%d" %playerID)

def resetGameVariables():
    global FILE_NUM
    FILE_NUM = 0
    global players
    players = []
    global game_start
    game_start = 0

def host_game():
    clearConsole()

    if (os.path.exists("./hostedGame")):
    	shutil.rmtree("./hostedGame", ignore_errors=False, onerror=None)
    	

    os.makedirs("./hostedGame")

    print(Fore.LIGHTRED_EX + "Start Hosting Game...\n")

    waitingBar(1)

    sleep(promptingDelay)
    print()
    print(Fore.LIGHTRED_EX + "Enter your name:")
    player_name = input()
    print()
    clearConsole()

    print("Starting up server... Please tell your players to wait until you see the lobby to have them join.")

    # Start Pyro NameServer
    name_server_thread = threading.Thread(target=start_name_server, daemon=True)
    name_server_thread.start()

    # Give time for the nameserver to start
    sleep(2)
    clearConsole()
    print("Starting up server... Please tell your players to wait until you see the lobby to have them join.")

    # Start Pyro ServerHost
    server_host_thread = threading.Thread(target=start_server_host, daemon=True)
    server_host_thread.start()

    # Give time for the server host to start
    sleep(10)

    game_lobby(player_name)

    #clean up previous game files
    shutil.rmtree("./hostedGame", ignore_errors=False, onerror=None)


def join_game():
	clearConsole()

	print(Fore.LIGHTRED_EX + "Joining Game...\n")

	waitingBar(1)

	sleep(promptingDelay)
	print()
	print(Fore.LIGHTRED_EX + "Enter your name:")
	player_name = input()
	print()

	game_lobby(player_name)

def print_player_list(players):
	clearConsole()
	print("Players:\n")
	for i in range(len(players)):
		print(i, players[i])


def game_lobby(player_name):
	
    serverhost = Pyro4.Proxy("PYRONAME:reversetelephone.serverhost")    # use name server object lookup uri shortcut
    playerInfo = Player(player_name, serverhost.register(player_name))
    createLocalDirectory(playerInfo.id)

    print_player_list(serverhost.getPlayerList())
    if(playerInfo.id == 0):
    	print("\n\nType 'start game' to start the game (4+ players required) or press enter to refresh the player list.")
    	user_input = ""
    	while(user_input != "start game"):
    		print_player_list(serverhost.getPlayerList())
    		print("\n\nType 'start game' to start the game (4+ players required) or press enter to refresh the player list.")
    		user_input = input().lower()
    	serverhost.startGame()
    	createGameDirectories()
    else:
        print("\n\nType 'ready' when host starts game (4+ players required) or press enter to refresh the player list.")
        user_input = ""
        while(user_input != "ready" or serverhost.ready() != 1):
            print_player_list(serverhost.getPlayerList())
            print("\n\nType 'ready' when host starts game (4+ players required) or press enter to refresh the player list.")
            if(serverhost.ready() != 1):
                print("\nHost is not ready.")
            user_input = input().lower()

    start_multidevice_game(playerInfo, serverhost)
    shutil.rmtree("./%d" %playerInfo.id, ignore_errors=False, onerror=None)

    user_input = ""
    print("Type 'end game' once every player gets to view the games.")
    if(playerInfo.id == 0):
        while(user_input != "end game"):
            user_input = input().lower()


def start_multidevice_game(playerInfo, serverhost):
    player_count = len(serverhost.getPlayerList())

    round_counter = 0

    round_counter += 1
    multidevice_round1(playerInfo, serverhost)

    round_counter += 1
    multidevice_round2(playerInfo, serverhost)

    round_counter += 1
    while round_counter < player_count:
        if round_counter % 2 == 1:
            multidevice_reverse_round(playerInfo, serverhost, round_counter)
            round_counter += 1
        else:
            multidevice_interpret_round(playerInfo, serverhost, round_counter)
            round_counter += 1

    multidevice_guess_round(playerInfo, serverhost, round_counter)

    multidevice_spectate_games(serverhost, player_count, serverhost.getPlayerList(), playerInfo)

def multidevice_round1(playerInfo, serverhost):
	clearConsole()
	print(Fore.LIGHTRED_EX +"%s enter a word:" %playerInfo.name)
	phrase = input()
	serverhost.writeInitPhrase(phrase, playerInfo.id)

def multidevice_round2(playerInfo, serverhost):
    clearConsole()
    print("Waiting for other players...")
    data = serverhost.get_round_data(playerInfo.id, 2)
    clearConsole()
    phrase = data

    print(Fore.LIGHTRED_EX + "Record yourself saying this word.")
    sleep(promptingDelay)
    print(phrase)
    print()
    sleep(promptingDelay)
    print(Fore.LIGHTRED_EX +"Ready to record?")
    ready_check([playerInfo.name], 0)
    local_record_audio(playerInfo.id)
    prep_send_audio_round_data(playerInfo, serverhost, 2)
    print()

def load_audio_string_to_wave(audioStr, playerInfo):
    audioStr = binascii.unhexlify(audioStr.encode('utf-8'))
    waveFile = wave.open("./%d/audio-recording.wav" %playerInfo.id, 'wb')
    waveFile.setnchannels(CHANNELS)
    waveFile.setsampwidth(audio.get_sample_size(FORMAT))
    waveFile.setframerate(RATE)
    waveFile.writeframes(audioStr)
    waveFile.close()

def multidevice_reverse_round(playerInfo, serverhost, round_counter):
    clearConsole()
    print("Waiting for other players...")
    audioStr = serverhost.get_round_data(playerInfo.id, round_counter)
    clearConsole()

    load_audio_string_to_wave(audioStr, playerInfo)

    print(Fore.LIGHTRED_EX +"Record yourself repeating the what you will hear.")
    ready_check([playerInfo.name], 0)
    local_play_audio(playerInfo.id)

    print(Fore.LIGHTRED_EX +"Type 'replay' to re-hear the audio, or just press enter to start recording.")
    localReplayAudioLoop(playerInfo.id)

    local_record_audio(playerInfo.id)

    prep_send_audio_round_data(playerInfo, serverhost, round_counter)
    print()
	

def multidevice_interpret_round(playerInfo, serverhost, round_counter):
    clearConsole()
    print("Waiting for other players...")
    audioStr = serverhost.get_round_data(playerInfo.id, round_counter)
    clearConsole()

    audioStr = binascii.unhexlify(audioStr.encode('utf-8'))
    waveFile = wave.open("./%d/audio-recording.wav" %playerInfo.id, 'wb')
    waveFile.setnchannels(CHANNELS)
    waveFile.setsampwidth(audio.get_sample_size(FORMAT))
    waveFile.setframerate(RATE)
    waveFile.writeframes(audioStr)
    waveFile.close()

    print(Fore.LIGHTRED_EX +"Record your best guess of what the original word was after hearing the reversed audio.")
    ready_check([playerInfo.name], 0)
    local_play_audio(playerInfo.id)

    print(Fore.LIGHTRED_EX +"Type 'replay' to re-hear the audio, or just press enter to start recording.")
    localReplayAudioLoop(playerInfo.id)

    local_record_audio(playerInfo.id)

    prep_send_audio_round_data(playerInfo, serverhost, round_counter)
    print()


def multidevice_guess_round(playerInfo, serverhost, round_counter):
    clearConsole()
    print("Waiting for other players...")
    audioStr = serverhost.get_round_data(playerInfo.id, round_counter)
    clearConsole()

    audioStr = binascii.unhexlify(audioStr.encode('utf-8'))
    waveFile = wave.open("./%d/audio-recording.wav" %playerInfo.id, 'wb')
    waveFile.setnchannels(CHANNELS)
    waveFile.setsampwidth(audio.get_sample_size(FORMAT))
    waveFile.setframerate(RATE)
    waveFile.writeframes(audioStr)
    waveFile.close()

    print(Fore.LIGHTRED_EX +"Type your best guess of what the original word was after hearing audio.")
    print(Fore.LIGHTRED_EX +"Ready to hear the recording?")
    ready_check([playerInfo.name], 0)
    local_play_audio(playerInfo.id)


    print(Fore.LIGHTRED_EX +"Type 'replay' to re-hear the audio, or just press enter to continue.")
    localReplayAudioLoop(playerInfo.id)

    print(Fore.LIGHTRED_EX +"Type your answer: ")
    phrase = input()
    serverhost.writeFinalGuess(phrase, playerInfo.id, round_counter)

def multidevice_spectate_games(serverhost, player_num, players, playerInfo): 
	clearConsole()
	for game in range(player_num):
		multidevice_spectate_game(serverhost, player_num, players, game, playerInfo)

def multidevice_spectate_game(serverhost, player_num, players, game, playerInfo): 
    clearConsole()

    init_phrase = serverhost.getInitPhrase(game)
    print("Waiting for other players...")
    final_guess = serverhost.getFinalGuess(game)
    clearConsole()

    print("\nViewing: ")
    #LOOP THROUGH PLAYERS AND THEIR INPUTS ONE BY ONE 

    print("Press enter to proceed")
    input()


    for i in range(player_num):
        if (i==0):
        	print("%s entered:" %players[i], init_phrase)

        elif (i != player_num-1):
            print("Press enter to proceed")
            input()
            print("%s said:" %players[i])

            audioStr = serverhost.getAudio(game, i, 0)
            load_audio_string_to_wave(audioStr, playerInfo)

            local_play_audio(playerInfo.id)
            if (not (i + 1 == player_num - 1 and (player_num % 2 == 1))):
                print("Press enter to proceed")
                input()
                print("%s heard:" %players[i+1])


                audioStr = serverhost.getAudio(game, i, 1)
                load_audio_string_to_wave(audioStr, playerInfo)

                local_play_audio(playerInfo.id)
        else: 
            print("Press enter to proceed")
            input()
            print("%s thought the original word was: " %players[i], final_guess)
            if(init_phrase.lower() == final_guess.lower()):
            	print("And it was indeed ' %s '. Good Job!" %init_phrase)
            else:
            	print("But it really was: ' %s '! \n" %init_phrase)
            if(game == player_num - 1):
                print("Game Over.")
            else:
                print("Press enter to spectate next game.")
            input()




def prep_send_audio_round_data(playerInfo, serverhost, roundNumber):

    wf = wave.open("./%d/audio-recording.wav" %playerInfo.id, 'rb')

    data = wf.readframes(CHUNK)
    b = bytearray()
    while len(data) > 0:
        b.extend(data)
        data = wf.readframes(CHUNK)


    #b = ''.join(chr(x) for x in b)
    hex_data = binascii.hexlify(b)
    str_data = hex_data.decode('utf-8')

    wf.close()

    serverhost.send_audio_round_data([playerInfo.id, roundNumber, str_data])

    

def start_game(player_count):
	round_counter = 0

	print(Fore.LIGHTRED_EX + "Game starting with %d players...\n" %player_count)
	sleep(promptingDelay)

	player_names = []
	for i in range(player_count):
		print(Fore.LIGHTRED_EX + "Enter name for player", i+1, ":")
		player_names.append(input())
		print()

	#Start Round 1
	round_counter += 1
	round1(player_names)
	#End Round 1

	#Start Round 2
	round_counter += 1
	round2(player_names)
	#End Round 2

	#Start Round 3
	#But we will be alternating between reverse and interpret rounds now 
	round_counter += 1
	while round_counter < player_count:
		if round_counter % 2 == 1:
			reverse_round(player_names, round_counter - 1)
		else:
			interpret_round(player_names, round_counter - 1)
		round_counter += 1

	#Start Round player_count
	if player_count % 2 == 0:
		# Extra reverse for even number of player games
		reverse_audio()

	final_guess = guess_round(player_names, round_counter - 1) #store for the recap round
	with open('./localGame/final-guess.txt', 'w') as f: #store for recap round
		f.write(final_guess)

	spectate(player_count, player_names)

def round1(player_names):
	clearConsole()
	prompt_player(player_names, 0)
	print(Fore.LIGHTRED_EX +"%s enter a word:" %player_names[0])
	phrase = input() 
	with open('./localGame/init-phrase.txt', 'w') as f: #store for recap round
		f.write(phrase)
	print()

	return phrase

def round2(player_names):
	clearConsole()
	prompt_player(player_names, 1)
	print(Fore.LIGHTRED_EX + "Record yourself saying this word.")
	sleep(promptingDelay)
	print(get_init_phrase())
	print()
	sleep(promptingDelay)
	print(Fore.LIGHTRED_EX +"Ready to record?")
	ready_check(player_names, 1)
	record_audio()
	print()

def replayAudioLoop(reverse):
	while(input() == "replay"): 
		play_audio(reverse)
	print()

def reverse_round(player_names, i):
	clearConsole()
	prompt_player(player_names, i)
	print(Fore.LIGHTRED_EX +"Record yourself repeating the what you will hear.")
	ready_check(player_names, i)
	reverse_audio()
	play_audio(1)
	

	print(Fore.LIGHTRED_EX +"Type 'replay' to re-hear the audio, or just press enter to start recording.")
	replayAudioLoop(1)

	record_audio()
	print()
	

def interpret_round(player_names, i):
	clearConsole()
	prompt_player(player_names, i)
	print(Fore.LIGHTRED_EX +"Record your best guess of what the original word was after hearing the reversed audio.")
	ready_check(player_names, i)
	reverse_audio()
	play_audio(1)


	print(Fore.LIGHTRED_EX +"Type 'replay' to re-hear the audio, or just press enter to start recording.")
	replayAudioLoop(1)

	record_audio()
	print()

def guess_round(player_names, i):
	clearConsole()
	prompt_player(player_names, i)
	print(Fore.LIGHTRED_EX +"Type your best guess of what the original word was after hearing audio.")
	print(Fore.LIGHTRED_EX +"Ready to hear the recording?")
	ready_check(player_names, i)
	if (len(player_names) % 2 == 0):
		play_audio(1)
	else:
		play_audio(0)


	print(Fore.LIGHTRED_EX +"Type 'replay' to re-hear the audio, or just press enter to continue.")
	if (len(player_names) % 2 == 0):
		replayAudioLoop(1)
	else:
		replayAudioLoop(0)

	print(Fore.LIGHTRED_EX +"Type your answer: ")
	phrase = input()
	
	return phrase

#Helper to play specific file at any given moment
def give_audio(file):
	wf = wave.open(file, 'rb')

	stream = audio.open(
	    format = audio.get_format_from_width(wf.getsampwidth()),
	    channels = wf.getnchannels(),
	    rate = wf.getframerate(),
	    output = True
	)

	data = wf.readframes(CHUNK)
	while len(data) > 0:
	    stream.write(data)
	    data = wf.readframes(CHUNK)
	wf.close()

	stream.close()

def get_init_phrase():
	f = open("./localGame/init-phrase.txt", "r")
	phrase = f.read()
	f.close()
	return phrase

def get_final_guess():
	f = open("./localGame/final-guess.txt", "r")
	phrase = f.read()
	f.close()
	return phrase

#Function to show the proceedings of the game
def spectate(player_num, players): 
    clearConsole()

    init_phrase = get_init_phrase()
    final_guess = get_final_guess()

    print("\nHere is the playback, hope you had fun! ")
    #LOOP THROUGH PLAYERS AND THEIR INPUTS ONE BY ONE 

    print("Press enter to proceed")
    input()


    for i in range(player_num):
        if (i==0):
            print("%s entered:" %players[i], init_phrase)

        elif (i != player_num-1):
            print("Press enter to proceed")
            input()
            print("%s said:" %players[i])
            give_audio("./localGame/"+str(i)+".wav")
            if (not (i + 1 == player_num - 1 and (player_num % 2 == 1))):
            	print("Press enter to proceed")
            	input()
            	print("%s heard:" %players[i+1])
            	give_audio("./localGame/"+str(i)+"-reverse"+".wav")
        else: 
            print("Press enter to proceed")
            input()
            print("%s thought the original word was: " %players[i], final_guess)
            if(init_phrase.lower() == final_guess.lower()):
            	print("And it was indeed ' %s '. Good Job!" %init_phrase)
            else:
            	print("But it really was: ' %s '! \n" %init_phrase)

            print("Game over.")
            print("Press enter to proceed")
            input()



def prompt_player(player_names, i):
	click.clear()
	prompt_player_text = text2art(player_names[i], font='small')
	print(f"{Fore.LIGHTGREEN_EX}{prompt_player_text}")
	print(Fore.LIGHTRED_EX + "Pass the device to %s...\n" %player_names[i])
	ready_check(player_names, i)

def ready_check(player_names, i):
	print(Fore.LIGHTRED_EX + "%s type \"ready\" to continue..." %player_names[i])
	while(input() != "ready"):
		pass
	print()

def localReplayAudioLoop(playerID):
	while(input() == "replay"): 
		local_play_audio(playerID)
	print()

def local_play_audio(playerID):

	wf = wave.open("./%d/audio-recording.wav" %playerID, 'rb')

	stream = audio.open(
	    format = audio.get_format_from_width(wf.getsampwidth()),
	    channels = wf.getnchannels(),
	    rate = wf.getframerate(),
	    output = True
	)

	data = wf.readframes(CHUNK)
	while len(data) > 0:
	    stream.write(data)
	    data = wf.readframes(CHUNK)
	
	wf.close()
	stream.close()

def local_record_audio(playerID):

	stream = audio.open(format=FORMAT, channels=CHANNELS,
                rate=RATE, input=True,input_device_index = audioDevice,
                frames_per_buffer=CHUNK)
	print (Fore.LIGHTRED_EX + "recording started")
	Recordframes = []
	

	timer_recording = threading.Thread(target=waitingBar, args=(2,), daemon=True)
	timer_recording.start()
	for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
	    data = stream.read(CHUNK)
	    Recordframes.append(data)
	print (Fore.LIGHTRED_EX + "recording stopped")
	 
	stream.stop_stream()
	stream.close()

	waveFile = wave.open("./%d/audio-recording.wav" %playerID, 'wb')
	waveFile.setnchannels(CHANNELS)
	waveFile.setsampwidth(audio.get_sample_size(FORMAT))
	waveFile.setframerate(RATE)
	waveFile.writeframes(b''.join(Recordframes))
	waveFile.close()

def record_audio():

	stream = audio.open(format=FORMAT, channels=CHANNELS,
                rate=RATE, input=True,input_device_index = audioDevice,
                frames_per_buffer=CHUNK)
	print (Fore.LIGHTRED_EX + "recording started")
	Recordframes = []
	

	timer_recording = threading.Thread(target=waitingBar, args=(2,), daemon=True)
	timer_recording.start()
	for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
	    data = stream.read(CHUNK)
	    Recordframes.append(data)
	print (Fore.LIGHTRED_EX + "recording stopped")
	 
	stream.stop_stream()
	stream.close()

	# Makes this function recognize our global variables
	global FILE_NUM

	FILE_NUM += 1

	waveFile = wave.open("./localGame/" + str(FILE_NUM)+".wav", 'wb')
	waveFile.setnchannels(CHANNELS)
	waveFile.setsampwidth(audio.get_sample_size(FORMAT))
	waveFile.setframerate(RATE)
	waveFile.writeframes(b''.join(Recordframes))
	waveFile.close()

def reverse_audio():
	wf = wave.open("./localGame/"+str(FILE_NUM)+".wav", 'rb')

	stream = audio.open(
	    format = audio.get_format_from_width(wf.getsampwidth()),
	    channels = wf.getnchannels(),
	    rate = wf.getframerate(),
	    output = True
	)

	recording = []
	data = wf.readframes(CHUNK)
	while len(data) > 0:
	    data = wf.readframes(CHUNK)
	    recording.append(data)
	wf.close()

	recording = recording[::-1]
	waveFile = wave.open("./localGame/"+str(FILE_NUM)+"-reverse"+".wav", 'wb') #concatenate file number here
	waveFile.setnchannels(CHANNELS)
	waveFile.setsampwidth(audio.get_sample_size(FORMAT))
	waveFile.setframerate(RATE)
	waveFile.writeframes(b''.join(recording))
	waveFile.close()

	stream.close()

def play_audio(reverse):
	if (reverse):
		wf = wave.open("./localGame/"+str(FILE_NUM)+"-reverse"+".wav", 'rb')
	else:
		wf = wave.open("./localGame/"+str(FILE_NUM)+".wav", 'rb')

	stream = audio.open(
	    format = audio.get_format_from_width(wf.getsampwidth()),
	    channels = wf.getnchannels(),
	    rate = wf.getframerate(),
	    output = True
	)

	data = wf.readframes(CHUNK)
	while len(data) > 0:
	    stream.write(data)
	    data = wf.readframes(CHUNK)
	
	wf.close()
	stream.close()

def setupAudioDevice():
	print("\t\t\t\t\t\t----------------------RECORDING DEVICE LIST---------------------")
	info = audio.get_host_api_info_by_index(0)
	numdevices = info.get('deviceCount')
	for i in range(0, numdevices):
	        if (audio.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) > 0:
	            print("\t\t\t\t\t\tInput Device id ", i, " - ", audio.get_device_info_by_host_api_device_index(0, i).get('name'))

	print("\t\t\t\t\t\t----------------------------------------------------------------")

	index = click.prompt(Fore.LIGHTRED_EX + 'Choose your audio device', type=int)
	print("recording via index "+str(index))
	click.clear()
	return index

def clearConsole():
    command = 'clear'
    if os.name in ('nt', 'dos'):  # If Machine is running on Windows, use cls
        command = 'cls'
    os.system(command)

def main():
	titleScreen()

if __name__ == "__main__":

	audioDevice = setupAudioDevice();
	main()
