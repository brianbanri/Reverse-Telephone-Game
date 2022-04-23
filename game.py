import pyaudio
import wave
import time
import os
import shutil
import click
from colorama import Fore, Back
from colorama import init as colorama_init
from art import text2art
from tqdm import trange
from time import sleep


# Globals Variables for Audio Setup
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 512
RECORD_SECONDS = 3
audio = pyaudio.PyAudio()
FILE_NUM = 0
promptingDelay = 1

#Beginning of CLUI
os.system('mode con: cols=170 lines=40')
click.clear()
colorama_init(autoreset=True)
Art = text2art("                                               WELCOME", font='big')
print(f"{Fore.LIGHTGREEN_EX}{Art}")


# Function that puts the players on the title screen to start or join a game
def titleScreen():
	clearConsole()

	# UI Prompt
	titleScreen = text2art("                       WELCOME                   TO \nREVERSE TELEPHONE GAME", font='big')
	print(f"{Fore.LIGHTGREEN_EX}{titleScreen}")
	time.sleep(promptingDelay)
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
	time.sleep(promptingDelay)
	print(Fore.LIGHTRED_EX + "Enter number of players:")
	player_count = int(input())
	print()
	if(player_count < 4):
		print(Fore.LIGHTRED_EX +"You need 4 or more players to play this game.")
		time.sleep(promptingDelay)
		print(Fore.LIGHTRED_EX +"Exiting to title screen...")
		shutil.rmtree("./localGame", ignore_errors=False, onerror=None)
		titleScreen()
	else:
		start_game(player_count)
		shutil.rmtree("./localGame", ignore_errors=False, onerror=None)



def host_game():
	clearConsole()
	print("hosting game...\n")

def join_game():
	clearConsole()
	print("joining game...\n")

def start_game(player_count):
	round_counter = 0

	print(Fore.LIGHTRED_EX + "Game starting with %d players...\n" %player_count)
	time.sleep(promptingDelay)

	player_names = []
	for i in range(player_count):
		print(Fore.LIGHTRED_EX + "Enter name for player", i+1, ":")
		player_names.append(input())
		print()

	#Start Round 1
	round_counter += 1
	sentence = round1(player_names)
	#End Round 1

	#Start Round 2
	round_counter += 1
	audio = round2(sentence, player_names)
	#End Round 2

	#Start Round 3
	#But we will be alternating between reverse and interpret rounds now 
	round_counter += 1
	while round_counter < player_count:
		if round_counter % 2 == 1:
			audio = reverse_round(player_names, round_counter - 1)
		else:
			audio = interpret_round(player_names, round_counter - 1)
		round_counter += 1

	#Start Round player_count
	if player_count % 2 == 0:
		# Extra reverse for even number of player games
		reverse_audio()

	final_guess = guess_round(player_names, round_counter - 1) #store for the recap round
	with open('./localGame/final-guess.txt', 'w') as f: #store for recap round
		f.write(final_guess)

	spectate(sentence, final_guess, player_count, player_names)

def round1(player_names):
	clearConsole()
	prompt_player(player_names, 0)
	print(Fore.LIGHTRED_EX +"%s enter a word:" %player_names[0])
	sentence = input() 
	with open('./localGame/init-phrase.txt', 'w') as f: #store for recap round
		f.write(sentence)
	print()

	return sentence

def round2(sentence, player_names):
	clearConsole()
	prompt_player(player_names, 1)
	print(Fore.LIGHTRED_EX + "Record yourself saying this word.")
	time.sleep(promptingDelay)
	print(sentence)
	print()
	time.sleep(promptingDelay)
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
	print(Fore.LIGHTRED_EX +"Record yourself saying repeating the word you will hear.")
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
	sentence = input()
	
	return sentence

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
def spectate(beginning, end, player_num, players): 
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
			if (i + 1 != player_num - 1):
				print("Press enter to proceed")
				input()
				print("%s heard:" %players[i+1])
				give_audio("./localGame/"+str(i)+"-reverse"+".wav")
		else:
			print("Press enter to proceed")
			input()
			print("%s thought the original word was: " %players[i], final_guess)
			if(init_phrase.lower() == final_guess.lower()):
				print("And it was indeed ' %s '. Good Job!" %beginning)
			else:
				print("But it really was: ' %s '! \n" %beginning)



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

def record_audio():

	stream = audio.open(format=FORMAT, channels=CHANNELS,
                rate=RATE, input=True,input_device_index = audioDevice,
                frames_per_buffer=CHUNK)
	print ("recording started")
	Recordframes = []
	 
	for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
	    data = stream.read(CHUNK)
	    Recordframes.append(data)
	print ("recording stopped")
	 
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

#test